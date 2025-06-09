import logging
import os
import requests

def send_discord_alert(news: dict):
    webhook_url = os.environ.get("discordwebhooknews")
    if not webhook_url:
        raise ValueError("Missing 'discordwebhooknews' in environment")

    content = f"📰 **{news.get('symbol')}** – {news.get('headline')}\n<{news.get('url')}>"
    payload = {"content": content}

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            logging.info(f"[DISCORD] ✅ Sent alert for {news.get('symbol')}")
        else:
            logging.warning(f"[DISCORD] ⚠️ Status {response.status_code}: {response.text}")
    except Exception as e:
        logging.error(f"[DISCORD] ❌ Error sending alert: {e}")
