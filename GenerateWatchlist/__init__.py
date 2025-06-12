import azure.functions as func
import logging
import pandas as pd
import requests
import time
import os
import pg8000
from datetime import datetime

def download_us_listed_tickers():
    nasdaq_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
    nyse_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
    try:
        nasdaq = pd.read_csv(nasdaq_url, sep="|")
        nyse = pd.read_csv(nyse_url, sep="|")
        tickers = pd.concat([nasdaq, nyse])
        tickers = tickers[tickers["Test Issue"] == "N"]
        return tickers["Symbol"].tolist()
    except Exception as e:
        logging.error(f"[Watchlist] Ticker list fetch error: {e}")
        return []

def get_microcap_watchlist(tickers, cap_limit=50_000_000):
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        logging.error("❌ FINNHUB_API_KEY not set.")
        return pd.DataFrame()

    results = []
    for symbol in tickers:
        try:
            url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
            r = requests.get(url, timeout=10)
            data = r.json()
            cap = data.get("marketCapitalization", 0)
            if cap and cap * 1_000_000 < cap_limit:
                results.append({
                    "ticker": symbol,
                    "name": data.get("name", ""),
                    "exchange": data.get("exchange", ""),
                    "market_cap": int(cap * 1_000_000),
                    "sector": data.get("finnhubIndustry", ""),
                    "country": data.get("country", ""),
                    "updated_at": datetime.utcnow()
                })
        except Exception as e:
            logging.warning(f"[Watchlist] Failed to process {symbol}: {e}")
        time.sleep(0.3)
    return pd.DataFrame(results)

def insert_watchlist_to_db(df):
    if df.empty:
        logging.warning("⚠️ No microcaps found.")
        return

    try:
        conn = pg8000.connect(
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST"),
            port=int(os.getenv("PGPORT", "5432")),
            database=os.getenv("PGDATABASE")
        )
        cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO watchlist (ticker, name, exchange, market_cap, sector, country, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (ticker) DO UPDATE SET
                    name = EXCLUDED.name,
                    exchange = EXCLUDED.exchange,
                    market_cap = EXCLUDED.market_cap,
                    sector = EXCLUDED.sector,
                    country = EXCLUDED.country,
                    updated_at = EXCLUDED.updated_at;
            """, tuple(row))
        conn.commit()
        logging.info(f"✅ Inserted/updated {len(df)} tickers into watchlist.")
    except Exception as e:
        logging.error(f"[DB] Error writing to watchlist: {e}")
    finally:
        conn.close()

def main(mytimer: func.TimerRequest) -> None:
    logging.info("📅 GenerateWatchlist triggered")
    tickers = download_us_listed_tickers()
    df = get_microcap_watchlist(tickers)
    insert_watchlist_to_db(df)
