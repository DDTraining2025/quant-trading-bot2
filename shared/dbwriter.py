import os
import pg8000
import logging

def log_alert(ticker, headline, url, published, news_id, source):
    try:
        conn = pg8000.connect(
            host=os.getenv("PGHOST"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            port=int(os.getenv("PGPORT", 5432)),
            ssl_context=None,  # Use this or pass ssl if needed
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (ticker, headline, url, published, news_id, source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (ticker, headline, url, published, news_id, source),
        )
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Logged alert for {ticker} to Postgres.")
    except Exception as e:
        logging.error(f"DB log failed: {e}")
