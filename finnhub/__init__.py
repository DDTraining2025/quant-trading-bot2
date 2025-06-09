# finnhub/__init__.py

import os
import requests
from datetime import datetime, timedelta
from logger import log_error

# Load Finnhub API key from environment
FINNHUB_API_KEY = os.getenv("FINNHUB")
BASE_URL = "https://finnhub.io/api/v1"

def get_news_items(minutes=5):
    """
    Fetch general market news from Finnhub, filter for recent articles.
    """
    try:
        url = f"{BASE_URL}/news?category=general&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        all_news = response.json()

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        recent_items = []
        for item in all_news:
            ts = item.get("datetime")
            if not ts:
                continue

            published_dt = datetime.utcfromtimestamp(ts)
            if published_dt < cutoff:
                continue

            recent_items.append({
                "title": item.get("headline", ""),
                "url": item.get("url", ""),
                "published_utc": published_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "source": item.get("source", ""),
                "ticker": item.get("related", "")
            })

        return recent_items

    except Exception as e:
        log_error("❌ Error fetching news items from Finnhub", e)
        return []

def get_market_cap(ticker):
    """
    Fetch market capitalization for a given ticker.
    """
    try:
        url = f"{BASE_URL}/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("marketCapitalization")
    except Exception as e:
        log_error(f"❌ Error fetching market cap for {ticker}", e)
        return None
