from MH_libraries import threading, logging, pandas, gc
from MH_API import Money_Heist
from MH_savings import TradeData
from MH_config import DURATIONS, CANDLES_COUNT, Maximum_assets
from MH_indicator_factory import Indicators
from MH_trading_factory import Trading_Assets


class Candles_Assets(threading.Thread):
    def __init__(self, active_name:str, schedule:float):
        super().__init__(daemon=True)  # Proper initialization
        self.killed = threading.Event()
        self.active_name = active_name
        self.schedule = schedule
        self.interval = DURATIONS * 60
        self.candles_count = CANDLES_COUNT
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData._instance or TradeData()  # Access the already initialized instance
        self.stock = []  # Initialize stock as a list
        self.trading_threads = []  # List to store active trading threads
        self.sleeping_threads = []  # List to store reusable sleeping threads
        self.recursion = 0
        logging.info(f"Initialized Candles_Assets for {self.active_name}")

    def start_trading_thread(self, latest_row, Indication):
        """Start or reuse a trading thread for the specified asset."""
        merge = self.merge_rows(Indication)
        if self.sleeping_threads:
            # Reuse a sleeping thread
            thread = self.sleeping_threads.pop()
            thread.trade_signal = latest_row['final_dir']  # Latest trade signal
            thread.trade_time = latest_row['Trade_time']  # Latest trade time
            thread.stock_data = merge  # Pass part of the DataFrame
            thread.start()
            logging.info(f"Reusing a sleeping trading thread for {self.active_name} in {latest_row['final_dir'] }.")
        else:
            
            # Start a new thread
            thread = self.active_name
            thread = Trading_Assets(
                active_name=self.active_name,
                schedule=self.schedule,
                trade_signal=latest_row['final_dir'],  # Latest trade signal
                trade_time=latest_row['Trade_time'],  # Latest trade time
                stock_data=merge  # Pass part of the DataFrame
            )
            thread.start()
            logging.info(f"Starting a new trading thread for {self.active_name} in {latest_row['final_dir']}.")
        self.trading_threads.append(thread)
        gc.collect()

    def cleanup_threads(self):
        """Move fully killed threads from killing_threads to sleeping_threads."""
        if self.trading_threads:
            for thread in list(self.trading_threads):  # Use list() to avoid runtime errors
                if not thread.is_alive():  # Check if the thread has fully stopped)
                    thread.join()  # Ensure it is properly joined
                    self.sleeping_threads.append(thread)  # Move to sleeping_threads
                    self.trading_threads.remove(thread)  # Remove the thread from trading_threads
                    logging.info(f"Moved trading thread for {thread.active_name} to sleeping threads.")

    def fetch_candles(self, count):
        """Fetch candlestick data for the specified asset."""
        try:
            logging.info(f"Fetching {count} candles for {self.active_name}.")
            candles = self.api.get_candles(self.active_name, self.interval, count + 2, TradeData().get_app_timer())
            return candles
        except Exception as e:
            logging.error(f"Failed to fetch candles for {self.active_name}: {e}")
            return None

    def update_stock(self, candles):
        """Update the stock list with new candles."""
        if candles:
            logging.info(f"Updating stock for {self.active_name} with {len(candles)} new candles.")
            
            # Filter candles based on 'to' timestamp
            filtered_new_data = [candle for candle in candles if candle['to'] < self.trade_data.get_app_timer()]
            
            # If stock is empty, initialize with new data
            if not self.stock:
                self.stock = filtered_new_data
                logging.info(f"Initialized stock for {self.active_name} with {len(filtered_new_data)} candles.")
            else:
                logging.info(f"Current stock size: {len(self.stock)} candles. Merging new data.")
                self.stock.extend(filtered_new_data)

            # Remove duplicates based on 'from' and sort by 'from' value
            seen_ids = set()
            unique_stock = []
            for candle in reversed(self.stock):  # Iterate in reverse order
                if candle['from'] not in seen_ids:
                    unique_stock.append(candle)
                    seen_ids.add(candle['from'])

            # Sort the stock by 'id' timestamp
            self.stock = sorted(unique_stock, key=lambda x: x['from'])

            # Maintain rolling window of candles
            self.stock = self.stock[-self.candles_count:]
            
            # Check for gaps in the sequence based on the 'from' column
            cleaned_stock = []
            for i in range(len(self.stock)):
                if i > 0:
                    time_diff = self.stock[i]['from'] - self.stock[i - 1]['from']
                    if time_diff > 60:
                        logging.warning(f"Detected gaps in the stock data for {self.active_name}. Keeping only the first group.")
                        break
                cleaned_stock.append(self.stock[i])

            self.stock = cleaned_stock  # Replace original with cleaned one

            # Check if additional candles need to be fetched
            if len(self.stock) < self.candles_count:
                if self.recursion >= 3:
                    logging.error(f"Gaps persisted after 3 retries for {self.active_name}. Killing thread.")
                    self.kill()
                    return
                self.recursion += 1
                difference = max(1, self.candles_count - len(self.stock))
                additional_candles = self.fetch_candles(count=difference)
                if additional_candles:
                    logging.info(f"Fetched {len(additional_candles)} additional candles.")
                    self.update_stock(additional_candles)

            self.recursion = 0

            logging.info(f"Stock updated. New stock size: {len(self.stock)} candles after removing duplicates and sorting and rolling window.")
            # Apply indicators to the stock data
            Indication = Indicators(self.stock).run()

            # Check if it's time to kill the thread based on schedule and app timer
            if self.schedule <= self.trade_data.get_app_timer():
                logging.info(f"Schedule time reached. Killing thread for {self.active_name}.")
                self.kill()
            else:
                latest_row = Indication.loc[Indication['from'].idxmax()]  # Get row with max 'from'

                # Check trade condition
                if latest_row['final_dir'] in ['call', 'put'] and latest_row['Trade_time'] != 0:
                    time_to_trade = latest_row['Trade_time'] - self.trade_data.get_app_timer()
                    if time_to_trade >= 0.5:
                        logging.info(
                            f"Starting trading thread for {self.active_name} with signal {latest_row['final_dir']} "
                            f"after {time_to_trade:.2f}."
                        )
                        self.start_trading_thread(latest_row, Indication)


            # Final logging of stock size after all updates
            logging.info(f"Final stock size for {self.active_name} after update: {len(self.stock)} candles.")
            
            # Force garbage collection to release memory
            del Indication
            gc.collect()

    def merge_rows(self, df: pandas.DataFrame) -> pandas.DataFrame:
        idx = df['from'].idxmax()
        KEEP_SUFFIXES = ('_color', '_dir', 'pattern', 'MTD', 'GTD', 'RTD', 'Timing')
        MERGE_SIZES = (2, 3, 5, 10, 15, 25)
        DROP_COLS = {'id', 'from', 'to', 'at', 'open', 'close', 'min', 'max', 'volume', 'Trade_time'}

        keep_cols = [col for col in df.columns if col.endswith(KEEP_SUFFIXES)]
        merge_cols = list(set([col for col in df.columns if not col.endswith(KEEP_SUFFIXES)]) - DROP_COLS)

        merged_rows = []

        for size in MERGE_SIZES:
            start_idx = max(0, idx - (size - 1))
            subset = df.loc[start_idx:idx].tail(size)

            if len(subset) < size:
                continue

            subset_clean = subset.drop(columns=DROP_COLS, errors='ignore')
            merged_row = {'count': size}
            merged_row.update(subset_clean[keep_cols].iloc[-1].to_dict())

            for col in merge_cols:
                merged_row[col] = ', '.join(map(str, subset_clean[col].dropna().tolist()))

            merged_rows.append(merged_row)

        # merged_df = pandas.DataFrame(merged_rows)
        return merged_rows
            
    def run(self):
        """Main loop to update candlestick data."""
        logging.info(f"Starting Candles_Assets thread for {self.active_name}.")
        
        while not self.killed.is_set():
            # Wait until the API connection is established or the killed flag is set
            while not (self.trade_data.get_API_connected().is_set() and self.trade_data.get_OP_Code_event().is_set() and self.trade_data.get_app_timer() > 0):
                if self.killed.wait(1):  # Waits up to 1 second but exits if killed
                    logging.warning(f"Thread {self.active_name} received kill signal while waiting for API connection.")
                    self.kill()
                    return  # Exit immediately

            if self.killed.is_set():
                self.kill()
                return  # Exit if killed

            try:
                if not self.stock:  # If the stock is empty (list is empty)
                    logging.info(f"Stock is empty, fetching full candles count for {self.active_name}.")
                    candles = self.fetch_candles(count=self.candles_count)
                    if candles:
                        self.update_stock(candles)

                else:
                    # Calculate the delay based on the last 'to' value in stock and current app timer
                    latest_to = max(self.stock, key=lambda x: x['to'])['to']  + self.interval
                    delay = latest_to - self.trade_data.get_app_timer()
                    logging.info(f"Next candle time counting {delay:.3f} seconds for {self.active_name}, fetching in a while.")
                    while self.trade_data.get_app_timer() < latest_to:
                        delay = latest_to - self.trade_data.get_app_timer()
                        if int(delay * 100) > 0.01:
                            if self.killed.wait(delay * 0.9):  # Wait 90% of remaining time or until killed
                                self.kill()
                                return
                            continue  # Continue looping until we hit the exact trade time
                        elif delay < -1:
                            logging.warning(f"{self.active_name}: Delay too far behind ({delay:.2f}s). Forcing resync.")
                            candles = self.fetch_candles(count=self.candles_count)
                            if candles:
                                self.update_stock(candles)
                            break  # After resync, re-check delay and proceed
                        else:
                            break  # Exit once we've reached the scheduled time

                    logging.info(f"Getting Next candle time passed {delay:.3f} seconds for {self.active_name}.")
                    difference = max(1, self.candles_count - len(self.stock))
                    candles = self.fetch_candles(count=difference)
                    if candles:
                        self.update_stock(candles)

                gc.collect()

            except Exception as e:
                logging.error(f"Error updating candles for {self.active_name}: {e}")
                gc.collect()

            finally:
                if self.killed.is_set():
                    self.kill()
                    return  # Exit if killed

    def kill(self):
        """Gracefully stop the thread."""
        self.killed.set()
        
        # Check and kill all alive threads in trading_threads
        if self.trading_threads:
            for thread in list(self.trading_threads):  # Use list() to avoid runtime errors
                if thread.is_alive():  # Check if the thread is alive
                    logging.info(f"Killing trading thread for {thread.active_name}.")
                    thread.kill()  # Gracefully stop the thread
                    thread.join()
                self.trading_threads.remove(thread)  # Remove the thread from trading_threads
        
        # Check and kill all alive threads in sleeping_threads
        if self.sleeping_threads:
            for thread in list(self.sleeping_threads):  # Use list() to avoid runtime errors
                if thread.is_alive():  # Check if the thread is alive
                    logging.info(f"Killing sleeping thread for {thread.active_name}.")
                    thread.kill()  # Gracefully stop the thread
                    thread.join()
                self.sleeping_threads.remove(thread)  # Remove the thread from sleeping_threads
        
        # If stock exists and is not None, delete it
        if hasattr(self, 'stock') and self.stock:
            self.stock.clear()  # Clear the list instead of using del
            logging.info(f"Stock for {self.active_name} has been cleared.")
        
        logging.info(f"Thread for {self.active_name} stopped and memory cleaned up.")
        gc.collect()
