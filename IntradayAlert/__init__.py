import datetime
import logging
import requests
import os
import azure.functions as func

def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"[TEST] Intraday alert triggered at {now.isoformat()}")

    try:
        discord_url = os.getenv("DISCORDWEBHOOKNEWS")
        logging.info(f"Retrieved webhook: {discord_url}")

        if not discord_url:
            logging.error("DISCORDWEBHOOKNEWS is empty or not loaded.")
            return

        response = requests.post(discord_url, json={"content": f"🚨 Test Alert at {now}"})
        logging.info(f"Discord POST status: {response.status_code}, body: {response.text}")
    except Exception as e:
        logging.exception("Error while posting to Discord")
