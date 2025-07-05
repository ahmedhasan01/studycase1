from telethon import TelegramClient, events
from datetime import datetime, timedelta
from iqoptionapi.stable_api import IQ_Option
import pytz
import re
import time
import asyncio

# === Telegram credentials ===
api_id = 28437684
api_hash = 'af0ee77d4058c12d0138dcbb1bd1cfe6'
channel_username = 'iqpocket'

# === IQ Option credentials ===
IQ_USERNAME = 'ahmedhasan01@msn.com'
IQ_PASSWORD = '@hmed1992i'

# === Trade configuration ===
TRADE_AMOUNT = 1
BALANCE_TYPE = 'PRACTICE'  # or 'REAL'
TIMEZONE = pytz.timezone('Etc/UTC')  # adjust if needed

# === Create Telegram client ===
client = TelegramClient('session_name', api_id, api_hash)

# === Connect to IQ Option ===
I_want_money = IQ_Option(IQ_USERNAME, IQ_PASSWORD)
I_want_money.connect()
I_want_money.change_balance("PRACTICE")

print("✅ Connected to IQ Option")


assets = I_want_money.get_all_init_v2()['turbo']['actives']['76']['schedule']

# === Assets monitoring ===
assets = {}

def refresh_assets():
    global assets
    try:
        I_want_money.update_ACTIVES_OPCODE()
        op_code = I_want_money.get_all_ACTIVES_OPCODE()
        open_assets_info = I_want_money.get_all_open_time()['turbo']
        assets = [asset for asset, info in open_assets_info.items() if info.get('open')]
        assets = {
            asset: op_code.get(asset)
            for asset, info in open_assets_info.items()
            if info.get('open') and op_code.get(asset) is not None
        }
        print(f"🔄 Assets refreshed: {len(assets)} available")
    except Exception as e:
        print(f"⚠️ Error refreshing assets: {e}")

# === Separate background task to update assets every 2 minutes ===
async def keep_refreshing_assets():
    while True:
        refresh_assets()
        await asyncio.sleep(120)  # Wait 2 minutes

# === Signal extraction ===
def extract_signal(message):
    pattern = r"([A-Z]{3}/[A-Z]{3}).*?\b(CALL|PUT)\b"
    timeframe_pattern = r"TIMEFRAME\s+(M\d+)"
    
    signal_match = re.search(pattern, message.upper())
    timeframe_match = re.search(timeframe_pattern, message.upper())

    if signal_match:
        base_asset, direction = signal_match.groups()
        base_asset = base_asset.replace("/", "")

        # Match base_asset to the available asset list (assets)
        full_asset = None
        for a in assets:
            if base_asset in a.replace("-", "").replace("_", ""):
                full_asset = a
                break
        
        if full_asset is None:
            print(f"⚠️ Asset {base_asset} not found in available assets!")
            return None, None, None

        timeframe = timeframe_match.group(1) if timeframe_match else "M1"
        duration = int(timeframe[1:]) * 60  # e.g., M1 -> 60 seconds
        return full_asset, direction.lower(), duration

    return None, None, None

# === Place trade at perfect timing ===
def execute_trade(asset, direction, duration):
    now = datetime.now(TIMEZONE)
    next_candle = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    wait_seconds = (next_candle - now).total_seconds()
    
    print(f"⏳ Waiting {wait_seconds:.2f} seconds for entry at {next_candle.time()} (UTC−3)...")
    # time.sleep(wait_seconds)

    success, trade_id = I_want_money.buy(TRADE_AMOUNT, asset, direction, duration)
    print(f"📈 Trade executed: {success}, trade ID: {trade_id}")

# === Listen for new messages ===
@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    message = event.message.message
    asset, direction, duration = extract_signal(message)
    if asset and direction and duration:
        execute_trade(asset, direction, duration)
        print(f"\n🚨 Signal: {asset} | {direction.upper()} | {duration}min")

# === Start bot ===
async def main():
    await client.start()
    print("📡 Listening for signals in real time...")
    await asyncio.gather(
        client.run_until_disconnected(),
        keep_refreshing_assets()
    )

asyncio.run(main())
