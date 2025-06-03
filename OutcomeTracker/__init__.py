import os
import logging
import datetime
import azure.functions as func

from logger import load_today_alerts, log_outcome
from finnhub_api import get_daily_high_low_close
from discord_poster import send_discord_alert

DISCORD_REVIEW_WEBHOOK = os.getenv("DISCORDREVIEW")

def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"📊 [OutcomeTracker] Triggered at {now.isoformat()}")

    try:
        alerts = load_today_alerts()

        if not alerts:
            logging.info("📭 No alerts found to evaluate.")
            return

        results = []

        for alert in alerts:
            ticker = alert.get("ticker")
            entry = alert.get("entry")
            stop = alert.get("stop")
            target = alert.get("target")
            session = alert.get("session")
            mcp = alert.get("mcp_score")

            # Get OHLC data
            high, close = get_daily_high_low_close(ticker)
            if high is None or close is None:
                continue

            status = classify_outcome(entry, stop, target, high, close)
            gain_pct = round(((close - entry) / entry) * 100, 1)

            message = (
                f"📈 ${ticker} | Alert: ${entry} → High: ${high} → Close: ${close}\n"
                f"Gain: {gain_pct:+.1f}% | Session: {session} | MCP: {mcp}\n"
                f"Result: {status}"
            )
            results.append(message)

            log_outcome({
                "ticker": ticker,
                "entry": entry,
                "high": high,
                "close": close,
                "result": status,
                "session": session,
                "gain_pct": gain_pct
            })

        if results:
            send_discord_alert("📊 **Daily Outcome Summary**", webhook_url=DISCORD_REVIEW_WEBHOOK)
            for msg in results:
                send_discord_alert(msg, webhook_url=DISCORD_REVIEW_WEBHOOK)
        else:
            logging.info("⚠️ No outcome data available")

    except Exception as e:
        logging.exception("❌ Error during outcome tracking")

def classify_outcome(entry, stop, target, high, close):
    if high >= target:
        return "✅ Win"
    elif close < stop:
        return "❌ Loss"
    else:
        return "➖ Flat"
