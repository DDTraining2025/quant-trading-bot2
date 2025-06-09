import requests
import logging

def get_news_items(api_key: str):
    url = f"https://finnhub.io/api/v1/news?category=general&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logging.info(f"[FINN] ✅ Retrieved {len(data)} news items")
        return data
    except Exception as e:
        logging.error(f"[FINN] ❌ Failed to fetch news: {e}")
        return []

def get_market_cap(symbol: str, api_key: str) -> float:
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        profile = response.json()
        cap = profile.get("marketCapitalization", 0.0) * 1_000_000
        logging.info(f"[FINN] 💰 Market cap for {symbol}: ${cap:,.0f}")
        return cap
    except Exception as e:
        logging.warning(f"[FINN] ❌ Failed to get market cap for {symbol}: {e}")
        return 0.0
