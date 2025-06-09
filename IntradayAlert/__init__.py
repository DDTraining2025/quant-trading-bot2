import logging
import azure.functions as func

from shared.finnhubapi import fetch_recent_prs, get_market_cap
from shared.discordposter import send_discord_alert
from shared.dbwriter import log_alert

def main(mytimer: func.TimerRequest) -> None:
    logging.info("🔁 Intraday alert triggered.")

    prs = fetch_recent_prs()
    for pr in prs:
        ticker = pr["ticker"]
        title = pr["headline"]
        url = pr["url"]
        ts = pr["timestamp"]

        market_cap = get_market_cap(ticker)
        if not market_cap or market_cap > 50_000_000:
            continue

        send_discord_alert(ticker, title, url)
        log_alert(ticker, title, url, ts, market_cap)
