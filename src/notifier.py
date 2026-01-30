import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import Config

class Notifier:
    def __init__(self):
        self.slack_url = Config.SLACK_WEBHOOK_URL
        
    def send_slack_alert(self, new_jobs_count, deadline_jobs, page_url):
        if not self.slack_url:
            print("No Slack Webhook URL provided.")
            return

        message = f"📢 *오늘의 채용 브리핑* 📢\n\n"
        
        if deadline_jobs:
            message += f"🚨 *오늘 마감 공고 ({len(deadline_jobs)}건)*\n"
            for job in deadline_jobs[:3]: # Top 3 only
                message += f"• <{job['link']}|{job['title']}> ({job['company']})\n"
            if len(deadline_jobs) > 3:
                message += f"• 외 {len(deadline_jobs)-3}건...\n"
            message += "\n"
            
        message += f"✨ *신규 발견 공고:* {new_jobs_count}건\n"
        message += f"👉 <{page_url}|전체 공고 및 AI 자소서 전략 보러가기>\n"
        
        try:
            requests.post(self.slack_url, json={"text": message})
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
