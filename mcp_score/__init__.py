import random

def calculate_mcp_score(pr_keywords, sentiment, volume, ticker):
    # Placeholder logic — replace with model or heuristic
    score = 5.0

    if "contract" in pr_keywords:
        score += 2
    if "fda" in pr_keywords:
        score += 1.5
    if sentiment == "POSITIVE":
        score += 1
    if volume > 500_000:
        score += 0.5

    return round(min(score, 10.0), 1)
