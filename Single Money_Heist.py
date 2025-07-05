from MH_API import Money_Heist
from MH_indicator_factory import Indicators
from concurrent.futures import ThreadPoolExecutor
import sys, subprocess, logging, os, iqoptionapi, asyncio, psutil, shutil, time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    stream=sys.stdout
)

email = "ahmedhasan01@msn.com"
password = "@hmed1992i"
money_heist_api = None  # Will be initialized later
# money_heist_api_lock = asyncio.Lock()
internet_flag = False
last_known_ssid = None
api_flag = False
system_healthy = True
max_reconnection = 3
MAX_CONCURRENT_ASSETS = 2
trading_time = 1 *60
candles_count = 111
OP_code = {}
All_Actives = {}
All_Actives_Lock = asyncio.Lock()
APP_Timer = 0

# //// Checking WIFI Connection and Network - Reconnect to the last WIFI ///

async def is_connected_to_wifi():
    """Check if currently connected to Wi-Fi and update last_known_ssid."""
    global last_known_ssid

    try:
        proc = await asyncio.create_subprocess_shell(
            "netsh wlan show interfaces",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode(errors="ignore")

        if b"State" in stdout and b"connected" in stdout:
            for line in output.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":", 1)[-1].strip()
                    if ssid:
                        last_known_ssid = ssid  # Update the current WIFI name.
                    break
            return True
        return False
    except Exception:
        return False

