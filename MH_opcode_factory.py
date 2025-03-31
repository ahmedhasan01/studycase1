from MH_libraries import threading, logging, os, gc
from MH_API import Money_Heist
from MH_savings import TradeData


class OPCodeUpdater(threading.Thread):
    """Separate thread to update OP_code every 6 hours."""
    def __init__(self, update_interval = 6 * 3600):  # 6 hours in seconds
        threading.Thread.__init__(self)
        self.killed = threading.Event()  # Used for thread termination
        self.api = Money_Heist()
        self.trade_data = TradeData()
        self.update_interval = update_interval

    def fetch_op_code(self):
        """Fetch OP_code from the API and update the global OP_Code."""
        new_op_code = self.api.get_all_ACTIVES_OPCODE()
        
        if new_op_code != self.trade_data.get_OP_Code():  # Only update if there's a change
            self.trade_data.update_OP_Code(new_op_code)
            self.update_constants_file(new_op_code)
            self.trade_data.set_OP_Code()
            logging.info("OP_Code updated successfully.")
        else:
            logging.info("OP_Code unchanged. No update needed.")

    def update_constants_file(self, OP_Code):
        """Update the constants.py file in the iqoptionapi directory."""
        try:
            # Search for the constants.py file in the iqoptionapi folder (nested or not)
            constants_path = None
            for root, dirs, files in os.walk("."):  # Start searching from the current directory
                if "iqoptionapi" in dirs:
                    iqoptionapi_path = os.path.join(root, "iqoptionapi")
                    if "constants.py" in os.listdir(iqoptionapi_path):
                        constants_path = os.path.join(iqoptionapi_path, "constants.py")
                        break
                # Check if iqoptionapi is nested in subdirectories
                for dir_name in dirs:
                    if dir_name == "iqoptionapi":
                        iqoptionapi_path = os.path.join(root, dir_name)
                        if "constants.py" in os.listdir(iqoptionapi_path):
                            constants_path = os.path.join(iqoptionapi_path, "constants.py")
                            break

            if constants_path:
                # Open the constants.py file in write mode
                with open(constants_path, "w") as file:
                    # Write the updated ACTIVES dictionary to the file
                    file.write(f"ACTIVES = {OP_Code}\n")
                logging.info(f"constants.py file updated successfully at {constants_path}.")
            else:
                logging.error("constants.py file not found in the iqoptionapi folder.")
        except Exception as e:
            logging.error(f"Failed to update constants.py file: {e}")
    
    def run(self):
        """Main loop to update OP_code periodically."""
        logging.info("OPCodeUpdater started. Waiting for API connection...")
        while not self.killed.is_set() and self.trade_data.get_API_connected().is_set():
            
            if self.killed.is_set():
                self.kill()
                break  # Exit if killed

            try:
                # Fetch OP_code if it is None or every 6 hours
                if self.trade_data.get_OP_Code() is None:
                    self.fetch_op_code()
                else:
                    self.killed.wait(self.update_interval)  # Wait for the update interval, but wake up early if killed
                    self.fetch_op_code()
            except Exception as e:
                logging.error(f"Failed to update Op-Code: {e}")
            finally:
                if self.killed.is_set():
                    self.kill()
                    break  # Exit if killed

        logging.info("OPCodeUpdater thread stopped.")
        gc.collect()  # Clean up resources before exiting

    def kill(self):
        """Kill the thread gracefully."""
        self.killed.set()  # Wake up the thread if it's waiting
        gc.collect()
        logging.info("OPCodeUpdater thread stopped gracefully.")
