import requests
from bs4 import BeautifulSoup
import time
import random

class JobKoreaScraper:
    BASE_URL = "https://www.jobkorea.co.kr/Search/"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search(self, keywords):
        results = []
        for keyword in keywords:
            print(f"Searching JobKorea for: {keyword}")
            try:
                params = {
                    "stext": keyword,
                    "careerType": 1, # Entry level (신입)
                    "tabType": "recruit",
                    "Page_No": 1
                }
                
                response = requests.get(self.BASE_URL, params=params, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    items = soup.select(".list-default .list-post")
                    
                    for item in items:
                        try:
                            title_tag = item.select_one(".post-list-info .title")
                            company_tag = item.select_one(".post-list-corp .name")
                            date_tag = item.select_one(".post-list-info .date")
                            link_tag = item.select_one(".post-list-info .title")
                            
                            if not title_tag: continue
                            
                            title = title_tag.text.strip()
                            company = company_tag.text.strip()
                            link = "https://www.jobkorea.co.kr" + link_tag['href']
                            job_id = link.split("GI_No=")[1].split("&")[0] if "GI_No=" in link else str(hash(link))
                            deadline = date_tag.text.strip()
                            
                            results.append({
                                "id": f"jk_{job_id}",
                                "site": "JobKorea",
                                "title": title,
                                "company": company,
                                "link": link,
                                "deadline": deadline,
                                "hidden_keyword": keyword
                            })
                        except Exception as e:
                            continue
                            
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error scraping JobKorea for {keyword}: {e}")
                
        return results

    def get_details(self, url):
        # Placeholder for full text extraction
        return ""
