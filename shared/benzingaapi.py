import os
import requests
from datetime import datetime, timedelta, timezone

def fetch_recent_news(window_minutes=5):
    """Fetch Benzinga news within the last `window_minutes`."""
    api_key = os.getenv("BEZINGA")  # Make sure this is set as an environment variable!
    if not api_key:
        raise RuntimeError("BEZINGA API key not found in environment variables.")

    since = (datetime.utcnow() - timedelta(minutes=window_minutes)).replace(tzinfo=timezone.utc).isoformat()
    params = {
        "token": api_key,
        "display_output": "full",
        "published_since": since
        # Add more filters if you like: categories, tickers, etc.
    }
    headers = {"Accept": "application/json"}
    url = "https://api.benzinga.com/api/v2/news"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    news = response.json()
    return news.get("articles", [])
