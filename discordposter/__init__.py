import os
import requests
from logger import log_error, log_info

def send_discord_alert(
    webhook_env: str,
    content: str,
    embed: dict | None = None,
    timeout: int = 10
) -> None:
    """
    Sends a message to the configured Discord webhook.

    Args:
        webhook_env: Name of the environment variable holding the webhook URL.
        content: Message content as a plain string.
        embed: Optional dict following Discord embed schema.
        timeout: Request timeout in seconds.
    """
    try:
        url = os.getenv(webhook_env)
        if not url:
            raise ValueError(f"Missing webhook URL in env: {webhook_env}")

        payload: dict = {"content": content}
        if embed:
            payload["embeds"] = [embed]

        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        log_info(f"✅ Sent Discord alert via {webhook_env}")
    except Exception as e:
        log_error(f"❌ Failed to send Discord alert via {webhook_env}", e)

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
        f"> **Volume**: {volume:,} | **MCP Score**: {score:.2f} | **Sentiment**: {sentiment}\n"
        f"> [🔗 Read PR]({pr_url})"
    )
