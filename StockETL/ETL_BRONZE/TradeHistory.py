"""
SOURCE TO BRONZE LAYER - Trade History ETL.

This module processes raw trade history Excel files from various sources,
performs data harmonization, validates against data contracts, and stores
the cleaned data in the BRONZE layer as CSV files.

Process:
    1. Read Excel files from SOURCE/TradeHistory
    2. Identify correct sheet and headers
    3. Normalize column names and fix duplicates
    4. Apply corporate name standardization
    5. Validate against data contract
    6. Save as CSV in BRONZE/TradeHistory

Usage:
    python -m StockETL.ETL_BRONZE.TradeHistory
"""

import json
from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    CONFIG_CONSTANTS_PATH,
    BRONZE_TRADEHISTORY_PATH,
    SOURCE_TRADEHISTORY_PATH,
    CONFIG_DATA_CONTRACTS_BRONZE_PATH,
)
from StockETL.exceptions import FileProcessingError
from StockETL.common_utility import (
    find_correct_headers,
    find_correct_sheetname,
    align_with_datacontract,
    check_files_availability,
    fix_duplicate_column_names,
    replace_punctuation_from_columns,
)

logger = get_logger(__name__)


def read_and_process_trade_file(file_path: Path) -> pd.DataFrame:
    """
    Read and process a trade history Excel file with data harmonization.

    Performs a complete ETL pipeline on a single trade history file:
    - Reads multi-sheet Excel file
    - Identifies correct sheet and headers
    - Normalizes schema (column names, duplicates)
    - Validates against data contract
    - Returns cleaned DataFrame

    Args:
        file_path: Path to the Excel file containing trade history.

    Returns:
        Processed DataFrame with standardized columns and cleaned data.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        FileProcessingError: If file cannot be read or processed.
        DataContractError: If data doesn't match the expected schema.

    Examples:
        >>> path = Path("DATA/SOURCE/TradeHistory/user1/trade_2024.xlsx")
        >>> df = read_and_process_trade_file(path)
        >>> print(df.columns)
    """
    if not file_path.exists():
        logger.error(f"Trade file not found: {file_path}")
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.info(f"Processing trade file: {file_path.name}")

    try:
        # Read Excel file with all sheets
        df = pd.read_excel(
            file_path,
            engine="openpyxl",
            sheet_name=None,
            header=None,
            skipfooter=1,
        )
        logger.debug(f"Read {len(df)} sheet(s) from Excel file")

    except Exception as e:
        logger.error(f"Failed to read Excel file {file_path}: {e}", exc_info=True)
        raise FileProcessingError(
            f"Cannot read Excel file {file_path.name}: {e}"
        ) from e

    try:
        # Data harmonization pipeline
        df = find_correct_sheetname(df, sheet_name_regex="trade")
        df = find_correct_headers(df, global_header_regex="date")
        df = replace_punctuation_from_columns(df)
        df = fix_duplicate_column_names(df)

        # Remove empty rows
        initial_rows = len(df)
        df.dropna(how="all", inplace=True)
        removed_rows = initial_rows - len(df)
        if removed_rows > 0:
            logger.debug(f"Removed {removed_rows} empty row(s)")

        # Validate against data contract
        contract_path = CONFIG_DATA_CONTRACTS_BRONZE_PATH / "TradeHistory.json"
        df = align_with_datacontract(df, contract_path)

        logger.info(
            f"Successfully processed {len(df)} trade record(s) from {file_path.name}"
        )
        return df

    except Exception as e:
        logger.error(
            f"Error during data harmonization for {file_path.name}: {e}",
            exc_info=True,
        )
        raise FileProcessingError(
            f"Failed to process trade data from {file_path.name}: {e}"
        ) from e


# Load corporate name standardization mapping
CORPORATE_NAME_MAPPING: dict[str, str] = {}

try:
    corporate_changes_file = CONFIG_CONSTANTS_PATH / "corporate_name_changes.json"
    with open(corporate_changes_file, encoding="utf-8") as f:
        raw_mapping = json.load(f)
        # Normalize keys to lowercase for case-insensitive matching
        CORPORATE_NAME_MAPPING = {
            str(k).lower().strip(): v for k, v in raw_mapping.items()
        }
    logger.info(f"Loaded {len(CORPORATE_NAME_MAPPING)} corporate name mapping(s)")
