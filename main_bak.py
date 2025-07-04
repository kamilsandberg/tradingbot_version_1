# Updated main.py with dynamic capital and sector-aware risk logic
import schedule
import time
from data.fetcher import get_prices
from logic.strategy import make_decision
from trades.broker import execute_trade
from ai.sentiment import get_sentiment_score
from logic.indicators import get_atr, get_beta
from ai.status_writer import update_status
from ai.logger import log_event
from ai.trade_memory import log_trade, get_current_cash, update_cash, get_sector_exposure, update_sector_exposure
from sp500 import get_sp500_symbols
from ai.threshold_updater import compute_thresholds
from ai.trainer import run_trainer
from logic.sector_map import get_sector_for_symbol

# Constants
MAX_INVEST_PER_SECTOR = 0.25  # 25% of cash per sector
MAX_INVEST_PER_TRADE = 0.1    # 10% per trade
SECTOR_EXPOSURE = {}

# Launch self-learning services
log_event("🚀 Launching threshold updater...")
compute_thresholds()

log_event("\U0001f9e0 Launching trainer to analyze trade history...")
run_trainer()

# Bot logic
def run_bot():
    update_status("[Tick] Bot ticked: Analyzing prices...")
    log_event("\ud83d\udd01 Tick started")
    print("[Tick] Bot ticked!")

    symbols = get_sp500_symbols()
    log_event(f"📊 Processing {len(symbols)} symbols")

    try:
        prices = get_prices(symbols)
        update_status(f"📈 Prices fetched: {list(prices.keys())[:5]}...")
        log_event(f"📈 Prices fetched: {len(prices)} symbols")
    except Exception as e:
        update_status(f"❌ Error fetching prices: {e}")
        log_event(f"❌ Error fetching prices: {e}")
        return

    try:
        decisions = make_decision(prices)
        update_status(f"\U0001f4a1 Decisions made: {len(decisions)}")
        log_event(f"\U0001f4a1 Decisions made: {len(decisions)}")
    except Exception as e:
        update_status(f"❌ Decision logic error: {e}")
        log_event(f"❌ Decision logic error: {e}")
        return

    current_cash = get_current_cash()
    sector_allocations = get_sector_exposure()

    for symbol, action in decisions.items():
        if symbol not in prices:
            continue

        price = prices[symbol]
        sentiment_score = get_sentiment_score(symbol)
        atr = get_atr(symbol)
        beta = get_beta(symbol)
        risk_score = round((sentiment_score + (1 / (beta + 1)) + (1 / (atr + 1))) / 3, 2) if atr and beta else 0.5

        sector = get_sector_for_symbol(symbol)
        sector_cash_used = sector_allocations.get(sector, 0)
        allowed_invest = min(current_cash * MAX_INVEST_PER_TRADE, (current_cash * MAX_INVEST_PER_SECTOR) - sector_cash_used)

        if action == "buy" and price > allowed_invest:
            log_event(f"🛒 {symbol}: ❌ Buy failed for {symbol}: insufficient buying power")
            continue

        update_status(f"\U0001f6e0️ Executing {action} on {symbol} at ${price}")
        result = execute_trade(symbol, action, price)
        log_event(f"🛒 {symbol}: {result}")

        # Update memory
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

        # Adjust cash & sector if buy
        if action == "buy" and "success" in result:
            update_cash(-price)
            update_sector_exposure(sector, price)
        elif action == "sell" and "success" in result:
            update_cash(+price)
            update_sector_exposure(sector, -price)

    update_status("✅ Idle — waiting for next tick.")

schedule.every(1).minutes.do(run_bot)
print("🚀 Smart trading bot + services started. Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)
