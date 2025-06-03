def calculate_trade_plan(current_price, gap_pct=0.1):
    entry = round(current_price * (1 + gap_pct), 2)
    stop = round(current_price * (1 - gap_pct), 2)
    target = round(current_price * (1 + 2 * gap_pct), 2)
    return entry, stop, target

entry, stop, target = calculate_trade_plan(price)
