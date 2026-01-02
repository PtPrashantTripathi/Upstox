from typing import Self, Literal

from pydantic import BaseModel

from StockETL.portfolio.stock_info import StockInfo

ALL_BROKERAGE_RATES = {
    "eq_intraday": {
        "brokerage": 0.05,
        "stamp_duty": 0.003,
        "stt": {"buy": 0, "sell": 0.025},
        "transaction_charges": {
            "nse": 0.00322,
            "bse": 0.00297,
        },
        "sebi_charges": 0.0001,
    },
    "eq_delivery": {
        "brokerage": 0.05,
        "stamp_duty": 0.015,
        "stt": {"buy": 0.1, "sell": 0.1},
        "transaction_charges": {
            "nse": 0.00322,
            "bse": 0.00297,
        },
        "sebi_charges": 0.0001,
    },
    "future": {
        "brokerage": 20,
        "stamp_duty": 0.002,
        "stt": {"buy": 0, "sell": 0.02},
        "transaction_charges": {
            "nse": 0.00188,
            "bse": 0,
        },
        "sebi_charges": 0.0001,
    },
    "option": {
        "brokerage": 20,
        "stamp_duty": 0.003,
        "stt": {"buy": 0, "sell": 0.1},
        "transaction_charges": {"nse": 0.0495, "bse": 0.0495},
        "sebi_charges": 0.0001,
    },
    "commodity_future": {
        "brokerage": 20,
        "stamp_duty": 0.002,
        "stt": {"buy": 0.01, "sell": 0},
        "transaction_charges": {"nse": 0.0026, "bse": 0.0026},
        "sebi_charges": 0.0001,
    },
    "commodity_option": {
        "brokerage": 20,
        "stamp_duty": 0.003,
        "stt": {"buy": 0.05, "sell": 0},
        "transaction_charges": {"nse": 0.05, "bse": 0.05},
        "sebi_charges": 0.0001,
    },
}


class Brokerage(BaseModel):
    """Brokerage Class"""

    brokerage_charges: float | int = 0
    transaction_charges: float | int = 0
    sebi_charges: float | int = 0
    gst_tax: float | int = 0
    stt_ctt_tax: float | int = 0
    stamp_duty_tax: float | int = 0
    total: float | int = 0

    def round(self, decimal_places: int = 2) -> Self:
        self.brokerage_charges = round(self.brokerage_charges, decimal_places)
        self.transaction_charges = round(self.transaction_charges, decimal_places)
        self.sebi_charges = round(self.sebi_charges, decimal_places)
        self.gst_tax = round(self.gst_tax, decimal_places)
        self.stt_ctt_tax = round(self.stt_ctt_tax, decimal_places)
        self.stamp_duty_tax = round(self.stamp_duty_tax, decimal_places)
        self.total = round(self.total, decimal_places)
        return self


def get_brokerage_rates(
    stock_info: StockInfo,
    brokerage_type: (
        Literal[
            "eq_intraday",
            "eq_delivery",
            "future",
            "option",
            "commodity_future",
            "commodity_option",
        ]
        | None
    ) = None,
) -> dict:
    """
    Returns the brokerage rates for a specific stock based on the brokerage type.
    Args:
        stock_info(StockInfo): "Information about the stock, including details required for calculating brokerage.",
        brokerage_type(Literal['eq_intraday', 'eq_delivery', 'future', 'option', 'commodity_future', 'commodity_option']) : The type of brokerage to calculate (e.g., equity intraday, future, option, etc.). If not provided, defaults to None.
    Returns:
        A dictionary containing the brokerage rates for the specified stock and brokerage type.
    """
    if brokerage_type is None:
        if stock_info.exchange in ["NSE", "BSE"] and stock_info.segment == "EQ":
            brokerage_type = "eq_delivery"
        elif stock_info.exchange in ["FON"] and stock_info.segment == "FO":
            brokerage_type = "option"
        else:
            brokerage_type = ""
    return ALL_BROKERAGE_RATES.get(brokerage_type, {})
