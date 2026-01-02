import datetime as dt

from pydantic import BaseModel

from StockETL.portfolio.stock_info import StockInfo


class HoldingRecord(BaseModel):
    """Represents a record of stock holding."""

    stock_info: StockInfo  # The Information of the stock.
    datetime: dt.datetime  # The datetime of the holding record.
    holding_quantity: float | int = 0  # The quantity of stock held.
    avg_price: float | int = 0  # The average price of the held stock.
    holding_amount: float | int = 0  # The total amount of the holding.
