import os
import logging
import datetime
import azure.functions as func

from rss_listener import fetch_rss_entries
from nlp_processor import analyze_sentiment, tag_keywords
from finnhub_api import get_quote, get_company_profile
from mcp_score import calculate_mcp_score
from entry_target import calculate_trade_plan
from discord_poster import send_discord_alert
from logger import log_alert, format_log_data

WATCHLIST_WEBHOOK = os.getenv("DISCORDWATCHLIST")

FEEDS = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]


def process_entry(entry):
    try:
        headline = entry.title
        link = entry.link
        summary = entry.summary

        tickers = [w[1:] for w in headline.split() if w.startswith("$") and len(w) <= 6]
        if not tickers:
            return None

        ticker = tickers[0].upper()
        sentiment, _ = analyze_sentiment(headline)
        keywords = tag_keywords(summary + " " + headline)

        quote = get_quote(ticker)
        profile = get_company_profile(ticker)
        price = round(quote.get("c", 0), 2)
        volume = quote.get("v", 0)
        market_cap = profile.get("marketCapitalization", 0)

        if not price or market_cap > 50:
            return None

        mcp = calculate_mcp_score(keywords, sentiment, volume, ticker)
        trade_plan = calculate_trade_plan(price)
        if not trade_plan or len(trade_plan) != 3:
            logging.warning(f"⚠️ Invalid trade plan for {ticker} at price {price}")
            return None

        entry_price, stop, target = trade_plan

        if mcp < 7.5:
            return None

        msg = (
            f"📌 ${ticker} | PR: {headline}\n"
            f"Closed: ${price} | Session: Regular\n"
            f"MCP: {mcp} | Sentiment: {sentiment} | Volume: {volume:,}\n"
            f"Setup for tomorrow: Entry ${entry_price}, Target ${target}, Stop ${stop}\n"
            f"📎 [View PR]({link})"
        )

        log_data = format_log_data(
            ticker=ticker,
            price=price,
            volume=volume,
            sentiment=sentiment,
            mcp_score=mcp,
            session="Regular",
            label="Watchlist"
        )

        return msg, log_data

    except Exception as e:
        logging.exception(f"❌ Error processing entry: {entry.title}")
        return None


def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"🌙 [Watchlist] Triggered at {now.isoformat()}")

    try:
        entries = fetch_rss_entries(FEEDS)
        logging.info(f"📥 Fetched {len(entries)} PRs")

        strong_setups = []

        for entry in entries:
            result = process_entry(entry)
            if result:
                msg, log_data = result
                strong_setups.append(msg)
                log_alert(log_data)

        if strong_setups:
            today = now.strftime("%B %d")
            send_discord_alert(f"🌙 **Watchlist – {today}**", webhook_url=WATCHLIST_WEBHOOK)
            for msg in strong_setups:
                send_discord_alert(msg, webhook_url=WATCHLIST_WEBHOOK)
        else:
            logging.info("ℹ️ No strong setups for watchlist")

    except Exception as e:
        logging.exception("❌ Watchlist function failed")
