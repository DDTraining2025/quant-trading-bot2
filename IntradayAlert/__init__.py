import datetime
import logging
import pytz
import azure.functions as func

def main(timer: func.TimerRequest) -> None:
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_et = now_utc.astimezone(pytz.timezone("US/Eastern"))

    if now_et.hour < 4 or now_et.hour >= 20:
        logging.info(f"Outside active hours (now ET: {now_et}). Skipping.")
        return

    logging.info(f"Running IntradayAlert at {now_et.isoformat()}")
    # Your alert logic here
