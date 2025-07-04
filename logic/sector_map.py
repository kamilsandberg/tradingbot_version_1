# logic/sector_map.py

# Example mapping of tickers to sectors. Expand this as needed or make dynamic.
SECTOR_LOOKUP = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Communication Services",
    "TSLA": "Consumer Discretionary",
    "AMZN": "Consumer Discretionary",
    "JPM": "Financials",
    "XOM": "Energy",
    "JNJ": "Health Care",
    "V": "Financials",
    "NVDA": "Technology",
    # Add more tickers as needed...
}

DEFAULT_SECTOR = "Unknown"

def get_sector_for_symbol(symbol: str) -> str:
    return SECTOR_LOOKUP.get(symbol.upper(), DEFAULT_SECTOR)

