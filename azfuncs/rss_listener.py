import logging
import feedparser

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import azure.functions as func
from azure.functions import Blueprint, TimerRequest

bp = Blueprint()

logging.basicConfig(level=logging.INFO)

def fetch_rss_entries(feed_urls: list[str]) -> list[dict]:
    entries: list[dict] = []
    now_et = datetime.now(ZoneInfo("America/New_York"))

    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            logging.info(f"[RSS FETCH] {url} returned {len(parsed.entries)} entries")
            for entry in parsed.entries:
                try:
                    published_dt = (
                        datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        .astimezone(ZoneInfo("America/New_York"))
                    )

                    if (now_et - published_dt) <= timedelta(minutes=5):
                        entries.append({
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "published_et": published_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "published_gmt": published_dt.astimezone(timezone.utc)
                                                      .strftime("%Y-%m-%d %H:%M:%S"),
                            "source": url
                        })
                except Exception as inner_ex:
                    logging.error(f"[RSS PARSE ERROR] Skipped entry: {inner_ex}")
        except Exception as ex:
            logging.error(f"[RSS ERROR] Failed to parse {url}: {ex}")

    return entries

@bp.timer_trigger(
    name="rss_timer",
    schedule="0 */5 * * * *",  # every 5 minutes
    run_on_startup=True
)
def main(timer: TimerRequest) -> None:
    FEEDS = [
        "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
        "https://www.prnewswire.com/rss/technology-latest-news.rss"
    ]

    entries = fetch_rss_entries(FEEDS)
    logging.info(f"[RSS LISTENER] {len(entries)} new entries found")

    # …now hand off to your intraday or alert logic,
    # e.g. push into a queue, log them, or call another module…
    for e in entries:
        logging.info(f" → {e['published_et']} | {e['title']}")