except FileNotFoundError:
    logger.warning(
        f"Corporate name changes file not found: {corporate_changes_file}. "
        "Using empty mapping."
    )
    CORPORATE_NAME_MAPPING = {}
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in corporate changes file: {e}")
    raise


def standardize_corporate_name(company_name: str) -> str:
    """
    Standardize company names using the corporate name mapping.

    Handles corporate name changes, mergers, and acquisitions by mapping
    old or variant names to their current standardized form. Comparison
    is case-insensitive.

    Args:
        company_name: The company name to standardize.

    Returns:
        Standardized company name if mapping exists, otherwise original name.

    Examples:
        >>> standardize_corporate_name("HDFC Bank Ltd")
        'HDFC Bank Limited'
        >>> standardize_corporate_name("Unknown Corp")
        'Unknown Corp'
    """
    if not company_name or not isinstance(company_name, str):
        logger.warning(f"Invalid company name provided: {company_name}")
        return str(company_name) if company_name else ""

    normalized_key = company_name.lower().strip()
    standardized = CORPORATE_NAME_MAPPING.get(normalized_key, company_name)

    if standardized != company_name:
        logger.debug(f"Mapped '{company_name}' -> '{standardized}'")

    return standardized


def run() -> None:
    """
    Execute the SOURCE to BRONZE ETL pipeline for trade history.

    Orchestrates the complete workflow:
        1. Discover trade history Excel files in SOURCE layer
        2. Process each file with data harmonization
        3. Apply corporate name standardization
        4. Add user metadata
        5. Save to BRONZE layer as CSV
        6. Report processing statistics

    Raises:
        FileNotFoundError: If SOURCE directory doesn't exist.
        FileProcessingError: If critical processing errors occur.

    Note:
        Continues processing remaining files even if individual files fail.
    """
    logger.info("Starting SOURCE to BRONZE trade history ETL")

    try:
        # Discover source files
        file_paths = check_files_availability(
            SOURCE_TRADEHISTORY_PATH, file_pattern="trade_*.xlsx"
        )

        if not file_paths:
            logger.warning(
                f"No trade history files found in {SOURCE_TRADEHISTORY_PATH}"
            )
            return

        logger.info(f"Found {len(file_paths)} trade history file(s) to process")

        # Track processing statistics
        processed_count = 0
        failed_count = 0
        total_records = 0

        # Process each file
        for idx, file_path in enumerate(file_paths, 1):
            try:
                logger.info(
                    f"Processing file {idx}/{len(file_paths)}: {file_path.name}"
                )

                # Read and process the trade file
                df = read_and_process_trade_file(file_path)

                # Add metadata
                df["username"] = file_path.parent.name

                # Standardize corporate names
                if "company" in df.columns:
                    df["company"] = df["company"].apply(standardize_corporate_name)
                else:
                    logger.warning(f"'company' column not found in {file_path.name}")

                # Prepare output path
                output_filename = file_path.name.replace(".xlsx", ".csv")
                output_filepath = (
                    BRONZE_TRADEHISTORY_PATH / file_path.parent.name / output_filename
                )

                # Ensure output directory exists
                output_filepath.parent.mkdir(parents=True, exist_ok=True)

                # Save to CSV
                # df = df[df["scrip_code"].isin(["544569", "500570"])]
                df.to_csv(output_filepath, index=False)

                processed_count += 1
                total_records += len(df)
                logger.info(
                    f"✓ Saved {len(df)} record(s) to {output_filepath.relative_to(BRONZE_TRADEHISTORY_PATH)}"
                )

            except FileProcessingError as e:
                failed_count += 1
                logger.error(
                    f"✗ Failed to process {file_path.name}: {e}",
                    exc_info=True,
                )
                # Continue with next file
                continue

            except Exception as e:
                failed_count += 1
                logger.error(
                    f"✗ Unexpected error processing {file_path.name}: {e}",
                    exc_info=True,
                )
                continue

        # Report final statistics
        logger.info(
            f"\nETL completed: {processed_count} file(s) processed, "
            f"{total_records} record(s) total, {failed_count} failed"
        )

        if failed_count > 0:
            logger.warning(
                f"{failed_count} file(s) failed to process. Check logs for details."
            )

    except Exception as e:
        logger.error(
            f"Critical error in trade history ETL pipeline: {e}",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    run()
