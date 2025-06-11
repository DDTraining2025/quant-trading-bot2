import azure.functions as func
import logging
from shared.benzingaapi import fetch_recent_news
from shared.dbwriter import log_alert
from shared.discordposter import send_discord_alert

def main(mytimer: func.TimerRequest) -> None:
    logging.info("🔁 Intraday alert triggered")

    try:
        news = fetch_recent_news(window_minutes=5)
        seen_ids = set()

        for item in news:
            news_id = str(item.get("id"))
            headline = item.get("title", "")
            url = item.get("url", "")
            tickers = item.get("stocks", [])  # may be a list
            published_utc = item.get("created", "")

            # Avoid duplicate alerts
            if news_id in seen_ids:
                continue
            seen_ids.add(news_id)

            for ticker in tickers or ["???"]:
                send_discord_alert(ticker, headline, url)
                log_alert(news_id, ticker, headline, url, published_utc)

        logging.info(f"✅ Processed {len(news)} Benzinga news articles")
    except Exception as ex:
        logging.error(f"🔥 Exception in IntradayAlert: {ex}")
