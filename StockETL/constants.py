"""
Constants module for StockETL.

This module contains all constant values used throughout the application.
"""

import os
from enum import Enum
from typing import Final
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class TradeSide(str, Enum):
    """Trade side enumeration."""

    BUY = "BUY"
    SELL = "SELL"
    EXPIRED = "EXPIRED"


class TradePosition(str, Enum):
    """Trade position enumeration."""

    LONG = "LONG"
    SHORT = "SHORT"


class Exchange(str, Enum):
    """Stock exchange enumeration."""

    NSE = "NSE"
    BSE = "BSE"


class Segment(str, Enum):
    """Market segment enumeration."""

    EQ = "EQ"  # Equity
    FO = "FO"  # Futures & Options
    CD = "CD"  # Currency Derivatives


# File patterns
FILE_PATTERN_CSV: Final[str] = "*.csv"
FILE_PATTERN_EXCEL: Final[str] = "*.xlsx"
FILE_PATTERN_JSON: Final[str] = "*.json"

# Date formats
DATE_FORMAT_STANDARD: Final[str] = "%Y-%m-%d"
DATE_FORMAT_FULL: Final[str] = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_ISO: Final[str] = "%Y-%m-%dT%H:%M:%S"

# Numeric constants
DEFAULT_BROKERAGE_RATE: Final[float] = 0.03  # 0.03%
MAX_FILE_SIZE_MB: Final[int] = 100
ROUNDING_PRECISION: Final[int] = 2

# Regex patterns
REGEX_ESCAPE_STRING: Final[str] = r"""!"#$%&'()*+,-./:;<=>?@[\]^`{|}~"""

# Default values
DEFAULT_TIMESTAMP: Final[str] = "2000-01-01"
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_TIMEOUT: Final[int] = 30

# Path Configuration
# =================
# All paths are constructed relative to PROJECT_DIR environment variable.
# The directory structure follows a data lakehouse pattern: SOURCE -> BRONZE -> SILVER -> GOLD

# Base directory from environment
PROJECT_DIR: Final[str] = os.getenv("PROJECT_DIR", "")
ROOT_PATH: Final[Path] = Path(PROJECT_DIR).resolve() if PROJECT_DIR else Path.cwd()

# Top-level data directories
PATH_CONFIG: Final[Path] = ROOT_PATH / "DATA" / "CONFIG"
PATH_SOURCE: Final[Path] = ROOT_PATH / "DATA" / "SOURCE"  # Raw data ingestion
PATH_BRONZE: Final[Path] = ROOT_PATH / "DATA" / "BRONZE"  # Raw data with schema
PATH_SILVER: Final[Path] = ROOT_PATH / "DATA" / "SILVER"  # Cleaned & validated data
PATH_GOLD: Final[Path] = ROOT_PATH / "DATA" / "GOLD"  # Business-level aggregates
PATH_API: Final[Path] = ROOT_PATH / "DATA" / "API"

# Configuration subdirectories
CONFIG_CONSTANTS_PATH: Final[Path] = PATH_CONFIG / "CONSTANTS"
CONFIG_DATA_CONTRACTS_PATH: Final[Path] = PATH_CONFIG / "DATA_CONTRACTS"
CONFIG_DATA_CONTRACTS_SOURCE_PATH: Final[Path] = CONFIG_DATA_CONTRACTS_PATH / "SOURCE"
CONFIG_DATA_CONTRACTS_BRONZE_PATH: Final[Path] = CONFIG_DATA_CONTRACTS_PATH / "BRONZE"
CONFIG_DATA_CONTRACTS_SILVER_PATH: Final[Path] = CONFIG_DATA_CONTRACTS_PATH / "SILVER"
CONFIG_DATA_CONTRACTS_GOLD_PATH: Final[Path] = CONFIG_DATA_CONTRACTS_PATH / "GOLD"
CONFIG_STOCK_TICKERS_FILE_PATH: Final[Path] = (
    CONFIG_CONSTANTS_PATH / "stock_tickers.json"
)

# SOURCE layer: Raw data organized by domain
SOURCE_SYMBOL_PATH: Final[Path] = PATH_SOURCE / "Symbol"
SOURCE_DIVIDEND_PATH: Final[Path] = PATH_SOURCE / "Dividend"
SOURCE_TRADEHISTORY_PATH: Final[Path] = PATH_SOURCE / "TradeHistory"
SOURCE_HOLDING_FILE_PATH: Final[Path] = PATH_SOURCE / "Holding" / "Holding_data.csv"

