"""
Portfolio Management Module.

This module manages a collection of stocks for multiple users,
tracking trades, holdings, and profit/loss calculations.
"""

from StockETL.logger import get_logger
from StockETL.portfolio.stock import Stock
from StockETL.portfolio.stock_info import StockInfo
from StockETL.portfolio.trade_record import TradeRecord

logger = get_logger(__name__)


class Portfolio:
    """
    Manages a portfolio of stocks across multiple users.

    Attributes:
        userdata: Nested dictionary structure {username: {scrip_name: Stock}}
    """

    def __init__(self) -> None:
        """Initialize an empty portfolio."""
        self.userdata: dict[str, dict[str, Stock]] = {}

    def trade(self, data: dict) -> None:
        """
        Process a trade record for a specific stock in the portfolio.

        Creates or updates stock positions based on the trade data.
        Automatically initializes user and stock entries if they don't exist.

        Args:
            data: Dictionary containing trade information including:
                - username: The user executing the trade
                - scrip_name: The stock identifier
                - All other fields required by StockInfo and TradeRecord

        Raises:
            ValueError: If required fields are missing from data.
        """
        try:
            stock_info = StockInfo(**data)
        except Exception as e:
            logger.error(f"Failed to create StockInfo from trade data: {e}")
            raise ValueError(f"Invalid trade data: {e}") from e

        # Initialize user if not exists
        if stock_info.username not in self.userdata:
            self.userdata[stock_info.username] = {}
            logger.debug(f"Initialized portfolio for user: {stock_info.username}")

        # Initialize stock if not exists
        if stock_info.scrip_name not in self.userdata[stock_info.username]:
            self.userdata[stock_info.username][stock_info.scrip_name] = Stock(
                stock_info=stock_info
            )
            logger.debug(
                f"Initialized stock {stock_info.scrip_name} for user {stock_info.username}"
            )

        # Execute trade
        try:
            trade_record = TradeRecord(stock_info=stock_info, **data)
            self.userdata[stock_info.username][stock_info.scrip_name].trade(
                trade_record
            )
            logger.debug(
                f"Processed {trade_record.side} trade: "
                f"{trade_record.quantity} x {stock_info.scrip_name} "
                f"@ {trade_record.price}"
            )
        except Exception as e:
            logger.error(
                f"Failed to execute trade for {stock_info.scrip_name}: {e}",
                exc_info=True,
            )
            raise

    def check_expired_stocks(self) -> None:
        """
        Check all stocks in the portfolio for expiry and process them if expired.

        This is typically used for derivatives (futures/options) that have
        an expiry date.
        """
        logger.info("Checking for expired stocks")
        expired_count = 0

        for username, stocks in self.userdata.items():
            for scrip_name, stock in stocks.items():
                if stock.check_expired():
                    expired_count += 1
                    logger.info(
                        f"Processed expired stock: {scrip_name} for user {username}"
                    )

        if expired_count > 0:
            logger.info(f"Processed {expired_count} expired stock(s)")
        else:
            logger.debug("No expired stocks found")

    def get_holding_history(self) -> list[dict]:
        """
        Retrieve a list of holding records for all stocks in the portfolio.

        Returns:
            List of dictionaries, each containing:
                - username: The user who owns the stock
                - scrip_name: The stock name
                - symbol: The stock symbol
                - exchange: The exchange where traded
                - segment: The market segment
                - datetime: The timestamp of the holding record
                - holding_quantity: The quantity held
                - avg_price: The average price
                - holding_amount: The total value of holdings
        """
        logger.debug("Generating holding history")
        data = []

        for stocks in self.userdata.values():
            for stock in stocks.values():
                for holding in stock.holding_records:
                    data.append(
                        {
                            "username": holding.stock_info.username,
                            "scrip_name": holding.stock_info.scrip_name,
                            "symbol": holding.stock_info.symbol,
                            "exchange": holding.stock_info.exchange,
                            "segment": holding.stock_info.segment,
                            "datetime": holding.datetime,
                            "holding_quantity": holding.holding_quantity,
                            "avg_price": holding.avg_price,
                            "holding_amount": holding.holding_amount,
                        }
                    )

        logger.debug(f"Generated {len(data)} holding history record(s)")
        return data

    def get_current_holding(self) -> list[dict]:
        """
        Retrieve a list of currently open positions.

        Returns:
            List of dictionaries, each containing:
                - username: The user who owns the position
                - scrip_name: The stock name
                - symbol: The stock symbol
                - exchange: The exchange where traded
                - segment: The market segment
                - quantity: The quantity of the position
                - datetime: The timestamp when position was opened
                - side: BUY or SELL
                - price: The price at which position was opened
                - amount: The total value of the position
        """
        logger.debug("Generating current holdings")
        data = []

        for stocks in self.userdata.values():
            for stock in stocks.values():
                for position in stock.open_positions:
                    data.append(
                        {
                            "username": position.stock_info.username,
                            "scrip_name": position.stock_info.scrip_name,
                            "symbol": position.stock_info.symbol,
                            "exchange": position.stock_info.exchange,
                            "segment": position.stock_info.segment,
                            "quantity": position.quantity,
                            "datetime": position.datetime,
                            "side": position.side,
                            "price": position.price,
                            "amount": position.amount,
                        }
                    )

        logger.debug(f"Generated {len(data)} current holding record(s)")
        return data

    def get_pnl(self) -> list[dict]:
        """
        Retrieve a list of closed positions with profit/loss calculations.

        Returns:
            List of dictionaries, each containing:
                - username: The user who owned the position
                - scrip_name: The stock name
                - symbol: The stock symbol
                - exchange: The exchange where traded
                - segment: The market segment
                - quantity: The quantity that was closed
                - open_datetime: When the position was opened
                - open_side: BUY or SELL for opening trade
                - open_price: Price at opening
                - open_amount: Value at opening
                - close_datetime: When the position was closed
                - close_side: BUY or SELL for closing trade
                - close_price: Price at closing
                - close_amount: Value at closing
                - position: LONG or SHORT
                - pnl_amount: Profit or loss amount
                - pnl_percentage: Profit or loss percentage
                - brokerage: Total brokerage and charges
        """
        logger.debug("Generating P&L records")
        data = []

        for stocks in self.userdata.values():
            for stock in stocks.values():
                for position in stock.closed_positions:
                    data.append(
                        {
                            "username": position.close_position.stock_info.username,
                            "scrip_name": position.close_position.stock_info.scrip_name,
                            "symbol": position.close_position.stock_info.symbol,
                            "exchange": position.close_position.stock_info.exchange,
                            "segment": position.close_position.stock_info.segment,
                            "quantity": position.close_position.quantity,
                            "open_datetime": position.open_position.datetime,
                            "open_side": position.open_position.side,
                            "open_price": position.open_position.price,
                            "open_amount": position.open_position.amount,
                            "close_datetime": position.close_position.datetime,
                            "close_side": position.close_position.side,
                            "close_price": position.close_position.price,
                            "close_amount": position.close_position.amount,
                            "position": position.position,
                            "pnl_amount": position.pnl_amount,
                            "pnl_percentage": position.pnl_percentage,
                            "brokerage": position.brokerage.total,
                        }
                    )

        logger.debug(f"Generated {len(data)} P&L record(s)")
        return data
