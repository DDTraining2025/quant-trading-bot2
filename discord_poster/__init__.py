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
