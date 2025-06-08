import os
import psycopg2
from logger import log_error, log_info
from keyvault_loader import load_secrets

# Load secrets from Azure Key Vault
load_secrets(["PG_HOST", "PG_DATABASE", "PG_USER", "PG_PASSWORD"])

def connect_pg():
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        dbname=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        sslmode="require"
    )

def log_alert(ticker: str, score: float, entry: float, stop: float, target: float, pr_title: str):
    try:
        conn = connect_pg()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alerts (ticker, score, entry, stop, target, pr_title, alert_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (ticker.upper(), score, entry, stop, target, pr_title.strip()))
        conn.commit()
        cur.close()
        conn.close()
        log_info(f"✅ Alert logged for {ticker}")
    except Exception as e:
        log_error(f"❌ Failed to log alert for {ticker}", e)

# Optional CLI test
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", type=str, help="Mock ticker")
    args = parser.parse_args()

    if args.mock:
        log_alert(
            ticker=args.mock,
            score=8.5,
            entry=1.25,
            stop=1.00,
            target=2.00,
            pr_title="FDA Approval for Major Drug"
        )
