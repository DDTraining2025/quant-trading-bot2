# File: azfuncs/outcome_tracker.py

import os
import logging
import datetime
import azure.functions as func

from logger import load_today_alerts, log_outcome
from finnhubapi import get_daily_high_low_close
from discordposter import send_discord_alert

bp = func.Blueprint()
WEBHOOK_ENV = "discordreview"  # Env var name for outcome summary webhook

@bp.function_name(name="OutcomeTracker")
@bp.timer_trigger(schedule="0 15 21 * * *")  # Daily at 21:15 UTC (4:15 PM ET)
def outcome_tracker(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"📊 [OutcomeTracker] Triggered at {now.isoformat()}")

    try:
        alerts = load_today_alerts()
        if not alerts:
            logging.info("📭 No alerts found to evaluate.")
            return

        # Send header summary
        send_discord_alert(WEBHOOK_ENV, "📊 **Daily Outcome Summary**")

        for alert in alerts:
            ticker = alert["ticker"]
            entry = alert["entry"]
            stop = alert["stop"]
            target = alert["target"]
            session = alert["session"]
            mcp_score = alert.get("mcp_score")

            high, close = get_daily_high_low_close(ticker)
            if high is None or close is None:
                logging.warning(f"⚠️ Missing market data for {ticker}")
                continue

            status = classify_outcome(entry, stop, target, high, close)
            gain_pct = round(((close - entry) / entry) * 100, 1)

            message = (
                f"📈 ${ticker} | Entry: ${entry:.2f} → High: ${high:.2f} → Close: ${close:.2f}\n"
                f"Gain: {gain_pct:+.1f}% | Session: {session} | MCP: {mcp_score}\n"
                f"Result: {status}"
            )
            send_discord_alert(WEBHOOK_ENV, message)

            # Log outcome to CSV (or DB, depending on your logger)
            log_outcome({
                "ticker": ticker,
                "entry": entry,
                "high": high,
                "close": close,
                "gain_pct": gain_pct,
                "result": status,
                "session": session
            })

    except Exception:
        logging.exception("❌ Error during outcome tracking")


def classify_outcome(
    entry: float,
    stop: float,
    target: float,
    high: float,
    close: float
) -> str:
    """
    Determine outcome given entry/stop/target vs high and close.
    """
    if high >= target:
        return "✅ Win"
    if close < stop:
        return "❌ Loss"
    return "➖ Flat"
