from MH_libraries import threading, logging, os, pandas

class TradeData:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TradeData, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        
        self.API_connected = threading.Event()

        self.app_timer = 0  # Shared variable to store the synchronized timestamp in milliseconds
        self.app_timer_lock = threading.Lock()  # Lock for thread-safe access to app_timer

        self.OP_Code = None  # OP Code for storing information
        self.OP_Code_event = threading.Event()  # Event for thread-safe access to OP_Code

        self.trade_ids = {}  # List to store trade IDs
        self.trade_ids_lock = threading.Lock()  # Lock for thread-safe access to trade_ids

        self.trade_status = {}
        self.trade_status_lock = threading.Lock()  # Lock for thread-safe access to trade_status

        self.loss_records = {}
        self.loss_records_lock = threading.Lock()  # Lock for thread-safe access to loss_records

        self.__initialized = True  # Prevent re-initialization

    def API_connection(self, set: int = 0):
        # Remove the key and get its value
        if set == 1:
            self.API_connected.set()  # Mark API as connected (resume updates)
            logging.info("API connection established. Resuming updates.")
        elif set == 0:
            self.API_connected.clear()  # Mark API as disconnected (pause updates).
            logging.warning("API connection lost. Updates paused.")

    def get_API_connected(self):
        
        return self.API_connected

    def set_app_timer(self, time):
        """
        Set the app_timer by a specified value in a thread-safe manner.

        Args:
            Set: The value to add to app_timer (in milliseconds).
        """
        with self.app_timer_lock:
            self.app_timer = time

    def get_app_timer(self):
        
        return self.app_timer

    def get_OP_Code(self):
        
        return self.OP_Code

    def get_OP_Code_event(self):
        
        return self.OP_Code_event

    def update_OP_Code(self, value):
        
        self.OP_Code = value

    def set_OP_Code(self):
        
        self.OP_Code_event.set()

    def get_trade_ids(self):
        
        return self.trade_ids

    def get_trade_status(self):
        
        return self.trade_status

    def get_loss_records(self):
        
        return self.loss_records
    def update_trade_ids(self, key, value):
        with self.trade_ids_lock:
            self.trade_ids[key] = value

    def delete_trade_ids(self, id_list):
        with self.trade_ids_lock:
            for id in id_list:
                del self.trade_ids[id]

    def update_trade_status(self, status):
        with self.trade_status_lock:
            if status not in self.trade_status:
                self.trade_status[status] = 1
            else:
                self.trade_status[status] += 1

    def load_loss_records(self, filename="loss_records.csv"):
        """Loads loss records from a CSV file if it exists and updates the global loss_records dictionary."""

        if os.path.exists(filename):
            try:
                df = pandas.read_csv(filename)
                with self.loss_records_lock:
                    self.loss_records = df.to_dict('records')
                logging.info(f"Loaded {len(self.loss_records)} records from {filename}")
            except Exception as e:
                logging.error(f"Error loading {filename}: {e}")
        else:
            logging.info(f"No existing {filename} found, starting with an empty dictionary.")

    def update_loss_records(self, merged_list):
        
        if not merged_list:
            logging.info("Merged dictionary is empty. No updates will be made.")
            return  # Stop execution if merged_list is empty

        for new_entry in merged_list:
            direction = new_entry.get('final_dir')
            # Initialize call/put counts
            new_entry['call'] = 0
            new_entry['put'] = 0

            # Step 1: Add 'call' or 'put' key with value 1
            if direction in ['call', 'put']:
                new_entry[direction] += 1

            # Step 2: Create a comparable version of the entry (excluding final_dir, call, put)
            match_keys = {k: v for k, v in new_entry.items() if k not in ['final_dir', 'call', 'put']}

            found = False
            for record in self.loss_records:
                record_keys = {k: v for k, v in record.items() if k not in ['final_dir', 'call', 'put']}
                if match_keys == record_keys:
                    # If match, increment the existing 'call' or 'put' value
                    record[direction] += new_entry[direction]
                    found = True
                    break

            # Step 3: If no match, append new entry
            if not found:
                self.loss_records.append(new_entry)

        logging.info("Updated loss records with new entries.")

    def save_loss_records(self):
        """Saves loss_records dictionary to a CSV file."""
        try:
            df = pandas.DataFrame(self.loss_records)
            df.to_csv("loss_records.csv", index=False)  # Save as CSV
            logging.info(f"Successfully saved {len(self.loss_records)} records to loss_records.csv")
        except Exception as e:
            logging.error(f"Error saving loss records: {e}")
        finally: del df

    def check_loss_record_match(self, merged_list):
        """
        Check for matches between merged_list and loss_records.
        
        Args:
            merged_list (list of dicts): Incoming trade data entries.
        
        Returns:
            str or bool: Flipped signal if clear, False if ambiguous, or original signal if no match.
        """
        if not merged_list:
            return False

        for entry in merged_list:
            match_keys = {k: v for k, v in entry.items() if k not in ['call', 'put']}
            match_found = False

            for record in self.loss_records:
                record_keys = {k: v for k, v in record.items() if k not in ['call', 'put']}
                if match_keys == record_keys:
                    match_found = True
                    call_count = record.get('call', 0)
                    put_count = record.get('put', 0)

                    if call_count > 0 and put_count == 0:
                        return 'put'
                    elif put_count > 0 and call_count == 0:
                        return 'call'
                    else:
                        return False

            if not match_found:
                continue

        return merged_list[-1].get('final_dir', False)