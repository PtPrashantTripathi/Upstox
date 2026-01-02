"""
SILVER to GOLD Layer ETL Pipeline.

This module processes trade history data into structured holdings and profit/loss
information for the portfolio tracking system.

Module: StockETL.ETL_GOLD.Portfolio
"""

import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import (
    GOLD_HOLDING_FILE_PATH,
    SILVER_SYMBOL_FILE_PATH,
    SOURCE_HOLDING_FILE_PATH,
    GOLD_PROFITLOSS_FILE_PATH,
    SILVER_STOCKPRICE_FILE_PATH,
    GOLD_CURRENTHOLDING_FILE_PATH,
    SILVER_TRADEHISTORY_FILE_PATH,
    CONFIG_DATA_CONTRACTS_GOLD_PATH,
    CONFIG_DATA_CONTRACTS_SOURCE_PATH,
)
from StockETL.portfolio import Portfolio
from StockETL.common_utility import align_with_datacontract

# Initialize logger
logger = get_logger(__name__)

# Schema file paths
CURRENT_HOLDING_SCHEMA_PATH = CONFIG_DATA_CONTRACTS_GOLD_PATH / "CurrentHolding.json"
HOLDING_GOLD_SCHEMA_PATH = CONFIG_DATA_CONTRACTS_GOLD_PATH / "Holding.json"
HOLDING_SOURCE_SCHEMA_PATH = CONFIG_DATA_CONTRACTS_SOURCE_PATH / "Holding.json"
PROFITLOSS_SCHEMA_PATH = CONFIG_DATA_CONTRACTS_GOLD_PATH / "ProfitLoss.json"

# Constants
REQUIRED_SEGMENTS = {"EQ", "MF"}
OHLC_COLUMNS = ["open", "high", "low", "close"]


