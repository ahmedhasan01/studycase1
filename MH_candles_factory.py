from MH_libraries import threading, logging, pandas, gc
from MH_API import Money_Heist
from MH_savings import TradeData
from MH_config import DURATIONS, CANDLES_COUNT
from MH_indicator_factory import Indicators
from MH_trading_factor import Trading_Assets


class Candles_Assets(threading.Thread):
    def __init__(self, active_name:str, schedule:float):
        threading.Thread.__init__(self)
        self.killed = threading.Event()
        self.active_name = active_name
        self.schedule = schedule
        self.interval = DURATIONS * 60
        self.candles_count = CANDLES_COUNT
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData()
        self.stock = pandas.DataFrame()  # DataFrame to store candlestick data
        self.trading_threads = []  # List to store active trading threads
        self.sleeping_threads = []  # List to store reusable sleeping threads
        self.schedule_timer = None

    def start_trading_thread(self):
        """Start or reuse a trading thread for the specified asset."""
        merge = self.merge_rows()
        if self.sleeping_threads:
            # Reuse a sleeping thread
            thread = self.sleeping_threads.pop()
            thread.trade_signal = self.stock['final_dir'].iloc[-1]  # Latest trade signal
            thread.trade_time = self.stock['Trade_time'].iloc[-1]  # Latest trade time
            thread.stock_data = merge  # Pass part of the DataFrame
            thread.start()
        else:
            # Start a new thread
            thread = Trading_Assets(
                active_name=self.active_name,
                schedule=self.schedule,
                trade_signal=self.stock['final_dir'].iloc[-1],  # Latest trade signal
                trade_time=self.stock['Trade_time'].iloc[-1],  # Latest trade time
                stock_data=merge  # Pass part of the DataFrame
            )
            thread.start()
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
                    logging.info(f"Trading thread for {thread.active_name} moved to sleeping threads.")

    def fetch_candles(self, count, timestamp:int = TradeData().get_app_timer()):
        """Fetch candlestick data for the specified asset."""
        try:
            candles = self.api.get_candles(self.active_name, self.interval, count + 2, timestamp)
            return candles
        except Exception as e:
            logging.error(f"Failed to fetch candles for {self.active_name}: {e}")
            return None

    def update_stock(self, candles):
        """Update the stock DataFrame with new candles."""
        if candles:
            new_data = pandas.DataFrame(candles)
            new_data = new_data[new_data['to'] < self.trade_data.get_app_timer()]
            if self.stock.empty:
                self.stock = new_data
            else:
                self.stock = pandas.concat([self.stock, new_data], ignore_index=True)
            
            self.stock.drop_duplicates(subset='id', keep='last', inplace=True)
            self.stock.sort_values(by='id', ascending=True, ignore_index=True, inplace=True)
            self.stock.reset_index(drop=True, inplace=True)
            
            # Check for gaps in the sequence
            gap_groups = self.stock.groupby((self.stock['from'].diff().abs() > 60).cumsum())
            if len(gap_groups) > 1:
                self.stock = gap_groups.get_group(0)
            
            # Check for gaps and fetch additional candles if needed
            if len(self.stock) < self.candles_count:
                difference = self.candles_count - len(self.stock)
                additional_candles = self.fetch_candles(count=difference)
                if additional_candles:
                    self.update_stock(additional_candles)
            
            # Maintain rolling window
            self.stock = self.stock.tail(self.candles_count)
            self.stock = Indicators(self.stock).run()
            # Check if next_candle_time is reached
            if self.schedule <= self.trade_data.get_app_timer():
                self.kill()
            else:
                max_from_index = self.stock['from'].idxmax()  # Get the index of the maximum 'from' value
                latest_row = self.stock.loc[max_from_index]  # Get the row with the maximum 'from' value
                # Check if the latest row meets the conditions
                if latest_row['final_dir'] in ['call', 'put'] and latest_row['Trade_time'] != 0:
                    if latest_row['Trade_time'] < (self.trade_data.get_app_timer() - 0.2):
                        self.start_trading_thread()
            
            logging.info(f"Updated stock database for {self.active_name}.")
            gc.collect()  # Force garbage collection
    
    def merge_rows(self):
        idx = self.stock['from'].idxmax()  # Get the index of the maximum 'from' value
        KEEP_SUFFIXES = ('_color', '_dir', 'pattern', 'MTD', 'GTD', 'RTD', 'Timing')
        MERGE_SIZES = (2, 3, 5, 10, 15, 25)  # Define row merge sizes
        DROP_COLS = {'id', 'from', 'to', 'at', 'open', 'close', 'min', 'max', 'volume', 'Trade_time'}
        keep_cols = [col for col in self.stock.columns if col.endswith(KEEP_SUFFIXES)]
        merge_cols = list(set([col for col in self.stock.columns if not col.endswith(KEEP_SUFFIXES)]) - DROP_COLS)
        merged_dict = {}
        for size in MERGE_SIZES:
            subset = self.stock.loc[idx - (size - 1):idx].tail(size)  # Ensure we don't exceed the DataFrame length
            if len(subset) < size:
                continue  # Skip if not enough rows to merge
            subset = subset.drop(columns=DROP_COLS, errors='ignore')
            merged_row = {'count': size}  # Create a dictionary to store merged values
            merged_row.update(subset[keep_cols].iloc[-1].to_dict())
            for col in merge_cols:
                merged_row[col] = ', '.join(map(str, subset[col].dropna().tolist()))  # Merge non-specified columns with ','
            merged_dict[f'merge_{size}'] = merged_row
        gc.collect()
        
        return merged_dict
    
    def run(self):
        """Main loop to update candlestick data."""
        logging.info(f"Waiting for API connection for {self.active_name}...")
        while not self.killed.is_set() and self.trade_data.get_API_connected().is_set() and self.trade_data.get_OP_Code_event().is_set():
            
            if self.killed.is_set():
                self.kill()
                break  # Exit if killed
            
            try:
                if self.stock.empty:
                    # Fetch full candles_count if DataFrame is empty
                    candles = self.fetch_candles(count=self.candles_count)
                    if candles:
                        self.update_stock(candles)
                
                else:
                    delay = self.stock['to'].max() - self.trade_data.get_app_timer()
                    
                    if delay > 0:  # Ensure delay is positive
                        logging.info(f"Scheduling next update for {self.active_name} in {delay} seconds.")
                        self.schedule_timer = threading.Timer(self.stock['to'].max() - self.trade_data.get_app_timer(), self.update_stock_with_timer)
                        self.schedule_timer.start()
                    else:
                        logging.info(f"Next candle time for {self.active_name} has already passed. Fetching immediately.")
                        self.update_stock_with_timer()
                gc.collect()
                self.killed.wait(0.2)
            
            except Exception as e:
                logging.error(f"Error updating candles for {self.active_name}: {e}")
                logging.error(f"API connection lost due to an error. Setting API_connected to False.")
                gc.collect()
            finally:
                if self.killed.is_set():
                    self.kill()
                    break  # Exit if killed

    def update_stock_with_timer(self):
        """Fetch and update stock data when the timer triggers."""
        try:
            if not self.killed.is_set():
                difference = self.candles_count - len(self.stock)  # Fetch the next candle
                candles = self.fetch_candles(count=difference)
                if candles:
                    self.update_stock(candles)
                self.cleanup_threads()  # Check for non-alive threads in trading_threads and move them to sleeping_threads
                
                delay = self.stock['to'].max() - self.trade_data.get_app_timer()
                if delay > 0:  # Ensure delay is positive
                    logging.info(f"Scheduling next update for {self.active_name} in {delay} seconds.")
                    self.schedule_timer = threading.Timer(self.stock['to'].max() - self.trade_data.get_app_timer(), self.update_stock_with_timer)
                    self.schedule_timer.start()
                else:
                    logging.info(f"Next candle time for {self.active_name} has already passed. Fetching immediately.")
                    self.update_stock_with_timer()
                
                gc.collect()
            else:
                self.kill()
        except Exception as e:
            logging.error(f"Error in update_stock_with_timer for {self.active_name}: {e}")
    
    def kill(self):
        """Gracefully stop the thread."""
        self.killed.set()
        if self.schedule_timer:
            self.schedule_timer.cancel()  # Cancel the schedule timer if it exists
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
        del self.stock
        logging.info(f"Thread for {self.active_name} stopped and memory cleaned up.")
        gc.collect()
