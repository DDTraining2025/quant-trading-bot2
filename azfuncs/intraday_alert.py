import os
import json
import hashlib
import logging
import datetime

import azure.functions as func
from azure.functions import Blueprint, TimerRequest

from azfuncs.rss_listener import fetch_rss_entries
from nlpprocessor import analyze_sentiment, tag_keywords
from finnhubapi import get_quote, get_company_profile
from mcpscore import calculate_mcp_score
from entrytarget import calculate_trade_plan
from discordposter import format_alert, send_discord_alert
from logger import log_outcome as log_to_csv, format_log_data
from dbwriter import log_alert as log_to_db

bp = Blueprint()

# your two RSS feeds, and a local cache file for dedupe
FEEDS = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]
SEEN_FILE = "/tmp/seen_prs.json"
WEBHOOK_ENV = "discordwebhooknews"


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


@bp.function_name(name="IntradayAlert")
@bp.timer_trigger(
    name="intraday_timer",
    schedule="0 */5 * * * *",   # every 5 minutes
    run_on_startup=False
)
def intraday_alert(timer: TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"📡 [Intraday] Triggered at {now.isoformat()}")

    seen_ids = load_seen_ids()
    try:
        entries = fetch_rss_entries(FEEDS)
        logging.info(f"📥 Retrieved {len(entries)} PRs")

        for entry in entries:
            uid = hashlib.md5((entry["title"] + entry["link"]).encode()).hexdigest()
            if uid in seen_ids:
                continue
            seen_ids.add(uid)

            # extract $TICKER
            words   = entry["title"].split()
            tickers = [w[1:].upper() for w in words if w.startswith("$") and len(w) <= 6]
            if not tickers:
                continue
            ticker = tickers[0]

            # NLP
            sentiment, confidence = analyze_sentiment(entry["title"])
            keywords = tag_keywords(entry["summary"] + " " + entry["title"])

            # market data
            quote      = get_quote(ticker)
            profile    = get_company_profile(ticker)
            price      = round(quote.get("c", 0), 2)
            volume     = quote.get("v", 0)
            market_cap = profile.get("marketCapitalization", 0)

            # filter microcaps
            if not price or market_cap > 50_000_000:
                continue

            # score & plan
            mcp_score = calculate_mcp_score(keywords, sentiment, volume, ticker)
            plan      = calculate_trade_plan(price)
            entry_p   = plan["entry"]
            stop_p    = plan["stop"]
            target_p  = plan["target"]

            # session label
            hour   = now.hour
            session = "Pre-Market" if hour < 9 else "Regular" if hour < 16 else "After-Hours"

            # format & send
            discord_url = os.environ.get(WEBHOOK_ENV)
            message     = format_alert(
                ticker=ticker,
                headline=entry["title"],
                price=price,
                volume=volume,
                target=target_p,
                stop=stop_p,
                score=mcp_score,
                sentiment=f"{sentiment} ({confidence:.2f})",
                session=session,
                pr_url=entry["link"]
            )
            send_discord_alert(message, webhook_url=discord_url)
            logging.info(f"✅ Alert posted for ${ticker}")

            # record it
            log_to_csv(format_log_data(
                ticker=ticker,
                price=price,
                volume=volume,
                sentiment=sentiment,
                sentiment_confidence=round(confidence, 4),
                mcp_score=mcp_score,
                session=session,
                label="intraday"
            ))
            log_to_db(
                ticker=ticker,
                score=mcp_score,
                entry=entry_p,
                stop=stop_p,
                target=target_p,
                pr_title=entry["title"]
            )

    except Exception:
        logging.exception("❌ Intraday alert failed")

    save_seen_ids(seen_ids)
