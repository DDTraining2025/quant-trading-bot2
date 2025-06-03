import os
import requests
from datetime import datetime

DISCORD_URL = os.getenv("DISCORDWEBHOOKNEWS")

def send_discord_alert(message, webhook_url=DISCORD_URL):
    if not webhook_url:
        raise ValueError("Missing Discord webhook URL")
    response = requests.post(webhook_url, json={"content": message})
    response.raise_for_status()

def format_alert(ticker, headline, price, volume, target, stop, score, sentiment, session, pr_url):
    now = datetime.utcnow()
    et_time = now.strftime("%-I:%M %p ET")
    gmt_time = now.strftime("%H:%M GMT")
    return (
        f"🚨 ${ticker} | {headline}\n"
        f"🕒 {et_time} / {gmt_time} | Session: {session}\n"
        f"Price: ${price} | Target: ${target} | Stop: ${stop}\n"
        f"Volume: {volume:,}\n"
        f"MCP Score: {score} | Sentiment: {sentiment}\n"
        f"📎 [View PR]({pr_url})"
    )
