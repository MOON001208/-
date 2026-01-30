from src.config import Config
from src.scraper.saramin import SaraminScraper
from src.scraper.jobkorea import JobKoreaScraper
# Import others later

class ScraperManager:
    def __init__(self):
        self.scrapers = [
            SaraminScraper(),
            JobKoreaScraper()
            # Add others
        ]
        
    def run_all(self):
        all_jobs = []
        
        # Determine target keywords based on user config (For now we run ALL targets)
        # Or we can split by category if needed
        
        targets = []
        for category, keywords in Config.KEYWORDS.items():
            targets.extend(keywords)
            
        print(f"Starting scrape for {len(targets)} keywords across {len(self.scrapers)} sites...")
        
        for scraper in self.scrapers:
            try:
                # To avoid spamming, let's limit keywords per run or assume scraper handles it
                # For this MVP, we pass all keywords to each scraper
                # Optimization: Deduplicate keywords if needed
                jobs = scraper.search(targets)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Scraper failed: {e}")
                
        return all_jobs
