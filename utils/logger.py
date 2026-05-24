"""
Logging system for PyMinecraftLauncher
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory
LOGS_DIR = Path.home() / ".minecraft" / "launcher_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Log file path
LOG_FILE = LOGS_DIR / f"launcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logger
logger = logging.getLogger("PyMinecraftLauncher")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(f"PyMinecraftLauncher.{name}")
