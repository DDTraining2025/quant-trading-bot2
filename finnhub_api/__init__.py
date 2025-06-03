import requests
import os
import datetime
import logging

FINNHUB_KEY = os.getenv("Finnhub")

def get_daily_high_low_close(ticker):
    try:
        now = datetime.datetime.utcnow()
        from_time = int(datetime.datetime(now.year, now.month, now.day).timestamp())
        to_time = int(now.timestamp())

        url = (
            f"https://finnhub.io/api/v1/stock/candle"
            f"?symbol={ticker}&resolution=5&from={from_time}&to={to_time}&token={FINNHUB_KEY}"
        )

        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        if data.get("s") != "ok":
            logging.warning(f"Finnhub returned non-ok status for {ticker}: {data}")
            return None, None

        highs = data.get("h", [])
        closes = data.get("c", [])

        if not highs or not closes:
            return None, None

        return round(max(highs), 2), round(closes[-1], 2)

    except Exception as e:
        logging.exception(f"Failed to fetch candle data for {ticker}")
        return None, None