# BRONZE layer: Raw data with applied schema
BRONZE_SYMBOL_FILE_PATH: Final[Path] = PATH_BRONZE / "Symbol" / "Symbol_data.csv"
BRONZE_STOCKDATA_PATH: Final[Path] = PATH_BRONZE / "StockData"
BRONZE_TRADEHISTORY_PATH: Final[Path] = PATH_BRONZE / "TradeHistory"

# SILVER layer: Cleaned and enriched data
SILVER_SYMBOL_FILE_PATH: Final[Path] = PATH_SILVER / "Symbol" / "Symbol_data.csv"
SILVER_STOCKEVENTS_FILE_PATH: Final[Path] = (
    PATH_SILVER / "StockEvents" / "StockEvents_data.csv"
)
SILVER_STOCKPRICE_FILE_PATH: Final[Path] = (
    PATH_SILVER / "StockPrice" / "StockPrice_data.csv"
)
SILVER_TRADEHISTORY_FILE_PATH: Final[Path] = (
    PATH_SILVER / "TradeHistory" / "TradeHistory_data.csv"
)

# GOLD layer: Business-ready analytics data
GOLD_DIVIDEND_FILE_PATH: Final[Path] = PATH_GOLD / "Dividend" / "Dividend_data.csv"
GOLD_PROFITLOSS_FILE_PATH: Final[Path] = (
    PATH_GOLD / "ProfitLoss" / "ProfitLoss_data.csv"
)
GOLD_HOLDING_PATH: Final[Path] = PATH_GOLD / "Holding"
GOLD_HOLDING_FILE_PATH: Final[Path] = GOLD_HOLDING_PATH / "Holding_data.csv"
GOLD_CURRENTHOLDING_FILE_PATH: Final[Path] = (
    GOLD_HOLDING_PATH / "CurrentHolding_data.csv"
)


# # Column name mappings
# REQUIRED_COLUMNS: Final[dict] = {
#     "symbol": ["symbol", "scrip_name", "stock_symbol"],
#     "date": ["date", "datetime", "trade_date"],
#     "price": ["price", "close_price", "ltp"],
#     "quantity": ["quantity", "qty", "volume"],
# }
def ensure_exists(full_path: Path):
    """
    Ensures that the directory for the given path exists, creating it if necessary.

    Parameters
    ----------
    full_path : Path
        The full path object to check and create if necessary.
    """
    # Ensure the directory for the path exists
    if full_path.suffix:  # If the path is a file (has a file extension)
        full_path.parent.mkdir(parents=True, exist_ok=True)
    else:  # If the path is a directory
        full_path.mkdir(parents=True, exist_ok=True)
    return full_path


for path in [
    PATH_CONFIG,
    PATH_SOURCE,
    PATH_BRONZE,
    PATH_SILVER,
    PATH_GOLD,
    PATH_API,
    CONFIG_CONSTANTS_PATH,
    CONFIG_DATA_CONTRACTS_PATH,
    CONFIG_DATA_CONTRACTS_SOURCE_PATH,
    CONFIG_DATA_CONTRACTS_BRONZE_PATH,
    CONFIG_DATA_CONTRACTS_SILVER_PATH,
    CONFIG_DATA_CONTRACTS_GOLD_PATH,
    SOURCE_SYMBOL_PATH,
    SOURCE_DIVIDEND_PATH,
    SOURCE_TRADEHISTORY_PATH,
    SOURCE_HOLDING_FILE_PATH,
    BRONZE_SYMBOL_FILE_PATH,
    BRONZE_STOCKDATA_PATH,
    BRONZE_TRADEHISTORY_PATH,
    SILVER_SYMBOL_FILE_PATH,
    SILVER_STOCKEVENTS_FILE_PATH,
    SILVER_STOCKPRICE_FILE_PATH,
    SILVER_TRADEHISTORY_FILE_PATH,
    GOLD_DIVIDEND_FILE_PATH,
    GOLD_PROFITLOSS_FILE_PATH,
    GOLD_HOLDING_PATH,
]:
    ensure_exists(path)
