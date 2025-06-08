import os
import psycopg2
from logger import log_error

def connect_pg():
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        dbname=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD")
    )

def log_alert(ticker: str, score: float, entry: float, stop: float, target: float, pr_title: str):
    try:
        conn = connect_pg()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alerts (ticker, score, entry, stop, target, pr_title, alert_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (ticker, score, entry, stop, target, pr_title))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        log_error(f"Failed to log alert for {ticker}", e)
