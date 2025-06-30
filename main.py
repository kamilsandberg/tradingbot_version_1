import schedule
import time
from data.fetcher import get_prices
from logic.strategy import make_decision
from trades.broker import execute_trade
from ai.memory import log_trade

def run_bot():
    print("Running trading bot...")
    prices = get_prices(["AAPL", "BTC-USD"])
    decisions = make_decision(prices)

    for asset, action in decisions.items():
        result = execute_trade(asset, action, prices[asset])
        log_trade(asset, action, prices[asset], result)

# Schedule to run every hour
schedule.every().hour.do(run_bot)

print("Bot started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
