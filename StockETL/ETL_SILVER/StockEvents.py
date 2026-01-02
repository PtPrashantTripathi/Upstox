"""
BRONZE TO SILVER LAYER - Stock Events ETL.

This module processes stock event data (dividends, stock splits, capital gains)
from the BRONZE layer, transforms and aggregates it into a standardized format,
and stores the result in the SILVER layer.

Process:
    1. Load stock data CSV files from BRONZE/StockData
    2. Extract event columns (dividends, stock_splits, capital_gains)
    3. Transform data from wide to long format (melt)
    4. Filter out zero-value events
    5. Validate against data contract
    6. Save aggregated events to SILVER/StockEvents

Usage:
    python -m StockETL.ETL_SILVER.StockEvents
"""

import re
from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    BRONZE_STOCKDATA_PATH,
    SILVER_STOCKEVENTS_FILE_PATH,
    CONFIG_DATA_CONTRACTS_SILVER_PATH,
)
from StockETL.exceptions import FileProcessingError
from StockETL.common_utility import (
    align_with_datacontract,
    check_files_availability,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)

# Event types to extract from stock data
EVENT_COLUMNS = ["dividends", "stock_splits", "capital_gains"]

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
        >>> path = Path("AAPL_2024_01.csv")
        >>> extract_symbol_from_filename(path)
        'AAPL'
    """
    return DATE_PATTERN.sub("", file_path.name)


def process_stock_data_file(file_path: Path) -> pd.DataFrame | None:
    """
    Process a single stock data CSV file from BRONZE layer.

    Reads the CSV file, extracts the stock symbol, and prepares
    the data for event extraction.

    Args:
        file_path: Path to the BRONZE layer CSV file.

    Returns:
        DataFrame with stock data and symbol column, or None if processing fails.

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
            f"Cannot process stock data file {file_path.name}: {e}"
        ) from e


def transform_to_event_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform wide-format stock data to long-format event data.

    Converts columns (dividends, stock_splits, capital_gains) into rows
    with an event type and value. Filters out zero-value events.

    Args:
        df: DataFrame with stock data in wide format.

    Returns:
        DataFrame in long format with event types and values.

    Raises:
        ValueError: If required columns are missing.
    """
    required_columns = ["date", "symbol"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Identify available event columns
    available_events = [col for col in EVENT_COLUMNS if col in df.columns]

    if not available_events:
        logger.warning(f"No event columns found. Expected: {', '.join(EVENT_COLUMNS)}")
        return pd.DataFrame(columns=["date", "symbol", "event", "value"])

    logger.debug(
        f"Processing {len(available_events)} event type(s): {available_events}"
    )

    # Melt DataFrame from wide to long format
    df_events = df.melt(
        id_vars=["date", "symbol"],
        value_vars=available_events,
        var_name="event",
        value_name="value",
    )

    # Normalize event names to uppercase
    df_events["event"] = df_events["event"].str.upper()

    # Fill NaN values with 0 and round to 2 decimals
    df_events["value"] = df_events["value"].fillna(0).round(2)

    # Filter out zero or negative values
    initial_count = len(df_events)
    df_events = df_events[df_events["value"] > 0]
    filtered_count = initial_count - len(df_events)

    if filtered_count > 0:
        logger.debug(f"Filtered out {filtered_count} zero-value event(s)")

    return df_events


def run() -> None:
    """
    Execute the BRONZE to SILVER ETL pipeline for stock events.

    Orchestrates the complete workflow:
        1. Load all stock data files from BRONZE layer
        2. Extract event data (dividends, splits, capital gains)
        3. Transform from wide to long format
        4. Normalize and validate data
        5. Filter meaningful events (value > 0)
        6. Validate against data contract
        7. Save aggregated events to SILVER layer

    Raises:
        FileNotFoundError: If BRONZE directory doesn't exist.
        FileProcessingError: If critical processing errors occur.
        DataContractError: If data doesn't match schema.
    """
    logger.info("Starting BRONZE to SILVER stock events ETL")

    try:
        # Discover BRONZE layer files
        file_paths = check_files_availability(
            BRONZE_STOCKDATA_PATH, file_pattern="*.csv"
        )

        if not file_paths:
            logger.warning(f"No stock data files found in {BRONZE_STOCKDATA_PATH}")
            return

        logger.info(f"Found {len(file_paths)} stock data file(s) to process")

        # Process all files and collect DataFrames
        df_stock_events_list = []
        processed_files = 0
        failed_files = 0

        for idx, file_path in enumerate(file_paths, 1):
            try:
                df = process_stock_data_file(file_path)

                if df is not None:
                    df_stock_events_list.append(df)
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

        if not df_stock_events_list:
            logger.error("No data collected from BRONZE layer")
            raise FileProcessingError("Failed to process any stock data files")

        # Concatenate all DataFrames
        logger.info("Consolidating data from all files...")
        df = pd.concat(df_stock_events_list, ignore_index=True)
        logger.info(f"Consolidated {len(df):,} total record(s)")

        # Data harmonization
        df = replace_punctuation_from_columns(df)

        # Remove empty columns
        initial_cols = len(df.columns)
        df.dropna(how="all", axis=1, inplace=True)
        removed_cols = initial_cols - len(df.columns)
        if removed_cols > 0:
            logger.debug(f"Removed {removed_cols} empty column(s)")

        # Convert dates
        try:
            df["date"] = pd.to_datetime(df["date"]).dt.date
        except Exception as e:
            logger.error(f"Failed to convert dates: {e}")
            raise FileProcessingError(f"Date conversion failed: {e}") from e

        # Transform to event format
        logger.info("Transforming data to event format...")
        df_events = transform_to_event_format(df)

        if df_events.empty:
            logger.warning("No events found after transformation")
            return

        logger.info(
            f"Extracted {len(df_events):,} event(s) across "
            f"{df_events['symbol'].nunique()} stock(s)"
        )

        # Event statistics
        event_counts = df_events.groupby("event").size()
        for event_type, count in event_counts.items():
            logger.info(f"  - {event_type}: {count:,} event(s)")

        # Validate against data contract
        logger.info("Validating against data contract...")
        contract_path = CONFIG_DATA_CONTRACTS_SILVER_PATH / "StockEvents.json"
        df_events = align_with_datacontract(df_events, contract_path)

        # Ensure output directory exists
        SILVER_STOCKEVENTS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save to SILVER layer
        df_events.to_csv(SILVER_STOCKEVENTS_FILE_PATH, index=False)
        logger.info(
            f"✓ Successfully saved stock events to: " f"{SILVER_STOCKEVENTS_FILE_PATH}"
        )

        # Summary statistics
        logger.info(
            f"\nETL Summary:"
            f"\n  Total records: {len(df_events):,}"
            f"\n  Unique stocks: {df_events['symbol'].nunique()}"
            f"\n  Date range: {df_events['date'].min()} to {df_events['date'].max()}"
            f"\n  Event types: {', '.join(df_events['event'].unique())}"
        )

    except FileNotFoundError as e:
        logger.error(f"BRONZE layer path not found: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Critical error in stock events ETL pipeline: {e}",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    run()
