from MH_libraries import IQ_Option, logging, gc, time
from MH_savings import TradeData
from MH_config import HEADERS, INSTRUMENTS


class Money_Heist:
    """Class to handle IQ Option API interactions.
    
    This class provides methods to connect to the IQ Option API, retrieve account information,
    fetch candlestick data, and place trades. It uses a singleton pattern to ensure only one
    instance of the API is created.
    """
    """Singleton class to handle IQ Option API interactions."""
    _instance = None
    
    def __new__(cls, Email: str, Password: str):
        if cls._instance is None:
            cls._instance = super(Money_Heist, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, Email: str, Password: str):
        if self._initialized:
            return
        
        if not Email or not Password:
            raise ValueError("Email and Password must be provided")
        
        logging.info("Initializing IQ Option API connection.")
        self.money_heist = IQ_Option(Email, Password)
        self.trade_data = TradeData._instance or TradeData()  # Access the already initialized instance
        self.last_connection_time = None
        self._initialized = True
        
        self.connect()

    def connect(self):
        """Connect to the IQ Option API with session refresh."""
        if self.last_connection_time is None or time.time() - self.last_connection_time > 1800:
            logging.info("Session expired. Reconnecting...")
            logging.info(f"API_connected {self.trade_data.get_API_connected().is_set()}.")
            return self._attempt_connection()
        elif not self.trade_data.get_API_connected().is_set():
            return self._attempt_connection()

    def _attempt_connection(self) -> bool:
        """
        Connect to the IQ Option API.
        
        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            logging.info("Connecting to IQ Option API.")
            success, reason = self.money_heist.connect()
            self.money_heist.set_session(header=HEADERS, cookie={})
            if success:
                self.trade_data.API_connection(1)
                self.last_connection_time = time.time()
                logging.info("Successfully connected to IQ Option API.")
                return True
            else:
                self.trade_data.API_connection(0)
                logging.warning(f"Failed to connect - {reason}")
                return False
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
            return False
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to connect to IQ Option API: {e}")
            return False

    def check_connection(self) -> bool:
        """Connects to API. Thread-safe through TradeData locks."""
        """
        Check if the API connection is active.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            if self.money_heist.check_connect():
                self.trade_data.API_connection(1)
                logging.info("API connection is active.")
                return True
            else:
                self.trade_data.API_connection(0)
                logging.warning("API connection is not active.")
                return False
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to check API connection: {e}")
            return False

    def get_server_timestamp(self) -> float:
        """
        Retrieve Server Time Stamp.
        
        Returns:
            float: Server Time Stamp.
        """
        try:
            return self.money_heist.get_server_timestamp()
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch Server Time Stamp: {e}")
            return 0  # Return 0 on failure

    def get_profile_ansyc(self) -> dict:
        """
        Retrieve the profile information asynchronously.
        
        Returns:
            dict: A dictionary containing the profile information.
        """
        try:
            logging.info("Fetching profile information asynchronously.")
            profile = self.money_heist.get_profile_ansyc()
            gc.collect()  # Force garbage collection
            return profile
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch profile information: {e}")
            return {}  # Return an empty dictionary on failure

    def get_balance_mode(self) -> str:
        """
        Retrieve the balance mode.
        
        Returns:
            str: The balance mode.
        """
        try:
            logging.info("Fetching balance mode.")
            balance_mode = self.money_heist.get_balance_mode()
            gc.collect()  # Force garbage collection
            return balance_mode
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch balance mode: {e}")
            return ""  # Return an empty string on failure

    def get_balance_id(self) -> int:
        """
        Retrieve the balance ID.
        
        Returns:
            int: The balance ID.
        """
        try:
            logging.info("Fetching balance ID.")
            balance_id = self.money_heist.get_balance_id()
            gc.collect()  # Force garbage collection
            return balance_id
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch balance ID: {e}")
            return int()  # Return an empty string on failure

    def get_currency(self):
        """
        Retrieve the account currency.
        
        Returns:
            str: The account currency.
        """
        try:
            currency = self.money_heist.get_currency()
            logging.info(f"Fetching account currency is {currency}.")
            gc.collect()  # Force garbage collection
            return currency
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch currency: {e}")
            return ""  # Return an empty string on failure

    def get_all_ACTIVES_OPCODE(self):
        """
        Retrieve All ACTIVES OPCODE.
        
        Returns:
            dict: A dictionary containing All ACTIVES OPCODE.
        """
        try:
            logging.info("Fetching all actives opcode.")
            self.money_heist.update_ACTIVES_OPCODE()
            OP_Code = self.money_heist.get_all_ACTIVES_OPCODE()
            logging.info("OP_Code updated successfully.")
            gc.collect()  # Force garbage collection
            return OP_Code
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch all actives opcode: {e}")
            return {}  # Return an empty dictionary on failure

    def get_all_init_v2(self):
        """
        Retrieve All ACTIVES schedule.
        
        Returns:
            dict: A dictionary containing All ACTIVES schedule.
        """
        try:
            logging.info("Fetching actives schedule.")
            all_init = self.money_heist.get_all_init_v2()[INSTRUMENTS]['actives']
            gc.collect()  # Force garbage collection
            return all_init
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch actives schedule : {e}")
            return {}  # Return an empty dictionary on failure

    def get_all_open_time(self):
        """
        Retrieve the all actives names.
        
        Returns:
            dict: A dictionary containing the all actives names.
        """
        try:
            logging.info("Fetching all actives names.")
            actives = self.money_heist.get_all_open_time()[INSTRUMENTS]
            gc.collect()  # Force garbage collection
            return actives
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch actives names: {e}")
            return {}  # Return an empty dictionary on failure

    def get_candles(self, asset, interval, count, timestamp):
        """
        Retrieve candlestick data for a specific asset.
        
        Args:
            asset (str): The asset symbol (e.g., 'EURUSD').
            interval (int): The interval between candles in seconds.
            count (int): The number of candles to retrieve.
        
        Returns:
            dict: A dictionary containing the Candles.
        """
        try:
            candles = self.money_heist.get_candles(asset, interval, count, timestamp)
            gc.collect()  # Force garbage collection
            return candles
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch {asset} candles: {e}")
            return []  # Return an empty list on failure

    def buy(self, amount, active, direction, duration):
        """
        Place a trade on the IQ Option platform.
        
        Args:
            active (str): The active symbol (e.g., 'EURUSD').
            amount (float): The amount to trade.
            direction (str): The trade direction ('call' or 'put').
            duration (int): The duration of the trade in minutes.
        
        Returns:
            boolean: success is True or False
            int: The trade ID if successful, None otherwise.
        """
        try:
            success, id = self.money_heist.buy(amount, active, direction, duration)
            logging.info(f"Placing {direction} trade on {active} for {duration} minutes with amount {amount}.")
            gc.collect()  # Force garbage collection
            return success, id
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to place {direction} trade on {active}: {e}")
            return False, None  # Return False, None on failure

    def get_balance(self) -> float:
        """
        Retrieve the account balance.
        
        Returns:
            float: The account balance.
        """
        try:
            balance = self.money_heist.get_balance()
            logging.info(f"Account balance: {balance}")
            gc.collect()  # Force garbage collection
            return balance
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Failed to fetch account balance: {e}")
            return 0.0  # Return 0.0 on failure

    def get_optioninfo(self, count):
        """
        Retrieve option info for a specific count.
        
        Args:
            count (int): The number of requistion to retrieve.
        
        Returns:
            dict: A dictionary containing the option info.
        """
        try:
            check_win = self.money_heist.get_optioninfo(count)['msg']['result']
            logging.info(f"Get Option Information requested successfully")
            gc.collect()  # Force garbage collection
            return check_win
        except ConnectionError as e:
            self.trade_data.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            self.trade_data.API_connection(0)
            logging.error(f"Get Option Information failed to request: {e}")
            return {}

    def close_connection(self):
        """
        Close the API connection.
        """
        self.trade_data.API_connection(0)
        self.money_heist.logout()
        logging.info("Closing IQ Option API connection.")
        gc.collect()  # Force garbage collection
        raise SystemExit("API connection closed.")