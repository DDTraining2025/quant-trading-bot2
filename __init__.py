import os
from datetime import datetime
import pytz
from discord_poster import send_to_discord
from logger import write_log
from watchlist import get_qualified_stocks, format_watchlist_message

def main(req):
    print("🔧 Manually triggered watchlist.")
    run_watchlist_logic()
    return {"status": "done"}

def run_watchlist_logic():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    today_str = now.strftime('%B %d')

    qualified_stocks = get_qualified_stocks()

    if qualified_stocks:
        message = format_watchlist_message(qualified_stocks)
    else:
        message = f"🌙 Watchlist – {today_str}
No stocks met the MCP/sentiment criteria for inclusion."
        write_log({
            "date": today_str,
            "ticker": "N/A",
            "event": "No qualified PRs",
            "mcp_score": 0,
            "sentiment": "N/A",
            "session": "N/A",
            "status": "nil"
        })

    webhook = os.getenv('DISCORD_WATCHLIST_WEBHOOK')
    send_to_discord(message, webhook)