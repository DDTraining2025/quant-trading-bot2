import datetime
import logging
import requests
import os
import azure.functions as func
import http.client as http_client

# Enable HTTPS-level debugging
http_client.HTTPConnection.debuglevel = 1
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"[TEST] Intraday alert triggered at {now.isoformat()}")

    try:
        discord_url = os.getenv("DISCORDWEBHOOKNEWS")
        logging.debug(f"Retrieved webhook: {discord_url}")

        if not discord_url:
            raise EnvironmentError("❌ DISCORDWEBHOOKNEWS is empty or not loaded")

        payload = {"content": f"🚨 Test Alert from Azure Function at {now.isoformat()} UTC"}
        response = requests.post(discord_url, json=payload)
        response.raise_for_status()

        logging.info(f"✅ Discord POST status: {response.status_code}, body: {response.text}")

    except Exception as e:
        logging.exception("❌ Error while posting to Discord")
