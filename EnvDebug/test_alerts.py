import os
import datetime
import requests
import csv
import logging
from pathlib import Path

# ✅ Correct ENV keys matching Azure Key Vault bindings
DISCORD_WEBHOOKS = {
    "news": os.getenv("DISCORDWEBHOOKNEWS"),
    "watchlist": os.getenv("DISCORDWATCHLIST"),
    "review": os.getenv("DISCORDREVIEW"),
}

# ✅ Azure Functions: write to /tmp directory
LOG_PATH = Path("/tmp/mcp_test_log.csv")

def post_to_discord(channel, message):
    url = DISCORD_WEBHOOKS.get(channel)
    if not url:
        logging.warning(f"❌ No webhook configured for {channel}")
        return

    logging.info(f"🔗 Posting to {channel} -> {url}")
    try:
        resp = requests.post(url, json={"content": message.strip()})
        if resp.ok:
            logging.info(f"✅ Sent alert to {channel}")
        else:
            logging.error(f"❌ Failed for {channel}: {resp.status_code} - {resp.text}")
    except Exception as e:
        logging.exception(f"❌ Exception while posting to {channel}: {e}")

def log_alert(channel, symbol, headline, mcp_score, sentiment, session, price, volume):
    row = {
        "timestamp_et": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_gmt": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "session": session,
        "ticker": symbol,
        "headline": headline,
        "price": price,
        "volume": volume,
        "mcp_score": mcp_score,
        "sentiment": sentiment,
        "channel": channel
    }

    try:
        write_header = not LOG_PATH.exists()
        with open(LOG_PATH, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        logging.info(f"📄 Logged alert for {symbol} to {LOG_PATH}")
    except Exception as e:
        logging.exception("❌ Failed to log MCP row")

def generate_test_messages():
    now = datetime.datetime.utcnow()
    et_time = (now - datetime.timedelta(hours=4)).strftime("%I:%M %p ET")
    gmt_time = now.strftime("%H:%M GMT")

    return {
        "news": {
            "symbol": "$XYZ",
            "headline": "AI Contract with Amazon",
            "text": f"""
🚨 $XYZ | AI Contract with Amazon  
🕒 {et_time} / {gmt_time} | Session: Pre-Market  
Price: $1.22 | Target: $1.45 | Stop: $1.12  
Volume: 310K (5d avg: 190K)  
MCP Score: 8.7 | Sentiment: Positive  
📎 [View PR](https://example.com)
""",
            "price": 1.22,
            "volume": 310000,
            "score": 8.7,
            "sentiment": "Positive",
            "session": "Pre-Market"
        },

        "watchlist": {
            "symbol": "$ABC",
            "headline": "$25M Government Contract",
            "text": f"""
🌙 **Watchlist – {now.strftime('%B %d')}**  
📌 $ABC | PR: $25M Government Contract  
Closed: $0.78 | Session: Regular  
MCP: 9.1 | Sentiment: Strong Positive | Volume: 4.2M  
Setup for tomorrow: Entry $0.80, Target $0.92, Stop $0.72
""",
            "price": 0.78,
            "volume": 4200000,
            "score": 9.1,
            "sentiment": "Strong Positive",
            "session": "Regular"
        },

        "review": {
            "symbol": "$XYZ",
            "headline": "Alert: $1.22 → High: $1.44 → Close: $1.38",
            "text": f"""
📈 $XYZ | Alert: $1.22 → High: $1.44 → Close: $1.38  
Gain: +18% | Session: Pre-Market | MCP: 8.7  
Result: ✅ Win
""",
            "price": 1.38,
            "volume": 0,
            "score": 8.7,
            "sentiment": "Positive",
            "session": "Pre-Market"
        }
    }

def main():
    logging.info("🟢 test_alerts.main() started")
    messages = generate_test_messages()
    for channel, data in messages.items():
        post_to_discord(channel, data["text"])
        log_alert(
            channel=channel,
            symbol=data["symbol"],
            headline=data["headline"],
            mcp_score=data["score"],
            sentiment=data["sentiment"],
            session=data["session"],
            price=data["price"],
            volume=data["volume"]
        )
    logging.info("✅ test_alerts.main() finished")
