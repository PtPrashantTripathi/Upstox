"""
Common utility functions for StockETL.

This module provides reusable utility functions for data processing,
file handling, and data contract alignment.
"""

import os
import re
import json
from typing import Any
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

from StockETL.logger import get_logger
from StockETL.constants import ROUNDING_PRECISION, REGEX_ESCAPE_STRING
from StockETL.exceptions import (
    SchemaLoadError,
    DataContractError,
    DataNotFoundError,
    FileProcessingError,
)

logger = get_logger(__name__)


def replace_punctuation_from_string(input_str: Any) -> str:
    """
    Remove punctuation and normalize a string for use as a column name.

    Converts the input to lowercase, removes special characters, and replaces
    whitespace and special characters with underscores.

    Args:
        input_str: The input string to normalize.

    Returns:
        The normalized string suitable for use as a column name.

    Examples:
        >>> replace_punctuation_from_string("Price (USD)")
        'price_usd'
        >>> replace_punctuation_from_string("Stock-Name!")
        'stockname'
    """
    regex_remove_punctuation = re.compile(f"[{re.escape(REGEX_ESCAPE_STRING)}]")
    output_str = (
        regex_remove_punctuation.sub("", str(input_str))
        .strip()
        .replace(" ", "_")
        .replace("\n", "_")
        .replace("\t", "_")
        .replace("\r", "_")
        .lower()
    )
    # Remove consecutive underscores
    while "__" in output_str:
        output_str = output_str.replace("__", "_")
    return output_str.strip("_")


