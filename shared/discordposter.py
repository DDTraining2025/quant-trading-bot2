import os
import requests
import logging
logging.basicConfig(level=logging.INFO)

def send_discord_alert(ticker, headline, url):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("Discord webhook URL not set!")
    content = f"**[{ticker}]** {headline}\n<{url}>"
    data = {"content": content}
    requests.post(webhook_url, json=data, timeout=5)
