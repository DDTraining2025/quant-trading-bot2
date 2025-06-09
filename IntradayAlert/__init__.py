# intraday_alert.py
import logging
from finnhubnews import fetch_general_news
from finnhubapi import get_company_profile
from dbwriter import log_alert
from discordposter import send_discord_alert, send_no_news_message

def run_intraday_alert():
    logging.info("[INTRADAY] 🔁 Fetching recent PRs from Finnhub...")
    news_items = fetch_general_news(minutes=5)

    if not news_items:
        logging.info("[INTRADAY] No new PRs or API limit reached.")
        send_no_news_message("No news items returned by API or outside PR window.")
        return

    count_valid = 0

    for item in news_items:
        headline = item.get("title", "").strip()
        url = item.get("url", "").strip()
        published_time = item.get("published_utc")
        source = item.get("source", "")
        ticker_field = item.get("ticker", "").strip()

        # Basic sanity checks
        if not ticker_field or not headline or not url:
            logging.warning(f"[SKIP] Incomplete PR: ticker={ticker_field}, headline={headline}")
            continue

        # Handle multi-ticker case (e.g. "ABC,XYZ")
        ticker = ticker_field.split(",")[0].strip().upper()

        try:
            profile = get_company_profile(ticker)
            market_cap = profile.get("marketCapitalization")

            if not market_cap or market_cap > 50:
                logging.info(f"[FILTER] Skipping {ticker} – Market Cap: {market_cap}")
                continue

            # ✅ PASSED FILTERS
            count_valid += 1
            logging.info(f"[ALERT] {ticker} – ${market_cap:.1f}M – {headline}")

            # 🧾 Log to DB
            log_alert({
                "ticker": ticker,
                "headline": headline,
                "url": url,
                "timestamp": published_time,
                "market_cap": market_cap,
                "source": source,
                "sentiment": "N/A",
                "mcp_score": None
            })

            # 📢 Send Discord Alert
            send_discord_alert({
                "ticker": ticker,
                "headline": headline,
