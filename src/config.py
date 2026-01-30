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
    
    # 카테고리별 이메일 수신자 설정
    # 각 카테고리별로 다른 사람에게 보낼 수 있음
    GMAIL_RECIPIENTS = {
        "Data": os.getenv("GMAIL_TO_DATA"),           # 데이터 직군 공고 받을 사람
        "Accounting": os.getenv("GMAIL_TO_ACCOUNTING"), # 회계 직군 공고 받을 사람  
        "HR": os.getenv("GMAIL_TO_HR"),               # 인사 직군 공고 받을 사람
        "All": os.getenv("GMAIL_TO")                  # 전체 공고 받을 사람 (기존 호환)
    }
    
    # Paths
    DATA_FILE = "docs/jobs.json"
