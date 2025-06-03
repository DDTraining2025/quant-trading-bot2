import os
import requests

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

BASE_URL = "https://finnhub.io/api/v1"

def get_quote(symbol):
    url = f"{BASE_URL}/quote"
    params = {"symbol": symbol, "token": FINNHUB_API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

def get_company_profile(symbol):
    url = f"{BASE_URL}/stock/profile2"
    params = {"symbol": symbol, "token": FINNHUB_API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

def get_candles(symbol, resolution="5", count=1):
    from time import time
    end = int(time())
    start = end - (count * 60 * 5)  # last 5-min block(s)
    url = f"{BASE_URL}/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": start,
        "to": end,
        "token": FINNHUB_API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()
