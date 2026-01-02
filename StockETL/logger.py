"""
Logging configuration module for StockETL.

This module provides a simple logging setup for console output.
"""

import os
import logging

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


def get_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with console output.

    Args:
        name: The name of the logger (typically __name__ of the calling module).
        level: The logging level (default: logging.INFO).

    Returns:
        A configured logger instance.
    """
    # Log formatting
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format=os.getenv(
            "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        datefmt=os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S"),
        force=True,
    )
    return logging.getLogger(name)
