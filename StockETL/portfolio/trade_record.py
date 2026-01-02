import datetime as dt
from typing import Self, Annotated

from pydantic import BaseModel, BeforeValidator
from pydantic_core.core_schema import ValidationInfo

from StockETL.portfolio.brokerage import Brokerage, get_brokerage_rates
from StockETL.portfolio.stock_info import StockInfo


def fix_amount(value, info: ValidationInfo):
    """Calculates amount if it is 0 using quantity and price."""
    if value == 0:
        qty = info.data.get("quantity", 0)
        prc = info.data.get("price", 0)
        return qty * prc
    return value


def parse_datetime(value):
    """Validates and parses the datetime."""
    try:
        if value is None or str(value).lower() in ("nan", "", "none"):
            return None
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise ValueError("Invalid DateTime format. Expected YYYY-MM-DD HH:MM:SS") from e


# --- TradeRecord Model ---
class TradeRecord(BaseModel):
    """Represents a trade record."""

    # The Information of the stock.
    stock_info: StockInfo
    # The datetime of the trade.
    datetime: Annotated[dt.datetime, BeforeValidator(parse_datetime)]
    # The side of the trade ("BUY" or "SELL").
    side: str
    # The quantity of stock traded.
    quantity: float | int = 0
    # The price at which the trade occurred.
    price: float | int = 0
    # The total amount of the trade.
    amount: Annotated[float | int, BeforeValidator(fix_amount)] = 0

    def calculate_brokerage(self, close_position: Self) -> Brokerage:
        """Calculate brokerage"""

        brokerage_rates = get_brokerage_rates(close_position.stock_info)

        # BROKERAGE CHARGES
        brokerage = Brokerage()

        if close_position.stock_info.segment in ["FO"]:
            brokerage.brokerage_charges = 40
        else:
            brokerage.brokerage_charges = min(
                (brokerage_rates.get("brokerage", 0) * self.amount) / 100, 20
            ) + min(
                (brokerage_rates.get("brokerage", 0) * close_position.amount) / 100, 20
            )

        # STT CTT TAX
        brokerage.stt_ctt_tax = (
            brokerage_rates.get("stt", {}).get("buy", 0) * self.amount
            + brokerage_rates.get("stt", {}).get("sell", 0) * close_position.amount
        ) / 100

        # SEBI CHARGES
        brokerage.sebi_charges = (
            (self.amount + close_position.amount)
            * brokerage_rates.get("sebi_charges", 0)
        ) / 100

        # EXCHANGE CHARGES
        brokerage.transaction_charges = (
            (self.amount + close_position.amount)
            * brokerage_rates.get("transaction_charges", {}).get(
                close_position.stock_info.exchange, 0
            )
        ) / 100

        # STAMP DUTY
        brokerage.stamp_duty_tax = (
            (brokerage_rates.get("stamp_duty", 0)) * self.quantity * self.price
        ) / 100

        brokerage.gst_tax = (
            (brokerage.brokerage_charges + brokerage.transaction_charges) * 18 / 100
        )

        brokerage.total = (
            brokerage.brokerage_charges
            + brokerage.transaction_charges
            + brokerage.sebi_charges
            + brokerage.stt_ctt_tax
            + brokerage.stamp_duty_tax
            + brokerage.gst_tax
        )
        return brokerage


if __name__ == "__main__":
    # Example Usage:
    data = {
        "username": "investor_01",
        "datetime": "2021-01-01 01:00:00",
        "exchange": "NSE",
        "segment": "EQ",
        "symbol": "TMPV",
        "scrip_name": "TMPV",
        "side": "SELL",
        "quantity": 5,
        "price": 150,
        "amount": 750,
        "expiry_date": "2021-01-01",
    }
    stock_info = StockInfo(**data)
    test = TradeRecord(stock_info=stock_info, **data)
    print(test)
