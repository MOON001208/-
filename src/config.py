import os

class Config:
    # 3 categories as requested
    KEYWORDS = {
        "Data": ["데이터 분석", "Data Analyst", "데이터 엔지니어", "Data Scientist", "머신러닝", "AI"],
        "Accounting": ["회계", "재무", "세무", "결산"],
        "HR": ["인사", "HRM", "HRD", "총무", "채용"]
    }
    
    # Secrets (Environment Variables)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
    
    # Paths
    DATA_FILE = "docs/jobs.json"
