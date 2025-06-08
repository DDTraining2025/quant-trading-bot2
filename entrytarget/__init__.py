def calculate_trade_plan(entry_price: float) -> dict[str, float]:
    """
    Generate a simple rule-based trade plan based on the entry price.
    The target is 25% above the entry and the stop is 10% below the entry.

    Args:
        entry_price: The entry price for the trade.

    Returns:
        A dict containing 'entry', 'stop', and 'target' prices.
    """
    entry = round(entry_price, 2)
    target = round(entry * 1.25, 2)
    stop = round(entry * 0.90, 2)
    return {
        "entry": entry,
        "stop": stop,
        "target": target
    }
