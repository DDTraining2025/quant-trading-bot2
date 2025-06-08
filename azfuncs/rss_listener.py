import feedparser
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import logging

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
                    # Parse published timestamp into a UTC-aware datetime…
                    published_dt = datetime(
                        *entry.published_parsed[:6],
                        tzinfo=timezone.utc
                    ).astimezone(ZoneInfo("America/New_York"))

                    # …and only keep items from the last 5 minutes
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
