import datetime as dt
from typing import Annotated

from pydantic import BaseModel, BeforeValidator


def parse_expiry_date(value: dt.datetime | str = None):
    """Validates and parses the expiry date."""
    try:
        # Handle empty strings or NaN values often found in data imports
        if value is None or str(value).lower() in ("nan", "", "none"):
            return None

        # If it's already a datetime object, just return it
        if isinstance(value, dt.datetime):
            return value

        # Parse the date string and combine with specific time (15:30)
        return dt.datetime.combine(
            dt.datetime.strptime(str(value).split(" ")[0], "%Y-%m-%d").date(),
            dt.time(15, 30),
        )
    except ValueError as e:
        raise ValueError("Invalid expiry_date format. Expected YYYY-MM-DD") from e


class StockInfo(BaseModel):
    """Base class for models that include stock information."""

    # The name of the owner
    username: str
    # The name of the stock.
    scrip_name: str
    # The symbol or stock id of the stock.
    symbol: str = None
    # The exchange where the stock is traded.
    exchange: str = None
    # The market segment of the stock.
    segment: str = None
    # The expiry date for options or futures.
    expiry_date: Annotated[dt.datetime | None, BeforeValidator(parse_expiry_date)] = (
        None
    )


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

    stock = StockInfo(**data)
    print(stock)
