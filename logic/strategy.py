def make_decision(prices):
    decisions = {}
    for symbol, price in prices.items():
        if price > 100:  # very basic logic
            decisions[symbol] = "buy"
        else:
            decisions[symbol] = "hold"
    return decisions
