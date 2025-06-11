import os
import logging
import azure.functions as func

from shared.finnhubapi import fetch_recent_prs, get_market_cap
from shared.discordposter import send_discord_alert
from shared.dbwriter import already_logged, log_alert

def main(mytimer: func.TimerRequest) -> None:
    logging.info("🔁 Intraday alert triggered")

    # 1) Fetch PRs from Finnhub (last 5 minutes)
    prs = fetch_recent_prs(window_minutes=1)
    logging.info(f"✅ PR list now has {len(prs)} item(s)")

    for pr in prs:
        ticker   = pr["ticker"]
        title    = pr["headline"]
        url      = pr["url"]
        ts       = pr["timestamp"]
        market_cap = get_market_cap(ticker)

        # 2) Skip duplicates in DB
        if already_logged(ticker, title, ts):
            logging.info(f"⏭ Skipping duplicate for {ticker} @ {ts}")
            continue

        # 3) Dispatch to Discord
        try:
            send_discord_alert(ticker, title, url)
            logging.info(f"✅ Discord alert sent for {ticker}")
        except Exception as e:
            logging.error(f"❌ Failed to send Discord alert for {ticker}: {e}")
            # decide whether to continue or break
            continue

        # 4) Log to PostgreSQL
        try:
            log_alert(ticker, title, url, ts, market_cap)
        except Exception:
            logging.error(f"❌ Error logging alert for {ticker}")
            # if you want to retry, you could re-raise here

    logging.info("✅ IntradayAlert run complete")
