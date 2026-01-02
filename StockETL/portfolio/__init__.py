from StockETL.portfolio.stock import Stock
from StockETL.portfolio.brokerage import Brokerage
from StockETL.portfolio.portfolio import Portfolio
from StockETL.portfolio.stock_info import StockInfo
from StockETL.portfolio.trade_record import TradeRecord
from StockETL.portfolio.holding_record import HoldingRecord
from StockETL.portfolio.trade_position import TradePosition

__all__ = [
    "Portfolio",
    "Stock",
    "StockInfo",
    "TradeRecord",
    "HoldingRecord",
    "Brokerage",
    "TradePosition",
]


if __name__ == "__main__":
    trade_history = [
        {
            "username": "investor_01",
            "datetime": "2020-01-01 00:00:00",
            "exchange": "NSE",
            "segment": "EQ",
            "symbol": "TMPV",
            "scrip_name": "TMPV",
            "side": "BUY",
            "quantity": 10,
            "price": 100,
            "amount": 1000,
            "expiry_date": "",
        },
        {
            "username": "investor_01",
            "datetime": "2021-01-01 00:00:00",
            "exchange": "NSE",
            "segment": "EQ",
            "symbol": "TMPV",
            "scrip_name": "TMPV",
            "side": "SELL",
            "quantity": 5,
            "price": 200,
            "amount": 1000,
            "expiry_date": "",
        },
        {
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
            "expiry_date": "",
        },
    ]

    portfolio = Portfolio()
    for record in trade_history:
        portfolio.trade(record)

    portfolio.check_expired_stocks()
    import json

    print(
        "Holding history\n",
        json.dumps(portfolio.get_holding_history(), indent=4, default=str),
    )
    print(
        "Current Holding\n",
        json.dumps(portfolio.get_current_holding(), indent=4, default=str),
    )
    print("PNL history\n", json.dumps(portfolio.get_pnl(), indent=4, default=str))
