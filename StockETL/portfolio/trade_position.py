from pydantic import BaseModel

from StockETL.portfolio.brokerage import Brokerage
from StockETL.portfolio.trade_record import TradeRecord


class TradePosition(BaseModel):
    """Represents a trade position, including open and close details."""

    open_position: TradeRecord  # open trade record.
    close_position: TradeRecord  # close trade record.
    position: str = None  # The position of the trade ("LONG" or "SHORT" or "EXPIRE").
    pnl_amount: float | int = 0  # The profit or loss amount for position.
    pnl_percentage: float | int = 0  # The profit or loss percentage for position.
    brokerage: Brokerage = Brokerage()  # The brokerage details of Position.
