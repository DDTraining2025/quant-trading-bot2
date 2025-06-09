# intraday_alert.py
import logging
from finnhubnews import fetch_general_news
from finnhubapi import get_company_profile
from dbwriter import log_alert
from discordposter import send_discord_alert

def run_intraday_alert():
    logging.info("[INTRADAY] 🔁 Fetching news from Finnhub...")
    news_items = fetch_general_news(minutes=5)

    if not news_items:
        logging.info("[INTRADAY] No new PRs or API limit reached.")
        return

    count_valid = 0

    for item in news_items:
        ticker = item.get("ticker", "").split(",")[0].strip().upper()
        if not ticker:
            logging.warning(f"[INTRADAY] Skipping headline with no ticker: {item['title']}")
            continue

        try:
            profile = get_company_profile(ticker)
            market_cap = profile.get("marketCapitalization", 0)

            if not market_cap or market_cap > 50:
                logging.info(f"[FILTER] Skipping {ticker} – Market Cap: ${market_cap}M")
                continue

            # ✅ PASSES FILTER
            count_valid += 1
            logging.info(f"[ALERT] {ticker} – ${market_cap:.1f}M – {item['title']}")

            # 🧾 Log to PostgreSQL
            log_alert({
                "ticker": ticker,
                "headline": item["title"],
                "url": item["url"],
                "timestamp": item["published_utc"],
                "market_cap": market_cap,
                "source": item.get("source", ""),
                "sentiment": "N/A",   # placeholder
                "mcp_score": None     # placeholder
            })

            # 📢 Send to Discord
            send_discord_alert({
                "ticker": ticker,
                "headline": item["title"],
                "market_cap": market_cap,
                "url": item["url"],
                "timestamp": item["published_utc"]
            })

        except Exception as e:
            logging.error(f"[INTRADAY] ❌ Error for {ticker}: {e}")

    if count_valid == 0:
        logging.info("[INTRADAY] No qualifying microcap PRs found.")
