import json
from datetime import datetime

STATUS_FILE = "ai/status.json"

def update_status(text):
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": text
    }
    print(f"[DEBUG] Writing status: {status}")  # Add this to confirm it's called
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)

