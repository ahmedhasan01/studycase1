from MH_libraries import threading, logging, pandas, gc, datetime
from MH_API import Money_Heist
from MH_savings import TradeData


class Profile(threading.Thread):
    """Thread to fetch and update profile information daily."""

    def __init__(self):
        super().__init__(daemon=True)  # Proper initialization
        self.killed = threading.Event()
        self.Profile_Information = pandas.DataFrame(columns=["my_info"])
        self.profile_list = [
            'confirmation_required',
            'group_id',
            'user_id',
            'name',
            'city',
            'address',
            'gender',
            'email',
            'confirmed_phones',
            'need_phone_confirmation',
            'balance_id',
            'currency',
            'balance',
            'deposit_count'
        ]
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData._instance or TradeData()  # Access the already initialized instance

    def run(self):
        """Main loop to fetch and update profile information."""
        logging.info("Profile Factory started. Waiting for API connection...")

        while not self.killed.is_set():  # Check for thread termination
            # Wait until the API connection is established or the killed flag is set
            while not self.trade_data.get_API_connected().is_set():
                if self.killed.wait(1):
                    self.kill()
                    return  # Exit immediately

            if self.killed.is_set():
                self.kill()
                return

            # Fetch profile information
            try:
                self.fetch_profile_information()
            except Exception as e:
                logging.error(f"Failed to fetch profile: {e}. Retrying in 10 seconds...")
                if self.killed.wait(10):
                    self.kill()
                    return

            # Wait for 6 hours before the next update
            logging.info("Waiting for 6 hours before the next profile update...")
            if self.killed.wait(21600):  # 6 hours in seconds
                self.kill()
                return

    def fetch_profile_information(self):
        """Fetch and update profile information."""
        logging.info("Fetching profile information...")
        get_profile = self.api.get_profile_ansyc()

        # Update profile information
        for x in self.profile_list:
            self.Profile_Information.loc[x, 'my_info'] = get_profile[x]

        Mode = self.api.get_balance_mode()
        self.Profile_Information.loc[f"{Mode}_balance_mode", 'my_info'] = Mode
        self.Profile_Information.loc[f"{Mode}_balance_id", 'my_info'] = self.api.get_balance_id()
        self.Profile_Information.loc[f"{Mode}_balance", 'my_info'] = self.api.get_balance()
        for status, count in self.trade_data.get_trade_status().items():
            self.Profile_Information.loc[f"{status}", 'my_info'] = count

        # Save profile information to Excel
        filename = f"{datetime.datetime.today().strftime('%a-%d-%b-%y')}.xlsx"
        self.Profile_Information.to_excel(filename, sheet_name="My_Profile")
        logging.info(f"Profile information saved to {filename}")
        gc.collect()  # Manually trigger garbage collection

    def kill(self):
        """Kill the thread gracefully."""
        self.killed.set()
        self.fetch_profile_information()
        gc.collect()
        logging.info("Profile thread stopped gracefully.")
