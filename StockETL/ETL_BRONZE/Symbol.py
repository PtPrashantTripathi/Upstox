"""
ETL Bronze Layer - Symbol Processing.

This module reads raw symbol/stock data from source files and performs
initial data harmonization to create the Bronze layer Symbol dataset.
"""

from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    FILE_PATTERN_CSV,
    SOURCE_SYMBOL_PATH,
    BRONZE_SYMBOL_FILE_PATH,
    CONFIG_DATA_CONTRACTS_BRONZE_PATH,
)
from StockETL.exceptions import FileProcessingError
from StockETL.common_utility import (
    align_with_datacontract,
    check_files_availability,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)


def read_file(file_path: Path) -> pd.DataFrame | None:
    """
    Read and process a single CSV file.

    Args:
        file_path: Path to the CSV file to process.

    Returns:
        Processed DataFrame, or None if processing fails.
    """
    logger.info(f"Processing file: {file_path.name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_path)

        if df.empty:
            logger.warning(f"File is empty: {file_path}")
            return None

        # Harmonize column names
        df = replace_punctuation_from_columns(df)

        # Drop rows where 'isin' is missing (required field)
        initial_rows = len(df)
        df = df.dropna(subset=["isin"])
        dropped_rows = initial_rows - len(df)

        if dropped_rows > 0:
            logger.debug(f"Dropped {dropped_rows} rows with missing ISIN")

        # Align with DataContract schema
        df = align_with_datacontract(
            df, CONFIG_DATA_CONTRACTS_BRONZE_PATH / "Symbol.json"
        )

        # Drop columns where all elements are NaN
        df = df.dropna(how="all", axis=1)

        logger.debug(f"Successfully processed {len(df)} rows from {file_path.name}")
        return df

    except pd.errors.EmptyDataError:
        logger.error(f"File is empty or corrupted: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
        return None


def run() -> None:
    """
    Execute the Symbol Bronze layer ETL process.

    This function:
    1. Identifies all CSV files in the source directory
    2. Processes each file individually
    3. Consolidates data into a single DataFrame
    4. Aligns with the DataContract schema
    5. Saves the result to the Bronze layer

    Raises:
        FileProcessingError: If no files are found or processing fails.
    """
    logger.info("Starting Symbol Bronze Layer ETL")

    try:
        # Find available source files
        file_paths = check_files_availability(
            SOURCE_SYMBOL_PATH,
            file_pattern=FILE_PATTERN_CSV,
        )

        logger.info(f"Found {len(file_paths)} CSV file(s) to process")

        # Process all files
        df_list = []
        failed_files = []

        for file_path in file_paths:
            df = read_file(file_path)
            if df is not None and not df.empty:
                df_list.append(df)
            else:
                failed_files.append(file_path.name)

        if not df_list:
            raise FileProcessingError(
                "No valid data extracted from any source files",
                details={"failed_files": failed_files},
            )

        if failed_files:
            logger.warning(
                f"Failed to process {len(failed_files)} file(s): {failed_files}"
            )

        # Consolidate all DataFrames
        logger.info(f"Consolidating data from {len(df_list)} file(s)")
        df_combined = pd.concat(df_list, ignore_index=True)

        # Final alignment with DataContract
        df_combined = align_with_datacontract(
            df_combined, CONFIG_DATA_CONTRACTS_BRONZE_PATH / "Symbol.json"
        )

        # Save to Bronze layer
        df_combined.to_csv(BRONZE_SYMBOL_FILE_PATH, index=False)
        logger.info(f"Bronze layer CSV saved: {BRONZE_SYMBOL_FILE_PATH}")
        logger.info(
            f"Total rows: {len(df_combined)}, Total columns: {len(df_combined.columns)}"
        )

    except Exception as e:
        logger.error(f"Symbol Bronze Layer ETL failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()
