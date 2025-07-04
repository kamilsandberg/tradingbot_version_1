
import requests
import pandas as pd
import os
import time
import json

CACHE_FILE = "sp500_cache.json"
CACHE_TTL = 24 * 60 * 60  # 24 hours

def get_sp500_symbols(cache=True):
    if cache and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            if time.time() - data["timestamp"] < CACHE_TTL:
                return data["symbols"]

    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        symbols = df["Symbol"].tolist()

        # Format for Alpaca (BRK-B -> BRK.B)
        symbols = [s.replace("-", ".") for s in symbols]

        # Cache result
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "symbols": symbols}, f)

        return symbols
    except Exception as e:
        print(f"❌ Failed to fetch S&P 500 tickers: {e}")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)["symbols"]
        return []

if __name__ == "__main__":
    tickers = get_sp500_symbols()
    print(f"✅ Loaded {len(tickers)} S&P 500 tickers:")
    print(tickers[:10])
