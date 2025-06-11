import azure.functions as func
import logging
import datetime
from shared.benzingaapi import fetch_recent_news
from shared.dbwriter import log_alert
from shared.discordposter import send_discord_alert

def main(mytimer: func.TimerRequest) -> None:
    logging.info("🔁 Intraday alert triggered")

    try: 
        # Calculate 'published_since' (5 minutes ago)
        utc_now = datetime.datetime.utcnow()
        published_since = (utc_now - datetime.timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
        
        news = fetch_recent_news(published_since)
        seen_ids = set()
        
        if not news:
            logging.info("No Benzinga news found in the last 5 minutes.")
            send_discord_alert("NONE", "No news in the last 5 minutes.", "")
            return
            
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
