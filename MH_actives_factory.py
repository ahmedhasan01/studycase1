from MH_libraries import threading, logging, pandas, gc, psutil
from MH_API import Money_Heist
from MH_savings import TradeData
from MH_candles_factory import Candles_Assets


class Active_Assets(threading.Thread):
    def __init__(self, asset_timer=10*60):  # Configurable timer interval
        threading.Thread.__init__(self)
        self.killed = threading.Event()
        self.asset_timer = asset_timer
        self.api = Money_Heist()
        self.Asset_Information = pandas.DataFrame(columns=['active_name', 'active_id', 'status', 'schedule', 'candle_status'])
        self.candle_threads = {}  # Dictionary to store active candle threads
        self.sleeping_threads = []  # List to store reusable sleeping threads
        self.max_cpu_usage = 90  # Maximum allowed CPU usage (in percentage)
        self.max_memory_usage = 92  # Maximum allowed memory usage (in percentage)

    def run(self):
        """Main loop to update active assets and manage candle threads."""
        logging.info("Active Assets updater started. Waiting for API connection...")
        while not self.killed.is_set() and TradeData.API_connected.is_set() and TradeData.OP_Code_event.is_set():

            if self.killed.is_set():
                self.kill()
                break

            try:
                # Update immediately if Asset_Information is empty
                if self.Asset_Information.empty:
                    logging.info("Asset_Information is empty. Updating immediately.")
                    self.update_asset_information()
                else:
                    nearest_schedule = self.Asset_Information['schedule'].min()  # Calculate nearest_schedule
                    asset_timer_end = self.asset_timer + TradeData.app_timer  # Calculate asset_timer + server_timestamp
                    next_update_time = min(nearest_schedule, asset_timer_end)  # Determine the minimum between nearest_schedule and asset_timer_end
                    
                    if TradeData.app_timer >= next_update_time:  # Check if server_timestamp is greater than or equal to next_update_time
                        logging.info("Scheduled update time reached. Updating asset information.")
                        self.update_asset_information()
                    else:
                        # Calculate delay for threading.Timer
                        delay = next_update_time - TradeData.app_timer
                        logging.info(f"Scheduling next update in {delay} seconds.")
                        threading.Timer(delay, self.update_asset_information).start()

                # Manage candle threads based on asset status and schedule
                self.manage_candle_threads()

                # Move fully killed threads from killing_threads to sleeping_threads
                self.cleanup_live_threads()

                logging.info("Active assets and candle threads updated successfully.")
            except Exception as e:
                logging.error(f"Failed to update active assets or manage candle threads: {e}")
            finally:
                # Reset the asset_timer to its default value (optional)
                self.asset_timer = 10 * 60  # Reset to 10 minutes
                if self.killed.is_set():
                    self.kill()
                    break

        logging.info("Active assets thread stopped gracefully.")
        gc.collect()  # Clean up resources before exiting

    def update_asset_information(self):
        """Update the Asset_Information DataFrame with the latest asset data."""
        asset_status = self.api.get_all_open_time()
        updating_OP_Code = TradeData.OP_Code
        sched_init = self.api.get_all_init_v2()
        for active_name, status_data in asset_status.items():
            active_id = updating_OP_Code.get(active_name, None)  # Use OP_Code from Money_Heist_API.py
            if active_id is not None:
                status = status_data['open']
                schedule = self.get_nearest_schedule(active_id, sched_init)
                if schedule is not None:
                    # Check if the asset already exists in the DataFrame
                    if active_name in self.Asset_Information['active_name'].values:
                        # Update existing row
                        self.Asset_Information.loc[self.Asset_Information['active_name'] == active_name, ['status', 'schedule']] = [status, schedule]
                    else:
                        # Add new row
                        self.Asset_Information.loc[len(self.Asset_Information), ['active_name', 'active_id', 'status', 'schedule', 'candle_status']] = [active_name, active_id, status, schedule, False]
        gc.collect()

    def get_nearest_schedule(self, active_id, sched_init):
        """Get the nearest schedule timestamp for the given active_id."""
        try:
            schedules_list = sched_init[str(active_id)]['schedule']
            nearest_schedule = min([x for sublist in schedules_list for x in sublist if x >= TradeData.app_timer])
            gc.collect()
            return nearest_schedule  # Return a single value
        except Exception as e:
            logging.error(f"Failed to fetch schedule for active_id {active_id}: {e}")
            return None

    def manage_candle_threads(self):
        """Manage candle threads based on asset status and schedule."""
        if not self.Asset_Information.empty:
            
            for index, row in self.Asset_Information.iterrows():
                active_name = row['active_name']
                status = row['status']
                schedule = row['schedule'] - 60 # sec
                candle_status = row['candle_status']

                if not status and candle_status:
                    # If status is False and candle_status is True, kill the thread and move it to killing_threads
                    if active_name in self.candle_threads:
                        thread = self.candle_threads[active_name]
                        thread.kill()
                        self.sleeping_threads.append(thread)  # Move to killing_threads
                        del self.candle_threads[active_name]
                    self.Asset_Information.at[index, 'candle_status'] = False
                    logging.info(f"Candle thread for {active_name} killed and moved to killing threads.")

                elif status and TradeData.app_timer < (schedule - 5*60) and not candle_status:
                    # If status is True, schedule is not reached, and candle_status is False, start a thread
                    # Check system resources before starting thread
                    cpu_usage = psutil.cpu_percent(interval=0.1)
                    memory_usage = psutil.virtual_memory().percent
                    if cpu_usage < 95 and memory_usage < 95:
                        if self.sleeping_threads:
                            # Reuse a sleeping thread
                            thread = self.sleeping_threads.pop()
                            thread.active_name = active_name
                            thread.schedule = schedule
                            thread.start()
                        else:
                            # Start a new thread
                            thread = Candles_Assets(active_name, schedule)
                            thread.start()
                        self.candle_threads[active_name] = thread
                        self.Asset_Information.at[index, 'candle_status'] = True
                        logging.info(f"Candle thread for {active_name} started.")
                    else:
                        logging.warning(f"Resources still high - Skipping {active_name} | CPU: {cpu_usage}% | Mem: {memory_usage}%")

    def cleanup_live_threads(self):
        """Optimized thread cleanup with resource monitoring"""
        try:
            # Phase 1: Normal cleanup of dead threads
            cleaned_count = 0
            for active_name, thread in list(self.candle_threads.items()):
                if not thread.is_alive():
                    thread.join()  # Ensure complete cleanup
                    self.sleeping_threads.append(thread)
                    del self.candle_threads[active_name]
                    self.Asset_Information.loc[self.Asset_Information['active_name'] == active_name, 'candle_status'] = False
                    cleaned_count += 1
                    logging.debug(f"Recycled thread: {active_name}")

            # Phase 2: Resource monitoring
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            resource_status = f"CPU: {cpu_usage:.1f}% | Mem: {memory_usage:.1f}%"

            # Phase 3: Emergency reduction if needed
            if cpu_usage >= 95 or memory_usage >= 95:
                logging.warning(f"CRITICAL RESOURCES - {resource_status}")
                if self.candle_threads:
                    oldest_thread = next(iter(self.candle_threads.values()))
                    oldest_thread.kill()
                    oldest_thread.join()
                    self.Asset_Information.loc[self.Asset_Information['active_name'] == oldest_thread.active_name, 'candle_status'] = False
                    self.sleeping_threads.append(oldest_thread)
                    del self.candle_threads[oldest_thread.active_name]
                    logging.warning(f"Stopped oldest thread: {oldest_thread.active_name}")

                    # Immediate resource recheck
                    new_cpu = psutil.cpu_percent(interval=0.1)
                    new_mem = psutil.virtual_memory().percent
                    if new_cpu >= 95 or new_mem >= 95:
                        logging.warning("Persistent overload - Recursing cleanup")
                        self.cleanup_live_threads()  # Recursive call
                    else:
                        logging.info(f"Resources normalized - {resource_status}")
            else:
                if cleaned_count > 0:
                    logging.info(f"Normal cleanup | {resource_status} | Recycled: {cleaned_count}")
                
        except Exception as e:
            logging.error(f"Cleanup error: {str(e)}", exc_info=True)
    
    def kill(self):
        """Kill the thread gracefully."""
        self.killed.is_set()
        # Kill all active candle threads
        if self.candle_threads:
            for actives, thread in self.candle_threads.items():
                thread.kill()
                thread.join()  # Wait for the thread to fully stop
            logging.info("All candle_threads cleaned up.")
        # Kill all sleeping threads
        if self.sleeping_threads:
            for thread in self.sleeping_threads:
                thread.kill()
                thread.join()  # Wait for the thread to fully stop
            logging.info("All sleeping_threads cleaned up.")
        self.candle_threads.clear()
        self.sleeping_threads.clear()
        gc.collect()  # Clean up resources
        logging.info("Active assets thread and all candle threads stopped gracefully.")
