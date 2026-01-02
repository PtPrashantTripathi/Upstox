[![Header](https://raw.githubusercontent.com/PtPrashantTripathi/PortfolioTracker/main/public/img/portfolio_tracker_header.png)](https://github.com/PtPrashantTripathi/PortfolioTracker)

# Portfolio Tracker - Stock ETL with Medallion Architecture

[![data_update](https://github.com/PtPrashantTripathi/PortfolioTracker/actions/workflows/data_update.yml/badge.svg)](https://github.com/PtPrashantTripathi/PortfolioTracker/actions/workflows/data_update.yml)
[![deploy_github_pages](https://github.com/PtPrashantTripathi/PortfolioTracker/actions/workflows/deploy_github_pages.yml/badge.svg)](https://github.com/PtPrashantTripathi/PortfolioTracker/actions/workflows/deploy_github_pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

> A comprehensive, industry-standard ETL (Extract, Transform, Load) pipeline for processing stock market data, calculating profit/loss, and generating financial analysis reports using Medallion Architecture.

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Layers](#data-layers)
- [Portfolio Management](#portfolio-management)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Support](#support)

## 🎯 Overview

Portfolio Tracker is an exciting ETL solution that leverages the power of Medallion architecture to transform trading data into actionable insights. It seamlessly extracts, transforms, and loads data from trading accounts (Upstox and others) into a multi-tiered storage system: **BRONZE**, **SILVER**, and **GOLD** layers, providing a robust foundation for data management, analytics, and decision-making in trading activities.

### Why Portfolio Tracker?

📊 **Data-Driven Trading**: Make informed decisions based on comprehensive portfolio analysis
🔄 **Automated Processing**: Set it and forget it - automated ETL pipeline handles everything
📈 **Performance Tracking**: Real-time P&L calculation and portfolio performance metrics
💼 **Multi-User Support**: Track portfolios for multiple users and accounts
🎯 **Production Ready**: Industry-standard code with comprehensive logging and error handling
🚀 **Scalable Design**: Medallion architecture that grows with your data needs

## 🌟 Features

### Core Capabilities

- ✅ **Multi-Layer Architecture**: Progressive data refinement through Bronze → Silver → Gold → API layers
- ✅ **Portfolio Management**: Track stocks across multiple users and trading accounts
- ✅ **P&L Calculation**: Automated profit/loss calculation with FIFO position matching
- ✅ **Brokerage & Taxes**: Accurate calculation of brokerage, STT, stamp duty, and GST
- ✅ **Multiple Asset Classes**: Support for equities, futures, options, and commodities
- ✅ **Data Validation**: Schema-based data contracts ensure data quality
- ✅ **Comprehensive Logging**: Structured logging for debugging and monitoring
- ✅ **Type Safety**: Full type hints throughout the codebase for better IDE support
- ✅ **Error Handling**: Custom exceptions for better error management
- ✅ **CLI Interface**: Flexible command-line interface with multiple options
- ✅ **Web Dashboard**: Interactive visualizations and insights (coming soon)

### Trading Features

🔗 **Exchange Integration**: Connect with Upstox and other trading platforms
📊 **Real-Time Data**: Process real-time and historical trading data
💰 **Dividend Tracking**: Track and analyze dividend income
📈 **Trend Analysis**: Visualize portfolio performance over time
🎯 **Position Management**: Track open and closed positions with detailed metrics
📉 **Risk Analysis**: Understand your portfolio risk exposure

### Technical Features

🏗️ **Medallion Architecture**: Industry-standard lakehouse architecture
🐍 **Python-Powered**: Built with modern Python (3.7+)
📦 **Modular Design**: Clean, maintainable, and extensible codebase
🔍 **Data Contracts**: Schema validation for data quality
📝 **Documentation**: Comprehensive guides and API documentation
🧪 **Testing Ready**: Structure supports comprehensive test coverage

## 🏗️ Architecture

### Medallion Architecture

Portfolio Tracker implements the **Medallion Architecture**, a data design pattern used to organize data in a lakehouse logically:

```
┌─────────────┐
│   SOURCE    │  Raw data files (CSV, Excel, JSON)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   BRONZE    │  Harmonized data with standardized schema
└──────┬──────┘  - Data type conversion
       │         - Column name normalization
       │         - Basic validation
       ▼
┌─────────────┐
│   SILVER    │  Cleansed, validated, and enriched data
└──────┬──────┘  - Data quality checks
       │         - Duplicate removal
       │         - Enrichment with reference data
       ▼
┌─────────────┐
│    GOLD     │  Business-ready aggregated analytics
└──────┬──────┘  - Portfolio calculations
       │         - P&L computation
       │         - Aggregations and metrics
       ▼
┌─────────────┐
│     API     │  JSON endpoints for frontend consumption
└─────────────┘  - User-specific data
                 - Optimized for web/mobile apps
```

### System Architecture

```
Portfolio Tracker
│
├── StockETL/              # Core ETL Package
│   ├── ETL_BRONZE/       # Bronze layer processors
│   ├── ETL_SILVER/       # Silver layer processors
│   ├── ETL_GOLD/         # Gold layer processors
│   ├── ETL_API/          # API generation
│   ├── portfolio/        # Portfolio management
│   ├── common_utility/   # Shared utilities
│   ├── logger.py         # Logging system
│   ├── exceptions.py     # Custom exceptions
│   └── constants.py      # Constants & config
│
├── DATA/                 # Data Storage
│   ├── SOURCE/          # Raw input files
│   ├── BRONZE/          # Harmonized data
│   ├── SILVER/          # Cleansed data
│   ├── GOLD/            # Analytics-ready data
│   ├── API/             # JSON outputs
│   ├── CONFIG/          # Data contracts
│   └── logs/            # Application logs
│
└── src/                 # Frontend Application
    └── pages/           # React/Vue pages
```

## ⚡ Quick Start

Get started in 5 minutes with Portfolio Tracker:

```bash
# 1. Clone the repository
git clone https://github.com/PtPrashantTripathi/PortfolioTracker.git
cd PortfolioTracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set PROJECT_DIR

# 4. Run the pipeline
python -m StockETL

# 5. Check the results
ls -la DATA/API/
```

For a detailed guide, see [QUICKSTART.md](QUICKSTART.md)

## 📋 Requirements

### System Requirements

- Python 3.7 or higher
- 2GB RAM minimum (4GB recommended)
- 500MB disk space for data storage

### Dependencies

```
pandas >= 2.2.2
python-dotenv >= 1.0.1
pydantic >= 2.0.0
numpy >= 1.24.0
```

## 🚀 Installation

### Method 1: From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/PtPrashantTripathi/PortfolioTracker.git
cd PortfolioTracker

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 2: Using pip (if published)

```bash
pip install StockETL
```

### Method 3: Docker (Coming Soon)

```bash
docker pull ptprashanttripathi/portfolio-tracker
docker run -v $(pwd)/DATA:/app/DATA portfolio-tracker
```

## ⚙️ Configuration

### Environment Setup

1. **Copy the environment template:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your settings:**

   ```env
   # Required
   PROJECT_DIR=/absolute/path/to/your/PortfolioTracker

   # Optional
   LOG_LEVEL=INFO
   ```

### Directory Structure

Ensure the following structure exists (created automatically):

```
DATA/
├── SOURCE/              # Place your raw data files here
│   ├── Symbol/         # Stock master data (CSV)
│   ├── TradeHistory/   # Trade transactions (CSV/Excel)
│   ├── Dividend/       # Dividend data
│   └── Holding/        # Current holdings
│
├── BRONZE/             # Harmonized data (auto-generated)
├── SILVER/             # Cleansed data (auto-generated)
├── GOLD/               # Analytics data (auto-generated)
├── API/                # JSON outputs (auto-generated)
├── CONFIG/             # Data contracts & schemas
│   └── DATA_CONTRACTS/ # JSON schema files
└── logs/               # Application logs
```

### Data Contract Configuration

Create JSON schema files in `DATA/CONFIG/DATA_CONTRACTS/`:

```json
{
  "data_schema": [
    {
      "col_name": "symbol",
      "data_type": "string"
    },
    {
      "col_name": "price",
      "data_type": "float64"
    },
    {
      "col_name": "quantity",
      "data_type": "int64"
    }
  ],
  "order_by": ["date", "symbol"]
}
```

## 📖 Usage

### Command Line Interface

**Run the complete pipeline:**

```bash
python -m StockETL
```

**Run specific layers:**

```bash
# Run only Bronze and Silver
python -m StockETL --layers bronze silver

# Run Gold and API layers
python -m StockETL --layers gold api
```

**Control logging:**

```bash
# Verbose output
python -m StockETL --verbose

# Quiet mode (errors only)
python -m StockETL --quiet

# Custom log level
python -m StockETL --log-level DEBUG
```

**View help:**

```bash
python -m StockETL --help
```

### Programmatic Usage

**Run ETL layers individually:**

```python
from StockETL import ETL_BRONZE, ETL_SILVER, ETL_GOLD, ETL_API

# Bronze Layer - Data Harmonization
ETL_BRONZE.Symbol.run()
ETL_BRONZE.TradeHistory.run()
ETL_BRONZE.StockData.run()

# Silver Layer - Data Cleansing
ETL_SILVER.Symbol.run()
ETL_SILVER.StockPrice.run()
ETL_SILVER.StockEvents.run()
ETL_SILVER.TradeHistory.run()

# Gold Layer - Analytics
ETL_GOLD.Portfolio.run()
ETL_GOLD.Dividend.run()

# API Layer - JSON Generation
ETL_API.API.run()
```

**Use the Portfolio Manager:**

```python
from StockETL.portfolio import Portfolio

# Create a portfolio
portfolio = Portfolio()

# Process trades
trade_data = {
    "username": "investor_01",
    "datetime": "2024-01-15 10:30:00",
    "exchange": "NSE",
    "segment": "EQ",
    "symbol": "RELIANCE",
    "scrip_name": "Reliance Industries",
    "side": "BUY",
    "quantity": 100,
    "price": 2500.50,
    "amount": 250050.00,
}

portfolio.trade(trade_data)

# Get current holdings
holdings = portfolio.get_current_holding()
print(f"Current Holdings: {len(holdings)} positions")

# Get P&L
pnl = portfolio.get_pnl()
total_pnl = sum(p['pnl_amount'] for p in pnl)
print(f"Total P&L: ₹{total_pnl:,.2f}")

# Get holding history
history = portfolio.get_holding_history()
print(f"Total Records: {len(history)}")
```

**Custom Logging:**

```python
from StockETL.logger import get_logger
import logging

# Get a logger for your module
logger = get_logger(__name__)

# Use it
logger.info("Processing started")
logger.debug("Detailed debug information")
logger.warning("Warning message")
logger.error("Error occurred")
```

## 📊 Data Layers

### SOURCE Layer

**Purpose**: Raw data ingestion point

**Input**: CSV, Excel, JSON files from trading platforms
**Process**: None (raw data)
**Output**: Original files stored for audit trail

**Example Files:**

- `TradeHistory_2024.csv` - Your trade transactions
- `Symbol_Master.csv` - Stock master data
- `Dividend_2024.xlsx` - Dividend records

### BRONZE Layer

**Purpose**: Data harmonization and standardization

**Process:**

- Column name normalization
- Data type conversion
- Basic validation
- Duplicate removal

**Output**: Standardized CSV files

**Example Transformation:**

```
Before (SOURCE):
"Stock Name", "Qty", "Price"
"RELIANCE", "100", "2500.50"

After (BRONZE):
"scrip_name", "quantity", "price"
"RELIANCE", 100, 2500.50
```

### SILVER Layer

**Purpose**: Data cleansing and enrichment

**Process:**

- Data quality checks
- Missing value handling
- Reference data enrichment
- Business rule application

**Output**: Cleansed and enriched CSV files

**Features:**

- Stock price history
- Corporate actions (splits, bonuses)
- Symbol standardization
- Trade validation

### GOLD Layer

**Purpose**: Business-ready analytics

**Process:**

- Portfolio calculations
- P&L computation
- Aggregations
- Metrics calculation

**Output**: Analytics-ready CSV files

**Reports Generated:**

- Current holdings with unrealized P&L
- Closed positions with realized P&L
- Portfolio trends over time
- Dividend summary

### API Layer

**Purpose**: Frontend-ready JSON endpoints

**Process:**

- User-specific data segregation
- JSON formatting
- API structure creation

**Output**: JSON files per user

**API Endpoints:**

```json
DATA/API/username/
├── current_holding_data.json    # Current positions
├── holding_trands_data.json     # Portfolio trends
├── profit_loss_data.json        # P&L summary
└── dividend_data.json           # Dividend history
```

## 💼 Portfolio Management

### Trade Processing

The portfolio manager uses **FIFO (First In, First Out)** for position matching:

```python
# Example: Buy and Sell matching
portfolio.trade({
    "side": "BUY",
    "quantity": 100,
    "price": 2500
})

portfolio.trade({
    "side": "SELL",
    "quantity": 50,
    "price": 2600
})
# Automatically matches and calculates P&L
```

### Brokerage Calculation

Accurate brokerage calculation including:

- **Brokerage Charges**: Exchange-specific rates
- **STT/CTT**: Securities Transaction Tax
- **Stamp Duty**: State stamp duty
- **Exchange Charges**: NSE/BSE transaction charges
- **SEBI Charges**: Regulatory charges
- **GST**: 18% on applicable charges

### Supported Instruments

- **Equities (EQ)**: Delivery and Intraday
- **Futures (FO)**: Stock and Index futures
- **Options (FO)**: Call and Put options
- **Commodities**: MCX instruments (planned)

## 🧪 Development

### Code Quality Standards

The codebase follows industry best practices:

✅ **PEP 8 Compliance**: Python style guide
✅ **Type Hints**: Full type annotations
✅ **Docstrings**: Comprehensive documentation
✅ **Error Handling**: Proper exception handling
✅ **Logging**: Structured logging throughout
✅ **Modularity**: Clear separation of concerns

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=StockETL --cov-report=html

# Run specific tests
pytest tests/test_portfolio.py
```

### Code Formatting

```bash
# Format code with Black
black StockETL/

# Sort imports with isort
isort StockETL/

# Check with flake8
flake8 StockETL/
```

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev,testing]"

# Setup pre-commit hooks
pre-commit install

# Run pre-commit checks
pre-commit run --all-files
```

## 📝 Logging

Portfolio Tracker uses comprehensive structured logging:

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

### Log Configuration

Configure via environment variables or CLI:

```bash
# Set log level
export LOG_LEVEL=DEBUG


# Or use CLI
python -m StockETL --log-level DEBUG --log-file DATA/logs/debug.log
```

### Log Output

Logs are written to:

- **Console**: Real-time feedback
- **File**: Persistent logging with rotation

Example log entry:

```
2024-12-29 10:30:45 - StockETL.ETL_BRONZE.Symbol - INFO - Processing file: Symbol_Master.csv
2024-12-29 10:30:46 - StockETL.ETL_BRONZE.Symbol - DEBUG - Processed 1250 rows
2024-12-29 10:30:46 - StockETL.ETL_BRONZE.Symbol - INFO - ✓ Symbol processing complete
```

## 📚 API Documentation

### Output Format

All API endpoints return JSON in this format:

```json
{
  "data": [...],
  "load_timestamp": "2024-12-29 10:30:45"
}
```

### Current Holdings API

**File**: `DATA/API/{username}/current_holding_data.json`

```json
{
  "data": [
    {
      "symbol": "RELIANCE",
      "scrip_name": "Reliance Industries",
      "quantity": 50,
      "price": 2500.50,
      "amount": 125025.00,
      "close_price": 2600.00,
      "close_amount": 130000.00,
      "pnl_amount": 4975.00,
      "side": "BUY",
      "datetime": "2024-01-15 10:30:00"
    }
  ],
  "load_timestamp": "2024-12-29 10:30:45"
}
```

### P&L API

**File**: `DATA/API/{username}/profit_loss_data.json`

```json
{
  "data": [
    {
      "symbol": "RELIANCE",
      "quantity": 50,
      "open_price": 2500.50,
      "close_price": 2600.00,
      "pnl_amount": 4975.00,
      "pnl_percentage": 3.98,
      "brokerage": 125.50,
      "position": "LONG",
      "open_datetime": "2024-01-15 10:30:00",
      "close_datetime": "2024-01-20 14:00:00"
    }
  ],
  "load_timestamp": "2024-12-29 10:30:45"
}
```

### Holding Trends API

**File**: `DATA/API/{username}/holding_trands_data.json`

```json
{
  "data": [
    {
      "date": "2024-01-15",
      "open": 125025.00,
      "high": 130000.00,
      "low": 123000.00,
      "close": 127500.00,
      "holding": 127500.00
    }
  ],
  "load_timestamp": "2024-12-29 10:30:45"
}
```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** if applicable
5. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation as needed

## 🗺️ Roadmap

### Version 1.0 (Q1 2025)

- [x] Multi-layer ETL architecture
- [x] Portfolio management
- [x] P&L calculation
- [x] Comprehensive logging
- [x] CLI interface
- [ ] Unit test coverage > 80%
- [ ] Integration tests

### Version 1.1 (Q2 2025)

- [ ] Real-time data ingestion
- [ ] WebSocket support
- [ ] Advanced analytics
- [ ] Performance optimizations
- [ ] Docker containerization

### Version 2.0 (Q3 2025)

- [ ] RESTful API server with FastAPI
- [ ] Web dashboard (React/Vue)
- [ ] Mobile app
- [ ] Multi-exchange support (BSE, MCX)
- [ ] Cloud deployment (AWS/GCP)

### Future

- [ ] Machine learning predictions
- [ ] Risk analysis tools
- [ ] Alert notifications
- [ ] Social trading features
- [ ] Tax optimization suggestions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2023-2025 Pt. Prashant Tripathi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 👤 Author

**Pt. Prashant Tripathi**

- 📧 Email: <ptprashanttripathi@outlook.com>
- 🐙 GitHub: [@PtPrashantTripathi](https://github.com/PtPrashantTripathi)
- 🔗 LinkedIn: [Pt. Prashant Tripathi](https://linkedin.com/in/ptprashanttripathi)
- 🌐 Website: [ptprashanttripathi.github.io](https://ptprashanttripathi.github.io)

## 🙏 Acknowledgments

- Thanks to all contributors and the open-source community
- Inspired by modern data engineering practices and Medallion architecture
- Built with ❤️ for the Indian stock market trading community
- Special thanks to Databricks for the Medallion architecture pattern

## 📞 Support

### Get Help

- 📖 **Documentation**: Check [QUICKSTART.md](QUICKSTART.md) and this README
- 🐛 **Issues**: [GitHub Issues](https://github.com/PtPrashantTripathi/PortfolioTracker/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/PtPrashantTripathi/PortfolioTracker/discussions)
- 📧 **Email**: <ptprashanttripathi@outlook.com>

### Community

Join our community to:

- Share trading strategies
- Report bugs and request features
- Contribute to the project
- Learn from other traders

### Reporting Issues

When reporting issues, please include:

1. Clear description of the problem
2. Steps to reproduce
3. Expected vs actual behavior
4. Python version and OS
5. Relevant log files
6. Screenshots if applicable

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/PtPrashantTripathi/PortfolioTracker)
![GitHub forks](https://img.shields.io/github/forks/PtPrashantTripathi/PortfolioTracker)
![GitHub issues](https://img.shields.io/github/issues/PtPrashantTripathi/PortfolioTracker)
![GitHub pull requests](https://img.shields.io/github/issues-pr/PtPrashantTripathi/PortfolioTracker)

## 🏷️ Tags

`#DataAnalytics` `#TradingStrategies` `#MedallionArchitecture` `#ETLProcess` `#UpstoxData` `#DataDrivenDecisions` `#FinanceTech` `#DataInsights` `#Python` `#Trading` `#Portfolio` `#StockMarket` `#NSE` `#BSE` `#FinancialAnalysis`

---

<div align="center">

**Version**: 0.8.12
**Status**: Production Ready
**Last Updated**: December 2025

Made with ❤️ by [Pt. Prashant Tripathi](https://github.com/PtPrashantTripathi)

[⭐ Star this repo](https://github.com/PtPrashantTripathi/PortfolioTracker) if you find it helpful!

</div>
