from MH_libraries import threading, logging, gc, psutil
from MH_API import Money_Heist
from MH_savings import TradeData
from MH_candles_factory import Candles_Assets, Maximum_assets


class Active_Assets(threading.Thread):
    def __init__(self, asset_timer=10*60):  # Configurable timer interval
        super().__init__(daemon=True)  # Proper initialization
        self.killed = threading.Event()
        self.asset_timer = asset_timer
        self.api = Money_Heist._instance  # Access the already initialized instance
        self.trade_data = TradeData._instance or TradeData()  # Access the already initialized instance
        self.Asset_Information = {}
        self.candle_threads = {}  # Dictionary to store active candle threads
        self.sleeping_threads = []  # List to store reusable sleeping threads
        self.max_cpu_usage = 90  # Maximum allowed CPU usage (in percentage)
        self.max_memory_usage = 95  # Maximum allowed memory usage (in percentage)

    def run(self):
        """Main loop to update active assets and manage candle threads."""
        while not self.killed.is_set():

            # Wait until the API connection is established or the killed flag is set
            while not (self.trade_data.get_API_connected().is_set() and self.trade_data.get_OP_Code_event().is_set()) or self.trade_data.get_app_timer() == 0:
                logging.info("Active Assets updater started. Waiting for API connection...")
                if self.killed.wait(1):
                    self.kill()
                    return  # Exit immediately

            if self.killed.is_set():
                self.kill()
                return

            try:
                # Update immediately if Asset_Information is empty
                if not self.Asset_Information:
                    logging.info("No assets found. Updating immediately.")
                    self._update_assets()
                else:
                    self._process_scheduled_update()

                logging.info("Active assets and candle threads updated successfully.")
            except Exception as e:
                logging.error(f"Failed to update active assets or manage candle threads: {e}")
            finally:
                # Reset the asset_timer to its default value (optional)
                self.asset_timer = 10 * 60  # Reset to 10 minutes
                if self.killed.is_set():
                    self.kill()
                    return

        # logging.info("Active assets thread stopped gracefully.")
        gc.collect()  # Clean up resources before exiting

    def _update_assets(self):
        """Update the Asset_Information DataFrame with the latest asset data."""
        asset_status = self.api.get_all_open_time()
        updating_OP_Code = self.trade_data.get_OP_Code()
        sched_init = self.api.get_all_init_v2()

        for active_name, status_data in asset_status.items():
            active_id = updating_OP_Code.get(active_name)
            if active_id is None:
                continue  # Skip this asset

            status = status_data.get('open', None)  # Default to False if key doesn't exist
            schedule = self._get_nearest_schedule(active_id, sched_init)

            if (status is None) or (schedule is None):
                # logging.warning(f"No schedule found for {active_name} (ID: {active_id}). Skipping asset.")
                continue  # Skip this asset

            # Update existing asset or add a new one
            if active_name in self.Asset_Information:
                self.Asset_Information[active_name]['status'] = status
                self.Asset_Information[active_name]['schedule'] = schedule
            else:
                self.Asset_Information[active_name] = {
                    'active_name': active_name,
                    'active_id': active_id,
                    'status': status,
                    'schedule': schedule,
                    'candle_status': False
                }

        # logging.info(f"Updated {len(self.Asset_Information)} assets")

        self._manage_candle_threads()  # Manage candle threads based on asset status and schedule

        self._cleanup_threads()  # Move fully killed threads from sleeping_threads to sleeping_threads

        gc.collect()

    def _get_nearest_schedule(self, active_id, sched_init):
        """Get the nearest schedule timestamp for the given active_id."""
        schedule = sched_init[str(active_id)]['schedule']

        valid_times = [t for item in schedule if isinstance(item, list) for t in item if t > Money_Heist._instance.get_server_timestamp()]

        return min(valid_times, default=None)  # Use default=None to handle empty lists

    def _process_scheduled_update(self):
        """Handle timed updates"""
        # logging.info("process_scheduled_update")
        nearest_schedule = min(info['schedule'] for info in self.Asset_Information.values())  # Calculate nearest_schedule
        asset_timer_end = self.asset_timer + self.trade_data.get_app_timer()  # Calculate asset_timer + server_timestamp
        next_update_time = min(nearest_schedule, asset_timer_end)  # Determine the minimum between nearest_schedule and asset_timer_end
        # logging.info(f"Nearest Scheduled is {nearest_schedule} but next sched {next_update_time}.")
        
        if self.trade_data.get_app_timer() >= next_update_time:  # Check if server_timestamp is greater than or equal to next_update_time
            logging.info("Scheduled update time reached. Updating asset information.")
            self._update_assets()
        else:
            # Calculate delay for threading.Timer
            delay = next_update_time - self.trade_data.get_app_timer()
            logging.info(f"Scheduling next update in {delay} seconds.")
            if self.killed.wait(delay):  # Waits up to 1 second but exits if killed
                self.kill()
                return  # Exit immediately
            self._update_assets()

    def _manage_candle_threads(self):
        """Manage candle threads based on asset status and schedule."""
        for active_name, info in self.Asset_Information.items():
            if self.killed.wait(2):
                self.kill()
                return
            status = info['status']
            schedule = info['schedule'] - 60
            candle_status = info['candle_status']

            if not status and candle_status:
                # If status is False and candle_status is True, kill the thread and move it to sleeping_threads
                if active_name in self.candle_threads:
                    thread = self.candle_threads[active_name]
                    thread.kill()
                    self.sleeping_threads.append(thread)  # Move to sleeping_threads
                    del self.candle_threads[active_name]
                self.Asset_Information[active_name]['candle_status'] = False
                logging.info(f"Candle thread for {active_name} killed and moved to killing threads.")

            elif status and self.trade_data.get_app_timer() < (schedule) and not candle_status:
                # If status is True, schedule is not reached, and candle_status is False, start a thread
                
                count = len(self.candle_threads)
                if count < Maximum_assets:
                    cpu_usage = psutil.cpu_percent(interval=0.1)  # Check system resources before starting thread
                    memory_usage = psutil.virtual_memory().percent
                    if cpu_usage < self.max_cpu_usage and memory_usage < self.max_memory_usage:
                        if self.sleeping_threads:
                            # Reuse a sleeping thread
                            thread = self.sleeping_threads.pop()
                            thread.active_name = active_name
                            thread.schedule = schedule
                            thread.start()
                        else:
                            # Start a new thread
                            thread = (active_name, schedule)
                            thread = Candles_Assets(active_name, schedule)
                            thread.start()
                        self.candle_threads[active_name] = thread
                        self.Asset_Information[active_name]['candle_status'] = True
                        logging.info(f"Candle thread for {active_name} ends {schedule}.")
                    else:
                        logging.warning(f"Resources still high - Skipping {active_name} | CPU: {cpu_usage}% | Mem: {memory_usage}%")

    def _cleanup_threads(self):
        """Optimized thread cleanup with resource monitoring"""
        try:
            # Phase 1: Normal cleanup of dead threads
            cleaned_count = 0
            for active_name, thread in list(self.candle_threads.items()):
                if not thread.is_alive():
                    thread.join()  # Ensure complete cleanup
                    self.sleeping_threads.append(thread)
                    del self.candle_threads[active_name]
                    self.Asset_Information[active_name]['candle_status'] = False
                    cleaned_count += 1

            # Phase 2: Resource monitoring
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            resource_status = f"CPU: {cpu_usage:.1f}% | Mem: {memory_usage:.1f}%"

            # Phase 3: Emergency reduction if needed
            if cpu_usage >= self.max_cpu_usage or memory_usage >= self.max_memory_usage:
                logging.warning(f"CRITICAL RESOURCES - {resource_status}")
                if self.candle_threads:
                    oldest_thread = next(iter(self.candle_threads.values()))
                    oldest_thread.kill()
                    oldest_thread.join()
                    self.Asset_Information[oldest_thread.active_name]['candle_status'] = False
                    self.sleeping_threads.append(oldest_thread)
                    del self.candle_threads[oldest_thread.active_name]
                    logging.warning(f"Stopped oldest thread: {oldest_thread.active_name}")

                    # Immediate resource recheck
                    new_cpu = psutil.cpu_percent(interval=0.1)
                    new_mem = psutil.virtual_memory().percent
                    if new_cpu >= 95 or new_mem >= 95:
                        logging.warning("Persistent overload - Recursing cleanup")
                        self._cleanup_threads()  # Recursive call
                    else:
                        logging.info(f"Resources normalized - {resource_status}")
                
        except Exception as e:
            logging.error(f"Cleanup error: {str(e)}", exc_info=True)
    
    def kill(self):
        """Kill the thread gracefully."""
        self.killed.set()
        # Kill all active candle threads
        if self.candle_threads:
            for actives, thread in self.candle_threads.items():
                thread.kill()
                thread.join()  # Wait for the thread to fully stop
        # Kill all sleeping threads
        if self.sleeping_threads:
            for thread in self.sleeping_threads:
                thread.kill()
                thread.join()  # Wait for the thread to fully stop
        self.candle_threads.clear()
        self.sleeping_threads.clear()
        self.Asset_Information.clear()
        gc.collect()  # Clean up resources
        logging.info("Active assets thread and all candle threads stopped gracefully.")
