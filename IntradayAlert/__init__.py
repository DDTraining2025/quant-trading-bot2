import datetime
import logging
import requests
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import azure.functions as func


def get_secret():
    kv_url = "https://quant-trading-vault.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_url, credential=credential)
    return client.get_secret("DISCORDWEBHOOKNEWS").value


def main(timer: func.TimerRequest) -> None:
    now = datetime.datetime.utcnow()
    logging.info(f"[TEST] Intraday alert triggered at {now.isoformat()}")

    try:
        discord_url = get_secret()
        message = {
            "content": f"🚨 Test Alert from IntradayAlert at {now.isoformat()} UTC"
        }
        response = requests.post(discord_url, json=message)
        logging.info(f"Sent to Discord, status: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Failed to post Discord alert: {str(e)}")
