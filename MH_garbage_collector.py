from MH_libraries import logging, threading, gc


class GCManager(threading.Thread):
    """A background thread that performs garbage collection every 60 seconds."""
    
    def __init__(self, interval=60):
        super().__init__()
        self.interval = interval  # Run GC every `interval` seconds
        self.setDaemon(True)  # Daemon mode so it exits when the main app stops
        self.killed = threading.Event()
    
    def run(self):
        while not self.killed.is_set():
            self.killed.wait(self.interval)  # Run GC every 60 seconds
            logging.info("Running garbage collection...")
            gc.collect()  # Trigger garbage collection
            logging.info("Garbage collection completed.")

    def kill(self):
        """Stops the garbage collection thread."""
        self.killed.set()
        gc.collect()
