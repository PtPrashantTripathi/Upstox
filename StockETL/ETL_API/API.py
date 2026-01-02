"""
ETL API Layer - JSON Output Generation.

This module transforms Gold layer data into JSON API endpoints
for consumption by frontend applications.
"""

import json
from typing import Any
from pathlib import Path

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    PATH_API,
    GOLD_HOLDING_FILE_PATH,
    GOLD_DIVIDEND_FILE_PATH,
    GOLD_PROFITLOSS_FILE_PATH,
    SILVER_STOCKPRICE_FILE_PATH,
    GOLD_CURRENTHOLDING_FILE_PATH,
    ensure_exists,
)
from StockETL.exceptions import FileProcessingError
from StockETL.datetimeutils import DateTimeUtil
from StockETL.common_utility import replace_nan_with_empty

logger = get_logger(__name__)


def load_csv_data(file_path: Path, description: str) -> pd.DataFrame:
    """
    Load CSV data with error handling.

    Args:
        file_path: Path to the CSV file.
        description: Description of the data for logging.

    Returns:
        Loaded DataFrame.

    Raises:
        FileProcessingError: If the file cannot be loaded.
    """
    try:
        logger.info(f"Loading {description} from: {file_path.name}")
        df = pd.read_csv(file_path)
        logger.debug(f"Loaded {len(df)} rows from {description}")
        return df
    except FileNotFoundError:
        raise FileProcessingError(
            f"{description} file not found",
            details={"path": str(file_path)},
        )
    except pd.errors.EmptyDataError:
        raise FileProcessingError(
            f"{description} file is empty",
            details={"path": str(file_path)},
        )
    except Exception as e:
        raise FileProcessingError(
            f"Failed to load {description}",
            details={"path": str(file_path), "error": str(e)},
        )


def process_current_holdings(
    df_holding: pd.DataFrame, df_stock_price: pd.DataFrame
) -> dict[str, Any]:
    """
    Process current holdings data and merge with latest stock prices.

    Args:
        df_holding: Current holdings DataFrame.
        df_stock_price: Stock price DataFrame.

    Returns:
        Dictionary of holdings grouped by username.
    """
    logger.info("Processing current holdings data")

    # Get latest prices for each symbol
    df_stock_price = df_stock_price.copy()
    df_stock_price["date"] = pd.to_datetime(df_stock_price["date"])
    df_stock_price["close_price"] = df_stock_price["close"]

    # Get the most recent price for each symbol
    idx = df_stock_price.groupby("symbol")["date"].idxmax()
    df_latest_prices = df_stock_price.loc[idx, ["symbol", "close_price"]].reset_index(
        drop=True
    )

    # Merge holdings with latest prices
    df_merged = pd.merge(
        df_holding,
        df_latest_prices,
        on="symbol",
        how="left",
    )

    # Calculate PnL
    df_merged["close_amount"] = df_merged["close_price"] * df_merged["quantity"]
    df_merged["pnl_amount"] = df_merged["close_amount"] - df_merged["amount"]
    df_merged = df_merged.round(2)

    # Group by username
    result = (
        df_merged.groupby("username")[
            [col for col in df_merged.columns if col != "username"]
        ]
        .apply(lambda x: x.to_dict("records"), include_groups=False)
        .to_dict()
    )

    logger.debug(f"Processed holdings for {len(result)} user(s)")
    return result


def process_holding_trends(df_holding: pd.DataFrame) -> dict[str, Any]:
    """
    Process holding history data to calculate trends.

    Args:
        df_holding: Holdings DataFrame.

    Returns:
        Dictionary of holding trends grouped by username.
    """
    logger.info("Processing holding trends data")

    df = df_holding.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Aggregate by user and date
    df_aggregated = (
        df.groupby(["username", "date"])[
            [
                "holding_amount",
                "open_amount",
                "high_amount",
                "low_amount",
                "close_amount",
            ]
        ]
        .sum()
        .reset_index()
    )

    # Rename columns for consistency
    df_aggregated = df_aggregated.round(2).rename(
        columns={col: col.replace("_amount", "") for col in df_aggregated.columns}
    )

    # Sort by date
    df_aggregated = (
        df_aggregated[["username", "date", "open", "high", "low", "close", "holding"]]
        .sort_values(by=["date"])
        .reset_index(drop=True)
    )

    # Group by username
    result = (
        df_aggregated.groupby("username")[
            [col for col in df_aggregated.columns if col != "username"]
        ]
        .apply(lambda x: x.to_dict("records"), include_groups=False)
        .to_dict()
    )

    logger.debug(f"Processed trends for {len(result)} user(s)")
    return result


