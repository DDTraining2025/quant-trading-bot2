import os
import requests
import datetime

FINNHUB_KEY = os.getenv("finnhub")

def fetch_recent_prs():
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
    resp = requests.get(url)
    data = resp.json()

    results = []
    for item in data:
        ts = datetime.datetime.utcfromtimestamp(item["datetime"])
        if (datetime.datetime.utcnow() - ts).total_seconds() < 300:
            if "symbol" in item:
                results.append({
                    "ticker": item["symbol"],
                    "headline": item["headline"],
                    "url": item["url"],
                    "timestamp": ts.isoformat()
                })
    return results

def get_market_cap(ticker):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_KEY}"
    r = requests.get(url).json()
    return r.get("marketCapitalization", 0) * 1_000_000
