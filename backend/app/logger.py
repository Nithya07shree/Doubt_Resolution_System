import logging
import sys
from datetime import datetime
from pathlib import Path

# Determine the backend root directory for log file placement
BACKEND_DIR = Path(__file__).resolve().parent / "logs"

# Ensure the backend root path exists
BACKEND_DIR.mkdir(parents=True, exist_ok=True)

# Generate a uniquely timestamped log file in the backend root directory
timestamp = datetime.now().strftime("%Y-%m-%d")
log_file_path = BACKEND_DIR / f"log-{timestamp}.log"

# Define standard log format
LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

# Initialize standard root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Stream handler for console logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# File handler for log-to-file persistence
try:
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    logging.info(f"Structured logging successfully configured. Log file created at: {log_file_path}")
except Exception as e:
    logging.error(f"Failed to initialize FileHandler for logging: {e}")

def get_logger(name: str) -> logging.Logger:
    """Helper function to fetch named loggers."""
    return logging.getLogger(name)
