"""
GOLD Layer Dividend Processing Pipeline.

This module processes dividend data from stock events and merges it with holding
information to calculate dividend amounts and organize by financial year.

Module: StockETL.ETL_GOLD.Dividend
"""

from datetime import datetime

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    GOLD_HOLDING_FILE_PATH,
    GOLD_DIVIDEND_FILE_PATH,
    SILVER_STOCKEVENTS_FILE_PATH,
    CONFIG_DATA_CONTRACTS_GOLD_PATH,
)
from StockETL.common_utility import align_with_datacontract

# Initialize logger
logger = get_logger(__name__)

# Constants
DIVIDEND_SCHEMA_PATH = CONFIG_DATA_CONTRACTS_GOLD_PATH / "Dividend.json"
DIVIDEND_EVENT_TYPE = "DIVIDENDS"
FINANCIAL_YEAR_START_MONTH = 4


def get_financial_year(date: pd.Timestamp) -> str:
    """
    Calculate the financial year for a given date.

    Financial year runs from April to March. Dates before April belong to
    the previous financial year.

    Args:
        date: The date for which to calculate the financial year.

    Returns:
        Financial year in format 'FYYYYY-YY' (e.g., 'FY2025-26').

    Raises:
        TypeError: If date is not a pandas Timestamp or datetime object.
    """
    try:
        if not isinstance(date, (pd.Timestamp, datetime)):
            logger.warning(f"Non-timestamp date provided: {type(date)}")
            date = pd.Timestamp(date)

        start_year = (
            date.year - 1 if date.month < FINANCIAL_YEAR_START_MONTH else date.year
        )
        end_year = start_year + 1

        return f"FY{start_year}-{str(end_year)[-2:]}"

    except Exception as e:
        logger.error(f"Error calculating financial year for {date}: {str(e)}")
        raise


def _load_holding_data() -> pd.DataFrame:
    """
    Load holding data from GOLD layer.

    Returns:
        DataFrame with holding data and datetime column.

    Raises:
        FileNotFoundError: If holding file doesn't exist.
        Exception: If data loading or conversion fails.
    """
    try:
        df_holding = pd.read_csv(GOLD_HOLDING_FILE_PATH)
        df_holding["date"] = pd.to_datetime(df_holding["date"])
        logger.info(
            f"Loaded holding data from GOLD layer: {GOLD_HOLDING_FILE_PATH} "
            f"({len(df_holding)} records)"
        )
        return df_holding

    except FileNotFoundError:
        logger.error(f"Holding file not found: {GOLD_HOLDING_FILE_PATH}")
        raise
    except Exception as e:
        logger.error(f"Error loading holding data: {str(e)}")
        raise


def _load_dividend_events() -> pd.DataFrame:
    """
    Load dividend events from SILVER layer.

    Returns:
        DataFrame with dividend events filtered for DIVIDENDS type.

    Raises:
        FileNotFoundError: If stock events file doesn't exist.
        ValueError: If no dividend events found after filtering.
        Exception: If data loading or conversion fails.
    """
    try:
        df_events = pd.read_csv(SILVER_STOCKEVENTS_FILE_PATH)
        df_events["date"] = pd.to_datetime(df_events["date"])
        logger.info(
            f"Loaded stock events from SILVER layer: {SILVER_STOCKEVENTS_FILE_PATH} "
            f"({len(df_events)} records)"
        )

        # Filter for dividend events
        df_dividends = df_events[df_events["event"].str.upper() == DIVIDEND_EVENT_TYPE]

        if df_dividends.empty:
            logger.warning("No dividend events found in stock events data")

        logger.info(f"Filtered dividend events: {len(df_dividends)} records")
        return df_dividends

    except FileNotFoundError:
        logger.error(f"Stock events file not found: {SILVER_STOCKEVENTS_FILE_PATH}")
        raise
    except Exception as e:
        logger.error(f"Error loading dividend events: {str(e)}")
        raise


def _calculate_dividends(
    df_holding: pd.DataFrame, df_dividends: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge holding and dividend data, calculate dividend amounts.

    Args:
        df_holding: Holding data from GOLD layer.
        df_dividends: Filtered dividend events from SILVER layer.

    Returns:
        DataFrame with merged data and calculated dividend amounts.

    Raises:
        Exception: If merge or calculation operations fail.
    """
    try:
        # Merge on date and symbol
        df_dividend = pd.merge(
            df_holding, df_dividends, on=["date", "symbol"], how="left"
        )

        # Calculate dividend amount
        df_dividend["dividend_amount"] = (
            df_dividend["value"].fillna(0) * df_dividend["holding_quantity"]
        )

        # Filter out zero dividend amounts
        initial_count = len(df_dividend)
        df_dividend = df_dividend[df_dividend["dividend_amount"] != 0]
        filtered_count = len(df_dividend)

        logger.info(
            f"Calculated dividends: {filtered_count} records after filtering "
            f"(removed {initial_count - filtered_count} zero-dividend records)"
        )

        return df_dividend

    except Exception as e:
        logger.error(f"Error calculating dividends: {str(e)}")
        raise


def _add_financial_year(df_dividend: pd.DataFrame) -> pd.DataFrame:
    """
    Add financial year column to dividend data.

    Args:
        df_dividend: Dividend data DataFrame.

    Returns:
        DataFrame with added financial_year column.

    Raises:
        Exception: If financial year calculation fails.
    """
    try:
        df_dividend["financial_year"] = pd.to_datetime(df_dividend["date"]).apply(
            get_financial_year
        )

        logger.debug(f"Added financial year column to {len(df_dividend)} records")
        return df_dividend

    except Exception as e:
        logger.error(f"Error adding financial year: {str(e)}")
        raise


def _save_dividend_data(df_dividend: pd.DataFrame) -> None:
    """
    Validate, align schema, and save dividend data to GOLD layer.

    Args:
        df_dividend: Processed dividend data.

    Raises:
        Exception: If alignment or file operations fail.
    """
    try:
        if df_dividend.empty:
            logger.warning("No dividend data to save")
            return

        # Align with data contract
        df_dividend = align_with_datacontract(df_dividend, DIVIDEND_SCHEMA_PATH)

        # Save to CSV
        df_dividend.to_csv(GOLD_DIVIDEND_FILE_PATH, index=False)
        logger.info(
            f"Dividend data saved to GOLD layer: {GOLD_DIVIDEND_FILE_PATH} "
            f"({len(df_dividend)} records)"
        )

    except Exception as e:
        logger.error(f"Error saving dividend data: {str(e)}")
        raise


def run() -> None:
    """
    Execute dividend processing pipeline.

    This function orchestrates the entire dividend processing pipeline:
    1. Loads holding data from GOLD layer
    2. Loads dividend events from SILVER layer
    3. Merges and calculates dividend amounts
    4. Adds financial year classification
    5. Aligns with schema and saves results

    Raises:
        Exception: Re-raises any exceptions from sub-processes with logging.
    """
    try:
        logger.info("Starting dividend processing pipeline")

        # Load data sources
        df_holding = _load_holding_data()
        df_dividends = _load_dividend_events()

        # Process dividends
        df_dividend = _calculate_dividends(df_holding, df_dividends)

        if not df_dividend.empty:
            df_dividend = _add_financial_year(df_dividend)
            _save_dividend_data(df_dividend)
        else:
            logger.warning("No dividend data to process")

        logger.info("Dividend processing pipeline completed successfully")

    except Exception as e:
        logger.error(f"Dividend processing pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run()
