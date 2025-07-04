
from alpaca_trade_api.rest import REST
from alpaca.secrets import APCA_API_KEY_ID, APCA_API_SECRET_KEY, BASE_URL
from datetime import datetime
import random

api = REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, BASE_URL)

def get_positions():
    try:
        return api.list_positions()
    except:
        return []

def get_profit_loss(symbol, entry_price, current_price):
    return (current_price - entry_price) / entry_price

def risk_score(symbol):
    # Placeholder: Randomized risk for now
    return random.uniform(0, 1)

def make_decision(prices):
    decisions = {}
    positions = {p.symbol: p for p in get_positions()}

    for symbol, current_price in prices.items():
        if symbol in positions:
            position = positions[symbol]
            entry_price = float(position.avg_entry_price)
            qty = int(float(position.qty))
            unrealized_plpc = float(position.unrealized_plpc)

            # Basic sell logic
            if unrealized_plpc > 0.05:
                decisions[symbol] = "sell"
            elif unrealized_plpc < -0.03:
                decisions[symbol] = "sell"
            else:
                decisions[symbol] = "hold"
        else:
            # Only buy if risk score is good and price above $5
            score = risk_score(symbol)
            if score > 0.7 and current_price > 5:
                decisions[symbol] = "buy"
            else:
                decisions[symbol] = "hold"

    return decisions