def process_profit_loss(df_pnl: pd.DataFrame) -> dict[str, Any]:
    """
    Process profit and loss data.

    Args:
        df_pnl: Profit/Loss DataFrame.

    Returns:
        Dictionary of P&L data grouped by username.
    """
    logger.info("Processing profit/loss data")

    result = (
        df_pnl.groupby("username")[[col for col in df_pnl.columns if col != "username"]]
        .apply(lambda x: x.to_dict("records"), include_groups=False)
        .to_dict()
    )

    logger.debug(f"Processed P&L for {len(result)} user(s)")
    return result


def process_dividends(df_dividend: pd.DataFrame) -> dict[str, Any]:
    """
    Process dividend data.

    Args:
        df_dividend: Dividend DataFrame.

    Returns:
        Dictionary of dividend data grouped by username.
    """
    logger.info("Processing dividend data")

    result = (
        df_dividend.groupby("username")[
            [col for col in df_dividend.columns if col != "username"]
        ]
        .apply(lambda x: x.to_dict("records"), include_groups=False)
        .to_dict()
    )

    logger.debug(f"Processed dividends for {len(result)} user(s)")
    return result


def write_api_output(
    api_name: str, username: str, data: Any, load_timestamp: str
) -> None:
    """
    Write API output to JSON file.

    Args:
        api_name: Name of the API endpoint.
        username: Username for the data.
        data: Data to write.
        load_timestamp: Timestamp of data generation.
    """
    api_file_path = ensure_exists(PATH_API / username / f"{api_name}.json")

    output = {
        "data": data,
        "load_timestamp": load_timestamp,
    }

    # Clean the output (replace NaN values)
    output = replace_nan_with_empty(output)

    try:

        with open((api_file_path), "w", encoding="utf-8") as json_file:
            json.dump(
                output,
                json_file,
                indent=4,
                allow_nan=False,
                ensure_ascii=True,
                default=str,
                sort_keys=True,
            )
            json_file.write("\n")  # Add trailing newline

        logger.debug(f"Wrote API output: {api_file_path}")

    except Exception as e:
        raise FileProcessingError(
            f"Failed to write API output for {username}/{api_name}",
            details={"error": str(e)},
        )


def run() -> None:
    """
    Execute the API layer generation process.

    This function:
    1. Loads Gold layer data
    2. Processes and transforms data for each API endpoint
    3. Writes JSON outputs grouped by username

    Raises:
        FileProcessingError: If data loading or processing fails.
    """
    logger.info("Starting API Layer Generation")

    try:
        # Load all required data
        df_current_holding = load_csv_data(
            GOLD_CURRENTHOLDING_FILE_PATH, "Current Holdings"
        )
        df_stock_price = load_csv_data(SILVER_STOCKPRICE_FILE_PATH, "Stock Prices")
        df_holding = load_csv_data(GOLD_HOLDING_FILE_PATH, "Holding History")
        df_pnl = load_csv_data(GOLD_PROFITLOSS_FILE_PATH, "Profit/Loss")
        df_dividend = load_csv_data(GOLD_DIVIDEND_FILE_PATH, "Dividends")

        # Process data for each API endpoint
        api_outputs = {
            "current_holding_data": process_current_holdings(
                df_current_holding, df_stock_price
            ),
            "holding_trands_data": process_holding_trends(df_holding),
            "profit_loss_data": process_profit_loss(df_pnl),
            "dividend_data": process_dividends(df_dividend),
        }

        # Generate timestamp
        load_timestamp = str(DateTimeUtil.today())

        # Write outputs for each user and API endpoint
        total_files = 0
        for api_name, user_data in api_outputs.items():
            for username, data in user_data.items():
                write_api_output(api_name, username, data, load_timestamp)
                total_files += 1

        logger.info("API Layer Generation completed successfully")
        logger.info(f"Generated {total_files} API output file(s)")

    except Exception as e:
        logger.error(f"API Layer Generation failed: {e}", exc_info=True)
        raise
