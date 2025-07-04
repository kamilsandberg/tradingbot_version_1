
from alpaca_trade_api.rest import REST, TimeFrame
from alpaca.secrets import APCA_API_KEY_ID, APCA_API_SECRET_KEY, BASE_URL
import yfinance as yf
import pandas as pd
import numpy as np
import os
import json
import time
from datetime import datetime, timedelta

api = REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, BASE_URL)

YF_CACHE_FILE = "ai/yf_cache.json"
YF_CACHE_TTL = 15 * 60  # 15 minutes

def get_yfinance_data(symbol, period="6mo", interval="1d"):
    now = time.time()
    cache = {}
    if df.empty:
        log_event(f"⚠️ YFinance returned empty data for {symbol}")
        return None
    
    if os.path.exists(YF_CACHE_FILE):
        with open(YF_CACHE_FILE, "r") as f:
            cache = json.load(f)

    if symbol in cache and (now - cache[symbol]["timestamp"] < YF_CACHE_TTL):
        df = pd.read_json(cache[symbol]["data"])
        return df

    try:
        df = yf.download(symbol, period=period, interval=interval)
        if df.empty:
            return None
        cache[symbol] = {
            "timestamp": now,
            "data": df.to_json()
        }
        with open(YF_CACHE_FILE, "w") as f:
            json.dump(cache, f)
        return df
    except Exception:
        return None

def get_atr(symbol, period=14):
    try:
        # Alpaca bars
        bars = api.get_bars(symbol, TimeFrame.Day, limit=period+1).df
        bars = bars[bars['symbol'] == symbol]
        bars['H-L'] = bars['high'] - bars['low']
        bars['H-PC'] = abs(bars['high'] - bars['close'].shift(1))
        bars['L-PC'] = abs(bars['low'] - bars['close'].shift(1))
        tr = bars[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr_alpaca = tr.rolling(window=period).mean().iloc[-1]
    except Exception:
        atr_alpaca = None

    try:
        df_yf = get_yfinance_data(symbol, period="1mo", interval="1d")
        df_yf['H-L'] = df_yf['High'] - df_yf['Low']
        df_yf['H-PC'] = abs(df_yf['High'] - df_yf['Close'].shift(1))
        df_yf['L-PC'] = abs(df_yf['Low'] - df_yf['Close'].shift(1))
        tr = df_yf[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr_yf = tr.rolling(window=period).mean().iloc[-1]
    except Exception:
        atr_yf = None

    if atr_alpaca and atr_yf:
        return round((atr_alpaca + atr_yf) / 2, 2)
    return round(atr_alpaca or atr_yf or 0, 2)

def get_beta(symbol, benchmark="^GSPC"):
    try:
        bars = api.get_bars(symbol, TimeFrame.Day, limit=120).df['close'].pct_change().dropna()
        bars_bench = get_yfinance_data(benchmark, period="6mo", interval="1d")['Close'].pct_change().dropna()

        min_len = min(len(bars), len(bars_bench))
        bars = bars[-min_len:]
        bars_bench = bars_bench[-min_len:]

        covariance = np.cov(bars, bars_bench)[0][1]
        beta = covariance / np.var(bars_bench)
        return round(beta, 2)
    except Exception:
        return None
