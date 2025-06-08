import os
import logging
import datetime
import json
import hashlib
import azure.functions as func

from rsslistener import fetch_rss_entries
from nlpprocessor import analyze_sentiment, tag_keywords
from finnhubapi import get_quote, get_company_profile
from mcpscore import calculate_mcp_score
from entrytarget import calculate_trade_plan
from discordposter import format_alert, send_discord_alert
from logger import log_alert as log_to_csv, format_log_data
from dbwriter import log_alert as log_to_db

bp = func.Blueprint()

FEEDS = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]

SEEN_FILE = "/tmp/seen_prs.json"

def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

@bp.function_name(name="IntradayAlert")
@bp.timer_trigger(schedule="0 */5 * * * *")  # every 5 minutes
def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"📡 [Intraday] Triggered at {now.isoformat()}")

    seen_ids = load_seen_ids()

    try:
        entries = fetch_rss_entries(FEEDS)
        logging.info(f"📥 Retrieved {len(entries)} PRs")

        for entry in entries:
            headline = entry.title
            link = entry.link
            published = entry.published
            summary = entry.summary

            logging.debug(f"🔎 Processing: {headline}")

            uid = hashlib.md5((headline + link).encode()).hexdigest()
            if uid in seen_ids:
                logging.debug(f"⏭ Skipping duplicate PR: {headline}")
                continue
            seen_ids.add(uid)

            words = headline.split()
            tickers = [w[1:] for w in words if w.startswith("$") and len(w) <= 6]
            if not tickers:
                continue
            ticker = tickers[0].upper()

            sentiment, confidence = analyze_sentiment(headline)
            keywords = tag_keywords(summary + " " + headline)

            quote = get_quote(ticker)
            profile = get_company_profile(ticker)
            price = round(quote.get("c", 0), 2)
            volume = quote.get("v", 0)
            market_cap = profile.get("marketCapitalization", 0)

            if not price or market_cap > 50:
                logging.info(f"⏭ Skipping ${ticker} — price/market cap check failed")
                continue

            mcp = calculate_mcp_score(keywords, sentiment, volume, ticker)
            entry, stop, target = calculate_trade_plan(price)

            hour = now.hour
            if hour < 9:
                session = "Pre-Market"
            elif hour < 16:
                session = "Regular"
            else:
                session = "After-Hours"

            message = format_alert(
                ticker=ticker,
                headline=headline,
                price=price,
                volume=volume,
                target=target,
                stop=stop,
                score=mcp,
                sentiment=f"{sentiment} ({confidence:.2f})",
                session=session,
                pr_url=link
            )
            send_discord_alert(message)
            logging.info(f"✅ Alert posted for ${ticker}")

            log_to_csv(format_log_data(
                ticker=ticker,
                price=price,
                volume=volume,
                sentiment=sentiment,
                sentiment_confidence=round(confidence, 4),
                mcp_score=mcp,
                session=session,
                label="Intraday"
            ))

            log_to_db(
                ticker=ticker,
                score=mcp,
                entry=entry,
                stop=stop,
                target=target,
                pr_title=headline
            )

    except Exception:
        logging.exception("❌ Intraday alert failed")

    save_seen_ids(seen_ids)
