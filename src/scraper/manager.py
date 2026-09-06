from src.config import Config
from src.scraper.saramin import SaraminScraper
from src.scraper.jobkorea import JobKoreaScraper
from src.scraper.linkareer import LinkareerScraper
from src.scraper.incruit import IncruitScraper
from src.scraper.wanted import WantedScraper
from src.logic.job_relevance import evaluate_data_job, is_data_candidate, matched_roles, search_category
from collections import deque
import time

class ScraperManager:
    def __init__(self):
        self.scrapers = [
            SaraminScraper(),      # 사람인
            JobKoreaScraper(),     # 잡코리아
            LinkareerScraper(),    # 링커리어
            IncruitScraper(),      # 인크루트
            WantedScraper()        # 원티드
        ]
        self.detail_cache = {}
        self.detail_requests = 0
        self.detail_started_at = None

    def run_all(self):
        all_jobs = []

        # 모든 카테고리의 키워드 수집
        targets = []
        for category, keywords in Config.KEYWORDS.items():
            targets.extend(keywords)

        # 중복 키워드 제거
        targets = list(dict.fromkeys(targets))

        print(f"🔍 Starting scrape for {len(targets)} keywords across {len(self.scrapers)} sites...")
        print(f"📍 Sites: 사람인, 잡코리아, 링커리어, 인크루트, 원티드")
        
        for scraper in self.scrapers:
            scraper_name = scraper.__class__.__name__
            try:
                print(f"\n▶ Running {scraper_name}...")
                jobs = scraper.search(targets)
                print(f"  ✅ {scraper_name}: {len(jobs)}개 공고 수집")
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  ❌ {scraper_name} failed: {e}")
        
        print(f"\n📊 Total collected: {len(all_jobs)} jobs")
        return all_jobs

    def review_jobs(self, jobs, fetch_details=True):
        """신규 및 저장 공고에 같은 데이터 직군 기준을 적용한다."""
        if fetch_details:
            # 한 사이트가 예산을 모두 사용하지 않도록 번갈아 읽는다.
            # 명확한 직무명을 먼저 확인하고, 포괄적인 제목도 JD로 검토한다.
            buckets = {}
            for job in sorted(jobs, key=lambda j: not bool(matched_roles(j.get('title', '')))):
                if is_data_candidate(job) and not job.get('description'):
                    buckets.setdefault(job.get('site', ''), deque()).append(job)
            while any(buckets.values()):
                if self.detail_requests >= Config.DATA_DETAIL_LIMIT:
                    break
                if (self.detail_started_at is not None and
                        time.monotonic() - self.detail_started_at >= Config.DATA_DETAIL_BUDGET_SECONDS):
                    break
                for bucket in buckets.values():
                    if bucket:
                        self._get_details(bucket.popleft())
        accepted = []
        seen = set()
        rejected = 0
        for original in jobs:
            if original['id'] in seen:
                continue
            seen.add(original['id'])
            job = dict(original)
            if is_data_candidate(job):
                if not job.get('description') and fetch_details:
                    job['description'] = self._get_details(job)
                job['data_relevance'] = evaluate_data_job(job)
                if not job['data_relevance']['matched']:
                    rejected += 1
                    continue
                job['category'] = 'Data'
            else:
                job['category'] = search_category(job)
            accepted.append(job)
        print(f"Data relevance: {rejected}개 제외, {len(accepted)}개 유지")
        return accepted

    def _get_details(self, job):
        key = job['id']
        if key in self.detail_cache:
            return self.detail_cache[key]
        if self.detail_started_at is None:
            self.detail_started_at = time.monotonic()
        if (self.detail_requests >= Config.DATA_DETAIL_LIMIT or
                time.monotonic() - self.detail_started_at >= Config.DATA_DETAIL_BUDGET_SECONDS):
            return ''
        scraper = next((s for s in self.scrapers
                        if s.__class__.__name__ == job.get('site', '') + 'Scraper'), None)
        if scraper is None or not job.get('link'):
            return ''
        self.detail_requests += 1
        try:
            text = scraper.get_details(job['link']) or ''
        except Exception as exc:
            print(f"JD 조회 실패 ({job['site']}): {type(exc).__name__}")
            text = ''
        self.detail_cache[key] = text[:20000]
        return self.detail_cache[key]
