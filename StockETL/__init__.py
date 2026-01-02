"""
StockETL - A Complete ETL Pipeline for Stock Portfolio Analysis.

This package provides a comprehensive ETL (Extract, Transform, Load) pipeline
for processing stock market data, calculating profit/loss, and generating
financial analysis reports.

Features:
    - Multi-layer data processing (Bronze, Silver, Gold)
    - Portfolio management and P&L calculation
    - Support for equities, derivatives, and commodities
    - Automated brokerage and tax calculations
    - API generation for frontend consumption

Usage:
    To run the complete ETL pipeline:

    >>> python -m StockETL

    Or programmatically:

    >>> from StockETL import ETL_BRONZE, ETL_SILVER, ETL_GOLD, ETL_API
    >>> ETL_BRONZE.Symbol.run()
    >>> ETL_SILVER.Symbol.run()
    >>> ETL_GOLD.Portfolio.run()
    >>> ETL_API.API.run()
"""

from StockETL import version, portfolio, datetimeutils

__doc__ = f"""StockETL v{version.VERSION}

A complete ETL pipeline for stock exchanges with P&L calculation
and financial analysis tools.

Repository: https://github.com/PtPrashantTripathi/PortfolioTracker
Copyright 2023-{datetimeutils.DateTimeUtil.today().year} Pt. Prashant Tripathi"""

__version__ = version.VERSION
__author__ = [
    {
        "name": "ptprashanttripathi",
        "email": "ptprashanttripathi@outlook.com",
    }
]
__all__ = portfolio.__all__ + datetimeutils.__all__
__license__ = "MIT"
__maintainer__ = "ptprashanttripathi"
__status__ = "Production"


def get_version() -> str:
    """
    Get the current version of StockETL.

    Returns:
        The version string.
    """
    return __version__


def print_info() -> None:
    """Print package information."""
    print(__doc__)
    print(f"Version: {__version__}")
    print(f"Author: {__author__[0]['name']} <{__author__[0]['email']}>")
    print(f"License: {__license__}")
    print(f"Status: {__status__}")


if __name__ == "__main__":
    print_info()
