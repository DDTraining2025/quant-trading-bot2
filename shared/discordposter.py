import os
import requests
import logging

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_alert(ticker, headline, url):
    if not DISCORD_WEBHOOK_URL:
        logging.error("[Discord] Webhook URL is not set!")
        return
    content = f"🚨 **{ticker}**\n**{headline}**\n<{url}>"
    data = {"content": content}
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=5)
        if resp.status_code == 204 or resp.status_code == 200:
            logging.info(f"[Discord] Alert sent for {ticker}: {headline}")
        else:
            logging.error(f"[Discord] Failed to send alert: {resp.status_code} {resp.text}")
    except Exception as e:
        logging.error(f"[Discord] Error sending alert: {e}")
