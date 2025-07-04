
import sqlite3
import pandas as pd
import json
import os

DB_PATH = "ai/trade_memory.db"
THRESHOLD_FILE = "ai/thresholds.json"

def compute_thresholds():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trades WHERE pnl IS NOT NULL", conn)
    conn.close()

    if df.empty:
        print("No completed trades available.")
        return

    thresholds = {}

    for symbol, group in df.groupby("symbol"):
        wins = group[group["pnl"] > 0]
        losses = group[group["pnl"] <= 0]

        if not wins.empty:
            avg_win = wins["pnl"].mean()
        else:
            avg_win = 0.05  # fallback

        if not losses.empty:
            avg_loss = losses["pnl"].mean()
        else:
            avg_loss = -0.03  # fallback

        thresholds[symbol] = {
            "take_profit_threshold": round(avg_win, 4),
            "stop_loss_threshold": round(avg_loss, 4)
        }

    with open(THRESHOLD_FILE, "w") as f:
        json.dump(thresholds, f, indent=2)

    print(f"✅ Updated {len(thresholds)} symbol thresholds.")
    print(json.dumps(thresholds, indent=2))

if __name__ == "__main__":
    compute_thresholds()
