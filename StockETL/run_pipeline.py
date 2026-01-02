"""
StockETL Main Entry Point.

This module orchestrates the ETL pipeline, running data transformations
from Bronze to Silver to Gold layers, and finally generating API outputs.
"""

import sys

from StockETL import ETL_API, ETL_GOLD, ETL_BRONZE, ETL_SILVER
from StockETL.logger import get_logger

logger = get_logger(__name__)


def run_bronze_layer() -> bool:
    """
    Execute Bronze layer ETL processes.

    The Bronze layer reads raw data from source files and performs
    initial data harmonization.

    Returns:
        True if all processes complete successfully, False otherwise.
    """
    logger.info("=" * 80)
    logger.info("Starting Bronze Layer ETL")
    logger.info("=" * 80)

    try:
        ETL_BRONZE.Symbol.run()
        logger.info("✓ Symbol processing complete")

        ETL_BRONZE.TradeHistory.run()
        logger.info("✓ TradeHistory processing complete")

        ETL_BRONZE.StockData.run()
        logger.info("✓ StockData processing complete")

        logger.info("Bronze Layer ETL completed successfully")
        return True

    except Exception as e:
        logger.error(f"Bronze Layer ETL failed: {e}", exc_info=True)
        return False


def run_silver_layer() -> bool:
    """
    Execute Silver layer ETL processes.

    The Silver layer performs data cleansing, transformation, and enrichment
    on Bronze layer outputs.

    Returns:
        True if all processes complete successfully, False otherwise.
    """
    logger.info("=" * 80)
    logger.info("Starting Silver Layer ETL")
    logger.info("=" * 80)

    try:
        ETL_SILVER.Symbol.run()
        logger.info("✓ Symbol processing complete")

        ETL_SILVER.StockPrice.run()
        logger.info("✓ StockPrice processing complete")

        ETL_SILVER.StockEvents.run()
        logger.info("✓ StockEvents processing complete")

        ETL_SILVER.TradeHistory.run()
        logger.info("✓ TradeHistory processing complete")

        logger.info("Silver Layer ETL completed successfully")
        return True

    except Exception as e:
        logger.error(f"Silver Layer ETL failed: {e}", exc_info=True)
        return False


def run_gold_layer() -> bool:
    """
    Execute Gold layer ETL processes.

    The Gold layer creates business-ready aggregated data and analytics.

    Returns:
        True if all processes complete successfully, False otherwise.
    """
    logger.info("=" * 80)
    logger.info("Starting Gold Layer ETL")
    logger.info("=" * 80)

    try:
        ETL_GOLD.Portfolio.run()
        logger.info("✓ Portfolio processing complete")

        ETL_GOLD.Dividend.run()
        logger.info("✓ Dividend processing complete")

        logger.info("Gold Layer ETL completed successfully")
        return True

    except Exception as e:
        logger.error(f"Gold Layer ETL failed: {e}", exc_info=True)
        return False


def run_api_layer() -> bool:
    """
    Execute API layer generation.

    The API layer generates JSON outputs for external consumption.

    Returns:
        True if all processes complete successfully, False otherwise.
    """
    logger.info("=" * 80)
    logger.info("Starting API Layer Generation")
    logger.info("=" * 80)

    try:
        ETL_API.API.run()
        logger.info("✓ API generation complete")

        logger.info("API Layer Generation completed successfully")
        return True

    except Exception as e:
        logger.error(f"API Layer Generation failed: {e}", exc_info=True)
        return False


def main(layers: list[str] | None = None) -> int:
    """
    Run the complete StockETL pipeline or specific layers.

    Args:
        layers: Optional list of layer names to run. If None, runs all layers.
                Valid values: ['bronze', 'silver', 'gold', 'api']

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logger.info("StockETL Pipeline Starting")
    logger.info("=" * 80)

    # Define the pipeline stages
    pipeline = {
        "bronze": run_bronze_layer,
        "silver": run_silver_layer,
        "gold": run_gold_layer,
        "api": run_api_layer,
    }

    # Determine which layers to run
    if layers is None:
        layers_to_run = list(pipeline.keys())
    else:
        layers_to_run = [layer.lower() for layer in layers]
        invalid_layers = set(layers_to_run) - set(pipeline.keys())
        if invalid_layers:
            logger.error(f"Invalid layer names: {invalid_layers}")
            return 1

    # Execute the pipeline
    failed_layers = []
    for layer_name in layers_to_run:
        if not pipeline[layer_name]():
            failed_layers.append(layer_name)
            logger.error(f"Layer '{layer_name}' failed. Stopping pipeline.")
            break

    # Report final status
    logger.info("=" * 80)
    if failed_layers:
        logger.error(f"Pipeline FAILED at layer(s): {', '.join(failed_layers)}")
        return 1
    else:
        logger.info("Pipeline completed SUCCESSFULLY")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
