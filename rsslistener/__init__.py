import feedparser
import azure.functions as func
from datetime import datetime, timezone, timedelta
import pytz
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# RSS Feeds to watch
feed_urls = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]

def fetch_rss_entries(feed_urls):
    entries = []
    now_et = datetime.now(pytz.timezone("US/Eastern"))

    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            logging.info(f"[RSS FETCH] {url} returned {len(parsed.entries)} entries")

            for entry in parsed.entries:
                try:
                    published = entry.get("published", "") or entry.get("updated", "")
                    published_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(pytz.timezone("US/Eastern"))

                    # Only keep PRs published in the last 5 minutes
                    if (now_et - published_dt) <= timedelta(minutes=5):
                        entries.append({
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "published_et": published_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "published_gmt": published_dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                            "source": url
                        })
                except Exception as inner_ex:
                    logging.error(f"[RSS PARSE ERROR] Skipped entry: {inner_ex}")

        except Exception as ex:
            logging.error(f"[RSS ERROR] Failed to parse {url}: {ex}")

    return entries

def main(timer: func.TimerRequest) -> None:
    logging.info("RSS Listener triggered")
    entries = fetch_rss_entries(feed_urls)
    logging.info(f"Fetched {len(entries)} recent entries")

    for entry in entries:
        logging.info(f"Title: {entry['title']}, Published ET: {entry['published_et']}, Link: {entry['link']}")
