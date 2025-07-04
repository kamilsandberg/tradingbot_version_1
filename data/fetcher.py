from alpaca_trade_api.rest import REST
from alpaca.secrets import APCA_API_KEY_ID, APCA_API_SECRET_KEY, BASE_URL

api = REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, BASE_URL)

def get_prices(symbols):
    prices = {}
    for symbol in symbols:
        try:
            barset = api.get_latest_trade(symbol)
            prices[symbol] = barset.price
        except Exception as e:
            log_event(f"❌ Alpaca error for {symbol}: {e}")
            # Optional: also write to invalid ticker log here
            with open("logs/invalid_tickers.log", "a") as f:
                f.write(f"{symbol} - {e}\\n")
            continue
    return prices

