from ib_insync import IB, Stock
from datetime import datetime
import os
import pg8000
from shared.dbwriter import log_alert
from shared.discordposter import send_discord_alert

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

def get_pr_hash(ticker, headline):
    import hashlib
    return hashlib.sha256(f"{ticker}|{headline}".encode()).hexdigest()

def is_duplicate_pr(pr_hash):
    conn = pg8000.connect(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=int(os.getenv("PGPORT", "5432")),
        database=os.getenv("PGDATABASE")
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM alerts WHERE news_id = %s", (pr_hash,))
        return cur.fetchone() is not None
    finally:
        conn.close()

def log_new_pr(ticker, headline, pr_hash):
    log_alert(pr_hash, ticker, headline, "", datetime.utcnow().isoformat())

def main():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    watchlist = get_active_watchlist()
    contracts = [Stock(t, 'SMART', 'USD') for t in watchlist]
    ib.qualifyContracts(*contracts)

    for contract in contracts:
        ib.reqMktData(contract, genericTickList='292', snapshot=False)

    @ib.pendingTickersEvent
    def on_tick(tickers):
        for t in tickers:
            if t.tickType == 292 and hasattr(t, 'message'):
                ticker = t.contract.symbol
                headline = t.message
                pr_hash = get_pr_hash(ticker, headline)
                if not is_duplicate_pr(pr_hash):
                    log_new_pr(ticker, headline, pr_hash)
                    send_discord_alert({
                        "title": headline,
                        "stocks": [ticker],
                        "url": "",
                        "created": datetime.utcnow().isoformat()
                    })
    ib.run()

if __name__ == "__main__":
    main()
