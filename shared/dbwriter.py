import os
import pg8000
import logging

def log_alert(news_id, ticker, headline, url, published_utc):
    """Write a news alert to the PostgreSQL database."""
    conn = None
    try:
        conn = pg8000.connect(
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST"),
            port=int(os.getenv("PGPORT", "5432")),
            database=os.getenv("PGDATABASE"),
            ssl_context=True,
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alerts (news_id, ticker, headline, url, published_utc)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (news_id) DO NOTHING
        """, (news_id, ticker, headline, url, published_utc))
        conn.commit()
        cur.close()
    except Exception as e:
        logging.error(f"[DB] Error logging alert: {e}")
    finally:
        if conn:
            conn.close()
