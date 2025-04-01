from MH_libraries import threading, logging, gc
from MH_API import Money_Heist
from MH_savings import TradeData


class CheckWin(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.killed = threading.Event()
        self.interval = 5 * 60  # 5 minutes in seconds
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData()

    def run(self):
        """Main execution loop with 5-minute intervals"""
        while not self.killed.is_set():
            
        # Wait until the API connection is established or the killed flag is set
            while not self.trade_data.get_API_connected().is_set():
                if self.killed.wait(1):
                    self.kill()
                    return  # Exit immediately

            self.killed.wait(self.interval)  # Initial delay

            if self.killed.is_set():
                self.kill()
                return  # Exit immediately

            try:
                if self.trade_data.get_API_connected().is_set():
                    self.process_trades()
            except Exception as e:
                logging.error(f"CheckWin error: {e}", exc_info=True)
            finally:
                if self.killed.is_set():
                    self.kill()
                    return  # Exit immediately

    def process_trades(self):
        """Core trade processing logic"""
        logging.info("Starting checking win processing.")
        # Step 3: Copy and clear trade_ids
        copied_trades = self.trade_data.get_trade_ids()
        for id in copied_trades:
            self.trade_data.delete_trade_ids(id)
        
        if not copied_trades:
            logging.info("No check win to process. Exiting function.")
            return

        logging.info(f"Processing {len(copied_trades)} check win.")

        # Step 5-7: Check open options
        check_win = self.api.get_optioninfo(1)
        open_options = check_win.get('open_options', [])
        
        # Add missing open trades
        for option in open_options:
            if option['id'] not in copied_trades:
                copied_trades[option['id']] = {}

        logging.info(f"Current open options: {len(open_options)}")

        # Step 8: Wait for expiration if needed
        if open_options:
            max_exp = max(opt['exp_time'] for opt in open_options)
            logging.info(f"Waiting for open options to expire (approx {max_exp} seconds).")
            while self.trade_data.get_app_timer() < max_exp:
                self.killed.wait(max_exp - self.trade_data.get_app_timer() + 1)

        # Step 9-11: Check closed options
        check_win = self.api.get_optioninfo(len(copied_trades))
        closed_options = check_win.get('closed_options', [])

        logging.info(f"Closed options retrieved: {len(closed_options)}")

        # Step 12-13: Process results
        for option in closed_options:
            for opt_id in option['id']:
                if opt_id in copied_trades:
                    if option['win'] == 'win':
                        self.trade_data.update_trade_status(option['win'])
                        del copied_trades[opt_id]
                        logging.info(f"Trade {opt_id} won and removed.")
                    else:
                        logging.info(f"Trade {opt_id} lost. Logging details.")
                        self.trade_data.update_trade_status(option['win'])
                        self.trade_data.update_loss_records(copied_trades[opt_id])
        
        gc.collect()

    def kill(self):
        """Graceful shutdown"""
        self.killed.set()
        self.process_trades()
        gc.collect()
        logging.info("CheckWin thread stopped gracefully.")
