import sqlite3
import pandas as pd

DB_PATH = "ai/trade_memory.db"

def load_trade_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trades WHERE pnl IS NOT NULL", conn)
    conn.close()
    return df

def analyze_trades(df):
    if df.empty:
        print("No completed trades with outcome available.")
        return

    print("✅ Loaded", len(df), "completed trades\n")

    print("📈 Average P&L:", round(df['pnl'].mean(), 2))
    print("✅ Win rate:", round((df['pnl'] > 0).mean() * 100, 2), "%")

    print("\n--- Performance by Symbol ---")
    print(df.groupby("symbol")["pnl"].agg(["count", "mean", "sum"]).sort_values("sum", ascending=False))

    print("\n--- Strategy Score Buckets ---")
    df['score_bucket'] = pd.cut(df['score'], bins=[0, 0.4, 0.6, 0.8, 1.0])
    print(df.groupby("score_bucket")["pnl"].agg(["count", "mean", "sum"]))

    print("\n--- Sentiment Score Buckets ---")
    df['sentiment_bucket'] = pd.cut(df['sentiment_score'], bins=[0, 0.4, 0.6, 0.8, 1.0])
    print(df.groupby("sentiment_bucket")["pnl"].agg(["count", "mean", "sum"]))

    print("\n--- Volatility (Beta) Buckets ---")
    df = df[df['beta'].notnull()]
    df['beta_bucket'] = pd.cut(df['beta'], bins=[-1, 0.5, 1.0, 1.5, 2.0, 10])
    print(df.groupby("beta_bucket")["pnl"].agg(["count", "mean", "sum"]))

def run_trainer():
    df = load_trade_data()
    analyze_trades(df)

if __name__ == "__main__":
    run_trainer()

