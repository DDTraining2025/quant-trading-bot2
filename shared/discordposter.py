import os
import requests

WEBHOOK = os.getenv("discordwebhooknews")

def send_discord_alert(ticker, title, url):
    payload = {
        "content": f"📰 **{ticker}** - {title}\n<{url}>"
    }
    requests.post(WEBHOOK, json=payload)