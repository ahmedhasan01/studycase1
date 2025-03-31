from MH_libraries import threading, logging, gc, time
from MH_API import Money_Heist
from MH_savings import TradeData


class ServerTimeSynchronizer(threading.Thread):
    def __init__(self, sync_interval: int = 60):
        """
        Initialize the ServerTimeSynchronizer.

        Args:
            api: An instance of the IQOption API to fetch the server timestamp.
            sync_interval: The interval (in seconds) between server timestamp synchronization requests.
        """
        threading.Thread.__init__(self)
        self.api = Money_Heist()
        self.trade_data = TradeData()
        self.sync_interval = sync_interval  # Time between API requests (in seconds)
        self.offset = 0  # Difference between server timestamp and local time
        self.last_sync_time = 0  # Timestamp of the last synchronization
        self.killed = threading.Event()  # Flag to control the thread's lifecycle

    def run(self):
        """Main loop to update and synchronize the app_timer."""
        logging.info("ServerTimeSynchronizer started. Waiting for API connection...")
        while not self.killed.is_set() and self.trade_data.get_API_connected().is_set():
            
            if self.killed.is_set():
                self.kill()
                break

            try:
                # Fetch the server timestamp from the API if necessary
                current_time = time.perf_counter()  # High-resolution current time
                elapsed_time = current_time - self.last_sync_time  # Time elapsed since last update
                if elapsed_time >= self.sync_interval:
                    server_timestamp = self.api.get_server_timestamp() * 1000  # Convert to milliseconds
                    self.trade_data.set_app_timer(server_timestamp)
                    self.offset = server_timestamp - (time.perf_counter() * 1000)  # Calculate the offset
                    self.last_sync_time = current_time
                    logging.info(f"Synchronized app_timer with server timestamp: {server_timestamp}")

                self.trade_data.set_app_timer((time.perf_counter() * 1000) + self.offset)  # Convert elapsed_time to milliseconds

                # Sleep for a short interval to avoid busy-waiting
                self.killed.wait(0.01)  # Sleep for 10ms (adjust as needed)

            except Exception as e:
                logging.error(f"Error in ServerTimeSynchronizer thread: {e}")
                self.killed.wait(1)  # Wait before retrying
            finally:
                if self.killed.is_set():
                    self.kill()
                    break

    def kill(self):
        """Gracefully stop the thread."""
        self.killed.set()
        gc.collect()
        logging.info("ServerTimeSynchronizer thread stopped gracefully.")
