import json
from datetime import datetime
import os

MEMORY_FILE = "ai/trade_memory.json"

def log_trade(symbol, action, price, result):
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)

    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)

    memory.append({
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "action": action,
        "price": price,
        "result": result
    })

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
