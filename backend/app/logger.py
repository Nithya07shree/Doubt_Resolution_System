import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Determine the backend logs directory (used for local development)
BACKEND_DIR = Path(__file__).resolve().parent / "logs"

# Define standard log format
LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

# Initialize standard root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# File handler setup wrapped in a robust environment check and try-except block.
# This prevents crashes on read-only serverless filesystems like Vercel/AWS Lambda.
try:
    if "VERCEL" not in os.environ:
        BACKEND_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        log_file_path = BACKEND_DIR / f"log-{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        logging.info(f"Structured logging successfully configured. Log file created at: {log_file_path}")
    else:
        logging.info("Vercel serverless environment detected. File logger bypassed; streaming directly to Vercel console logs.")
except Exception as e:
    # Silent fallback to console-only logging if filesystem is read-only
    logging.warning(f"Bypassing file logger setup (non-writable filesystem): {e}")

def get_logger(name: str) -> logging.Logger:
    """Helper function to fetch named loggers."""
    return logging.getLogger(name)
