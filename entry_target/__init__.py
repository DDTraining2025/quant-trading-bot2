def calculate_trade_plan(current_price, gap_pct=0.1):
    if not isinstance(current_price, (int, float)) or current_price <= 0:
        return None

    entry = round(current_price * (1 + gap_pct), 2)
    stop = round(current_price * (1 - gap_pct), 2)
    target = round(current_price * (1 + 2 * gap_pct), 2)

    # Sanity check: ensure logical structure
    if not (stop < entry < target):
        return None

    return entry, stop, target
