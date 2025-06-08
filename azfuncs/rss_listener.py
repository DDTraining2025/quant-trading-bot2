import os
import json
import hashlib
import logging
import datetime
import azure.functions as func

from rsslistener import fetch_rss_entries
from nlpprocessor import analyze_sentiment, tag_keywords
from finnhubapi import get_quote, get_company_profile
from mcpscore import calculate_mcp_score
from entrytarget import calculate_trade_plan
from discordposter import format_alert, send_discord_alert
from logger import log_outcome as log_to_csv, format_log_data
from dbwriter import log_alert as log_to_db

bp = func.Blueprint()

FEEDS = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]
SEEN_FILE = "/tmp/seen_prs.json"
WEBHOOK_ENV = "discordwebhooknews"  # Env var for real-time alerts

def load_seen_ids() -> set[str]:
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            logging.warning("Could not load seen PRs file; starting fresh.")
    return set()

def save_seen_ids(seen: set[str]) -> None:
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen), f)
    except Exception:
        logging.warning("Failed to save seen PRs file.")

@bp.function_name(name="RssListener")
@bp.timer_trigger(schedule="0 */5 * * * *")  # every 5 minutes
def rss_listener(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"📡 [RSSListener] Triggered at {now.isoformat()}")

    seen_ids = load_seen_ids()

    try:
        entries = fetch_rss_entries(FEEDS)
        logging.info(f"📥 Retrieved {len(entries)} PRs")

        for entry in entries:
            headline = entry.title
            link = entry.link
            summary = entry.summary

            uid = hashlib.md5((headline + link).encode()).hexdigest()
            if uid in seen_ids:
                logging.debug(f"⏭ Skipping duplicate PR: {headline}")
                continue
            seen_ids.add(uid)

            # Extract ticker symbols like $ABC
            tickers = [w[1:].upper() for w in headline.split() if w.startswith("$") and len(w) <= 6]
            if not tickers:
                continue
            ticker = tickers[0]

            # Perform NLP analysis
            sentiment, confidence = analyze_sentiment(headline)
            keywords = tag_keywords(f"{summary} {headline}")

            # Fetch market data
            quote = get_quote(ticker)
            profile = get_company_profile(ticker)
            price = round(quote.get("c", 0), 2)
            volume = quote.get("v", 0)
            market_cap = profile.get("marketCapitalization", 0)

            if not price or market_cap > 50_000_000:
                logging.info(f"⏭ Skipping ${ticker}—price/market cap check failed")
                continue

            # Score and trade plan
            mcp_score = calculate_mcp_score(keywords, sentiment, volume, ticker)
            plan = calculate_trade_plan(price)
            entry_price = plan["entry"]
            stop_price = plan["stop"]
            target_price = plan["target"]

            # Determine trading session
            hour = now.hour
            session = "Pre-Market" if hour < 9 else "Regular" if hour < 16 else "After-Hours"

            # Format and send Discord alert
            message = format_alert(
                ticker=ticker,
                headline=headline,
                price=price,
                volume=volume,
                target=target_price,
                stop=stop_price,
                score=mcp_score,
                sentiment=f"{sentiment} ({confidence:.2f})",
                session=session,
                pr_url=link
            )
            send_discord_alert(WEBHOOK_ENV, message)
            logging.info(f"✅ RSS alert posted for ${ticker}")

            # Log internally and to DB
            log_to_csv(format_log_data(
                ticker=ticker,
                price=price,
                volume=volume,
                sentiment=sentiment,
                sentiment_confidence=round(confidence, 4),
                mcp_score=mcp_score,
                session=session,
                label="rss"
            ))
            log_to_db(
                ticker=ticker,
                score=mcp_score,
                entry=entry_price,
                stop=stop_price,
                target=target_price,
                pr_title=headline
            )

    except Exception:
        logging.exception("❌ RSSListener failed")

    save_seen_ids(seen_ids)
