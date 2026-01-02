"""
SOURCE TO BRONZE LAYER - Stock Data ETL.

This module fetches daily stock data from Yahoo Finance and processes it
according to the data contract specifications. It handles data normalization,
validation, and storage in the BRONZE layer of the data lakehouse.

Process:
    1. Load stock ticker configuration and override mappings
    2. Retrieve holding history from the SOURCE layer
    3. Generate monthly date ranges for data fetching
    4. Download stock data from Yahoo Finance or cache
    5. Normalize column names and validate schema compliance
    6. Store processed data in BRONZE layer

"""

import json
from typing import Any
from pathlib import Path
from datetime import time, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
import yfinance as yf

from StockETL.logger import get_logger
from StockETL.constants import (
    BRONZE_STOCKDATA_PATH,
    SOURCE_HOLDING_FILE_PATH,
    CONFIG_STOCK_TICKERS_FILE_PATH,
    CONFIG_DATA_CONTRACTS_BRONZE_PATH,
)
from StockETL.datetimeutils import DateTimeUtil
from StockETL.common_utility import (
    align_with_datacontract,
    fix_duplicate_column_names,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)

# Calculate effective date for data processing
now_ist: datetime = datetime.now()
CUTOFF_TIME: time = time(15, 30)  # 15:30 IST
EFFECTIVE_DATE: datetime = (
    now_ist - timedelta(days=1) if now_ist.time() < CUTOFF_TIME else now_ist
)

logger.debug(f"Current IST timestamp: {now_ist}")
logger.debug(f"Effective date for processing: {EFFECTIVE_DATE}")

# Load stock ticker override configuration
OVERWRITE_TICKERS: dict[str, str] = {}
try:
    with open(CONFIG_STOCK_TICKERS_FILE_PATH, encoding="utf-8") as f:
        OVERWRITE_TICKERS = json.load(f)
    logger.debug(f"Loaded {len(OVERWRITE_TICKERS)} ticker overrides")
except FileNotFoundError:
    logger.warning(f"Ticker override file not found: {CONFIG_STOCK_TICKERS_FILE_PATH}")
    OVERWRITE_TICKERS = {}
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in ticker file: {e}")
    raise


def generate_date_list(
    start_date: datetime.date, end_date: datetime.date
) -> list[DateTimeUtil]:
    """
    Generate a list of DateTimeUtil objects for each month in the date range.

    Creates a list representing the first day of each month between start_date
    and end_date. Dates beyond the effective processing date are excluded.

    Args:
        start_date: Start date of the range.
        end_date: End date of the range.

    Returns:
        List of DateTimeUtil objects, one for each month in the range.

    Raises:
        ValueError: If start_date > end_date.

    Examples:
        >>> dates = generate_date_list(date(2024, 1, 15), date(2024, 3, 20))
        >>> len(dates)
        3
    """
    if start_date > end_date:
        raise ValueError(
            f"start_date ({start_date}) cannot be after end_date ({end_date})"
        )

    month_list: list[DateTimeUtil] = []
    current_date = min(start_date, EFFECTIVE_DATE)
    end_date = min(end_date, EFFECTIVE_DATE)

    while current_date <= end_date:
        month_list.append(DateTimeUtil(current_date.year, current_date.month, 1))

        # Move to first day of next month
        if current_date.month == 12:
            current_date = current_date.replace(
                year=current_date.year + 1, month=1, day=1
            )
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)

    logger.debug(f"Generated {len(month_list)} month(s) for date range")
    return month_list


def download_file_from_github(output_file: Path) -> bool:
    """
    Download a cached stock data file from GitHub repository.

    Attempts to download a previously cached CSV file from the GitHub repository
    to avoid redundant API calls. This is useful for historical data that doesn't
    change frequently.

    Args:
        output_file: Path object where the file should be saved.

    Returns:
        True if download was successful, False otherwise.

    Note:
        Requires internet connectivity and the file to exist in the GitHub repository.
    """
    try:
        github_data_url = (
            f"https://raw.githubusercontent.com/PtPrashantTripathi/"
            f"PortfolioTracker/main/DATA/BRONZE/StockData/"
            f"{str(output_file).split('StockData/')[1]}"
        )
        response = requests.get(github_data_url, timeout=10)

        if response.status_code == 200:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "wb") as file:
                file.write(response.content)
            logger.debug(f"Downloaded file from GitHub: {output_file.name}")
            return True
        else:
            logger.debug(f"GitHub file not found (status {response.status_code})")
            return False

    except requests.RequestException as e:
        logger.debug(f"Failed to download from GitHub: {e}")
        return False
    except OSError as e:
        logger.error(f"Failed to write file {output_file}: {e}")
        return False


