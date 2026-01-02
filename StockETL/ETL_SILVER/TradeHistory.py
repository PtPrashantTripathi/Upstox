"""
BRONZE TO SILVER LAYER - Trade History ETL.

This module processes trade history data from the BRONZE layer, enriches it
with symbol information, aggregates batch trades, and creates a unified
trade history dataset in the SILVER layer.

Process:
    1. Load trade history CSV files from BRONZE/TradeHistory
    2. Parse and normalize trade data (dates, times, sides)
    3. Generate scrip names based on instrument type (equity, options)
    4. Calculate trade amounts
    5. Enrich with symbol data from SILVER layer
    6. Aggregate batch trades
    7. Validate against data contract
    8. Save to SILVER/TradeHistory

Usage:
    python -m StockETL.ETL_SILVER.TradeHistory
"""

from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    SILVER_SYMBOL_FILE_PATH,
    BRONZE_TRADEHISTORY_PATH,
    SILVER_TRADEHISTORY_FILE_PATH,
    CONFIG_DATA_CONTRACTS_SILVER_PATH,
)
from StockETL.exceptions import DataContractError, FileProcessingError
from StockETL.common_utility import (
    align_with_datacontract,
    check_files_availability,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)


def generate_scrip_name(row: pd.Series) -> str:
    """
    Generate standardized scrip name based on instrument type.

    Creates formatted scrip names for different instrument types:
    - Options (European Call/Put): COMPANY-CE/PE-STRIKE-EXPIRY
    - Other instruments: Use company name as-is

    Args:
        row: DataFrame row containing instrument data with columns:
            - instrument_type: Type of instrument
            - company: Company/stock name
            - strike_price: Strike price (for options)
            - expiry: Expiry date (for options)

    Returns:
        Standardized scrip name in uppercase, stripped of whitespace.

    Examples:
        >>> row = pd.Series({
        ...     'instrument_type': 'European Call',
        ...     'company': 'RELIANCE',
        ...     'strike_price': 2500,
        ...     'expiry': '31DEC2024'
        ... })
        >>> generate_scrip_name(row)
        'RELIANCE-CE-2500-31DEC2024'
    """
    instrument_type = row.get("instrument_type", "")
    company = str(row.get("company", ""))

    try:
        if instrument_type == "European Call":
            scrip_name = f"{company}-CE-" f"{row['strike_price']}-" f"{row['expiry']}"
        elif instrument_type == "European Put":
            scrip_name = f"{company}-PE-" f"{row['strike_price']}-" f"{row['expiry']}"
        else:
            scrip_name = company

        return scrip_name.strip().upper()

    except KeyError as e:
        logger.warning(f"Missing field for {instrument_type}: {e}. Using company name.")
        return company.strip().upper()