def expand_dates(stock_df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand date range for each stock and forward-fill missing values.

    This function fills gaps in trading data by reindexing to include all dates
    from the minimum date to today and forward-fills values for missing dates.

    Args:
        stock_df: DataFrame with stock data containing a 'date' column.

    Returns:
        DataFrame with expanded date range and forward-filled values.

    Raises:
        KeyError: If 'date' column is missing from the DataFrame.
        ValueError: If the DataFrame is empty.
    """
    if stock_df.empty:
        logger.warning("Empty DataFrame provided to expand_dates")
        return stock_df

    if "date" not in stock_df.columns:
        logger.error("Missing 'date' column in DataFrame")
        raise KeyError("DataFrame must contain a 'date' column")

    try:
        min_date = stock_df["date"].min()
        date_range = pd.date_range(start=min_date, end=pd.to_datetime("today"))

        expanded_df = (
            stock_df.set_index("date")
            .reindex(date_range)
            .ffill()
            .reset_index()
            .rename(columns={"index": "date"})
        )

        logger.debug(f"Expanded dates from {min_date} to today for stock data")
        return expanded_df

    except Exception as e:
        logger.error(f"Error expanding dates: {str(e)}")
        raise


def _load_and_prepare_trade_history() -> pd.DataFrame:
    """
    Load and prepare trade history data from SILVER layer.

    Returns:
        Filtered and sorted trade history DataFrame.

    Raises:
        FileNotFoundError: If trade history file doesn't exist.
        ValueError: If no valid trade records found.
    """
    try:
        df_trade_history = pd.read_csv(SILVER_TRADEHISTORY_FILE_PATH)
        logger.info(
            f"Loaded trade history from: {SILVER_TRADEHISTORY_FILE_PATH} "
            f"({len(df_trade_history)} records)"
        )

        # Filter for equity and mutual fund segments
        df_trade_history = df_trade_history[
            df_trade_history["segment"].isin(REQUIRED_SEGMENTS)
        ]

        if df_trade_history.empty:
            logger.warning("No valid trade records after segment filtering")

        # Convert and sort by datetime
        df_trade_history["datetime"] = pd.to_datetime(df_trade_history["datetime"])
        df_trade_history = df_trade_history.sort_values(by="datetime")

        logger.info(f"Prepared {len(df_trade_history)} trade records")
        return df_trade_history

    except FileNotFoundError:
        logger.error(f"Trade history file not found: {SILVER_TRADEHISTORY_FILE_PATH}")
        raise
    except Exception as e:
        logger.error(f"Error loading trade history: {str(e)}")
        raise


def _process_current_holding(portfolio: Portfolio) -> None:
    """
    Process current holdings from portfolio and save to GOLD layer.

    Args:
        portfolio: Portfolio instance with processed trades.

    Raises:
        Exception: If alignment or file operations fail.
    """
    try:
        df_current_holding = pd.DataFrame(portfolio.get_current_holding())
        df_current_holding = align_with_datacontract(
            df_current_holding, CURRENT_HOLDING_SCHEMA_PATH
        )

        df_current_holding.to_csv(GOLD_CURRENTHOLDING_FILE_PATH, index=False)
        logger.info(
            f"Current holding data saved to: {GOLD_CURRENTHOLDING_FILE_PATH} "
            f"({len(df_current_holding)} records)"
        )

    except Exception as e:
        logger.error(f"Error processing current holding: {str(e)}")
        raise


def _process_holding_history(portfolio: Portfolio) -> None:
    """
    Process holding history with expanded dates and stock prices.

    Args:
        portfolio: Portfolio instance with processed trades.

    Raises:
        Exception: If data processing or file operations fail.
    """
    try:
        # Get and prepare holding history
        df_holding = pd.DataFrame(portfolio.get_holding_history())
        df_holding["date"] = df_holding["datetime"].dt.date

        # Get latest record per day per stock
        idx = df_holding.groupby(["username", "scrip_name", "date"])[
            "datetime"
        ].idxmax()
        df_holding = df_holding.loc[idx].reset_index(drop=True)

        # Expand date ranges for each stock
        df_holding = (
            df_holding.groupby(["username", "scrip_name"])
            .apply(expand_dates, include_groups=False)
            .reset_index(drop=False)
        )

        # Load stock prices
        df_stock_price = pd.read_csv(SILVER_STOCKPRICE_FILE_PATH)
        df_stock_price["date"] = pd.to_datetime(df_stock_price["date"])
        logger.info(f"Loaded stock prices from: {SILVER_STOCKPRICE_FILE_PATH}")

        # Merge with stock prices
        df_holding = pd.merge(
            df_holding, df_stock_price, on=["date", "symbol"], how="left"
        )

        # Calculate OHLC amounts
        for col in OHLC_COLUMNS:
            df_holding[f"{col}_price"] = df_holding[col]
            df_holding[f"{col}_amount"] = (
                df_holding[col] * df_holding["holding_quantity"]
            )

        # Clean and filter
        df_holding = df_holding.ffill()
        df_holding = df_holding[df_holding["holding_quantity"] != 0]
        df_holding = df_holding.reset_index(drop=True)

        # Align with schema and save
        df_holding = align_with_datacontract(df_holding, HOLDING_GOLD_SCHEMA_PATH)
        df_holding.to_csv(GOLD_HOLDING_FILE_PATH, index=False)

        logger.info(
            f"Holding history saved to: {GOLD_HOLDING_FILE_PATH} "
            f"({len(df_holding)} records)"
        )

    except Exception as e:
        logger.error(f"Error processing holding history: {str(e)}")
        raise


def _process_source_holding(df_holding: pd.DataFrame) -> None:
    """
    Process source-level holding aggregates.

    Args:
        df_holding: Holding history DataFrame.

    Raises:
        Exception: If processing or file operations fail.
    """
    try:
        df_symbol = pd.read_csv(SILVER_SYMBOL_FILE_PATH)
        logger.info(f"Loaded symbols from: {SILVER_SYMBOL_FILE_PATH}")

        # Aggregate by segment, exchange, and symbol
        df_source_holding = (
            df_holding.groupby(["segment", "exchange", "symbol"])
            .agg(min_date=("date", "min"), max_date=("date", "max"))
            .reset_index()
        )

        # Merge with symbol details
        df_source_holding = df_source_holding.merge(
            df_symbol[["symbol", "isin"]], on="symbol", how="left"
        )

        # Align with schema and save
        df_source_holding = align_with_datacontract(
            df_source_holding, HOLDING_SOURCE_SCHEMA_PATH
        )
        df_source_holding.to_csv(SOURCE_HOLDING_FILE_PATH, index=False)
        logger.info(
            f"Source holding saved to: {SOURCE_HOLDING_FILE_PATH} "
            f"({len(df_source_holding)} records)"
        )

    except Exception as e:
        logger.error(f"Error processing source holding: {str(e)}")
        raise


def _process_profit_loss(portfolio: Portfolio) -> None:
    """
    Process profit/loss data and save to GOLD layer.

    Args:
        portfolio: Portfolio instance with processed trades.

    Raises:
        Exception: If processing or file operations fail.
    """
    try:
        df_pnl = pd.DataFrame(portfolio.get_pnl())
        df_pnl = df_pnl.reset_index(drop=True)
        df_pnl = align_with_datacontract(df_pnl, PROFITLOSS_SCHEMA_PATH)

        df_pnl.to_csv(GOLD_PROFITLOSS_FILE_PATH, index=False)
        logger.info(
            f"Profit/Loss data saved to: {GOLD_PROFITLOSS_FILE_PATH} "
            f"({len(df_pnl)} records)"
        )

    except Exception as e:
        logger.error(f"Error processing profit/loss: {str(e)}")
        raise


def run() -> None:
    """
    Execute SILVER to GOLD layer ETL pipeline.

    This function orchestrates the entire data transformation pipeline:
    1. Loads and prepares trade history
    2. Applies portfolio logic and calculations
    3. Processes current holdings
    4. Processes holding history with price data
    5. Processes source-level holdings
    6. Processes profit/loss calculations

    Raises:
        Exception: Re-raises any exceptions from sub-processes with logging.
    """
    try:
        logger.info("Starting SILVER to GOLD layer ETL pipeline")

        # Load trade history
        df_trade_history = _load_and_prepare_trade_history()

        # Process trades through portfolio
        portfolio = Portfolio()
        for record in df_trade_history.to_dict(orient="records"):
            portfolio.trade(record)

        portfolio.check_expired_stocks()
        logger.info("Trade processing completed")

        # Process each output dataset
        _process_current_holding(portfolio)
        _process_profit_loss(portfolio)

        # Process holding history (returns DataFrame for source holding processing)
        df_holding_for_source = pd.DataFrame(portfolio.get_holding_history())
        df_holding_for_source["date"] = df_holding_for_source["datetime"].dt.date
        idx = df_holding_for_source.groupby(["username", "scrip_name", "date"])[
            "datetime"
        ].idxmax()
        df_holding_for_source = df_holding_for_source.loc[idx].reset_index(drop=True)

        _process_holding_history(portfolio)
        _process_source_holding(df_holding_for_source)

        logger.info("SILVER to GOLD layer ETL pipeline completed successfully")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run()
