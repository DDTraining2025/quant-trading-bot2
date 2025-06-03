import csv
import os
from datetime import datetime

def log_alert(data, filename="alerts_log.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def format_log_data(ticker, price, volume, sentiment, mcp_score, session, label):
    return {
        "time_utc": datetime.utcnow().isoformat(),
        "ticker": ticker,
        "price": price,
        "volume": volume,
        "sentiment": sentiment,
        "mcp_score": mcp_score,
        "session": session,
        "label": label
    }
