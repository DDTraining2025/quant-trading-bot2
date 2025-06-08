def generate_trade_plan(entry_price: float) -> dict:
    """
    Very simple rule-based trade plan generator.
    Adjust this with gap logic, float-based rules, etc.
    """
    target = round(entry_price * 1.25, 2)
    stop = round(entry_price * 0.90, 2)
    return {
        "entry": round(entry_price, 2),
        "stop": stop,
        "target": target
    }
