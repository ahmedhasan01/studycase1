from MH_libraries import threading, logging, pandas, gc, datetime
from MH_API import Money_Heist
from MH_savings import TradeData


class Profile(threading.Thread):
    """Thread to fetch and update profile information daily."""

    def __init__(self):
        threading.Thread.__init__(self)
        self.killed = threading.Event()
        self.profile_timer = None  # Timer for daily profile updates
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
        self.api = Money_Heist()

    def run(self):
        """Main loop to fetch and update profile information."""
        logging.info("Profile Factory started. Waiting for API connection...")
        while not self.killed.is_set() and TradeData.get_API_connected().is_set():  # Check for thread termination

            if self.killed.is_set():
                self.kill()
                break

            # Fetch profile information
            try:
                self.fetch_profile_information()
            except Exception as e:
                logging.error(f"Failed to fetch profile: {e}. Retrying in 10 seconds...")
                self.killed.wait(10)
            finally:
                if self.killed.is_set():
                    self.kill()
                    break

            # Schedule the next profile update for the next day
            self.schedule_daily_update()

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
        for status, count in TradeData.get_trade_status().items():
            self.Profile_Information.loc[f"{status}", 'my_info'] = count

        # Save profile information to Excel
        filename = f"{datetime.datetime.today().strftime('%a-%d-%b-%y')}.xlsx"
        self.Profile_Information.to_excel(filename, sheet_name="My_Profile")
        logging.info(f"Profile information saved to {filename}")
        gc.collect()  # Manually trigger garbage collection

    def schedule_daily_update(self):
        """Schedule the next profile update for the next day."""
        now = datetime.datetime.now()
        next_day = now + datetime.timedelta(days=1)
        next_day_midnight = datetime.datetime.combine(next_day, datetime.time.min)  # Next day at midnight
        delay = (next_day_midnight - now).total_seconds()  # Delay in seconds

        # Cancel the existing timer (if any)
        if self.profile_timer:
            self.profile_timer.cancel()

        # Schedule the next update
        self.profile_timer = threading.Timer(delay, self.run)
        self.profile_timer.start()
        logging.info(f"Next profile update scheduled for {next_day_midnight}")
        gc.collect()  # Manually trigger garbage collection

    def kill(self):
        """Kill the thread gracefully."""
        self.killed.set()
        if self.profile_timer:
            self.profile_timer.cancel()
        self.fetch_profile_information()
        gc.collect()
        logging.info("Profile thread stopped gracefully.")
