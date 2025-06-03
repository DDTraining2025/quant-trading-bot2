import datetime
import logging
import requests
import os
import azure.functions as func

def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"[TEST] Intraday alert triggered at {now.isoformat()}")

    discord_url = os.getenv("DISCORDWEBHOOKNEWS") or "https://discord.com/api/webhooks/1379185897626402836/Zd3Wb7aSErubDBlHp-bGG6kOY5ragzB0Fuyrza3id4sgjIXvJhYgGHFCuNCDpkID_qUX"
    if discord_url:
        message = {
            "content": f"🚨 Test Alert from IntradayAlert at {now.isoformat()} UTC"
        }
        requests.post(discord_url, json=message)
    else:
        logging.warning("DISCORDWEBHOOKNEWS not found in environment variables")
