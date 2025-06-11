import datetime
import logging
import azure.functions as func
from shared.benzingaapi import fetch_benzinga_news
from shared.discordposter import send_discord_alert

def main(mytimer: func.TimerRequest) -> None:
    utc_now = datetime.datetime.utcnow()
    logging.info("🔁 Intraday alert triggered at %s", utc_now)

    published_since = (utc_now - datetime.timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    news_list = fetch_benzinga_news(published_since)

    # Optional: Smoke test if nothing returned (for CI)
    if not news_list:
        news_list = [{
            "id": "test-smoke",
            "title": "Smoke Test News",
            "url": "https://example.com",
            "created": utc_now.isoformat()
        }]

    seen_ids = set()
    for news in news_list:
        news_id = str(news.get("id"))
        if news_id in seen_ids:
            continue
        seen_ids.add(news_id)
        # You can further filter/validate here!
        send_discord_alert(news)
