from MH_libraries import threading, logging, subprocess, gc, requests, random
from MH_API import Money_Heist
from MH_savings import TradeData


class Check_Email(threading.Thread):
    """Class to monitor network and API connection status."""

    def __init__(self):
        threading.Thread.__init__(self)
        self.killed = threading.Event()
        self.current_wifi = self.get_current_wifi()
        self.network_attempt_failed = 0
        self.signing_timer = 60  # Timer interval in seconds
        self.signing_timering = None
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData()

    def get_current_wifi(self):
        """Retrieve the current Wi-Fi network name using PowerShell."""
        try:
            result = subprocess.check_output("powershell.exe (get-netconnectionProfile).Name", shell=True)
            return result.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to retrieve Wi-Fi network name: {e}")
            return "Unknown"
        except Exception as e:
            logging.error(f"Unexpected error retrieving Wi-Fi network name: {e}")
            return "Unknown"

    def check_network_connection(self):
        """Check if there is an active internet connection."""
        try:
            response = requests.get("http://www.google.com", timeout=3)
            if response.status_code == 200:
                return True
            else:
                logging.warning(f"Unexpected status code: {response.status_code}")
                self.trade_data.API_connection(0)
                return False
        except requests.RequestException as e:
            self.trade_data.API_connection(0)
            logging.warning(f"No internet connection detected: {e}")
            return False
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Unexpected error checking network connection: {e}")
            return False

    def reconnect_to_wifi(self):
        """Attempt to reconnect to the Wi-Fi network."""
        try:
            subprocess.run(["powershell.exe", "netsh wlan connect name=" + self.current_wifi], shell=True, check=True)
            logging.warning(f"Attempting to reconnect to Wi-Fi: {self.current_wifi}")
        except subprocess.CalledProcessError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to reconnect to Wi-Fi: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Unexpected error reconnecting to Wi-Fi: {e}")

    def start_signing_timer(self):
        """Start or restart the signing timer."""
        try:
            if self.signing_timering is not None:
                self.signing_timering.cancel()  # Cancel the existing timer if it exists
            self.signing_timering = threading.Timer(self.signing_timer, self.run)
            self.signing_timering.start()
            logging.info("Signing timer started/restarted.")
        except Exception as e:
            logging.error(f"Failed to start/restart signing timer: {e}")

    def handle_network_issues(self):
        """Handle network connection issues."""
        try:
            while self.network_attempt_failed < 6:
                self.reconnect_to_wifi()
                if self.check_network_connection():
                    logging.info("Network connection restored.")
                    self.start_signing_timer()
                    return
                else:
                    self.network_attempt_failed += 1
                    logging.warning(f"Network reconnection attempt {self.network_attempt_failed} failed.")
            # If all attempts fail
            logging.error("Maximum network reconnection attempts reached. Exiting...")
            logging.info("Check Your Internet Connection")
            self.kill()
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error handling network issues: {e}")
            logging.info("Network handling error.")
            self.kill()

    def handle_api_connection(self):
        """Handle API connection issues."""
        try:
            if not self.trade_data.get_API_connected().is_set():
                logging.warning("API is disconnected. Attempting to reconnect...")
                if not self.api.connect():
                    self.handle_api_retries()
                else:
                    logging.info("Successfully reconnected to IQ Option API.")
                    self.start_signing_timer()
            else:
                logging.info("API connection is active.")
                self.start_signing_timer()
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error handling API connection: {e}")
            logging.info("API handling error.")
            self.kill()

    def handle_api_retries(self):
        retry_delay = 1  
        max_retry_delay = 20  # Increase max delay
        attempts = 0  

        while attempts < 10:  # Allow up to 10 attempts before giving up
            if self.api.connect():
                attempts = 0
                logging.info("Successfully reconnected to API.")
                return

            attempts += 1
            wait_time = retry_delay + random.uniform(0, 2)
            logging.warning(f"API reconnection failed. Retrying in {round(wait_time, 2)} seconds...")
            
            self.killed.wait(wait_time)
            retry_delay = min(retry_delay * 2, max_retry_delay)

        logging.error("API reconnection failed after multiple attempts. Exiting.")
        self.kill()

    def run(self):
        """Main loop to handle network and API connections."""
        logging.info("Check email started.")
        while not self.killed.is_set():
            try:
                if not self.check_network_connection():
                    self.handle_network_issues()
                elif not self.trade_data.get_API_connected().is_set():
                    self.handle_api_connection()
                
                if self.killed.is_set():
                    logging.error("Main loop is killed")
                    logging.info("Main loop shuting down.")
                    break
                
                # Sleep for a short interval to avoid busy-waiting
                self.killed.wait(1)
            except ConnectionError as e:
                self.trade_data.API_connection(0)
                logging.error(f"Connection error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error in main loop: {e}")
                logging.info("Main loop error.")
                self.kill()
    
    def kill(self):
        """Kill the thread gracefully."""
        self.trade_data.API_connection(0)
        self.killed.set()
        if self.signing_timering:
            self.signing_timering.cancel()
        gc.collect()
        logging.info("Check Email thread stopped gracefully.")
