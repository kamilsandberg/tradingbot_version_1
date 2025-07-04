import schedule
import time
import os

from data.fetcher import get_prices
from logic.strategy import make_decision
from trades.broker import execute_trade
from ai.sentiment import get_sentiment_score
from logic.indicators import get_atr, get_beta
from ai.status_writer import update_status
from ai.logger import log_event
from ai.trade_memory import log_trade
from ai.threshold_updater import compute_thresholds
from ai.trainer import run_trainer
from sp500 import get_sp500_symbols
from logic.sector_map import get_sector_for_symbol
from alpaca_trade_api.rest import REST

# ✅ Load secrets from file instead of hardcoding
from alpaca.secrets import APCA_API_KEY_ID, APCA_API_SECRET_KEY

os.environ["APCA_API_KEY_ID"] = APCA_API_KEY_ID
os.environ["APCA_API_SECRET_KEY"] = APCA_API_SECRET_KEY
os.environ["APCA_API_BASE_URL"] = "https://paper-api.alpaca.markets"

api = REST()

def run_bot():
    update_status("🔁 Bot ticked: Analyzing prices...")
    log_event("🔁 Tick started")
    print("🔁 Bot ticked!")

    symbols = get_sp500_symbols()

    # Step 1: Fetch prices
    try:
        prices = get_prices(symbols)
        update_status(f"📈 Prices fetched: {prices}")
        log_event(f"📈 Prices fetched: {prices}")
        print(f"Prices: {prices}")
    except Exception as e:
        update_status(f"❌ Error fetching prices: {e}")
        log_event(f"❌ Error fetching prices: {e}")
        return

    # Step 2: Make decisions
    try:
        decisions = make_decision(prices)
        update_status(f"💡 Decisions made: {decisions}")
        log_event(f"💡 Decisions made: {decisions}")
        print(f"Decisions: {decisions}")
    except Exception as e:
        update_status(f"❌ Error in decision logic: {e}")
        log_event(f"❌ Error in decision logic: {e}")
        return

    # Step 3: Get buying power
    try:
        account = api.get_account()
        buying_power = float(account.buying_power)
        has_cash = buying_power > 100
        log_event(f"💰 Buying power: ${buying_power}")
    except Exception as e:
        log_event(f"❌ Failed to get account info: {e}")
        return

    # Step 4: Execute trades
    for symbol, action in decisions.items():
        try:
            price = prices.get(symbol)
            if not price:
                continue

            sentiment_score = get_sentiment_score(symbol)
            atr = get_atr(symbol)
            beta = get_beta(symbol)
            risk_score = round((sentiment_score + (1 / (beta + 1)) + (1 / (atr + 1))) / 3, 2) if atr and beta else 0.5

            update_status(f"🛠️ Executing {action} on {symbol} at ${price}")

            if action == "sell":
                result = execute_trade(symbol, action, price)
                log_event(f"🛒 {symbol}: {result}")
                continue

            if action == "buy":
                if not has_cash:
                    log_event(f"⛔ Skipping buy for {symbol}: insufficient cash")
                    continue

                result = execute_trade(symbol, action, price)
                log_event(f"🛒 {symbol}: {result}")

                if "❌" in result or "insufficient" in result.lower():
                    has_cash = False

            log_trade(
                symbol=symbol,
                action=action,
                price=price,
                score=risk_score,
                sentiment_score=sentiment_score,
                volatility={"atr": atr, "beta": beta},
                outcome=None
            )

            log_event(f"[SCORE] {symbol} | Score: {risk_score} | Sentiment: {sentiment_score} | ATR: {atr} | Beta: {beta}")

        except Exception as e:
            update_status(f"❌ Error trading {symbol}: {e}")
            log_event(f"❌ Error trading {symbol}: {e}")
            continue

    update_status("✅ Idle — waiting for next tick.")

# Run every minute
schedule.every(1).minute.do(run_bot)

# Start supporting services once
log_event("🚀 Launching threshold updater...")
compute_thresholds()

log_event("🧠 Launching trainer to analyze trade history...")
run_trainer()

print("🚀 Smart trading bot + services started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
