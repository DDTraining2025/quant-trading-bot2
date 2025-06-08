import os
import requests
from logger import log_error

def send_discord_alert(webhook_env: str, content: str, embed: dict = None):
    """
    Sends a message to the configured Discord webhook.
    """
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

def format_alert(
    ticker: str,
    headline: str,
    price: float,
    volume: int,
    target: float,
    stop: float,
    score: float,
    sentiment: str,
    session: str,
    pr_url: str
) -> str:
    """
    Formats a structured alert message for Discord.
    """
    return (
        f"🚨 **${ticker} ALERT** ({session})\n"
        f"> **Headline**: {headline}\n"
        f"> **Price**: ${price:.2f} | **Target**: ${target:.2f} | **Stop**: ${stop:.2f}\n"
        f"> **Volume**: {volume:,} | **MCP Score**: {score} | **Sentiment**: {sentiment}\n"
        f"> [🔗 Read PR]({pr_url})"
    )
