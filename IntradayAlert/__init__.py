import os
import logging
from datetime import datetime, timedelta
from benzinga import BenzingaClient

# Benzinga API key from environment
API_KEY = os.getenv("Bezinga")


def fetch_recent_prs(window_minutes=5, seen_ids=None):
    """
    Fetch press releases via Benzinga Python client within the past window_minutes.
    Filters out items whose 'id' is in seen_ids to avoid duplicates.
    Returns a list of dicts: {id, ticker, headline, url}.

    Args:
        window_minutes (int): lookback window in minutes
        seen_ids (set): optional set of Benzinga news IDs to exclude
    """
    client = BenzingaClient(API_KEY)
    now = datetime.utcnow()
    since = now - timedelta(minutes=window_minutes)
    since_ts = int(since.timestamp())
    seen = seen_ids or set()

    try:
        items = client.news.get_news(
            updated_since=since_ts,
            content_types=["Press Release"],
            page_size=100
        )
        logging.info(f"Fetched {len(items)} items from Benzinga")
    except Exception as e:
        logging.error(f"Error fetching news from Benzinga: {e}")
        return []

    recent_prs = []
    for item in items:
        news_id = item.get("id")
        if not news_id or news_id in seen:
            continue

        pub_str = item.get("created")  # e.g. '2025-06-11T11:45:00Z'
        try:
            pub_dt = datetime.strptime(pub_str, "%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            continue

        if since <= pub_dt <= now:
            ticker = item.get("ticker")
            headline = item.get("title")
            url = item.get("url")
            if ticker and headline and url:
                recent_prs.append({
                    "id": news_id,
                    "ticker": ticker,
                    "headline": headline,
                    "url": url
                })
                seen.add(news_id)

    logging.info(f"Returning {len(recent_prs)} new PRs, filtered duplicates")
    return recent_prs
