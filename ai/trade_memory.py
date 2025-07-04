
import sqlite3
from datetime import datetime

DB_PATH = "trades/trade_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            action TEXT,
            price REAL,
            score REAL,
            sentiment_score REAL,
            atr REAL,
            beta REAL,
            outcome TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cash (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            amount REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sector_exposure (
            sector TEXT PRIMARY KEY,
            exposure REAL
        )
    """)
    c.execute("""INSERT OR IGNORE INTO cash (id, amount) VALUES (1, 100000.0)""")
    conn.commit()
    conn.close()

def log_trade(symbol, action, price, score, sentiment_score, volatility, outcome):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO trades (symbol, action, price, score, sentiment_score, atr, beta, outcome, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol, action, price, score, sentiment_score,
        volatility.get('atr', None), volatility.get('beta', None), outcome,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def get_current_cash():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT amount FROM cash WHERE id = 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0.0

def update_cash(new_amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE cash SET amount = ? WHERE id = 1", (new_amount,))
    conn.commit()
    conn.close()

def get_sector_exposure():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sector, exposure FROM sector_exposure")
    result = {sector: exposure for sector, exposure in c.fetchall()}
    conn.close()
    return result

def update_sector_exposure(sector, new_exposure):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sector_exposure (sector, exposure)
        VALUES (?, ?)
        ON CONFLICT(sector) DO UPDATE SET exposure = excluded.exposure
    """, (sector, new_exposure))
    conn.commit()
    conn.close()

init_db()
