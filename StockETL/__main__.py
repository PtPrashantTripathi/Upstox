"""
Command-Line Interface for StockETL.

This module provides a CLI for running the ETL pipeline with various options.
"""

import sys
import argparse
import traceback

from StockETL.version import __version__
from StockETL.run_pipeline import main as run_pipeline


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="StockETL",
        description="Stock Portfolio ETL Pipeline - Process and analyze stock market data",
        epilog="For more information, visit: https://github.com/PtPrashantTripathi/PortfolioTracker",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--layers",
        nargs="+",
        choices=["bronze", "silver", "gold", "api"],
        metavar="LAYER",
        help="Specify which layers to run (default: all layers)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv if None).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Run the pipeline
    try:
        return run_pipeline(layers=args.layers)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
