# watchlist_utils.py

import logging
from nlp_processor import analyze_sentiment, tag_keywords
from finnhub_api import get_quote, get_company_profile
from mcp_score import calculate_mcp_score
from entry_target import calculate_trade_plan
from logger import format_log_data

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
        logging.exception(f"❌ Error processing entry: {getattr(entry, 'title', 'Unknown')}")
        return None
