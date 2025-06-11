import requests
import os
import logging

def send_discord_alert(news):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        logging.error("Discord webhook not set!")
        return

    tickers = news.get('stocks', [])
    ticker_str = ', '.join(tickers) if tickers else 'N/A'

    message = {
        "content": (
            f"**{news.get('title', '[No title]')}**\n"
            f"{news.get('url', '')}\n"
            f"Published: {news.get('created', '')}\n"
            f"Tickers: {ticker_str}"
        )
    }
    try:
        resp = requests.post(webhook_url, json=message, timeout=10)
        if resp.status_code != 204:
            logging.error("Failed to send Discord alert: %s %s", resp.status_code, resp.text)
    except Exception as e:
        logging.exception("Exception sending Discord alert")
