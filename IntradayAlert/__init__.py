import logging
import traceback
import datetime
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

        # Add a test PR always
        prs.append({
            "ticker": "TEST",
            "headline": "Simulated FDA Approval",
            "url": "https://example.com/fda-test",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

        for pr in prs:
            try:
                ticker = pr["ticker"]
                title = pr["headline"]
                url = pr["url"]
                ts = pr["timestamp"]

                market_cap = get_market_cap(ticker) or 0
                logging.info(f"📢 Alerting {ticker}: {title}")

                send_discord_alert(ticker, title, url)
                log_alert(ticker, title, url, ts, market_cap)

            except Exception as inner_e:
                logging.error(f"❌ Error processing PR: {pr}\n{traceback.format_exc()}")

    except Exception as outer_e:
        logging.error(f"❌ UNCAUGHT error in intraday alert loop:\n{traceback.format_exc()}")
