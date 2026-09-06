import sys
import os

# Ensure we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# .env 파일 자동 로드 (로컬 실행용)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env 파일 로드 완료")
except ImportError:
    pass  # dotenv가 없으면 무시 (GitHub Actions에서는 환경변수가 이미 설정됨)

from src.scraper.manager import ScraperManager
from src.logic.data_manager import DataManager
from src.logic.deadline import DeadlineChecker
from src.logic.ai_agent import AIAgent
from src.notifier import Notifier
from src.config import Config

def main():
    print("Starting Job Scout Pipeline...")
    
    # 1. Setup
    data_manager = DataManager(Config.DATA_FILE)
    scraper_manager = ScraperManager()
    ai_agent = AIAgent()
    notifier = Notifier()
    
    # 2. Load Old Data
    existing_jobs = data_manager.load_existing_jobs()
    print(f"Loaded {len(existing_jobs)} existing jobs.")
    
    # 3. Scrape
    scraped_jobs = scraper_manager.run_all()
    print(f"Scraped {len(scraped_jobs)} jobs.")
    
    # 4. 검색 결과뿐 아니라 기존 데이터 공고도 같은 제목/JD 기준으로 재검사한다.
    scraped_jobs = DeadlineChecker.filter_active_jobs(scraped_jobs)
    existing_jobs = DeadlineChecker.filter_active_jobs(existing_jobs)
    # 이미 확보한 JD를 재사용하고 신규 공고부터 상세 조회 예산을 배정한다.
    scraper_manager.detail_cache.update({
        job['id']: job['description'] for job in existing_jobs if job.get('description')
    })
    existing_ids = {job['id'] for job in existing_jobs}
    scraped_jobs.sort(key=lambda job: job['id'] in existing_ids)
    scraped_jobs = scraper_manager.review_jobs(scraped_jobs)
    existing_jobs = scraper_manager.review_jobs(existing_jobs)
    new_jobs = data_manager.filter_new_jobs(scraped_jobs, existing_jobs)
    print(f"Found {len(new_jobs)} new jobs.")
    
    # 5. AI Analysis (Only for new jobs to save cost/time)
    for i, job in enumerate(new_jobs):
        print(f"Analyzing {i+1}/{len(new_jobs)}: {job['title']}")
        # 데이터 공고는 실제 JD로 분석한다. 본문을 못 읽으면 내용을 추측하지 않는다.
        analysis_text = job.get('description', '') if job.get('category') == 'Data' else job['title']
        job['ai_analysis'] = ai_agent.analyze_job(job['title'], analysis_text)
        
    # 6. Merge & Filter
    all_jobs = data_manager.merge_jobs(existing_jobs, new_jobs)
    
    # 기한이 지난 공고 자동 삭제
    print("\n🔍 Checking for expired jobs...")
    all_jobs = DeadlineChecker.filter_active_jobs(all_jobs)
    
    # Check deadlines
    today_deadline_jobs = DeadlineChecker.get_deadline_day_jobs(all_jobs)
    upcoming_jobs = DeadlineChecker.get_upcoming_deadline_jobs(all_jobs) # 내일 마감 (D-1)
    
    # Sort: Deadline Tomorrow (Priority) -> Deadline Today -> Newest
    all_jobs.sort(key=lambda x: (
        DeadlineChecker.is_deadline_tomorrow(x.get('deadline', '')),  # 1순위: 내일 마감
        DeadlineChecker.is_deadline_today(x.get('deadline', '')),     # 2순위: 오늘 마감
        x.get('scraped_at')                                         # 3순위: 최신순
    ), reverse=True)
    
    data_manager.save_jobs(all_jobs)
    print("Data saved.")
    
    # 7. Notify
    # GitHub Pages URL
    repo_name = os.getenv("GITHUB_REPOSITORY", "username/repo")
    page_url = f"https://{repo_name.split('/')[0]}.github.io/{repo_name.split('/')[1]}"
    
    # [TEST MODE]
    if len(new_jobs) == 0 and len(all_jobs) > 0:
        print("📢 [TEST MODE] No new jobs, but sending tailored alerts for testing.")
        test_jobs = all_jobs[:5]
        notifier.send_all_alerts(test_jobs, today_deadline_jobs, upcoming_jobs, page_url)
    elif len(new_jobs) > 0 or len(today_deadline_jobs) > 0 or len(upcoming_jobs) > 0:
        notifier.send_all_alerts(new_jobs, today_deadline_jobs, upcoming_jobs, page_url)
    else:
        print("No new jobs and no deadlines. Skipping notification.")
    
if __name__ == "__main__":
    main()
