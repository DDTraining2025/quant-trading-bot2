import csv
import os
import datetime
import logging

LOG_FILE = "logs/mcp_log.csv"
os.makedirs("logs", exist_ok=True)

def load_today_alerts():
    today = datetime.datetime.utcnow().date().isoformat()
    alerts = []
    if not os.path.exists(LOG_FILE):
        return alerts

    with open(LOG_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date") == today and row.get("type") == "intraday":
                try:
                    alerts.append({
                        "ticker": row["ticker"],
                        "entry": float(row["entry"]),
                        "stop": float(row["stop"]),
                        "target": float(row["target"]),
                        "session": row["session"],
                        "mcp_score": row.get("mcp_score")
                    })
                except Exception as e:
                    logging.warning(f"Skipping malformed row: {row}")
    return alerts

def log_outcome(result: dict):
    fieldnames = [
        "date", "ticker", "entry", "high", "close", "gain_pct", "result", "session"
    ]
    today = datetime.datetime.utcnow().date().isoformat()
    result["date"] = today

    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(result)