def replace_punctuation_from_columns(df_pandas: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize all column names in a DataFrame.

    Args:
        df_pandas: The DataFrame to process.

    Returns:
        The DataFrame with normalized column names.

    Raises:
        ValueError: If the DataFrame has no columns.
    """
    if df_pandas.empty or len(df_pandas.columns) == 0:
        logger.warning("DataFrame has no columns to process")
        return df_pandas

    new_col_names = [
        replace_punctuation_from_string(col_name) for col_name in df_pandas.columns
    ]
    df_pandas.columns = new_col_names
    logger.debug(f"Normalized {len(new_col_names)} column names")
    return df_pandas


def fix_duplicate_column_names(df_pandas: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all column names in a DataFrame are unique.

    If duplicate column names are found, they are renamed by appending
    an incremental number (e.g., 'column', 'column_1', 'column_2').

    Args:
        df_pandas: The DataFrame to process.

    Returns:
        The DataFrame with unique column names.

    Raises:
        ValueError: If the DataFrame has no columns.
    """
    if df_pandas.empty or len(df_pandas.columns) == 0:
        raise ValueError("DataFrame has no columns to process")

    result = []
    counts = {}

    for column_name in df_pandas.columns:
        normalized_name = replace_punctuation_from_string(str(column_name))

        if normalized_name not in counts:
            counts[normalized_name] = 0
            result.append(normalized_name)
        else:
            counts[normalized_name] += 1
            result.append(f"{normalized_name}_{counts[normalized_name]}")

    df_pandas.columns = result

    duplicates_fixed = sum(1 for count in counts.values() if count > 0)
    if duplicates_fixed > 0:
        logger.info(f"Fixed {duplicates_fixed} duplicate column names")

    return df_pandas


def find_correct_sheetname(
    df_pandas: dict[str, pd.DataFrame], sheet_name_regex: str
) -> pd.DataFrame:
    """
    Find the first sheet that matches the given regular expression pattern.

    Args:
        df_pandas: A dictionary where keys are sheet names and values are DataFrames.
        sheet_name_regex: A regular expression pattern to match sheet names.

    Returns:
        The DataFrame corresponding to the first matching sheet name.

    Raises:
        DataNotFoundError: If no sheet name matches the pattern.
    """
    pattern = re.compile(sheet_name_regex, re.IGNORECASE)

    for sheet_name in df_pandas.keys():
        if pattern.search(sheet_name):
            logger.info(f"Found matching sheet: {sheet_name}")
            return df_pandas[sheet_name]

    available_sheets = ", ".join(df_pandas.keys())
    raise DataNotFoundError(
        f"No sheet matching pattern '{sheet_name_regex}' found",
        details={"available_sheets": available_sheets},
    )


def find_correct_headers(
    df_pandas: pd.DataFrame, global_header_regex: str
) -> pd.DataFrame:
    """
    Find and extract data with the correct header row.

    Searches through the DataFrame to find a row that matches the header pattern,
    then uses that row as column names and returns the data below it.

    Args:
        df_pandas: The DataFrame to search.
        global_header_regex: A regex pattern to match against potential header values.

    Returns:
        The DataFrame with correctly identified headers and data.

    Raises:
        DataNotFoundError: If no matching header is found.
    """
    if not global_header_regex:
        raise ValueError("Header regex pattern cannot be empty")

    pattern = re.compile(global_header_regex, re.IGNORECASE)

    for header_row_index, row in df_pandas.iterrows():
        for cell_value in row.values:
            normalized_value = replace_punctuation_from_string(str(cell_value))
            if pattern.match(normalized_value):
                logger.info(f"Found header at row {header_row_index}")
                df = df_pandas.iloc[header_row_index + 1 :].copy()
                df.columns = df_pandas.iloc[header_row_index]
                return df

    raise DataNotFoundError(
        f"No header matching pattern '{global_header_regex}' found in DataFrame"
    )


def check_files_availability(
    dir_path: str | Path,
    file_pattern: str = "*",
    timestamp: datetime = datetime.strptime("2000-01-01", "%Y-%m-%d"),
) -> list[Path]:
    """
    Check for newly added or modified files in a directory after a specific timestamp.

    Args:
        dir_path: The directory to check for files.
        file_pattern: The glob pattern to filter files (default: "*" for all files).
        timestamp: The timestamp to compare file modification times against.

    Returns:
        A list of paths to files that were added or modified after the given timestamp.

    Raises:
        FileProcessingError: If the directory doesn't exist or no files are found.
    """
    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileProcessingError(
            f"Directory does not exist: {dir_path}",
            details={"dir_path": str(dir_path)},
        )

    if not dir_path.is_dir():
        raise FileProcessingError(
            f"Path is not a directory: {dir_path}",
            details={"dir_path": str(dir_path)},
        )

    file_paths = []

    for file_path in dir_path.rglob(file_pattern):
        if file_path.is_file():
            try:
                file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_modified_time > timestamp:
                    file_paths.append(file_path)
            except OSError as e:
                logger.warning(f"Failed to get modification time for {file_path}: {e}")
                continue

    if not file_paths:
        raise DataNotFoundError(
            f"No files matching pattern '{file_pattern}' found after {timestamp}",
            details={
                "directory": str(dir_path),
                "pattern": file_pattern,
                "timestamp": str(timestamp),
            },
        )

    logger.info(f"Found {len(file_paths)} file(s) matching pattern '{file_pattern}'")
    return file_paths


def align_with_datacontract(
    df: pd.DataFrame,
    data_contract_path: Path,
    rounding: bool = True,
) -> pd.DataFrame:
    """
    Align a DataFrame with a DataContract specified in a JSON schema file.

    This function:
    - Casts DataFrame columns to the data types specified in the schema
    - Creates missing columns with the correct data type
    - Arranges columns in the order specified by the schema
    - Optionally rounds numerical values

    Args:
        df: The input DataFrame to align.
        data_contract_path: Path to the JSON file containing DataContract information.
        rounding: Whether to round numerical values to 2 decimal places (default: True).

    Returns:
        The DataFrame aligned with the DataContract.

    Raises:
        SchemaLoadError: If the schema file cannot be loaded.
        DataContractError: If the schema is invalid or missing required fields.
    """
    try:
        with open(data_contract_path, encoding="utf-8") as schema_file:
            datacontract = json.load(schema_file)
            logger.debug(f"Loaded DataContract from: {data_contract_path}")
    except FileNotFoundError:
        raise SchemaLoadError(
            f"Schema file not found: {data_contract_path}",
            details={"path": str(data_contract_path)},
        )
    except json.JSONDecodeError as e:
        raise SchemaLoadError(
            f"Invalid JSON in schema file: {data_contract_path}",
            details={"error": str(e)},
        )

    # Extract schema definitions and column order from the JSON
    data_schema = datacontract.get("data_schema", [])
    order_by = datacontract.get("order_by", [])

    if not data_schema:
        raise DataContractError(
            "DataContract contains no schema definitions",
            details={"path": str(data_contract_path)},
        )

    # Iterate over the schema to align DataFrame columns
    for col_info in data_schema:
        col_name = col_info.get("col_name")
        col_type = col_info.get("data_type")

        if not col_name or not col_type:
            logger.warning(f"Skipping invalid schema entry: {col_info}")
            continue

        if col_name in df.columns:
            try:
                # Cast column to the specified data type
                df[col_name] = df[col_name].astype(col_type)
                if col_type == "string":
                    df[col_name] = df[col_name].str.strip()
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Failed to cast column '{col_name}' to type '{col_type}': {e}"
                )
        else:
            # Create missing column with NaN values and specified data type
            df[col_name] = pd.Series([None] * len(df), dtype=col_type)
            logger.debug(f"Created missing column: {col_name}")

    # Ensure only columns specified by the schema are included
    all_columns = [each["col_name"] for each in data_schema]
    df = df[all_columns]

    # Reorder DataFrame according to the order specified by the schema
    if order_by:
        order_by = list(dict.fromkeys(order_by + all_columns))
        try:
            df = df.sort_values(by=order_by).reset_index(drop=True)
        except KeyError as e:
            logger.warning(f"Some order_by columns not found in DataFrame: {e}")

    # Round numerical values to specified precision
    if rounding:
        df = df.round(ROUNDING_PRECISION)

    logger.info(f"Aligned DataFrame with {len(all_columns)} columns")
    return df


