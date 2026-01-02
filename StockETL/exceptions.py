"""
Custom exceptions for StockETL.

This module defines custom exception classes for better error handling
and debugging throughout the application.
"""


class StockETLException(Exception):
    """Base exception for all StockETL errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize the exception.

        Args:
            message: The error message.
            details: Additional details about the error.
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class DataValidationError(StockETLException):
    """Raised when data validation fails."""


class DataContractError(StockETLException):
    """Raised when data doesn't conform to the expected schema."""


class FileProcessingError(StockETLException):
    """Raised when file processing encounters an error."""


class ConfigurationError(StockETLException):
    """Raised when configuration is invalid or missing."""


class DataNotFoundError(StockETLException):
    """Raised when required data is not found."""


class PortfolioError(StockETLException):
    """Raised when portfolio operations encounter an error."""


class TradeExecutionError(StockETLException):
    """Raised when trade execution encounters an error."""


class SchemaLoadError(StockETLException):
    """Raised when schema loading fails."""
