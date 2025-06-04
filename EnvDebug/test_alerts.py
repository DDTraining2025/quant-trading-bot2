# test_alerts.py

import os
import datetime
import requests
import csv
from pathlib import Path

DISCORD_WEBHOOKS = {
    "news": os.getenv("DISCORD-WEBHOOK-NEWS"),
    "watchlist": os.getenv("DISCORD-Watchlist"),
    "review": os.getenv("DISCORD-Review"),
}

LOG_PATH = Path("logs") / "mcp_test_log.csv"

def post_to_discord(channel, message):
    webhook_url = DISCORD_WEBHOOKS.get(channel)
    if not webhook_url:
        print(f"❌ No webhook configured for {channel}")
        return

    resp = requests.post(webhook_url, json={"content": message})
    if resp.ok:
        print(f"✅ Sent to {channel}")
    else:
        print(f"❌ Failed for {channel}: {resp.status_code} - {resp.text}")

def log_alert(channel, symbol, headline, mcp_score, sentiment, session, price, volume):
    LOG_PATH.parent.mkdir(exist_ok=True)
    row = {
        "timestamp_et": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_gmt": datetime.datetime.u_
