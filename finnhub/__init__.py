# finnhub/__init__.py

import os
import requests
from datetime import datetime, timedelta
from logger import log_error

FINNHUB_API_KEY = os.getenv("FINNHUB")
BASE_URL = "https://finnhub.io/api/v1"

def get_news_items(minutes=5):
    try:
        url = f"{BASE_URL}/news?category=general&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        all_news = response.json()

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            {
                "title": n.get("headline"),
                "url": n.get("url"),
                "published_utc": n.get("datetime"),
                "source": n.get("source"),
                "ticker": n.get("related")
            }
            for n in all_news
            if n.get("datetime") and datetime.utcfromtimestamp(n["datetime"]) > cutoff
        ]
    except Exception as e:
        log_error("Failed to fetch Finnhub news", e)
        return []

def get_market_cap(ticker: str):
    try:
        url = f"{BASE_URL}/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("marketCapitalization")
    except Exception as e:
        log_error(f"Error fetching market cap for {ticker}", e)
        return None