def get_correct_datatype(input_datatype: str) -> str:
    """
    Map a data type string to a standardized data type.

    Args:
        input_datatype: The input data type string to map.

    Returns:
        The standardized data type string.

    Note:
        Supported data types:
        - Date: Store Date Only
        - string: String or character
        - Long: 8-byte signed integer (-9223372036854775808 to 9223372036854775807)
        - Timestamp: Date and time in ISO format
        - Double: 8-byte double-precision floating point
        - Boolean: True or False
    """
    input_datatype = str(input_datatype).lower().strip()

    datatypes_map = {
        "Date": ["date"],
        "string": ["string", "varchar", "char", "text", "object"],
        "Long": ["bigint", "int", "tinyint", "long"],
        "Timestamp": ["timestamp", "datetime"],
        "Double": ["double", "float", "decimal"],
        "Boolean": ["bool", "boolean"],
    }

    for standard_type, type_variants in datatypes_map.items():
        if input_datatype in type_variants:
            return standard_type

    logger.warning(f"Unknown data type '{input_datatype}', using as-is")
    return input_datatype


def create_data_contract(df: pd.DataFrame, schema_path: str | Path) -> None:
    """
    Create a DataContract JSON schema from a DataFrame's column structure.

    Args:
        df: The DataFrame to create a schema from.
        schema_path: The path where the schema JSON file will be saved.

    Raises:
        FileProcessingError: If the schema file cannot be written.
    """
    data_schema = [
        {
            "col_name": col,
            "data_type": str(dtype),
        }
        for col, dtype in df.dtypes.to_dict().items()
    ]

    schema_dict = {"data_schema": data_schema}

    try:
        with open(schema_path, "w", encoding="utf-8") as json_file:
            json.dump(schema_dict, json_file, indent=4)
        logger.info(f"DataContract schema written to: {schema_path}")
    except OSError as e:
        raise FileProcessingError(
            f"Failed to write schema file: {schema_path}",
            details={"error": str(e)},
        )


def replace_nan_with_empty(data: Any) -> Any:
    """
    Recursively replace NaN values with empty strings in nested data structures.

    This function handles dictionaries, lists, and float NaN values,
    replacing NaN with empty strings for JSON serialization compatibility.

    Args:
        data: The data structure to process (dict, list, or primitive type).

    Returns:
        The data structure with NaN values replaced by empty strings.
    """
    if isinstance(data, dict):
        return {key: replace_nan_with_empty(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_nan_with_empty(item) for item in data]
    elif isinstance(data, float) and np.isnan(data):
        return ""
    return data


class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles objects with __dict__ attribute.

    This encoder attempts to serialize objects by:
    1. Converting objects with __dict__ to dictionaries
    2. Using the default JSON encoder
    3. Converting to string as a fallback
    """

    def default(self, obj: Any) -> Any:
        """Override default encoding behavior."""
        try:
            return obj.__dict__
        except AttributeError:
            try:
                return super().default(obj)
            except TypeError:
                return str(obj)


def print_json(obj: Any) -> None:
    """
    Pretty-print an object as JSON.

    Args:
        obj: The object to print as JSON.
    """
    print(json.dumps(obj, cls=CustomEncoder, indent=4))
