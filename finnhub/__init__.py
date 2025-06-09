import os
import requests

FINNHUB_TOKEN = os.getenv("FINHUB")

def get_quote(ticker: str):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_TOKEN}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()
