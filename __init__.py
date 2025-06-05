import os
from datetime import datetime
import pytz
from discord_poster import send_to_discord
from logger import write_log
from tracker import get_outcome_entries, format_review_summary

def main(req):
    print("🔧 Manually triggered tracker.")
    run_tracker_logic()
    return {"status": "done"}

def run_tracker_logic():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    today_str = now.strftime('%B %d')

    outcome_entries = get_outcome_entries()

    if outcome_entries:
        message = format_review_summary(outcome_entries)
    else:
        message = f"📉 Outcome Summary – {today_str}
No PRs triggered alerts yesterday. Nothing to review."
        write_log({
            "date": today_str,
            "ticker": "N/A",
            "event": "No alerts triggered",
            "mcp_score": 0,
            "sentiment": "N/A",
            "session": "N/A",
            "status": "nil"
        })

    webhook = os.getenv('DISCORD_REVIEW_WEBHOOK')
    send_to_discord(message, webhook)