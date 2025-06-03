import datetime
import logging
import azure.functions as func

def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.now()
    logging.info(f"[RUN] Watchlist generator triggered at {now.isoformat()}")

    # TODO: check news sources for late PRs (e.g., 4PM–9PM ET)
    # TODO: select microcaps with key terms or high sentiment
    # TODO: generate formatted summary and send to Discord (watchlist channel)

    return
