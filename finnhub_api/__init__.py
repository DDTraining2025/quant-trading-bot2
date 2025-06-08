import os
import requests
from logger import log_error

FINNHUB_API_KEY = os.getenv("FINNHUB")
BASE_URL = "https://finnhub.io/api/v1"

def fetch_quote(ticker: str) -> dict:
    try:
        url = f"{BASE_URL}/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"Error fetching quote for {ticker}", e)
        return {}

def fetch_company_profile(ticker: str) -> dict:
    try:
        url = f"{BASE_URL}/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"Error fetching company profile for {ticker}", e)
        return {}

def fetch_float_and_shares_outstanding(ticker: str) -> dict:
    try:
        url = f"{BASE_URL}/stock/metric?symbol={ticker}&metric=all&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "float": data.get("metric", {}).get("float"),
            "shares_outstanding": data.get("metric", {}).get("sharesOutstanding")
        }
    except Exception as e:
        log_error(f"Error fetching float data for {ticker}", e)
        return {}
