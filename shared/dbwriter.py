import os
import pg8000
import logging

def log_alert(news_id, ticker, headline, url, published_utc):
    """Write a news alert to the PostgreSQL database using pg8000."""
    conn = None
    try:
        conn = pg8000.connect(
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST"),
            port=int(os.getenv("PGPORT", "5432")),
            database=os.getenv("PGDATABASE"),
            ssl=True  # ssl_context is not required unless customizing SSL
        )
        # pg8000 uses execute directly on the connection
        conn.execute("""
            INSERT INTO alerts (news_id, ticker, headline, url, published_utc)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (news_id) DO NOTHING
        """, (news_id, ticker, headline, url, published_utc))
        conn.commit()
    except Exception as e:
        logging.error(f"[DB] Error logging alert: {e}")
    finally:
        if conn:
            conn.close()
