import os
import requests
import logging
from datetime import datetime

# Get the Discord webhook URL from environment variable
DISCORD_URL = os.getenv("DISCORDWEBHOOKNEWS")

def send_discord_alert(message, webhook_url=DISCORD_URL):
    """
    Sends a message to the Discord webhook.

    Parameters:
    - message (str): The text message to send.
    - webhook_url (str): The Discord webhook URL, defaults to environment variable.

    Raises:
    - ValueError: If webhook_url is missing.
    - Logs any HTTP failure responses.
    """
    if not webhook_url:
        raise ValueError("❌ Missing Discord webhook URL")

    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)

        if not response.ok:
            # Log Discord errors with status and body
            logging.error(f"❌ Discord post failed: {response.status_code} - {response.text}")
        else:
            logging.info(f"✅ Discord alert posted successfully")
    except requests.RequestException as e:
        logging.exception(f"❌ Exception posting to Discord: {e}")

def format_alert(ticker, headline, price, volume, target, stop, score, sentiment, session, pr_url):
    """
    Formats the PR alert into a Markdown-friendly Discord message.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g. 'XYZ')
    - headline (str): PR headline
    - price (float): Current price
    - volume (int): Current volume
    - target (float): Trade target
    - stop (float): Suggested stop
    - score (float): MCP score
    - sentiment (str): Sentiment result (e.g. 'Positive')
    - session (str): Market session (e.g. 'Pre-Market')
    - pr_url (str): Link to the original press release

    Returns:
    - str: Formatted Discord message
    """
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
