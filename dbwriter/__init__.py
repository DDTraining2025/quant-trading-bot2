import os
import psycopg2
from logger import log_error, log_info
from keyvaultloader import load_secrets_from_vault

# Load secrets securely from Azure Key Vault
load_secrets_from_vault()

def connect_pg():
    return psycopg2.connect(
        host=os.getenv("pghost"),
        dbname=os.getenv("pgdatabase"),
        user=os.getenv("pguser"),
        password=os.getenv("pgpassword"),
        sslmode="require"
    )

def log_alert(
    ticker: str,
    score: float,
    entry: float,
    stop: float,
    target: float,
    pr_title: str
):
    try:
        with connect_pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO alerts
                        (ticker, score, entry, stop, target, pr_title, alert_time)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (ticker.upper(), score, entry, stop, target, pr_title.strip())
                )
            conn.commit()
        log_info(f"✅ Alert logged for {ticker.upper()}")
    except Exception as e:
        log_error(f"❌ Failed to log alert for {ticker}", e)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Mock alert insertion for testing."
    )
    parser.add_argument("--mock", type=str, help="Mock ticker symbol")
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
