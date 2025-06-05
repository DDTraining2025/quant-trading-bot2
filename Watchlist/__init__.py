import os
import logging
import datetime
import azure.functions as func

from rss_listener import fetch_rss_entries
from discord_poster import send_discord_alert
from logger import log_alert
from watchlist_utils import process_entry

WATCHLIST_WEBHOOK = os.getenv("DISCORDWATCHLIST")

FEEDS = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]

def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"🌙 [Watchlist] Triggered at {now.isoformat()}")

    try:
        entries = fetch_rss_entries(FEEDS)
        logging.info(f"📥 Fetched {len(entries)} PRs")

        strong_setups = []

        for entry in entries:
            result = process_entry(entry)
            if result:
                msg, log_data = result
                strong_setups.append(msg)
                log_alert(log_data)

        if strong_setups:
            today = now.strftime("%B %d")
            send_discord_alert(f"🌙 **Watchlist – {today}**", webhook_url=WATCHLIST_WEBHOOK)
            for msg in strong_setups:
                send_discord_alert(msg, webhook_url=WATCHLIST_WEBHOOK)
        else:
            logging.info("ℹ️ No strong setups for watchlist")

    except Exception as e:
        logging.exception("❌ Watchlist function failed")
