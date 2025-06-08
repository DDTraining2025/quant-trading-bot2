# Updated mcpscore/__init__.py

from typing import List, Dict

def calculate_mcp_score(
    keywords: List[str],
    sentiment: str,
    volume: int,
    ticker: str
) -> float:
    """
    Calculate a simplistic MCP score based on extracted keywords, sentiment, and volume.

    Args:
        keywords: List of keywords/tags extracted from the PR.
        sentiment: Sentiment label (e.g., "POSITIVE", "NEGATIVE", "NEUTRAL").
        volume: Trading volume.
        ticker: Stock ticker symbol (included for future use).

    Returns:
        A float score, rounded to two decimals.
    """
    score: float = 0.0

    # Keyword-based weights
    tag_weights: Dict[str, float] = {
        "fda": 2.5,
        "contract": 1.5,
        "guidance": 1.0,
        "merger": 1.5,
        "ai": 1.0,
        "patent": 1.0,
        "award": 0.5
    }

    # Add weights for each matching keyword
    for kw in keywords:
        score += tag_weights.get(kw.lower(), 0.0)

    # Add volume weight
    if volume > 500_000:
        score += 1.0

    # Simple sentiment boost
    lower_sent = sentiment.lower()
    if "positive" in lower_sent:
        score += 0.5
    elif "negative" in lower_sent:
        score -= 0.5

    return round(score, 2)

