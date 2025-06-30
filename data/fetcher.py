
import yfinance as yf

def get_prices(symbols):
    prices = {}
    for symbol in symbols:
        data = yf.Ticker(symbol)
        latest = data.history(period="1d", interval="1h").tail(1)
        prices[symbol] = latest['Close'].iloc[0]
    return prices
