"""
BRONZE TO SILVER LAYER - Stock Price ETL.

This module processes historical stock price data (OHLCV - Open, High, Low,
Close, Volume) from the BRONZE layer, aggregates and standardizes it, and
stores the result in the SILVER layer for analytical consumption.

Process:
    1. Load stock price CSV files from BRONZE/StockData
    2. Extract stock symbols from filenames
    3. Consolidate data from all files
    4. Normalize column names and clean data
    5. Convert dates to standard format
    6. Validate against data contract
    7. Save aggregated prices to SILVER/StockPrice

Usage:
    python -m StockETL.ETL_SILVER.StockPrice
"""

import re
from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    BRONZE_STOCKDATA_PATH,
    SILVER_STOCKPRICE_FILE_PATH,
    CONFIG_DATA_CONTRACTS_SILVER_PATH,
)
from StockETL.exceptions import DataContractError, FileProcessingError
from StockETL.common_utility import (
    align_with_datacontract,
    check_files_availability,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)

# Pattern to extract stock symbol from filename
DATE_PATTERN = re.compile(r"_\d{4}_\d{2}\.csv$")


def extract_symbol_from_filename(file_path: Path) -> str:
    """
    Extract stock symbol from a BRONZE layer filename.

    Removes the date pattern suffix (_YYYY_MM.csv) from the filename
    to extract the stock ticker symbol.

    Args:
        file_path: Path object of the stock data file.

    Returns:
        Stock ticker symbol extracted from filename.

    Examples:
        >>> path = Path("RELIANCE_2024_01.csv")
        >>> extract_symbol_from_filename(path)
        'RELIANCE'
    """
    return DATE_PATTERN.sub("", file_path.name)


def process_stock_price_file(file_path: Path) -> pd.DataFrame | None:
    """
    Process a single stock price CSV file from BRONZE layer.

    Reads the CSV file, extracts the stock symbol, and prepares
    the data for price aggregation.

    Args:
        file_path: Path to the BRONZE layer CSV file.

    Returns:
        DataFrame with stock price data and symbol column, or None if processing fails.

    Raises:
        FileProcessingError: If file cannot be read or is invalid.
    """
    try:
        logger.debug(f"Reading file: {file_path.name}")

        # Read CSV file
        df = pd.read_csv(file_path)

        if df.empty:
            logger.warning(f"Empty file: {file_path.name}")
            return None

        # Extract and add symbol column
        df["symbol"] = extract_symbol_from_filename(file_path)

        return df

    except pd.errors.EmptyDataError:
        logger.warning(f"Empty or corrupted file: {file_path.name}")
        return None
    except Exception as e:
        logger.error(
            f"Failed to process file {file_path.name}: {e}",
            exc_info=True,
        )
        raise FileProcessingError(
            f"Cannot process stock price file {file_path.name}: {e}"
        ) from e


def run() -> None:
    """
    Execute the BRONZE to SILVER ETL pipeline for stock prices.

    Orchestrates the complete workflow:
        1. Load all stock price files from BRONZE layer
        2. Extract and consolidate OHLCV data
        3. Normalize schema and clean data
        4. Convert dates to standard format
        5. Validate against data contract
        6. Save aggregated prices to SILVER layer

    Raises:
        FileNotFoundError: If BRONZE directory doesn't exist.
        FileProcessingError: If critical processing errors occur.
        DataContractError: If data doesn't match schema.
    """
    logger.info("Starting BRONZE to SILVER stock price ETL")

    try:
        # Discover BRONZE layer files
        file_paths = check_files_availability(
            BRONZE_STOCKDATA_PATH, file_pattern="*.csv"
        )

        if not file_paths:
            logger.warning(f"No stock price files found in {BRONZE_STOCKDATA_PATH}")
            return

        logger.info(f"Found {len(file_paths)} stock price file(s) to process")

        # Process all files and collect DataFrames
        df_stock_price_list = []
        processed_files = 0
        failed_files = 0

        for idx, file_path in enumerate(file_paths, 1):
            try:
                df = process_stock_price_file(file_path)

                if df is not None:
                    df_stock_price_list.append(df)
                    processed_files += 1
                else:
                    failed_files += 1

                # Log progress periodically
                if idx % 100 == 0:
                    logger.info(f"Progress: {idx}/{len(file_paths)} files processed")

            except FileProcessingError as e:
                failed_files += 1
                logger.error(f"Skipping file {file_path.name}: {e}")
                continue

        logger.info(
            f"File processing complete: {processed_files} successful, "
            f"{failed_files} failed"
        )

        if not df_stock_price_list:
            logger.error("No data collected from BRONZE layer")
            raise FileProcessingError("Failed to process any stock price files")

        # Concatenate all DataFrames
        logger.info("Consolidating data from all files...")
        df = pd.concat(df_stock_price_list, ignore_index=True)
        logger.info(f"Consolidated {len(df):,} total record(s)")

        # Data harmonization
        df = replace_punctuation_from_columns(df)

        # Remove empty columns
        initial_cols = len(df.columns)
        df.dropna(how="all", axis=1, inplace=True)
        removed_cols = initial_cols - len(df.columns)
        if removed_cols > 0:
            logger.debug(f"Removed {removed_cols} empty column(s)")

        # Convert dates to standard format
        try:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            logger.debug("Converted dates to standard format")
        except Exception as e:
            logger.error(f"Failed to convert dates: {e}")
            raise FileProcessingError(f"Date conversion failed: {e}") from e

        # Validate against data contract
        logger.info("Validating against data contract...")
        contract_path = CONFIG_DATA_CONTRACTS_SILVER_PATH / "StockPrice.json"
        df = align_with_datacontract(df, contract_path)

        # Ensure output directory exists
        SILVER_STOCKPRICE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save to SILVER layer
        df.to_csv(SILVER_STOCKPRICE_FILE_PATH, index=False)
        logger.info(
            f"✓ Successfully saved stock prices to: " f"{SILVER_STOCKPRICE_FILE_PATH}"
        )

        # Summary statistics
        logger.info(
            f"\nETL Summary:"
            f"\n  Total records: {len(df):,}"
            f"\n  Unique stocks: {df['symbol'].nunique()}"
            f"\n  Date range: {df['date'].min()} to {df['date'].max()}"
            f"\n  Columns: {', '.join(df.columns.tolist())}"
        )

    except FileNotFoundError as e:
        logger.error(f"BRONZE layer path not found: {e}")
        raise
    except DataContractError as e:
        logger.error(f"Data contract validation failed: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Critical error in stock price ETL pipeline: {e}",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    run()
