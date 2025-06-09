# intraday_alert.py

import logging
from finnhub import get_news_items, get_market_cap
from dbwriter import log_alert
from discordposter import send_discord_alert

def run_intraday_alert():
    logging.info("[INTRADAY] 🔁 Fetching recent news items from Finnhub...")
    news_items = get_news_items(minutes=5)

    if not news_items:
        logging.info("[INTRADAY] ⚠️ No new PRs found or API limit reached.")
        return

    count_valid = 0

    for item in news_items:
        headline = item.get("title", "").strip()
        url = item.get("url", "").strip()
        published_time = item.get("published_utc")
        source = item.get("source", "")
        ticker_field = item.get("ticker", "").strip()

        if not ticker_field or not headline or not url:
            logging.warning(f"[SKIP] Incomplete news item: ticker={ticker_field}, headline={headline}")
            continue

        # Handle cases like "TSLA,AAPL" by taking the first ticker
        ticker = ticker_field.split(",")[0].strip().upper()

        try:
            market_cap = get_market_cap(ticker)

            if not market_cap or market_cap > 50:
                logging.info(f"[FILTER] Skipping {ticker} – Market Cap: {market_cap}")
                continue

            count_valid += 1
            logging.info(f"[ALERT] {ticker} – ${market_cap:.1f}M – {headline}")

            # Log to PostgreSQL
            log_alert({
                "ticker": ticker,
                "headline": headline,
                "url": url,
                "timestamp": published_time,
                "market_cap": market_cap,
                "source": source,
                "sentiment": "N/A",   # Placeholder for future NLP
                "mcp_score": None     # Placeholder for MCP v2
            })

            # Notify via Discord
            send_discord_alert({
                "ticker": ticker,
                "headline": headline,
                "market_cap": market_cap,
                "url": url,
                "timestamp": published_time
            })

        except Exception as e:
            logging.error(f"[ERROR] Failed to process PR for {ticker}: {e}")

    if count_valid == 0:
        logging.info("[INTRADAY] No valid microcap PRs found this run.")
