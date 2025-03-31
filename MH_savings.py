from MH_libraries import threading, logging, os, pandas

class TradeData:
    def __init__(self):
        
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

    def get_app_timer(self):
        
        return self.app_timer

    def get_OP_Code(self):
        
        return self.OP_Code

    def get_OP_Code_event(self):
        
        return self.OP_Code_event

    def get_trade_ids(self):
        
        return self.trade_ids

    def get_trade_status(self):
        
        return self.trade_status

    def get_loss_records(self):
        
        return self.loss_records

    def set_app_timer(self, time):
        """
        Set the app_timer by a specified value in a thread-safe manner.

        Args:
            Set: The value to add to app_timer (in milliseconds).
        """
        with self.app_timer_lock:
            self.app_timer = time

    def update_OP_Code(self, value):
        
        self.OP_Code = value

    def set_OP_Code(self):
        
        self.OP_Code_event.is_set()

    def update_trade_ids(self, key, value):
        with self.trade_ids_lock:
            self.trade_ids[key] = value

    def delete_trade_ids(self, id):
        with self.trade_ids_lock:
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
                    self.loss_records = {
                        tuple(row.drop(["call", "put"]).astype(str).items()): {"call": row["call"], "put": row["put"]}
                        for _, row in df.iterrows()
                    }
                logging.info(f"Loaded {len(self.loss_records)} records from {filename}")
            except Exception as e:
                logging.error(f"Error loading {filename}: {e}")
        else:
            logging.info(f"No existing {filename} found, starting with an empty dictionary.")

    def update_loss_records(self, merged_dict):
        """Updates loss_records dictionary with new merged data and saves to CSV."""
        # matching_rows = loss_records[comparison_cols].merge(merged_df[comparison_cols], on=list(self.loss_records[comparison_cols]), how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1).index

        if not merged_dict:
            logging.info("Merged dictionary is empty. No updates will be made.")
            return  # Stop execution if merged_dict is empty

        logging.info(f"Updating loss records with {len(merged_dict)} new entries.")

        for key, record in merged_dict.items():
            # Convert all values to strings for consistency
            record = {k: str(v) for k, v in record.items()}
            # Initialize call/put counts
            record['call'] = 0
            record['put'] = 0
            # Increment call/put counts based on 'final_dir'
            if record.get('final_dir') == 'call':
                record['call'] += 1
            elif record.get('final_dir') == 'put':
                record['put'] += 1

            # Generate a unique identifier (hashable tuple of key-value pairs excluding 'call' and 'put')
            comparison_key = tuple((k, v) for k, v in record.items() if k not in {'call', 'put'})
            with self.loss_records_lock:
                if comparison_key in self.loss_records:
                    # Update existing entry
                    self.loss_records[comparison_key]['call'] += record['call']
                    self.loss_records[comparison_key]['put'] += record['put']
                    logging.info(f"Updated record: {comparison_key} | call: {self.loss_records[comparison_key]['call']}, put: {self.loss_records[comparison_key]['put']}")
                else:
                    # Store a new record
                    self.loss_records[comparison_key] = {'call': record['call'], 'put': record['put']}
                    logging.info(f"Added new record: {comparison_key}")
        """Saves loss_records dictionary to a CSV file."""
        try:
            df = pandas.DataFrame([
                {**dict(comparison_key), **counts}
                for comparison_key, counts in self.loss_records.items()
            ])
            df.to_csv("loss_records.csv", index=False)  # Save as CSV
            logging.info(f"Successfully saved {len(self.loss_records)} records to loss_records.csv")
        except Exception as e:
            logging.error(f"Error saving loss records: {e}")
        finally: del df

    def check_loss_record_match(self, merged_dict):
        """
        Check if any key in merged_dict exists in loss_records.
        
        Args:
            merged_dict (dict): The new data dictionary.
            self.loss_records (dict): The existing loss records dictionary.
        
        Returns:
            bool: True if at least one match is found, otherwise False.
        """
        if not self.loss_records:  # Check if loss_records is empty
            logging.info("Loss records are empty. No match possible.")
            return False
        
        for key, record in merged_dict.items():
            # Convert record to a comparable format (tuple)
            comparison_key = tuple((k, str(v)) for k, v in record.items() if k not in {'call', 'put'})
            
            # Check if the comparison_key exists in loss_records
            if comparison_key in self.loss_records:
                logging.info(f"Match found for key: {key}")
                return True  # Stop immediately if a match is found
        
        logging.info("No match found.")
        return False  # Return False if no match is found after checking all entries
