# shared/dbwriter.py

import os
import logging
import pg8000

def already_logged(ticker: str, title: str, ts: str) -> bool:
    """
    Check if an alert with the same ticker, headline, and timestamp
    already exists in the database.
    """
    conn = pg8000.connect(
        database=os.getenv("pg_database"),
        user=os.getenv("pg_user"),
        password=os.getenv("pg_password"),
        host=os.getenv("pg_host"),
        port=os.getenv("pg_port"),
    )
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM alerts WHERE ticker=%s AND headline=%s AND alert_time=%s",
            (ticker, title, ts),
        )
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

def log_alert(ticker: str, title: str, url: str, ts: str, market_cap: float) -> None:
    """
    Insert a row into the alerts table. If it already exists,
    ON CONFLICT DO NOTHING will silently skip.
    """
    conn = pg8000.connect(
        database=os.getenv("pg_database"),
        user=os.getenv("pg_user"),
        password=os.getenv("pg_password"),
        host=os.getenv("pg_host"),
        port=os.getenv("pg_port"),
    )
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alerts (ticker, headline, url, alert_time, market_cap)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT alerts_unique_pr
            DO NOTHING
        """, (ticker, title, url, ts, market_cap))
        conn.commit()
        logging.info(f"DB write complete for {ticker} @ {ts}")
    except Exception as e:
        logging.error(f"Error writing to DB for {ticker}: {e}")
        raise
    finally:
        cur.close()
        conn.close()
