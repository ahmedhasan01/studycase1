from MH_libraries import threading, logging, gc
from MH_API import Money_Heist
from MH_savings import TradeData
from MH_config import DURATIONS, CASH_TO_TRADE


class Trading_Assets(threading.Thread):
    def __init__(self, active_name: str, schedule: float, trade_signal: str, trade_time: float, stock_data: dict):
        threading.Thread.__init__(self)
        self.killed = threading.Event()
        self.api = Money_Heist()
        self.active_name = active_name
        self.schedule = schedule
        self.trade_signal = trade_signal  # 'call' or 'put'
        self.trade_time = trade_time  # Timestamp for the trade
        self.stock_data = stock_data # Part of the stock DataFrame
        self.timer = None

    def run(self):
        """Main loop to execute the trade at the precise time."""
        while not self.killed.is_set() and TradeData.API_connected.is_set():
            
            try:
                # Check if trade_time is in the past
                if self.trade_time < TradeData.app_timer:
                    logging.warning(f"Trade time for {self.active_name} has already passed. Killing thread.")
                    self.kill()
                    return

                if self.killed.is_set():
                    self.kill()
                    break

                # Check if the trade has a matching loss record and adjust trade_signal
                if TradeData.check_loss_record_match(self.stock_data):
                    original_signal = self.trade_signal
                    self.trade_signal = "call" if self.trade_signal == "put" else "put"
                    logging.info(f"Trade signal flipped from {original_signal} to {self.trade_signal} for {self.active_name} due to loss record match.")

                # Calculate the delay until the trade_time
                delay = self.trade_time - TradeData.app_timer

                if delay > 0:
                    # Use threading.Timer to get close to the trade_time
                    self.timer = threading.Timer(delay - 0.1, self.precise_trade)  # Schedule 100ms before trade_time
                    self.timer.start()
                else:
                    logging.warning(f"Trade time for {self.active_name} has already passed.")
                    self.kill()
            except Exception as e:
                logging.error(f"Error in Trading_Assets thread for {self.active_name}: {e}")
            finally: self.kill()

    def precise_trade(self):
        """Execute the trade with millisecond precision."""
        while not self.killed.is_set() and TradeData.API_connected.is_set():
            # Busy-wait loop for the final milliseconds
            while TradeData.app_timer < self.trade_time:
                self.killed.wait(max(0, self.trade_time - TradeData.app_timer - 0.001))  # Avoid overshooting

            if self.killed.is_set():
                break

            try:
                # Execute the trade
                success, id = self.api.buy(CASH_TO_TRADE, self.active_name, self.trade_signal, DURATIONS)
                if success:
                    logging.info(f"Trade executed successfully for {self.active_name}. Trade ID: {id}")
                    TradeData.update_trade_ids(id, self.stock_data)
                else:
                    logging.error(f"Failed to execute trade for {self.active_name}.")
            except Exception as e:
                logging.error(f"Error executing trade for {self.active_name}: {e}")
            finally: 
                self.kill()  # Ensure the thread is killed after trade execution

    def kill(self):
        """Gracefully stop the thread."""
        self.killed.set()
        if self.timer:
            self.timer.cancel()  # Cancel the timer if it exists
        del self.stock_data
        gc.collect()
        logging.info(f"Trading thread for {self.active_name} stopped.")
