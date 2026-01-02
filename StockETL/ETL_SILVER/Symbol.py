"""
BRONZE TO SILVER LAYER - Symbol/Security Master ETL.

This module processes security master data (symbols, ISINs, scrip codes) from
the BRONZE layer, standardizes instrument identifiers, and creates a unified
security reference table in the SILVER layer.

Process:
    1. Load symbol data from BRONZE layer
    2. Normalize column names and clean data
    3. Standardize scrip codes by instrument type:
       - Equity: Add "IN" prefix to scrip code
       - Mutual Fund: Use ISIN as scrip code and normalize symbol
    4. Remove invalid records (missing ISIN)
    5. Validate against data contract
    6. Save to SILVER/Symbol

Usage:
    python -m StockETL.ETL_SILVER.Symbol
"""

from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    BRONZE_SYMBOL_FILE_PATH,
    SILVER_SYMBOL_FILE_PATH,
    CONFIG_DATA_CONTRACTS_SILVER_PATH,
)
from StockETL.exceptions import DataContractError, FileProcessingError
from StockETL.common_utility import (
    align_with_datacontract,
    replace_punctuation_from_string,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)


def standardize_equity_scrip_code(row: pd.Series) -> str:
    """
    Standardize scrip code for equity instruments.

    Adds "IN" prefix to scrip codes for equity instruments to create
    a standardized international format.

    Args:
        row: DataFrame row containing scrip_code and instrument_type.

    Returns:
        Standardized scrip code with "IN" prefix.

    Examples:
        >>> standardize_equity_scrip_code(pd.Series({'scrip_code': '123456'}))
        'IN123456'
    """
    return f"IN{str(row['scrip_code']).strip()}"


def process_symbol_data(file_path: Path) -> pd.DataFrame:
    """
    Process symbol/security master data from BRONZE layer.

    Reads the CSV file, normalizes column names, standardizes instrument
    identifiers based on type, and cleans the data.

    Args:
        file_path: Path to the BRONZE layer symbol CSV file.

    Returns:
        Processed DataFrame with standardized security identifiers.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        FileProcessingError: If file cannot be read or processed.
    """
    if not file_path.exists():
        logger.error(f"Symbol file not found: {file_path}")
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.info(f"Processing symbol file: {file_path.name}")

    try:
        # Read CSV with scrip_code as string to preserve leading zeros
        df = pd.read_csv(file_path, dtype={"scrip_code": str})
        logger.debug(f"Loaded {len(df)} symbol record(s)")

        # Normalize column names
        df = replace_punctuation_from_columns(df)

        # Remove records without ISIN (invalid securities)
        initial_count = len(df)
        df = df.dropna(subset=["isin"])
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} record(s) with missing ISIN")

        # Process Equity instruments
        equity_mask = df["instrument_type"] == "Equity"
        equity_count = equity_mask.sum()
        if equity_count > 0:
            df.loc[equity_mask, "scrip_code"] = "IN" + df.loc[
                equity_mask, "scrip_code"
            ].astype(str)
            logger.debug(f"Standardized {equity_count} equity scrip code(s)")

        # Process Mutual Fund instruments
        mf_mask = df["instrument_type"] == "Mutual Fund"
        mf_count = mf_mask.sum()
        if mf_count > 0:
            # Use ISIN as scrip_code for mutual funds
            df.loc[mf_mask, "scrip_code"] = df.loc[mf_mask, "isin"]

            # Normalize symbol from scrip_name for mutual funds
            df.loc[mf_mask, "symbol"] = (
                df.loc[mf_mask, "scrip_name"]
                .apply(replace_punctuation_from_string)
                .str.upper()
            )
            logger.debug(f"Standardized {mf_count} mutual fund symbol(s)")

        # Normalize scrip_code format
        df["scrip_code"] = df["scrip_code"].astype(str).str.strip().str.upper()

        # Remove empty columns
        initial_cols = len(df.columns)
        df.dropna(how="all", axis=1, inplace=True)
        removed_cols = initial_cols - len(df.columns)
        if removed_cols > 0:
            logger.debug(f"Removed {removed_cols} empty column(s)")

        logger.info(
            f"Successfully processed {len(df)} symbol(s): "
            f"{equity_count} equity, {mf_count} mutual fund"
        )
        return df

    except pd.errors.EmptyDataError:
        logger.error(f"Empty or corrupted file: {file_path}")
        raise FileProcessingError(f"Symbol file is empty or corrupted: {file_path}")
    except KeyError as e:
        logger.error(f"Missing required column in symbol data: {e}")
        raise FileProcessingError(f"Symbol data missing required column: {e}") from e
    except Exception as e:
        logger.error(
            f"Failed to process symbol file: {e}",
            exc_info=True,
        )
        raise FileProcessingError(f"Cannot process symbol data: {e}") from e


def run() -> None:
    """
    Execute the BRONZE to SILVER ETL pipeline for symbol data.

    Orchestrates the complete workflow:
        1. Load symbol/security master data from BRONZE layer
        2. Standardize instrument identifiers by type
        3. Clean and normalize data
        4. Validate against data contract
        5. Save to SILVER layer

    Raises:
        FileNotFoundError: If BRONZE symbol file doesn't exist.
        FileProcessingError: If processing fails.
        DataContractError: If data doesn't match schema.
    """
    logger.info("Starting BRONZE to SILVER symbol ETL")

    try:
        # Process symbol data
        df = process_symbol_data(BRONZE_SYMBOL_FILE_PATH)

        # Validate against data contract
        logger.info("Validating against data contract...")
        contract_path = CONFIG_DATA_CONTRACTS_SILVER_PATH / "Symbol.json"
        df = align_with_datacontract(df, contract_path)

        # Ensure output directory exists
        SILVER_SYMBOL_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save to SILVER layer
        df.to_csv(SILVER_SYMBOL_FILE_PATH, index=False)
        logger.info(f"✓ Successfully saved symbol data to: {SILVER_SYMBOL_FILE_PATH}")

        # Summary statistics
        instrument_counts = df["instrument_type"].value_counts()
        logger.info(
            f"\nETL Summary:"
            f"\n  Total symbols: {len(df):,}"
            f"\n  Unique ISINs: {df['isin'].nunique()}"
            f"\n  Instrument types:"
        )
        for instrument_type, count in instrument_counts.items():
            logger.info(f"    - {instrument_type}: {count:,}")

    except FileNotFoundError as e:
        logger.error(f"Symbol file not found: {e}")
        raise
    except FileProcessingError as e:
        logger.error(f"Symbol processing failed: {e}")
        raise
    except DataContractError as e:
        logger.error(f"Data contract validation failed: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Critical error in symbol ETL pipeline: {e}",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    run()
