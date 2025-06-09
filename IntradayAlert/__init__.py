import logging
import azure.functions as func
from finnhubapi import get_quote

def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ IntradayAlert triggered")

    ticker = "VERB"
    try:
        quote = get_quote(ticker)
        logging.info(f"📈 Quote for {ticker}: {quote}")
    except Exception as e:
        logging.error(f"❌ Failed to fetch quote: {e}")
