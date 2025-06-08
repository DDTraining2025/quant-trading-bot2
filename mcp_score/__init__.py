def score_press_release(pr_title: str, volume: int, float_size: float) -> float:
    score = 0.0

    tags = {
        "fda": 2.5,
        "contract": 1.5,
        "guidance": 1.0,
        "merger": 1.5,
        "ai": 1.0,
        "patent": 1.0,
        "award": 0.5
    }

    title_lower = pr_title.lower()
    for tag, weight in tags.items():
        if tag in title_lower:
            score += weight

    if volume > 500000:
        score += 1.0
    if float_size and float_size < 10_000_000:
        score += 1.0

    return round(score, 2)
