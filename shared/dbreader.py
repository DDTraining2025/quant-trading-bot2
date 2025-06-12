import pg8000
import os

def get_active_watchlist():
    conn = pg8000.connect(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=int(os.getenv("PGPORT", "5432")),
        database=os.getenv("PGDATABASE")
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT ticker FROM watchlist WHERE market_cap < 50000000")
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()
