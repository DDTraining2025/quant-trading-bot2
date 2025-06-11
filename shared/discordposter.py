import requests
import os
import logging

def send_discord_alert(news):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        logging.error("Discord webhook not set!")
        return

    message = {
        "content": f"**{news.get('title','[No title]')}**\n{news.get('url','')}\nPublished: {news.get('created','')}"
    }
    try:
        resp = requests.post(webhook_url, json=message, timeout=10)
        if resp.status_code != 204:
            logging.error("Failed to send Discord alert: %s %s", resp.status_code, resp.text)
    except Exception as e:
        logging.exception("Exception sending Discord alert")
