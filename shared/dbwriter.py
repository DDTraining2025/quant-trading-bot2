import os
import pg8000

def log_alert(ticker, title, url, ts, market_cap):
    conn = pg8000.connect(
        dbname=os.getenv("pg_database"),
        user=os.getenv("pg_user"),
        password=os.getenv("pg_password"),
        host=os.getenv("pg_host"),
        port=os.getenv("pg_port")
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts (ticker, headline, url, alert_time, market_cap)
        VALUES (%s, %s, %s, %s, %s)
    """, (ticker, title, url, ts, market_cap))
    conn.commit()
    cur.close()
    conn.close()