def process_trade_file(file_path: Path) -> pd.DataFrame | None:
    """
    Process a single trade history CSV file from BRONZE layer.

    Reads and transforms trade data including:
    - Normalizing column names
    - Parsing dates and times into datetime
    - Formatting expiry dates
    - Standardizing trade sides (BUY/SELL)
    - Adding scrip code prefix
    - Generating scrip names
    - Calculating trade amounts

    Args:
        file_path: Path to the BRONZE layer CSV file.

    Returns:
        Processed DataFrame with standardized trade records, or None if empty.

    Raises:
        FileProcessingError: If file cannot be read or processed.
    """
    logger.debug(f"Processing file: {file_path.name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_path)

        if df.empty:
            logger.warning(f"Empty file: {file_path.name}")
            return None

        # Normalize column names
        df = replace_punctuation_from_columns(df)

        # Convert trade number to integer
        df["trade_num"] = df["trade_num"].fillna(0).astype(int)

        # Parse and create datetime column
        try:
            df["datetime"] = pd.to_datetime(
                df["date"].str.replace("00:00:00", "").str.strip()
                + " "
                + df["trade_time"]
                .fillna("00:00:00")
                .apply(lambda x: x if len(x.split(":")) == 3 else f"{x}:00"),
                format="%Y-%m-%d %H:%M:%S",
            )
        except Exception as e:
            logger.error(f"Failed to parse datetime in {file_path.name}: {e}")
            raise FileProcessingError(
                f"Cannot parse datetime in {file_path.name}: {e}"
            ) from e

        # Process expiry dates
        if "expiry" in df.columns:
            try:
                df["expiry_date"] = pd.to_datetime(
                    df["expiry"], format="%d-%m-%Y", errors="coerce"
                )
                df["expiry"] = df["expiry_date"].dt.strftime("%d%b%Y")
                df["expiry_date"] = df["expiry_date"].dt.strftime("%Y-%m-%d").fillna("")
            except Exception as e:
                logger.warning(f"Failed to parse expiry dates in {file_path.name}: {e}")
                df["expiry_date"] = ""
        else:
            df["expiry_date"] = ""

        # Standardize trade side (BUY/SELL)
        df["side"] = df["side"].astype(str).str.strip().str.upper()

        # Add "IN" prefix to scrip codes
        if "scrip_code" in df.columns:
            df["scrip_code"] = (
                "IN" + df["scrip_code"].astype(str).str.strip().str.upper()
            )

        # Generate standardized scrip names
        df["scrip_name"] = df.apply(generate_scrip_name, axis=1)

        # Calculate trade amounts
        df["amount"] = df["price"] * df["quantity"]

        # Remove all-NA columns
        df = df.dropna(axis=1, how="all")

        logger.debug(f"Processed {len(df)} trade(s) from {file_path.name}")
        return df

    except pd.errors.EmptyDataError:
        logger.warning(f"Empty or corrupted file: {file_path.name}")
        return None
    except KeyError as e:
        logger.error(f"Missing required column in {file_path.name}: {e}")
        raise FileProcessingError(f"Trade file missing required column: {e}") from e
    except Exception as e:
        logger.error(
            f"Failed to process trade file {file_path.name}: {e}",
            exc_info=True,
        )
        raise FileProcessingError(
            f"Cannot process trade file {file_path.name}: {e}"
        ) from e


def enrich_with_symbol_data(df_trades: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich trade data with symbol information from SILVER layer.

    Joins trade data with symbol master data to add standardized
    stock symbols.

    Args:
        df_trades: DataFrame containing trade records.

    Returns:
        DataFrame enriched with symbol information.

    Raises:
        FileNotFoundError: If symbol file doesn't exist.
        FileProcessingError: If enrichment fails.
    """
    try:
        logger.info("Enriching trade data with symbol information...")

        if not SILVER_SYMBOL_FILE_PATH.exists():
            raise FileNotFoundError(
                f"Symbol file not found: {SILVER_SYMBOL_FILE_PATH}. "
                "Please run Symbol ETL first."
            )

        # Load symbol data
        df_symbol = pd.read_csv(SILVER_SYMBOL_FILE_PATH)
        logger.debug(f"Loaded {len(df_symbol)} symbol(s) from master data")

        # Merge with trade data
        len(df_trades)
        df_enriched = df_trades.merge(
            df_symbol[["scrip_code", "symbol"]],
            on="scrip_code",
            how="left",
        )

        # Check for unmapped trades
        unmapped = df_enriched["symbol"].isna().sum()
        if unmapped > 0:
            logger.warning(f"{unmapped} trade(s) could not be mapped to symbols")

        logger.debug(f"Enriched {len(df_enriched)} trade record(s)")
        return df_enriched

    except Exception as e:
        logger.error(f"Failed to enrich trade data: {e}", exc_info=True)
        raise FileProcessingError(f"Cannot enrich trade data with symbols: {e}") from e


def aggregate_batch_trades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate batch trades by grouping and summing amounts/quantities.

    Groups trades by key dimensions and sums financial values to eliminate
    batchs or split trades.

    Args:
        df: DataFrame containing trade records.

    Returns:
        Aggregated DataFrame with unique trades.
    """
    logger.info("Aggregating batch trades...")

    initial_count = len(df)

    # Group by key dimensions
    groupby_cols = [
        "username",
        "datetime",
        "exchange",
        "segment",
        "symbol",
        "scrip_name",
        "side",
        "price",
        "expiry_date",
    ]

    # Aggregate numerical columns
    df_aggregated = df.groupby(groupby_cols, as_index=False).agg(
        {"amount": "sum", "quantity": "sum"}
    )

    final_count = len(df_aggregated)
    aggregated = initial_count - final_count

    if aggregated > 0:
        logger.info(
            f"Aggregated {aggregated} same batch trade(s) "
            f"({initial_count} -> {final_count} records)"
        )
    else:
        logger.debug("No batch trades found")

    return df_aggregated


def run() -> None:
    """
    Execute the BRONZE to SILVER ETL pipeline for trade history.

    Orchestrates the complete workflow:
        1. Load trade history files from BRONZE layer
        2. Process and normalize trade data
        3. Consolidate all trades
        4. Enrich with symbol data from SILVER layer
        5. Aggregate batch trades
        6. Validate against data contract
        7. Save to SILVER layer

    Raises:
        FileNotFoundError: If BRONZE directory or symbol file doesn't exist.
        FileProcessingError: If processing fails.
        DataContractError: If data doesn't match schema.
    """
    logger.info("Starting BRONZE to SILVER trade history ETL")

    try:
        # Discover BRONZE layer files
        file_paths = check_files_availability(
            BRONZE_TRADEHISTORY_PATH,
            file_pattern="*.csv",
        )

        if not file_paths:
            logger.warning(
                f"No trade history files found in {BRONZE_TRADEHISTORY_PATH}"
            )
            return

        logger.info(f"Found {len(file_paths)} trade history file(s) to process")

        # Process all files and collect DataFrames
        dfs: list[pd.DataFrame] = []
        processed_files = 0
        failed_files = 0

        for idx, file_path in enumerate(file_paths, 1):
            try:
                df = process_trade_file(file_path)

                if df is not None and not df.empty:
                    dfs.append(df)
                    processed_files += 1
                else:
                    failed_files += 1

            except FileProcessingError as e:
                failed_files += 1
                logger.error(f"Skipping file {file_path.name}: {e}")
                continue

        logger.info(
            f"File processing complete: {processed_files} successful, "
            f"{failed_files} failed"
        )

        if not dfs:
            logger.error("No trade data collected from BRONZE layer")
            raise FileProcessingError("Failed to process any trade history files")

        # Concatenate all DataFrames
        logger.info("Consolidating trade data from all files...")
        df_trade_history = pd.concat(dfs, ignore_index=True)
        logger.info(f"Consolidated {len(df_trade_history):,} trade record(s)")

        # Enrich with symbol data
        df_trade_history = enrich_with_symbol_data(df_trade_history)

        # Aggregate batch trades
        df_trade_history = aggregate_batch_trades(df_trade_history)

        # Validate against data contract
        logger.info("Validating against data contract...")
        contract_path = CONFIG_DATA_CONTRACTS_SILVER_PATH / "TradeHistory.json"
        df_trade_history = align_with_datacontract(df_trade_history, contract_path)

        # Ensure output directory exists
        SILVER_TRADEHISTORY_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save to SILVER layer
        df_trade_history.to_csv(SILVER_TRADEHISTORY_FILE_PATH, index=False)
        logger.info(
            f"✓ Successfully saved trade history to: "
            f"{SILVER_TRADEHISTORY_FILE_PATH}"
        )

        logger.info(
            f"\nETL Summary:"
            f"\n  Total trades: {len(df_trade_history):,}"
            f"\n  Unique users: {df_trade_history['username'].nunique()}"
            f"\n  Unique symbols: {df_trade_history['symbol'].nunique()}"
            f"\n  Date range: {df_trade_history['datetime'].min()} to {df_trade_history['datetime'].max()}"
        )

    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        raise
    except DataContractError as e:
        logger.error(f"Data contract validation failed: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Critical error in trade history ETL pipeline: {e}",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    run()
