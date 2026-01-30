import requests
from bs4 import BeautifulSoup
import time
import random

class SaraminScraper:
    BASE_URL = "https://www.saramin.co.kr/zf_user/search/recruit"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search(self, keywords):
        results = []
        for keyword in keywords:
            print(f"Searching Saramin for: {keyword}")
            try:
                # Basic parameters for Saramin search
                params = {
                    "searchType": "search",
                    "searchword": keyword,
                    "recruitPage": 1,
                    "recruitSort": "relation",
                    "recruitPageCount": 20,  # Get top 20 relevant
                    "exp_cd": 1,  # 신입 필터 (1=신입, 2=경력, 3=신입/경력)
                    "exp_none": 1  # 경력무관도 포함
                }
                
                response = requests.get(self.BASE_URL, params=params, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    items = soup.select(".item_recruit")
                    
                    for item in items:
                        try:
                            title_tag = item.select_one(".job_tit a")
                            company_tag = item.select_one(".corp_name a")
                            date_tag = item.select_one(".job_date .date")
                            
                            if not title_tag: continue
                            
                            job_id = title_tag['href'].split("rec_idx=")[1].split("&")[0]
                            title = title_tag.text.strip()
                            company = company_tag.text.strip()
                            link = "https://www.saramin.co.kr" + title_tag['href']
                            deadline = date_tag.text.strip() # needs parsing later
                            
                            results.append({
                                "id": f"saramin_{job_id}",
                                "site": "Saramin",
                                "title": title,
                                "company": company,
                                "link": link,
                                "deadline": deadline,
                                "hidden_keyword": keyword
                            })
                        except Exception as e:
                            print(f"Error parsing item: {e}")
                            continue
                
                # Be nice to the server
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error scraping Saramin for {keyword}: {e}")
                
        return results

    def get_details(self, url):
        # Implementation for getting full text will be needed for AI Summary
        # For now, we return empty string to avoid blocking
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            # This selector often changes, need to be generic
            content = soup.select_one(".wrap_jv_cont")
            return content.text.strip() if content else ""
        except:
            return ""
