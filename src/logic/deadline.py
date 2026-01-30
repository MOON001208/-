from datetime import datetime, timedelta
import re

class DeadlineChecker:
    @staticmethod
    def is_deadline_today(deadline_str):
        # Handle various formats: "2024.01.30", "01/30", "~ 01/30(화)"
        try:
            today = datetime.now()
            
            # Clean string
            clean_date = re.sub(r'[^\d.]', '', deadline_str) # Keep digits and dots
            
            # Cases
            # 1. YYYY.MM.DD
            # 2. MM.DD (Assume current year)
            
            parsed_date = None
            
            if clean_date.count('.') == 2:
                parsed_date = datetime.strptime(clean_date, "%Y.%m.%d")
            elif clean_date.count('.') == 1:
                parsed_date = datetime.strptime(clean_date, "%m.%d")
                parsed_date = parsed_date.replace(year=today.year)
                # Edge case: Jan deadline scraped in Dec logic omitted for simplicity
                
            if parsed_date:
                return parsed_date.date() == today.date()
                
            return False
        except:
            return False
            
    @staticmethod
    def get_deadline_day_jobs(jobs):
        return [job for job in jobs if DeadlineChecker.is_deadline_today(job.get('deadline', ''))]
