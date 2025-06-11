import os
import logging
import datetime
import azure.functions as func

from shared.dbwriter import log_alert
from shared.discordposter import send_discord_alert

import requests

BENZINGA_API_KEY = os.getenv("BEZINGA")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DEDUP_FILE = "/tmp/seen_benzinga_ids.txt"

def load_seen_ids():
    if not os.path.exists(DEDUP_FILE):
        return set()
    with open(DEDUP_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_seen_ids(ids):
    with open(DEDUP_FILE, "w") as f:
        for id in ids:
            f.write(f"{id}\n")

def fetch_benzinga_news():
    # Docs: https://docs.benzinga.com/python-client#returns-news
    url = "https://api.benzinga.com/api/v2/news"
    params = {
        "token": BENZINGA_API_KEY,
        "pagesize": 20,  # Adjust as needed
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "channels": "wires,pressReleases"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("articles", [])
    except Exception as e:
        logging.error(f"[Benzinga] Failed to fetch news: {e}")
        return []

def main(mytimer: func.TimerRequest) -> None:
    utc_now = datetime.datetime.utcnow()
    logging.info(f"🔁 Intraday alert triggered at {utc_now.isoformat()}")

    seen_ids = load_seen_ids()
    news_items = fetch_benzinga_news()
    new_ids = set(seen_ids)

    for item in news_items:
        news_id = str(item.get("id"))
        published = item.get("created", "")[:19]  # ISO format
        headline = item.get("title", "")
        url = item.get("url", "")
        tickers = item.get("stocks", [])
        source = item.get("source", "benzinga")

        # Only process news from last 5 minutes
        try:
            pub_dt = datetime.datetime.strptime(published, "%Y-%m-%dT%H:%M:%S")
        except Exception:
            continue

        if (utc_now - pub_dt).total_seconds() > 300:
            continue

        if news_id in seen_ids:
            continue  # Deduplicate

        # For each ticker, send alert and log
        for ticker in tickers:
            ticker = ticker.upper().strip()
            send_discord_alert(ticker, headline, url)
            log_alert(ticker, headline, url, published, news_id, source)
            logging.info(f"✅ Alert sent & logged for {ticker}: {headline}")

        new_ids.add(news_id)

    save_seen_ids(new_ids)
    logging.info(f"📝 Finished processing Benzinga news batch.")

