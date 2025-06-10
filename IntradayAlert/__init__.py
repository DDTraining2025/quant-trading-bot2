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

        # 🔧 Insert simulated PR for testing
        simulated_pr = {
            "ticker": "TEST",
            "headline": "Simulated FDA Approval",
            "url": "https://example.com/fda-test",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        prs.append(simulated_pr)

        logging.info(f"✅ PR list now has {len(prs)} item(s)")
    except Exception as e:
        logging.error(f"❌ PR fetch error: {e}")
        return

    for pr in prs:
        try:
            ticker = pr["ticker"]
            title = pr["headline"]
            url = pr["url"]
            ts = pr["timestamp"]

            # ⏸️ Market cap filter disabled for now
            market_cap = get_market_cap(ticker) or 0
            logging.info(f"🔎 Market cap for {ticker}: ${market_cap:,}")

            logging.info(f"📤 Dispatching Discord alert for {ticker} - {title}")
            send_discord_alert(ticker, title, url)
            logging.info(f"✅ Discord alert sent for {ticker}")

            logging.info(f"📝 Logging alert to DB: {ticker}")
            log_alert(ticker, title, url, ts, market_cap)

        except Exception as e:
            logging.error(f"❌ Error processing PR: {pr}\n{e}")
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

        # 🔧 Insert simulated PR for testing
        simulated_pr = {
            "ticker": "TEST",
            "headline": "Simulated FDA Approval",
            "url": "https://example.com/fda-test",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        prs.append(simulated_pr)

        logging.info(f"✅ PR list now has {len(prs)} item(s)")
    except Exception as e:
        logging.error(f"❌ PR fetch error: {e}")
        return

    for pr in prs:
        try:
            ticker = pr["ticker"]
            title = pr["headline"]
            url = pr["url"]
            ts = pr["timestamp"]

            # ⏸️ Market cap filter disabled for now
            market_cap = get_market_cap(ticker) or 0
            logging.info(f"🔎 Market cap for {ticker}: ${market_cap:,}")

            logging.info(f"📤 Dispatching Discord alert for {ticker} - {title}")
            send_discord_alert(ticker, title, url)
            logging.info(f"✅ Discord alert sent for {ticker}")

            logging.info(f"📝 Logging alert to DB: {ticker}")
            log_alert(ticker, title, url, ts, market_cap)

        except Exception as e:
            logging.error(f"❌ Error processing PR: {pr}\n{e}")
