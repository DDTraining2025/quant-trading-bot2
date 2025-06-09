import os
import logging
from finn import get_news_items, get_market_cap
from discordposter import send_discord_alert
from dbwriter import log_alert

def run_intraday_alert():
    logging.info("[ALERT] 🚨 Starting intraday alert workflow")

    # Load API key from environment
    finnhub_key = os.environ.get("finnhub")
    if not finnhub_key:
        logging.error("[ALERT] ❌ Missing 'finnhub' API key in environment")
        return

    logging.info("[ALERT] 🔑 Loaded Finnhub API key")

    # Step 1: Get news items
    try:
        news_items = get_news_items(finnhub_key)
        logging.info(f"[ALERT] 📰 Retrieved {len(news_items)} news items from Finnhub")
    except Exception as e:
        logging.error(f"[ALERT] ❌ Failed to fetch news: {e}")
        return

    if not news_items:
        logging.info("[ALERT] ⚠️ No news found in this cycle")
        return

    # Step 2: Filter microcaps and alert
    count_posted = 0
    for news in news_items:
        symbol = news.get("symbol")
        if not symbol:
            logging.warning("[ALERT] ❌ News item missing 'symbol': skipping")
            continue

        try:
            market_cap = get_market_cap(symbol, finnhub_key)
            logging.info(f"[ALERT] 💰 {symbol} market cap = ${market_cap:,.2f}")
        except Exception as e:
            logging.warning(f"[ALERT] ❌ Couldn't fetch market cap for {symbol}: {e}")
            continue

        if market_cap > 50_000_000:
            logging.info(f"[ALERT] ⛔ Skipping {symbol} (market cap too high)")
            continue

        # Step 3: Send Discord alert
        try:
            send_discord_alert(news)
            count_posted += 1
            logging.info(f"[ALERT] ✅ Sent alert for {symbol}")
        except Exception as e:
            logging.error(f"[ALERT] ❌ Failed to send Discord alert for {symbol}: {e}")

        # Step 4: Log to DB
        try:
            log_alert(news)
            logging.info(f"[ALERT] 🗃️ Logged alert for {symbol} to DB")
        except Exception as e:
            logging.warning(f"[ALERT] ⚠️ DB logging failed for {symbol}: {e}")

    logging.info(f"[ALERT] ✅ Done. Sent {count_posted} alert(s) this cycle.")
