import datetime as dt

from pydantic import BaseModel

from StockETL.portfolio.stock_info import StockInfo
from StockETL.portfolio.trade_record import TradeRecord
from StockETL.portfolio.holding_record import HoldingRecord
from StockETL.portfolio.trade_position import TradePosition


class Stock(BaseModel):
    """Represents a stock, including open and closed positions and holding records."""

    stock_info: StockInfo  # The Information of the stock.
    holding_quantity: float | int = 0  # The total quantity of the stock held.
    holding_amount: float | int = 0  # The total amount of the stock held.
    avg_price: float | int = 0  # The average price of the stock held.
    open_positions: list[TradeRecord] = []  # List of open trade positions.
    closed_positions: list[TradePosition] = []  # List of closed trade positions.
    holding_records: list[HoldingRecord] = []  # List of holding records.

    def trade(self, trade_record: TradeRecord):
        """
        Processes a trade record and updates open and closed positions.

        Args:
            trade_record (TradeRecord): The trade record to be processed.
        """
        # Iterate through open positions to close trades if possible
        for open_position in self.open_positions:
            if (
                trade_record.quantity > 0
                and open_position.quantity > 0
                and open_position.side != trade_record.side
            ):
                # Record closed position
                cp = self.update_position(
                    open_position.model_copy(deep=True),
                    trade_record.model_copy(deep=True),
                )
                self.closed_positions.append(cp)

                # Update current position quantity and amount after deduction of quantity
                open_position.quantity -= cp.close_position.quantity
                open_position.amount = open_position.quantity * open_position.price

                # Reduce the remaining trade quantity
                trade_record.quantity -= cp.close_position.quantity

        # Remove fully closed positions
        self.open_positions = [
            position for position in self.open_positions if position.quantity > 0
        ]

        # Add new position if trade is not fully matched
        if trade_record.quantity != 0:
            self.open_positions.append(trade_record)

        # Update holding records
        updated_holding_record = self.calc_holding(trade_record.datetime)
        self.holding_records.append(updated_holding_record)

    def update_position(self, open_position: TradeRecord, close_position: TradeRecord):
        """method to close the open position"""
        # Create close position quantity and amount
        close_position.quantity = min(close_position.quantity, open_position.quantity)
        close_position.amount = close_position.quantity * close_position.price

        # Create Open position and Update quantity and amount
        open_position.quantity = close_position.quantity
        open_position.amount = open_position.quantity * open_position.price

        # Calculate PNL for closing trade
        pnl_amount = (
            (close_position.price - open_position.price) * close_position.quantity
            if open_position.side == "BUY"
            else (open_position.price - close_position.price) * close_position.quantity
        )

        # Record closed position
        return TradePosition(
            open_position=open_position,
            close_position=close_position,
            # Determine position
            position={"SELL": "LONG", "BUY": "SHORT"}.get(
                close_position.side, close_position.side
            ),
            pnl_amount=pnl_amount,
            # Calculate PnL percentage if open_price is non-zero
            pnl_percentage=(
                (pnl_amount / (open_position.price * close_position.quantity)) * 100
                if open_position.price != 0
                else None
            ),
            brokerage=open_position.calculate_brokerage(
                close_position=close_position
            ).round(2),
        )

    def calc_holding(self, datetime: dt.datetime | None = None) -> HoldingRecord:
        """
        Calculates the current holding and updates holding metrics.

        Returns:
            HoldingRecord: The updated holding record.
        """
        self.holding_quantity = 0
        self.holding_amount = 0

        for open_position in self.open_positions:
            # Calculate holding values
            position_quantity = (
                open_position.quantity
                if open_position.side == "BUY"
                else -open_position.quantity
            )
            self.holding_quantity += position_quantity
            self.holding_amount += open_position.price * position_quantity

        self.avg_price = (
            0
            if self.holding_quantity == 0
            else self.holding_amount / self.holding_quantity
        )

        return HoldingRecord(
            stock_info=self.stock_info,
            datetime=datetime or dt.datetime.now(),
            holding_quantity=self.holding_quantity,
            avg_price=self.avg_price,
            holding_amount=self.holding_amount,
        )

    def check_expired(self) -> bool:
        """
        Check if the stock has expired and process expiry if applicable.

        This is relevant for derivatives (futures/options) that have an expiry date.
        If the stock is expired and has open positions, they are automatically closed.

        Returns:
            True if the stock was expired and processed, False otherwise.
        """
        if (
            self.holding_quantity != 0
            and self.stock_info.expiry_date is not None
            and dt.datetime.today() > self.stock_info.expiry_date
        ):
            print(f"{self.stock_info.scrip_name} => {self.holding_quantity} expired")
            self.trade(
                TradeRecord(
                    stock_info=self.stock_info,
                    datetime=self.stock_info.expiry_date,
                    side="EXPIRED",
                    quantity=abs(self.holding_quantity),
                    price=0,
                    amount=0,
                )
            )
            return True
        return False


if __name__ == "__main__":
    from pprint import pprint

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
    test = Stock(stock_info=stock_info)
    test.trade(TradeRecord(stock_info=stock_info, **data))
    pprint(test.__dict__, compact=True, sort_dicts=False)
