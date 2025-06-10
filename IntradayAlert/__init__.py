import logging
import datetime  # ✅ Required for simulated timestamp
import azure.functions as func

from shared.finnhubapi import fetch_recent_prs, get_market_cap
from shared.discordposter import send_discord_alert
from shared.dbwriter import log_alert

def main(mytimer: func.TimerRequest) -> None:
    logging.basicConfig(level=logging.INFO)
    logging.info("🔁 Intraday alert triggered")

    try:
        prs = fetch_recent_prs()
        logging.info(f"✅ PR fetch returned {len(prs)} items")

        # 🔧 Insert simulated PR for testing
        prs.append({
            "ticker": "TEST",
            "headline": "Simulated FDA Approval",
            "url": "https://example.com/fda-test",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

    except Exception as e:
        logging.error(f"❌ PR fetch error: {e}")
        return

    for pr in prs:
        try:
            ticker = pr["ticker"]
            title = pr["headline"]
            url = pr["url"]
            ts = pr["timestamp"]

            market_cap = get_market_cap(ticker)
            if not market_cap or market_cap > 50_000_000:
                market_cap = 45_000_000  # 💡 
                continue

            send_discord_alert(ticker, title, url)
            log_alert(ticker, title, url, ts, market_cap)

        except Exception as e:
            logging.error(f"❌ Error processing PR: {pr}\n{e}")
