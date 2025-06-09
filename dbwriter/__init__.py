# dbwriter.py
import os
import logging
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# --- Load DB credentials from environment (use Key Vault or local.settings.json) ---
PG_HOST = os.environ.get("pg_host")
PG_PORT = os.environ.get("pg_port", 5432)
PG_NAME = os.environ.get("pg_dbname", "quantbotdb")
PG_USER = os.environ.get("pg_user")
PG_PASS = os.environ.get("pg_password")

def log_alert(alert: dict):
    """
    Write a single PR alert to the PostgreSQL alerts table.
    Expects keys: ticker, headline, url, timestamp, market_cap, source, sentiment, mcp_score
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_NAME,
            user=PG_USER,
            password=PG_PASS
        )
        cur = conn.cursor()

        sql = """
        INSERT INTO alerts (
            ticker, headline, url, published_time,
            market_cap, source, sentiment, mcp_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(sql, (
            alert.get("ticker"),
            alert.get("headline"),
            alert.get("url"),
            alert.get("timestamp"),
            alert.get("market_cap"),
            alert.get("source"),
            alert.get("sentiment", None),
            alert.get("mcp_score", None)
        ))

        conn.commit()
        cur.close()
        logging.info(f"[DB] ✅ Logged alert for {alert['ticker']}")

    except Exception as e:
        logging.error(f"[DB] ❌ Error writing to database: {e}")
    finally:
        if conn:
            conn.close()
