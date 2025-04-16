from MH_libraries import threading, logging, gc
from MH_API import Money_Heist
from MH_savings import TradeData
from MH_config import DURATIONS, CASH_TO_TRADE


class Trading_Assets(threading.Thread):
    def __init__(self, active_name: str, schedule: float, trade_signal: str, trade_time: float, stock_data):
        super().__init__(daemon=True)  # Proper initialization
        self.killed = threading.Event()
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData._instance or TradeData()  # Access the already initialized instance
        self.active_name = active_name
        self.schedule = schedule
        self.trade_signal = trade_signal  # 'call' or 'put'
        self.trade_time = trade_time  # Timestamp for the trade
        self.stock_data = stock_data # Part of the stock DataFrame
        logging.info(f"Trading_Asset for {self.active_name} in {self.trade_signal} direction after {self.trade_time - self.trade_data.get_app_timer()}.")

    def run(self):
        """Main loop to execute the trade at the precise time."""
        while not self.killed.is_set() and self.trade_data.get_API_connected().is_set() and self.trade_data.get_app_timer() != 0:
            
            try:
                # Check if trade_time is in the past
                if (self.trade_time - self.trade_data.get_app_timer()) < 0:
                    logging.warning(f"Trade time for {self.active_name} has already passed. Killing thread.")
                    self.kill()
                    return

                if self.killed.is_set():
                    self.kill()
                    return

                # Check if the trade has a matching loss record and adjust trade_signal
                result = self.trade_data.check_loss_record_match(self.stock_data)
                if result is not False:
                    self.trade_signal = result
                    logging.info(f"Trade signal flipped to {self.trade_signal} for {self.active_name} due to loss record match.")
                else:
                    self.kill()
                    return

                # Very tight busy-wait to bridge the final microseconds
                while self.trade_data.get_app_timer() < self.trade_time:
                    delay = self.trade_time - self.trade_data.get_app_timer()
                    if int(delay * 100) > 0.01:
                        if self.killed.wait(delay * 0.9):  # Wait 90% of remaining time or until killed
                            self.kill()
                            return
                        continue  # Continue looping until we hit the exact trade time
                    elif delay < -0.05:
                        logging.warning(f"Trade time for {self.active_name} has already passed. Killing thread.")
                        self.kill()
                        return
                    else:
                        break  # Exit once we've reached the scheduled time

                # After precise wait, execute the trade
                try:
                    # Execute the trade
                    success, id = self.api.buy(CASH_TO_TRADE, self.active_name, self.trade_signal, DURATIONS)
                    if success:
                        logging.info(f"Trade executed successfully for {self.active_name}. Trade ID: {id}")
                        for item in self.stock_data:
                            item['final_dir'] = self.trade_signal
                        self.trade_data.update_trade_ids(id, self.stock_data)
                    else:
                        logging.error(f"Failed to execute trade for {self.active_name}.")
                except Exception as e:
                    logging.error(f"Error executing trade for {self.active_name}: {e}")

            except Exception as e:
                logging.error(f"Error in Trading_Assets thread for {self.active_name}: {e}")

    def kill(self):
        """Gracefully stop the thread."""
        self.killed.set()
        del self.stock_data
        gc.collect()
        logging.info(f"Trading thread for {self.active_name} stopped.")