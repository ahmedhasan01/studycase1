from MH_libraries import IQ_Option, logging, gc
from MH_savings import TradeData
from MH_config import HEADERS, INSTRUMENTS


class Money_Heist:
    """Class to handle IQ Option API interactions.
    
    This class provides methods to connect to the IQ Option API, retrieve account information,
    fetch candlestick data, and place trades. It uses a singleton pattern to ensure only one
    instance of the API is created.
    """
    money_heist = None  # Singleton instance of IQOption API
    
    @classmethod
    def API_starter(cls, Email, Password):
        """
        Initialize the IQ Option API connection.
        
        Args:
            email (str): IQ Option account email.
            password (str): IQ Option account password.
        
        Returns:
            IQOption: An instance of the IQOption API.
        """
        logging.info("Initializing IQ Option API connection.")
        cls.money_heist = IQ_Option(Email, Password)
        cls.money_heist.set_session(header=HEADERS, cookie={})
        return cls.money_heist
    
    @classmethod
    def connect(cls):
        """
        Connect to the IQ Option API.
        
        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            logging.info("Connecting to IQ Option API.")
            success, reason = cls.money_heist.connect()  # Unpack the tuple
            if success:
                TradeData.API_connection(1)
                logging.info("Successfully connected to IQ Option API.")
                return True
            else:
                TradeData.API_connection(0)
                logging.error(f"Failed to connect to IQ Option API. Reason: {reason}")
                return False
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to connect to IQ Option API: {e}")
            return False
    
    @classmethod
    def check_connection(cls):
        """
        Check if the API connection is active.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            if cls.money_heist and cls.money_heist.check_connect():
                TradeData.API_connection(1)
                logging.info("API connection is active.")
                return True
            else:
                TradeData.API_connection(0)
                logging.warning("API connection is not active.")
                return False
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to check API connection: {e}")
            return False
    
    @classmethod
    def get_server_timestamp(cls):
        """
        Retrieve Server Time Stamp.
        
        Returns:
            float: Server Time Stamp.
        """
        try:
            time_stamp = cls.money_heist.get_server_timestamp()
            return time_stamp
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch Server Time Stamp: {e}")
            return int()  # Return an empty int on failure
    
    @classmethod
    def get_profile_ansyc(cls):
        """
        Retrieve the profile information asynchronously.
        
        Returns:
            dict: A dictionary containing the profile information.
        """
        try:
            logging.info("Fetching profile information asynchronously.")
            profile = cls.money_heist.get_profile_ansyc()
            gc.collect()  # Force garbage collection
            return profile
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch profile information: {e}")
            return {}  # Return an empty dictionary on failure
    
    @classmethod
    def get_balance_mode(cls):
        """
        Retrieve the balance mode.
        
        Returns:
            str: The balance mode.
        """
        try:
            logging.info("Fetching balance mode.")
            balance_mode = cls.money_heist.get_balance_mode()
            gc.collect()  # Force garbage collection
            return balance_mode
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch balance mode: {e}")
            return ""  # Return an empty string on failure
    
    @classmethod
    def get_balance_id(cls):
        """
        Retrieve the balance ID.
        
        Returns:
            int: The balance ID.
        """
        try:
            logging.info("Fetching balance ID.")
            balance_id = cls.money_heist.get_balance_id()
            gc.collect()  # Force garbage collection
            return balance_id
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch balance ID: {e}")
            return int()  # Return an empty string on failure
    
    @classmethod
    def get_currency(cls):
        """
        Retrieve the account currency.
        
        Returns:
            str: The account currency.
        """
        try:
            currency = cls.money_heist.get_currency()
            logging.info(f"Fetching account currency is {currency}.")
            gc.collect()  # Force garbage collection
            return currency
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch currency: {e}")
            return ""  # Return an empty string on failure
    
    @classmethod
    def get_all_ACTIVES_OPCODE(cls):
        """
        Retrieve All ACTIVES OPCODE.
        
        Returns:
            dict: A dictionary containing All ACTIVES OPCODE.
        """
        try:
            logging.info("Fetching all actives opcode.")
            cls.money_heist.update_ACTIVES_OPCODE()
            OP_Code = cls.money_heist.get_all_ACTIVES_OPCODE()
            logging.info("OP_Code updated successfully.")
            gc.collect()  # Force garbage collection
            return OP_Code
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch all actives opcode: {e}")
            return {}  # Return an empty dictionary on failure
        
    @classmethod
    def get_all_init_v2(cls):
        """
        Retrieve All ACTIVES schedule.
        
        Returns:
            dict: A dictionary containing All ACTIVES schedule.
        """
        try:
            logging.info("Fetching actives schedule.")
            all_init = cls.money_heist.get_all_init_v2()[INSTRUMENTS]['actives']
            gc.collect()  # Force garbage collection
            return all_init
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch actives schedule : {e}")
            return {}  # Return an empty dictionary on failure
    
    @classmethod
    def get_all_open_time(cls):
        """
        Retrieve the all actives names.
        
        Returns:
            dict: A dictionary containing the all actives names.
        """
        try:
            logging.info("Fetching all actives names.")
            actives = cls.money_heist.get_all_open_time()[INSTRUMENTS]
            gc.collect()  # Force garbage collection
            return actives
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch actives names: {e}")
            return {}  # Return an empty dictionary on failure
    
    @classmethod
    def get_candles(cls, asset, interval, count):
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
            logging.info(f"Retrieving {count} candles for {asset} with interval {interval} seconds.")
            candles = cls.money_heist.get_candles(asset, interval, count)
            gc.collect()  # Force garbage collection
            return candles
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch {asset} candles: {e}")
            return []  # Return an empty list on failure
    
    @classmethod
    def buy(cls, amount, active, direction, duration):
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
            success, id = cls.money_heist.buy(amount, active, direction, duration)
            logging.info(f"Placing {direction} trade on {active} for {duration} minutes with amount {amount}.")
            gc.collect()  # Force garbage collection
            return success, id
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to place {direction} trade on {active}: {e}")
            return False, None  # Return False, None on failure
    
    @classmethod
    def get_balance(cls):
        """
        Retrieve the account balance.
        
        Returns:
            float: The account balance.
        """
        try:
            balance = cls.money_heist.get_balance()
            logging.info(f"Account balance: {balance}")
            gc.collect()  # Force garbage collection
            return balance
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Failed to fetch account balance: {e}")
            return 0.0  # Return 0.0 on failure
    
    @classmethod
    def get_optioninfo(cls, count):
        """
        Retrieve option info for a specific count.
        
        Args:
            count (int): The number of requistion to retrieve.
        
        Returns:
            dict: A dictionary containing the option info.
        """
        try:
            check_win = cls.money_heist.get_optioninfo(count)['msg']['result']
            logging.info(f"Get Option Information requested successfully")
            gc.collect()  # Force garbage collection
            return check_win
        except ConnectionError as e:
            TradeData.API_connection(0)
            logging.error(f"Connection error: {e}")
        except Exception as e:
            TradeData.API_connection(0)
            logging.error(f"Get Option Information failed to request: {e}")
            return {}
    
    @classmethod
    def close_connection(cls):
        """
        Close the API connection.
        """
        TradeData.API_connection(0)
        cls.money_heist.logout()
        logging.info("Closing IQ Option API connection.")
        gc.collect()  # Force garbage collection
        raise SystemExit("API connection closed.")