import os
import requests
from logger import log_error

def send_discord_alert(webhook_env: str, content: str, embed: dict = None):
    try:
        url = os.getenv(webhook_env)
        if not url:
            raise ValueError(f"Missing webhook URL in env: {webhook_env}")

        payload = {"content": content}
        if embed:
            payload["embeds"] = [embed]

        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        log_error(f"Failed to send Discord alert via {webhook_env}", e)
