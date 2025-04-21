# logger.py
import logging

# Global DEBUG flag (could be imported from config.py)
DEBUG = False

# Create the logger instance
logger = logging.getLogger("llm_app")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# Configure handler (console output)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s", datefmt="%H:%M:%S")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Prevent duplicate log entries
logger.propagate = False