# Function to download data
def process_stock_data(row: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Process stock data for a single ticker and save to BRONZE layer.

    Downloads historical OHLCV data for a stock from Yahoo Finance,
    normalizes the schema, and saves monthly CSV files. Attempts to reuse
    cached data when available.

    Args:
        row: Dictionary containing:
            - symbol: Stock ticker symbol
            - isin: ISIN code (used as fallback for ticker lookup)
            - min_date: Minimum date for data range
            - max_date: Maximum date for data range

    Returns:
        List of status dictionaries for each processed month, containing:
            - symbol: Stock ticker symbol
            - start_date: Period start date
            - end_date: Period end date
            - status: One of "exists", "downloaded", "failed"
            - info: Source ("github", "yfinance") or error message
            - file: Relative file path (on success)

    Note:
        Files are automatically created under DATA/BRONZE/StockData/{symbol}/.
    """
    all_status: list[dict[str, Any]] = []

    try:
        # Get stock ticker with override support
        ticker_symbol = OVERWRITE_TICKERS.get(row["symbol"], row["isin"])
        stock_ticker = yf.Ticker(ticker_symbol)
        stockdata_bronze_layer_path = BRONZE_STOCKDATA_PATH / row["symbol"]

        # Generate date range for monthly data chunks
        date_list = generate_date_list(
            row["min_date"].to_pydatetime(), row["max_date"].to_pydatetime()
        )

        for date in date_list:
            status: str | None = None
            info: str | None = None
            output_file = stockdata_bronze_layer_path / (
                f"{row['symbol']}_{date.year:04d}_{date.month:02d}.csv"
            )

            try:
                # Check if file already exists and is recent
                if output_file.exists() and date.month_difference(EFFECTIVE_DATE) >= 1:
                    status = "exists"
                    logger.debug(f"Using cached file: {output_file.name}")

                # Try downloading from GitHub cache
                elif download_file_from_github(output_file):
                    status = "downloaded"
                    info = "github"

                # Fetch from Yahoo Finance API
                else:
                    df = stock_ticker.history(
                        start=date.start_date,
                        end=min(date.end_date, EFFECTIVE_DATE),
                        interval="1d",
                        actions=True,
                        rounding=True,
                    )

                    if df.empty:
                        raise ValueError(
                            f"No data returned for {row['symbol']} "
                            f"({date.start_date} to {date.end_date})"
                        )

                    # Data normalization pipeline
                    df = df.reset_index()
                    df = replace_punctuation_from_columns(df)
                    df = fix_duplicate_column_names(df)
                    df = df.dropna(how="all")

                    # Validate against data contract
                    df = align_with_datacontract(
                        df, CONFIG_DATA_CONTRACTS_BRONZE_PATH / "StockData.json"
                    )

                    # Ensure output directory exists
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(output_file, index=False)

                    status = "downloaded"
                    info = "yfinance"
                    logger.info(f"Saved {len(df)} records to {output_file.name}")

            except Exception as e:
                status = "failed"
                info = f"{type(e).__name__}: {str(e)}"
                logger.error(
                    f"Failed to process {row['symbol']} for {date.year}-"
                    f"{date.month:02d}: {info}"
                )

            # Record processing result
            all_status.append(
                {
                    "symbol": row["symbol"],
                    "start_date": date.start_date,
                    "end_date": date.end_date,
                    "status": status,
                    "info": info,
                    "file": str(output_file),
                }
            )

    except Exception as e:
        logger.error(
            f"Critical error processing stock {row.get('symbol', 'unknown')}: {e}",
            exc_info=True,
        )
        all_status.append(
            {
                "symbol": row.get("symbol", "unknown"),
                "start_date": row.get("min_date", "N/A"),
                "end_date": row.get("max_date", "N/A"),
                "status": "failed",
                "error": f"{type(e).__name__}: {str(e)}",
            }
        )

    return all_status


def run() -> None:
    """
    Execute the SOURCE to BRONZE ETL pipeline for stock data.

    Orchestrates the complete workflow:
        1. Load holding history from SOURCE layer
        2. Aggregate date ranges by stock
        3. Process stock data in parallel
        4. Report on failures

    Raises:
        FileNotFoundError: If SOURCE data files are not found.
        Exception: Any critical error during processing (logged and reported).
    """
    try:
        logger.info("Starting SOURCE to BRONZE stock data ETL")

        # Load holding history from source files
        df_holding_history = pd.read_csv(SOURCE_HOLDING_FILE_PATH)

        if df_holding_history.empty:
            logger.warning("No holding data found in SOURCE layer")
            return

        # Convert to datetime
        df_holding_history["min_date"] = pd.to_datetime(df_holding_history["min_date"])
        df_holding_history["max_date"] = pd.to_datetime(df_holding_history["max_date"])

        # Aggregate date ranges by stock
        df_holding_history = df_holding_history.groupby(
            ["segment", "exchange", "symbol"], as_index=False
        ).agg(
            min_date=("min_date", "min"),
            max_date=("max_date", "max"),
            isin=("isin", "first"),
        )

        logger.info(
            f"Processing {len(df_holding_history)} unique stock(s) "
            f"across {df_holding_history['segment'].nunique()} segment(s)"
        )

        # Process in parallel for performance
        all_status: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(
                process_stock_data,
                df_holding_history.to_dict(orient="records"),
                chunksize=1,
            )

            for result in results:
                all_status.extend(result)

        # Report on processing results
        df_results = pd.DataFrame(all_status)
        successful = len(df_results[df_results["status"] == "downloaded"])
        failed = len(df_results[df_results["status"] == "failed"])
        cached = len(df_results[df_results["status"] == "exists"])

        logger.info(
            f"ETL completed: {successful} downloaded, "
            f"{cached} cached, {failed} failed"
        )

        # Show failures for investigation
        if failed > 0:
            failures = df_results[df_results["status"] == "failed"]
            logger.warning(f"Failed to process:\n{failures.to_string()}")

    except Exception as e:
        logger.error(f"Critical error in stock data ETL: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()
