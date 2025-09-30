"""
HEMouse Logger
Simple logging utility with file and console output
"""
import logging
import os
from datetime import datetime


class HEMouseLogger:
    """Logger for HEMouse application"""

    def __init__(self, log_dir="logs"):
        """
        Initialize logger

        Args:
            log_dir: Directory for log files
        """
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("HEMouse")
        self.logger.setLevel(logging.DEBUG)

        # File handler (DEBUG level)
        log_file = os.path.join(log_dir, f"hemouse_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler (INFO level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)


# Global logger instance
logger = HEMouseLogger()


# Test code
if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        1 / 0
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)