from MH_libraries import threading, logging, subprocess, gc, requests, random
from MH_API import Money_Heist
from MH_savings import TradeData


class Check_Email(threading.Thread):
    """Class to monitor network and API connection status."""

    def __init__(self):
        super().__init__(daemon=True)
        self.killed = threading.Event()
        self.current_wifi = self.get_current_wifi()
        self.network_attempt_failed = 0
        self.api = Money_Heist._instance
        self.trade_data = TradeData._instance or TradeData()
        logging.info("Check_Email thread initialized.")

    def get_current_wifi(self):
        """Retrieve the current Wi-Fi network name using PowerShell."""
        try:
            result = subprocess.check_output("powershell.exe (get-netconnectionProfile).Name", shell=True)
            wifi_name = result.decode("utf-8").strip()
            logging.info(f"Current Wi-Fi network: {wifi_name}")
            return wifi_name
        except Exception as e:
            logging.error(f"Error retrieving Wi-Fi network: {e}")
            return "Unknown"

    def check_network_connection(self):
        """Check if there is an active internet connection."""
        try:
            response = requests.get("http://www.google.com", timeout=3)
            if response.status_code == 200:
                logging.info("Internet connection is active.")
                return True
        except requests.RequestException:
            logging.warning("No internet connection detected.")
        
        self.trade_data.API_connection(0)
        return False

    def reconnect_to_wifi(self):
        """Attempt to reconnect to the Wi-Fi network."""
        try:
            logging.warning(f"Attempting to reconnect to Wi-Fi: {self.current_wifi}")
            subprocess.run(["powershell.exe", "netsh wlan connect name=" + self.current_wifi], shell=True, check=True)
            logging.info("Wi-Fi reconnection attempt made.")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Wi-Fi reconnection failed: {e}")

    def handle_network_issues(self):
        """Handle network reconnection attempts."""
        for attempt in range(6):
            logging.warning(f"Network reconnection attempt {attempt + 1}/6...")
            self.reconnect_to_wifi()
            if self.check_network_connection():
                logging.info("Network connection restored.")
                return
        
        logging.error("Maximum network reconnection attempts reached. Exiting...")
        self.kill()

    def handle_api_connection(self):
        """Attempt to reconnect to the API if disconnected."""
        if not self.trade_data.get_API_connected().is_set():
            logging.warning("API is disconnected. Attempting to reconnect...")
            if not self.api.connect():
                logging.error("Initial API reconnection attempt failed. Retrying...")
                self.handle_api_retries()
            else:
                logging.info("Successfully connected to API.")
        else:
            logging.info("API connection is active.")

    def handle_api_retries(self):
        """Exponential backoff for API reconnection attempts."""
        retry_delay = 1  # Initial retry delay
        max_retry_delay = 20

        for attempt in range(10):
            logging.warning(f"API reconnection attempt {attempt + 1}/10...")
            if self.api.connect():
                logging.info("Successfully reconnected to API.")
                return
            
            wait_time = min(retry_delay + random.uniform(0, 2), max_retry_delay)
            logging.warning(f"Retrying API connection in {round(wait_time, 2)} seconds...")
            self.killed.wait(wait_time)
            retry_delay *= 2

        logging.error("API reconnection failed after multiple attempts. Exiting.")
        self.kill()

    def run(self):
        """Main loop to handle network and API connections."""
        logging.info("Check email thread started.")
        
        while not self.killed.is_set():
            try:
                if not self.check_network_connection():
                    logging.warning("Network issue detected. Handling reconnection...")
                    self.handle_network_issues()
                elif not self.trade_data.get_API_connected().is_set():
                    logging.warning("API issue detected. Handling reconnection...")
                    self.handle_api_connection()
                
                if self.killed.is_set():
                    logging.info("Main loop shutting down.")
                    self.kill()
                    return
                
                # Dynamically adjust wait time
                wait_time = 60 if self.trade_data.get_API_connected().is_set() else 1
                logging.info(f"Next check in {wait_time} seconds.")
                self.killed.wait(wait_time)
            except Exception as e:
                logging.error(f"Unexpected error in main loop: {e}")
                self.kill()

    def kill(self):
        """Kill the thread gracefully."""
        logging.warning("Stopping Check Email thread.")
        self.trade_data.API_connection(0)
        self.killed.set()
        gc.collect()
        logging.info("Check Email thread stopped gracefully.")