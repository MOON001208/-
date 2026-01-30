import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def load_existing_jobs(self):
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
            
    def save_jobs(self, jobs):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
            
    def filter_new_jobs(self, scraped_jobs, existing_jobs):
        seen_ids = set(job['id'] for job in existing_jobs)
        new_jobs = []
        
        for job in scraped_jobs:
            if job['id'] not in seen_ids:
                # Add scraped date
                job['scraped_at'] = datetime.now().isoformat()
                job['is_new'] = True
                new_jobs.append(job)
                
        return new_jobs

    def merge_jobs(self, existing_jobs, new_jobs):
        # Create a map for easy updates
        job_map = {job['id']: job for job in existing_jobs}
        
        # Mark old jobs as not new
        for job in job_map.values():
            job['is_new'] = False
            
        # Add or update new jobs
        for job in new_jobs:
            job_map[job['id']] = job
            
        return list(job_map.values())
