import os
import logging
import datetime
import json
import hashlib

import azure.functions as func

from rss_listener import fetch_rss_entries
from nlp_processor import analyze_sentiment, tag_keywords
from finnhub_api import get_quote, get_company_profile
from mcp_score import calculate_mcp_score
from entry_target import calculate_trade_plan
from discord_poster import format_alert, send_discord_alert
from logger import log_alert, format_log_data

# RSS sources
FEEDS = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]

# File-based deduplication cache
SEEN_FILE = "/tmp/seen_prs.json"

def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

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

            # Deduplication based on headline+link hash
            uid = hashlib.md5((headline + link).encode()).hexdigest()
            if uid in seen_ids:
                logging.debug(f"⏭ Skipping duplicate PR: {headline}")
                continue
            seen_ids.add(uid)

            # Extract ticker (e.g., "$XYZ")
            words = headline.split()
            tickers = [w[1:] for w in words if w.startswith("$") and len(w) <= 6]
            if not tickers:
                continue
            ticker = tickers[0].upper()

            # NLP sentiment and keywords
            sentiment, confidence = analyze_sentiment(headline)
            keywords = tag_keywords(summary + " " + headline)

            # Market data
            quote = get_quote(ticker)
            profile = get_company_profile(ticker)
            price = round(quote.get("c", 0), 2)
            volume = quote.get("v", 0)
            market_cap = profile.get("marketCapitalization", 0)

            if not price or market_cap > 50:
                logging.info(f"⏭ Skipping ${ticker} — price/market cap check failed")
                continue

            # MCP scoring and trade setup
            mcp = calculate_mcp_score(keywords, sentiment, volume, ticker)
            entry, stop, target = calculate_trade_plan(price)

            # Market session labeling
            hour = now.hour
            if hour < 9:
                session = "Pre-Market"
            elif hour < 16:
                session = "Regular"
            else:
                session = "After-Hours"

            # Format and post alert
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

            # Log to CSV with FinBERT confidence
            data = format_log_data(
                ticker=ticker,
                price=price,
                volume=volume,
                sentiment=sentiment,
                sentiment_confidence=round(confidence, 4),
                mcp_score=mcp,
                session=session,
                label="Intraday"
            )
            log_alert(data)

    except Exception as e:
        logging.exception("❌ Intraday alert failed")

    # Persist updated seen PRs
    save_seen_ids(seen_ids)
