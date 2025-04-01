import time
import logging

# Import your modules
from MH_garbage_collector import GCManager
from MH_savings import TradeData
from MH_API import Money_Heist
from MH_timer_factory import ServerTimeSynchronizer
from MH_signner_factory import Check_Email
from MH_opcode_factory import OPCodeUpdater
from MH_profile_factory import Profile
from MH_actives_factory import Active_Assets
from MH_checkwin_factory import CheckWin
from MH_api_updater import update_iqoptionapi

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# update iq option api
update_iqoptionapi()

# Initialize the API
money_heist_api = Money_Heist("ahmedhasan01@msn.com", "@hmed1992i")

def main():
    """Main function to initialize and start all threads."""

    # Load previous loss records
    TradeData().load_loss_records()

    # Initialize and start GC Manager
    gc_manager = GCManager()
    gc_manager.start()

    # List to manage all threads
    threads = []

    # Start the network and API monitoring thread
    check_email = Check_Email()
    check_email.start()

    # Start the Server Time Synchronizer thread
    timer_synching = ServerTimeSynchronizer()
    timer_synching.start()

    # Start the OPCodeUpdater thread
    op_code_updater = OPCodeUpdater()
    op_code_updater.start()
    threads.append(op_code_updater)

    # Start the Profile thread
    profile_updater = Profile()
    profile_updater.start()
    threads.append(profile_updater)

    # Start the Active_Assets thread
    active_assets = Active_Assets()
    active_assets.start()
    threads.append(active_assets)

    # Start the CheckWin thread
    check_win = CheckWin()
    check_win.start()
    threads.append(check_win)

    logging.info("All system threads are running... Press Ctrl+C to stop.")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Application termination requested by user.")

        # Gracefully stop all threads
        for thread in threads:
            thread.kill()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()

        threads.clear()

        check_email.kill()
        check_email.join()

        timer_synching.kill()
        timer_synching.join()

        # Close API connection
        money_heist_api.close_connection()

        # Explicit garbage collection
        gc_manager.kill()
        gc_manager.join()

        logging.info("Application shut down successfully.")
        raise SystemExit("Your account has been stopped.")


if __name__ == "__main__":
    main()
