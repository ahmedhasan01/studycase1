""" 
MH_libraries.py - Centralized Library Imports and Logging Setup 
This file consolidates all imports and sets up logging to prevent redundancy.
"""

import pandas
import numpy
import talib
import logging
import threading
import datetime
import os
import requests
import subprocess
import time
import gc
import random
import psutil # type: ignore
from iqoptionapi.stable_api import IQ_Option


"""Configure logging for the application."""
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()         # Log to the console
    ]
)

logging.info("Logging initialized.")
logging.info("Libraries loaded successfully.")