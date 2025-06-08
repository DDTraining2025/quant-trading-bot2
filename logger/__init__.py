from pathlib import Path
import csv
import datetime
import logging
import traceback

# Define log directory and files
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
CSV_LOG = LOG_DIR / "mcp_log.csv"
ERROR_LOG_FILE = LOG_DIR / "error_log.txt"

# Configure standard logger for console and Azure Monitor
logger = logging.getLogger("quantbot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

def load_today_alerts() -> list[dict]:
    """
    Load alerts from today's CSV log labeled as 'intraday'.
    """
    today = datetime.datetime.utcnow().date().isoformat()
    alerts = []
    if not CSV_LOG.exists():
        return alerts

    with CSV_LOG.open(newline="") as f:
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
                except Exception:
                    logger.warning(f"Skipping malformed row: {row}")
    return alerts

def log_outcome(result: dict) -> None:
    """
    Append a new outcome record to the CSV log.
    """
    fieldnames = ["date", "ticker", "entry", "high", "close", "gain_pct", "result", "session"]
    record = result.copy()
    record["date"] = datetime.datetime.utcnow().date().isoformat()

    write_header = not CSV_LOG.exists()
    with CSV_LOG.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(record)

    logger.info(f"Logged outcome for {record['ticker']}: {record}")

def log_error(context: str, exception: Exception) -> None:
    """
    Log an error context and stack trace to a file, while also emitting via standard logger.
    """
    ts = datetime.datetime.utcnow().isoformat()
    trace = traceback.format_exc()

    with ERROR_LOG_FILE.open("a") as f:
        f.write(f"[{ts}] {context}\n")
        f.write(trace + "\n")

    logger.error(f"{context}: {exception}")

def format_log_data(
    ticker: str,
    price: float,
    volume: int,
    sentiment: str,
    sentiment_confidence: float,
    mcp_score: float,
    session: str,
    label: str
) -> dict:
    """
    Prepare a dict for CSV logging of alerts.
    """
    return {
        "date": datetime.datetime.utcnow().date().isoformat(),
        "ticker": ticker,
        "entry": price,
        "stop": round(price * 0.9, 2),
        "target": round(price * 1.25, 2),
        "volume": volume,
        "sentiment": sentiment,
        "sentiment_conf": sentiment_confidence,
        "mcp_score": mcp_score,
        "session": session,
        "type": label
    }
