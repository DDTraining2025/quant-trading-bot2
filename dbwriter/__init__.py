import logging
import psycopg2
import os

def log_alert(news: dict):
    try:
        conn = psycopg2.connect(
            host=os.environ.get("pg_host"),
            dbname=os.environ.get("pg_dbname"),
            user=os.environ.get("pg_user"),
            password=os.environ.get("pg_password")
        )
        logging.info("[DB] 📡 Connected to PostgreSQL")

        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO alerts (symbol, datetime_utc, headline, source, url)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    news.get("symbol"),
                    news.get("datetime"),
                    news.get("headline"),
                    news.get("source"),
                    news.get("url")
                ))
                logging.info(f"[DB] 📝 Inserted alert for {news.get('symbol')}")
    except Exception as e:
        logging.error(f"[DB] ❌ Failed to log alert: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            logging.info("[DB] 🔌 PostgreSQL connection closed")
