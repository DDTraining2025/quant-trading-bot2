import os
import datetime
import psycopg2
from logger import logger  # your standard logging instance
from keyvaultloader import load_secrets_from_vault

# Ensure secrets are loaded
load_secrets_from_vault()

def connect_pg():
    return psycopg2.connect(
        host=os.getenv("pghost"),
        dbname=os.getenv("pgdatabase"),
        user=os.getenv("pguser"),
        password=os.getenv("pgpassword"),
        sslmode="require"
    )

def load_today_alerts() -> list[dict]:
    """
    Load today's intraday alerts directly from the PostgreSQL 'alerts' table.
    """
    today_str = datetime.datetime.utcnow().date().isoformat()  # YYYY-MM-DD
    query = """
        SELECT ticker, entry, stop, target, alert_time
        FROM alerts
        WHERE alert_time::date = %s
          AND /* you might have a 'type' column? */ true
        ORDER BY alert_time;
    """
    results = []
    try:
        with connect_pg() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (today_str,))
                for ticker, entry, stop, target, alert_time in cur.fetchall():
                    # Derive session, MCP score, etc. if you store them
                    results.append({
                        "ticker": ticker,
                        "entry": float(entry),
                        "stop": float(stop),
                        "target": float(target),
                        "session": "intraday",      # or fetch from an extra column
                        "mcp_score": None           # or fetch if stored
                    })
    except Exception as e:
        logger.error(f"❌ Failed to load today's alerts from DB: {e}")
    return results
