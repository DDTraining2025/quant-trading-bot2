import os
import logging
import requests

# ✅ Load webhook securely from environment
WEBHOOK = os.getenv("DISCORDWEBHOOKNEWS")

def send_discord_alert(ticker, headline, url):
    if not WEBHOOK:
        logging.error("❌ DISCORDWEBHOOKNEWS is not set. Cannot send Discord alert.")
        return

    payload = {
        "content": f"📢 **{ticker}**: {headline}\n🔗 {url}"
    }

    try:
        response = requests.post(WEBHOOK, json=payload)
        response.raise_for_status()
        logging.info(f"✅ Alert sent for {ticker}")
    except Exception as e:
        logging.error(f"❌ Failed to send Discord alert: {e}")
