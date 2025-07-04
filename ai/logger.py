
import logging
import os

log_path = "ai/event_log.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logger = logging.getLogger("TradingBotLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_event(message):
    print(f"[LOG] {message}")
    logger.info(message)
    
def log_event(message=None, **kwargs):
    try:
        if message:
            print(f"[LOG] {message.encode('utf-8', errors='replace').decode('utf-8')}")
        if kwargs:
            print("[LOG]", json.dumps(kwargs, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[LOG ERROR] Failed to log event: {e}")

