
# config.py
# Configuration for IQ Option API
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "accept-encoding": "gzip, deflate, br, zstd",
    "content-type": "application/json",
    "Referer": "https://iqoption.com/",
    "Origin": "https://iqoption.com",
    "priority": "u=1, i",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "sec-fetch-storage-access": "active"
}

# Trading configuration
INSTRUMENTS = 'turbo'  # Options: 'turbo' or 'binary'
CASH_TO_TRADE = 50  # Default amount to trade
CANDLES_COUNT = 111  # Number of candles to retrieve
DURATIONS = 1 if INSTRUMENTS == 'turbo' else 5  # Duration of trades (in minutes)
maximum_opened = 5
Maximum_assets = max(1, (maximum_opened - 1))