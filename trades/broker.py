portfolio = {"USD": 10000, "AAPL": 0, "BTC-USD": 0}

def execute_trade(symbol, action, price):
    if action == "buy":
        amount = 1000
        if portfolio["USD"] >= amount:
            portfolio["USD"] -= amount
            portfolio[symbol] += amount / price
            return f"Bought {amount / price:.4f} of {symbol}"
    return f"Held {symbol}"
