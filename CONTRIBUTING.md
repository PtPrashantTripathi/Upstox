# Contributing to StockETL

Thank you for considering contributing to StockETL! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- **Bug Reports**: Found a bug? Please report it!
- **Feature Requests**: Have an idea? We'd love to hear it!
- **Code Contributions**: Want to write code? Great!
- **Documentation**: Help improve our docs
- **Testing**: Write or improve tests

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, package versions
6. **Code Samples**: Minimal code to reproduce the issue
7. **Logs**: Relevant log messages or error traces

## 💡 Suggesting Features

Feature requests should include:

1. **Use Case**: Why do you need this feature?
2. **Proposed Solution**: How would you like it to work?
3. **Alternatives**: Have you considered alternatives?
4. **Additional Context**: Any other relevant information

## 🔧 Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- pip

### Setup Steps

1. **Fork the Repository**

   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/PortfolioTracker.git
   cd PortfolioTracker
   ```

3. **Set Up Development Environment**

   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Install development dependencies
   pip install -e ".[dev,testing]"
   ```

4. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Create a Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Code Standards

### Style Guide

We follow **PEP 8** with some modifications:

- **Line Length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted using isort
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all public APIs

### Code Formatting

We use **Black** for code formatting and **isort** for import sorting:

```bash
# Format code
black StockETL/

# Sort imports
isort StockETL/

# Or use pre-commit (recommended)
pre-commit run --all-files
```

### Type Checking

We use type hints throughout the codebase:

```python
from typing import List, Dict, Optional

def process_data(
    data: List[Dict[str, any]],
    config: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Process data with optional configuration.

    Args:
        data: List of data dictionaries to process.
        config: Optional configuration dictionary.

    Returns:
        Processed DataFrame.
    """
    pass
```

### Documentation

All public functions, classes, and modules must have docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description (one line).

    Longer description if needed. Can span multiple lines
    and include details about the function's behavior.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is invalid.
        FileNotFoundError: When file doesn't exist.

    Examples:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Error Handling

Use custom exceptions from `StockETL.exceptions`:

```python
from StockETL.exceptions import DataValidationError

def validate_data(data: dict) -> None:
    """Validate input data."""
    if "required_field" not in data:
        raise DataValidationError(
            "Missing required field",
            details={"missing_field": "required_field"}
        )
```

### Logging

Use the centralized logger:

```python
from StockETL.logger import get_logger

logger = get_logger(__name__)

def process():
    logger.info("Starting process")
    try:
        # Do work
        logger.debug("Intermediate step completed")
    except Exception as e:
        logger.error(f"Process failed: {e}", exc_info=True)
        raise
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=StockETL --cov-report=html

# Run specific test file
pytest tests/test_portfolio.py

# Run specific test
pytest tests/test_portfolio.py::test_trade_execution
```

### Writing Tests

```python
import pytest
from StockETL.portfolio import Portfolio

def test_portfolio_creation():
    """Test that a portfolio can be created."""
    portfolio = Portfolio()
    assert isinstance(portfolio, Portfolio)
    assert len(portfolio.userdata) == 0

def test_trade_execution():
    """Test that trades are executed correctly."""
    portfolio = Portfolio()
    trade_data = {
        "username": "test_user",
        "scrip_name": "TEST",
        # ... other fields
    }
    portfolio.trade(trade_data)
    assert "test_user" in portfolio.userdata

def test_invalid_trade_raises_error():
    """Test that invalid trades raise appropriate errors."""
    portfolio = Portfolio()
    with pytest.raises(ValueError):
        portfolio.trade({})  # Missing required fields
```

## 📦 Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update CHANGELOG.md

2. **Add Tests**
   - Write tests for new functionality
   - Ensure all tests pass
   - Aim for >80% code coverage

3. **Run Quality Checks**

   ```bash
   # Format code
   black StockETL/
   isort StockETL/

   # Run tests
   pytest

   # Check types (optional)
   mypy StockETL/
   ```

4. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test changes
   - `chore:` Maintenance tasks

5. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Request review

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

## 🎯 Priority Areas

We especially welcome contributions in these areas:

1. **Testing**: Improve test coverage
2. **Documentation**: Enhance documentation and examples
3. **Performance**: Optimize data processing
4. **Error Handling**: Improve error messages
5. **New Features**: Add support for new exchanges/instruments

## 💬 Community

- **Issues**: [GitHub Issues](https://github.com/PtPrashantTripathi/PortfolioTracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PtPrashantTripathi/PortfolioTracker/discussions)
- **Email**: <ptprashanttripathi@outlook.com>

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Your contributions make this project better for everyone. Thank you for being part of the community!

---

**Questions?** Don't hesitate to ask! Open an issue or reach out via email.