async def has_internet():
    """Check internet by pinging 1.1.1.1 (lightweight)."""
    try:
        result = await asyncio.create_subprocess_shell(
            "ping -n 1 -w 1000 1.1.1.1",  # Windows ping
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        return await result.wait() == 0
    except Exception:
        return False

async def reconnect_wifi():
    """Reconnect to the last known Wi-Fi network."""

    if not last_known_ssid:
        print("Cannot reconnect: SSID is unknown.")
        return

    try:
        print(f"Attempting to reconnect to: {last_known_ssid}")
        proc = await asyncio.create_subprocess_shell(
            f'netsh wlan connect name="{last_known_ssid}"',
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()  # Waits for the netsh command to complete
    except Exception as e:
        print(f"Failed to reconnect: {e}")

async def check_network_loop():
    """Main async loop to check and maintain internet connection."""
    global internet_flag, api_flag

    while True:
        wifi_connected = await is_connected_to_wifi()
        if not wifi_connected:
            logging.info("Not connected to Wi-Fi. Attempting reconnect...")
            await reconnect_wifi() # Immediately recheck Wi-Fi and continue without delay
            continue
        else:
            logging.info(f"Connected to Wi-Fi: {last_known_ssid}")

        internet = await has_internet()
        if internet:
            internet_flag = True
        else:
            internet_flag = False
            api_flag = False

        logging.info(f"Internet available: {internet_flag}")
        await asyncio.sleep(3)  # Only sleep if everything is OK

# //// Check System health which CPU and Memory not to overdue ////

async def check_system_usage(interval=5):
    """
    Async task to monitor CPU and memory usage.
    
    Updates `system_healthy` flag every `interval` seconds.
    Returns True if both CPU and memory are below the threshold.
    """
    global system_healthy

    while True:
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_usage = psutil.virtual_memory().percent

            system_healthy = cpu_usage < 95 and memory_usage < 99

            logging.info(f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Healthy: {system_healthy}")

        except Exception as e:
            system_healthy = False
            logging.error(f"Error checking system usage: {e}")

        await asyncio.sleep(interval)

# //// Update IQ option Library from repo url ////

def update_iqoptionapi():
    """Checks if the IQ Option API needs an update, updates if required, and restarts the application."""
    
    while not internet_flag:
        logging.info("Waiting for internet_flag to become True to update_iqoptionapi")
        time.sleep(1)

    repo_url = "https://github.com/iqoptionapi/iqoptionapi.git"
    package_name = "api-iqoption-faria"

    # Check for git and pip
    if not shutil.which("git") or not shutil.which("pip"):
        logging.error("Required tools not found: 'git' or 'pip' is missing from PATH.")
        return

    try:
        logging.info("Checking IQ Option API for updates...")

        # Define package installation path
        package_path = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", package_name)

        # Check if package exists
        if os.path.exists(package_path):
            logging.info("Existing installation found, checking for updates...")
            try:
                subprocess.run(["git", "-C", package_path, "fetch"], capture_output=True, text=True, check=True)
                status = subprocess.run(["git", "-C", package_path, "status", "-uno"], capture_output=True, text=True, check=True)

                if "Your branch is behind" in status.stdout:
                    logging.info("Update required. Pulling latest changes...")
                    subprocess.run(["git", "-C", package_path, "pull"], check=True)
                else:
                    logging.info("IQ Option API is already up to date.")
                    return
            except subprocess.CalledProcessError as git_error:
                logging.error(f"Git operation failed: {git_error}")
                return
        else:
            logging.info("Package not found. Cloning repository...")
            try:
                subprocess.run(["git", "clone", repo_url, package_path], check=True)
            except subprocess.CalledProcessError as clone_error:
                logging.error(f"Git clone failed: {clone_error}")
                return

        # Reinstall the package
        try:
            logging.info("Installing the updated version...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", package_path],
                check=True
            )
        except subprocess.CalledProcessError as pip_error:
            logging.error(f"pip install failed: {pip_error}")
            return

        logging.info("IQ Option API updated successfully. Restarting application...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        logging.error(f"Unexpected error updating {package_name}: {e}")

# //// Handles API calls as 1 each time and have max retries ///

async def retry_api_call(func, *args, max_retries=5, timeout=3, priority=1, **kwargs):
    global api_flag

    # Delay low-priority tasks (e.g., priority 2+)
    if priority > 1:
        await asyncio.sleep((priority - 1) * 0.1)  # 0.1s per priority level
    
    for attempt in range(max_retries):
        try:
            # async with money_heist_api_lock:
            loop = asyncio.get_running_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                timeout=timeout
            )

            if not result or result == {} or result == []:
                api_flag = False
                raise ValueError("Received empty or faulty data")

            return result

        except Exception as e:
            logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying ...")
            await asyncio.sleep(0.2)

    logging.error("Max retries reached. API call failed permanently.")
    api_flag = False
    return

# //// Connect to the api and Check it frequently & reconnect or reintiate Money_Heist instance if needed ////

async def monitor_api_connection(max_retries=3):
    global money_heist_api, api_flag, internet_flag

    while True:
        if not api_flag and internet_flag:
            for attempt in range(1, max_retries + 1):
                try:
                    logging.info(f"[Reconnect Attempt {attempt}/{max_retries}] Resetting API and trying to connect...")

                    # Reset the singleton
                    Money_Heist._instance = None
                    
                    # Create a fresh new instance
                    new_api = Money_Heist(email, password)

                    if new_api.connect():
                        money_heist_api = new_api
                        api_flag = True
                        logging.info("Successfully reconnected to Money_Heist API.")
                        break
                    else:
                        api_flag = False
                        logging.warning(f"Connection attempt {attempt} failed.")

                except Exception as e:
                    api_flag = False
                    logging.error(f"Exception on connection attempt {attempt}: {e}")

                await asyncio.sleep(0.5)

            if not api_flag:
                logging.critical("All reconnection attempts failed. Exiting...")
                sys.exit(1)

        await asyncio.sleep(3)

# //// Update the Actives OP codes in the main api library and in the app it self ////

async def update_op_code(UPDATE_INTERVAL_SECONDS=6 * 3600):
    """Fetch OP_code from the API and update constants.py every 6 hours."""
    global OP_code, api_flag

    while True:
        if api_flag and internet_flag:
            try:
                logging.info("Fetching updated OP_code...")
                priority = 1 if not OP_code else 50
                new_op_code = await retry_api_call(money_heist_api.get_all_ACTIVES_OPCODE, timeout=10, priority=priority)

                if new_op_code:

                    # Update constants.py
                    lib_path = os.path.dirname(iqoptionapi.__file__)
                    constants_path = os.path.join(lib_path, "constants.py")

                    if os.path.exists(constants_path):
                        with open(constants_path, "w") as file:
                            file.write(f"ACTIVES = {new_op_code}\n")
                        logging.info(f"constants.py updated successfully at {constants_path}.")
                    else:
                        logging.error("constants.py file not found.")

                    OP_code.clear()
                    OP_code.update(new_op_code)
                    logging.info(f"OP_code updated successfully. Next update in {UPDATE_INTERVAL_SECONDS / 3600} hours.")

                else:
                    logging.warning("Failed to fetch new OP_code (empty result). Retrying later.")

            except Exception as e:
                api_flag = False
                logging.error(f"Error updating OP_code: {e}")

            await asyncio.sleep(UPDATE_INTERVAL_SECONDS)
        else:
            logging.info("API is not connected, waiting for reconnection.")
        
        await asyncio.sleep(1)

# //// synchronize app timer with server time stamp ////

async def synchronize_server_time(sync_interval=5, update_interval_ms=50):
    """
    Async task to synchronize local time with the server timestamp.
    
    sync_interval: seconds between server resyncs.
    update_interval_ms: how often to update the app timer in milliseconds.
    """
    global api_flag, APP_Timer

    offset = 0
    last_sync_time = time.perf_counter()

    while True:
        if api_flag and internet_flag:
            try:
                current_time = time.perf_counter()
                elapsed_time = current_time - last_sync_time

                if elapsed_time >= sync_interval:
                    # Sync with server
                    server_timestamp = await retry_api_call(money_heist_api.get_server_timestamp, priority=1)
                    current_time = time.perf_counter()
                    # Check if server time is behind or equal to current app timer
                    if server_timestamp <= APP_Timer - 0.001:
                        logging.warning("Server timestamp is not progressing — disabling API flag and retrying.")
                        api_flag = False
                        continue  # restart loop
                    APP_Timer = server_timestamp * 1000 / 1000
                    offset = server_timestamp * 1000 - (current_time * 1000)
                    last_sync_time = current_time

                # Continuously update app timer
                APP_Timer = ((time.perf_counter() * 1000) + offset) / 1000

            except Exception as e:
                logging.error(f"Error in async server time sync: {e}")
                await asyncio.sleep(1)  # Back off before retry
            else:
                await asyncio.sleep(update_interval_ms / 1000)  # Sleep ~50ms
        else:
            logging.info("API not connected — skipping time sync.")
            await asyncio.sleep(1)

# //// Get all Actives with there schedules and profits then save them to All_Actives dict////

async def get_active_schedule():
    global api_flag, OP_code, All_Actives

    while True:
        soonest_schedule = []
        new_actives = {}

        if api_flag and internet_flag and OP_code:
            try:
                logging.debug("Fetching market data: open time, init data, profit...")

                all_open = retry_api_call(money_heist_api.get_all_open_time, priority=1)
                all_init = retry_api_call(money_heist_api.get_all_init_v2, priority=1)
                all_profit = retry_api_call(money_heist_api.get_all_profit, priority=1)

                All_Open, All_Init, All_Profit = await asyncio.gather(all_open, all_init, all_profit)

                for active_name, status_data in All_Open.items():
                    OP = OP_code.get(active_name)
                    ST = status_data.get("open")

                    if OP and ST and str(OP) in All_Init:
                        schedule_list = All_Init[str(OP)].get("schedule", [])
                        future_schedules = [
                            s[0] for s in schedule_list if isinstance(s, list) and s[0] > APP_Timer
                        ]

                        if not future_schedules:
                            logging.debug(f"Skipping {active_name}: no future schedules found.")
                            continue

                        min_schedule = min(future_schedules)
                        soonest_schedule.append(min_schedule)

                        profit_dict = All_Profit.get(active_name, {})
                        profit_value = max(profit_dict.values()) if profit_dict else 0.0

                        new_actives[active_name] = {
                            "op_code": OP,
                            "open": ST,
                            "profit": profit_value,
                            "min_schedule": min_schedule
                        }

                async with All_Actives_Lock:
                    for active_name, new_data in new_actives.items():
                        if active_name not in All_Actives:
                            All_Actives[active_name] = new_data
                        else:
                            All_Actives[active_name].update(new_data)

                sorted_actives = dict(sorted(
                    All_Actives.items(),
                    key=lambda item: item[1]["profit"],
                    reverse=True
                ))

                running_count = sum(
                    1 for data in sorted_actives.values() if data.get("running") is True
                ) # count how many assets running in the background

                logging.info(f"Currently running assets: {running_count}/{MAX_CONCURRENT_ASSETS}")

                if running_count < MAX_CONCURRENT_ASSETS:
                    for active_name, data in sorted_actives.items():
                        if not data.get("running", False):
                            min_schedule = data.get("min_schedule")
                            if min_schedule is None:
                                continue

                            while not api_flag and not internet_flag:
                                logging.info("Waiting for api flag & internet_flag to connect to p[en actives]")
                                asyncio.sleep(1)

                            if system_healthy and (min_schedule - 5 * 60) > APP_Timer:
                                logging.info(f"Launching strategy for {active_name} — schedule {min_schedule}")
                                async with All_Actives_Lock:
                                    All_Actives[active_name]["running"] = True

                                asyncio.create_task(fetch_asset_candles(active_name, min_schedule))

                if soonest_schedule:
                    next_time = min(soonest_schedule)
                    sleep_time = max(1, next_time - APP_Timer)
                    logging.debug(f"Sleeping until next schedule in {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                else:
                    logging.debug("No valid schedules found. Sleeping for 5s.")
                    await asyncio.sleep(5)

            except Exception as e:
                api_flag = False
                logging.exception(f"Error in get_active_schedule loop: {e}")
                await asyncio.sleep(1)
        else:
            logging.info("API disconnected or not ready — retrying in 1s.")
            await asyncio.sleep(1)

async def fetch_asset_candles(active_name, min_schedule):
    global api_flag, candles_count, trading_time
    stock = []
    recursion = 0

    async def fetch_candles(count):
        global api_flag
        try:
            return await retry_api_call(
                money_heist_api.get_candles,
                active_name,
                trading_time,
                count,
                APP_Timer,
                timeout=5,
                max_retries=3,
                priority=2
            )
        except Exception as e:
            api_flag = False
            logging.error(f"[{active_name}] Failed to fetch candles: {e}")
            return None


    async def update_stock(candles):
        nonlocal stock, recursion

        if not candles:
            logging.warning(f"[{active_name}] Received empty candles list.")
            return False

        # Filter only historical candles
        filtered = [c for c in candles if c['to'] < APP_Timer]
        if not filtered:
            logging.warning(f"[{active_name}] All fetched candles are too new. Skipping update.")
            return False

        # Initialize or extend stock
        if not stock:
            stock = filtered
            logging.info(f"[{active_name}] Stock initialized with {len(filtered)} candles.")
        else:
            stock.extend(filtered)

        # Deduplicate by 'from' timestamp
        seen = set()
        unique_stock = []
        for c in reversed(stock):  # Start from newest
            if c['from'] not in seen:
                unique_stock.append(c)
                seen.add(c['from'])

        # Sort and trim
        stock = sorted(unique_stock, key=lambda x: x['from'])[-candles_count:]

        # Remove gaps larger than 60 seconds
        cleaned = []
        for i in range(len(stock)):
            if i > 0 and stock[i]['from'] - stock[i - 1]['from'] > 60:
                break  # Stop at the gap
            cleaned.append(stock[i])
        stock = cleaned

        # Retry if incomplete
        if len(stock) < candles_count:
            if recursion >= 3:
                logging.warning(f"[{active_name}] Too many retries. Exiting.")
                return False
            recursion += 1
            difference = candles_count - len(stock)
            extra = await fetch_candles(difference + 1)
            if extra:
                logging.info(f"[{active_name}] Fetched {len(extra)} additional candles.")
                return await update_stock(extra)

        recursion = 0  # Reset retry count
        return True


    while True:
        if api_flag or OP_code is not None:
            if (min_schedule - 5 * 60) <= APP_Timer:
                logging.info(f"[{active_name}] Schedule reached. Exiting task.")
                return

            try:
                if not stock:
                    candles = await fetch_candles(candles_count)
                    if candles and not await update_stock(candles):
                        return
                else:
                    latest_to = max(stock, key=lambda x: x['to'])['to'] + trading_time
                    while APP_Timer < latest_to:
                        delay = latest_to - APP_Timer
                        if delay < -1:
                            logging.warning(f"[{active_name}] Behind by {delay:.2f}s. Resyncing.")
                            candles = await fetch_candles(candles_count)
                            if candles and not await update_stock(candles):
                                return
                            break
                        elif delay > 0.01:
                            await asyncio.sleep(max(0.1, delay * 0.9))
                            continue
                        break

                    candles = await fetch_candles(max(1, candles_count - len(stock)))
                    if candles and not await update_stock(candles):
                        return

                # Run indicators
                result = Indicators(stock).run()
                if isinstance(result, tuple) and len(result) == 2:
                    final_dir, Trade_time = result
                    if final_dir in ['call', 'put'] and Trade_time != 0:
                        wait_time = Trade_time - APP_Timer
                        if wait_time >= 0.5:
                            logging.info(f"[{active_name}] Signal: {final_dir} in {wait_time:.2f}s — prepare to trade.")
            except Exception as e:
                api_flag = False
                logging.error(f"[{active_name}] Strategy failed: {e}")
                return
        else:
            logging.info(f"[{active_name}] Waiting for API connection...")
            await asyncio.sleep(1)

async def main():
    
    # Start background task
    asyncio.create_task(check_network_loop())
    update_iqoptionapi()
    asyncio.create_task(check_system_usage())
    asyncio.create_task(monitor_api_connection())
    asyncio.create_task(update_op_code())
    asyncio.create_task(synchronize_server_time())
    asyncio.create_task(get_active_schedule())

    # Continue your main app logic
    while True:
        await asyncio.sleep(10)  # Keep the event loop alive

if __name__ == "__main__":
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program stopped manually.")
        sys.exit(1)
