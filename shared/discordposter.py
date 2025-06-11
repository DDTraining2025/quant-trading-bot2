import os
import logging
import requests

# Discord webhook URL from environment
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_alert(news_id, ticker, headline, url, timestamp=None):
    """
    Send a structured alert to Discord with Benzinga news details.

    Args:
        news_id (int): Benzinga news identifier
        ticker (str): Stock symbol
        headline (str): PR headline
        url (str): Link to full PR
        timestamp (str): Optional ISO timestamp string for footer
    """
    embed = {
        "title": f"{ticker} ▶️ New PR #{news_id}",
        "description": headline,
        "url": url,
        "color": 5814783,
    }

    # Include timestamp in footer if provided
    if timestamp:
        embed["footer"] = {"text": f"Published: {timestamp}"}

    payload = {"embeds": [embed]}

    try:
        resp = requests.post(WEBHOOK_URL, json=payload)
        resp.raise_for_status()
        logging.info(f"Discord alert sent for {ticker} (ID: {news_id})")
    except Exception as e:
        logging.error(f"Error sending Discord alert for {ticker} (ID: {news_id}): {e}")
        raise
