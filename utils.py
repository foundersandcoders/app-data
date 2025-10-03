#!/usr/bin/env python3
"""
Shared utilities for apprenticeship data analysis scripts.

This module provides common functionality used across vacancy and starts
analysis scripts, including name cleaning, parsing, and file discovery.
"""

import csv
import glob
import os
import re
from io import StringIO
from typing import List, Dict, Any, Optional, Callable


def clean_company_name(name: str) -> str:
    """
    Clean company/provider names by removing common legal designations.

    Args:
        name: Original company or provider name

    Returns:
        Cleaned name with legal designations removed

    Examples:
        >>> clean_company_name("Acme Corp LIMITED")
        'Acme Corp'
        >>> clean_company_name("Tech Solutions LTD")
        'Tech Solutions'
    """
    if not name or name.strip() == '':
        return name

    # List of common legal designations to remove
    suffixes_to_remove = [
        'LIMITED', 'LTD', 'LTD.', 'LLP', 'PLC', 'COMPANY', 'CO', 'CO.',
        'CORP', 'CORPORATION', 'INC', 'INCORPORATED', 'LLC', 'L.L.C.',
        'GMBH', 'AG', 'SA', 'SRL', 'BV', 'NV', 'C.I.C.'
    ]

    cleaned_name = name.strip()

    # Remove suffixes (case insensitive)
    for suffix in suffixes_to_remove:
        # Try exact match at end with space
        if cleaned_name.upper().endswith(' ' + suffix):
            cleaned_name = cleaned_name[:-len(' ' + suffix)]
        # Handle cases where there's no space before suffix
        elif cleaned_name.upper().endswith(suffix) and len(cleaned_name) > len(suffix):
            cleaned_name = cleaned_name[:-len(suffix)]

    return cleaned_name.strip()


def clean_provider_name(name: str) -> str:
    """
    Clean provider names by removing UKPRN codes and legal designations.

    Args:
        name: Original provider name (may include UKPRN in parentheses)

    Returns:
        Cleaned provider name

    Examples:
        >>> clean_provider_name("Training Provider LTD (12345)")
        'Training Provider'
    """
    if not name or name.strip() == '':
        return name

    cleaned_name = name.strip()

    # Remove UKPRN pattern in parentheses at the end
    ukprn_pattern = r'\s*\(\d+\)$'
    cleaned_name = re.sub(ukprn_pattern, '', cleaned_name)

    # Apply general company name cleaning
    return clean_company_name(cleaned_name)


def parse_positions(positions_value: Any, default: int = 1) -> int:
    """
    Safely parse position/starts count from CSV data.

    Args:
        positions_value: The value to parse (string, int, or other)
        default: Default value if parsing fails

    Returns:
        Integer count of positions, or default if parsing fails

    Examples:
        >>> parse_positions("5")
        5
        >>> parse_positions("")
        1
        >>> parse_positions(None)
        1
    """
    try:
        if positions_value is None:
            return default

        if isinstance(positions_value, int):
            return positions_value

        if isinstance(positions_value, str):
            positions_str = positions_value.strip()
            if positions_str.isdigit():
                return int(positions_str)

        return default
    except (ValueError, AttributeError):
        return default


def format_academic_year(year: str) -> str:
    """
    Format academic year from compact format to readable format.

    Args:
        year: Academic year in format like "202021" or "2020-21"

    Returns:
        Formatted year like "2020-21"

    Examples:
        >>> format_academic_year("202021")
        '2020-21'
        >>> format_academic_year("2020-21")
        '2020-21'
    """
    # Extract digits only
    year_digits = ''.join(filter(str.isdigit, year))

    # Format as YYYY-YY if we have 6 digits
    if len(year_digits) == 6:
        return f"{year_digits[:4]}-{year_digits[4:]}"

    return year


def extract_year_quarter_from_filename(filename: str) -> tuple:
    """
    Extract academic year and quarter from a filename.

    Parses filenames like 'app-underlying-data-vacancies-202425-q2.csv' or
    'app-underlying-data-monthly-starts-202425-mar.csv'.

    Args:
        filename: The filename to parse

    Returns:
        Tuple of (year_start, year_end, quarter_num) where quarter_num is:
        - 1-4 for q1-q4
        - Month number (1-12) for month names
        - 0 if no quarter/month found

    Examples:
        >>> extract_year_quarter_from_filename('app-underlying-data-vacancies-202425-q2.csv')
        (2024, 25, 2)
        >>> extract_year_quarter_from_filename('app-underlying-data-starts-202324-q4.csv')
        (2023, 24, 4)
        >>> extract_year_quarter_from_filename('app-underlying-data-monthly-202425-mar.csv')
        (2024, 25, 3)
    """
    # Extract year pattern like 202425
    year_match = re.search(r'(\d{4})(\d{2})', filename)
    if not year_match:
        return (0, 0, 0)

    year_start = int(year_match.group(1))
    year_end = int(year_match.group(2))

    # Extract quarter (q1, q2, q3, q4)
    quarter_match = re.search(r'-q(\d)', filename, re.IGNORECASE)
    if quarter_match:
        quarter_num = int(quarter_match.group(1))
        return (year_start, year_end, quarter_num)

    # Extract month name and convert to number (for monthly files)
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    for month_name, month_num in month_map.items():
        if month_name in filename.lower():
            return (year_start, year_end, month_num)

    return (year_start, year_end, 0)


def find_latest_file(file_pattern: str, folder_prefix: str = 'apprenticeships',
                     subfolder: str = 'supporting-files') -> Optional[str]:
    """
    Find the most recent data file matching a pattern.

    Searches first in the current directory, then in apprenticeships_YYYY-YY folders,
    returning the most recent match based on academic year and quarter/month.

    Files are sorted by:
    1. Academic year (e.g., 2024-25 is newer than 2023-24)
    2. Quarter/month (e.g., q3 is newer than q2, Nov is newer than Mar)

    Args:
        file_pattern: Glob pattern to match files (e.g., 'app-underlying-data-vacancies-*.csv')
        folder_prefix: Prefix of folders to search (default: 'apprenticeships')
        subfolder: Subdirectory within folders to search (default: 'supporting-files')

    Returns:
        Path to the most recent file, or None if not found

    Examples:
        >>> find_latest_file('app-underlying-data-vacancies-*.csv')
        'apprenticeships_2024-25/supporting-files/app-underlying-data-vacancies-202425-q2.csv'
    """
    all_files = []

    # Check root directory
    root_files = glob.glob(file_pattern)
    all_files.extend(root_files)

    # Check apprenticeships folders
    folders = glob.glob(f'{folder_prefix}_*')
    for folder in folders:
        search_pattern = os.path.join(folder, subfolder, file_pattern)
        files = glob.glob(search_pattern)
        all_files.extend(files)

    if not all_files:
        return None

    # Sort files by (year_start, year_end, quarter) in descending order
    def sort_key(filepath: str) -> tuple:
        filename = os.path.basename(filepath)
        year_start, year_end, quarter = extract_year_quarter_from_filename(filename)
        return (year_start, year_end, quarter)

    all_files.sort(key=sort_key, reverse=True)
    return all_files[0]


def extract_from_zip_if_needed(zip_pattern: str, folder_prefix: str = 'apprenticeships',
                               subfolder: str = 'supporting-files') -> Optional[str]:
    """
    Find and extract CSV from zip file if needed.

    Finds the most recent zip file matching the pattern based on year and quarter,
    then extracts and returns the CSV file within it.

    Args:
        zip_pattern: Glob pattern to match zip files (e.g., 'app-underlying-data-starts-*.zip')
        folder_prefix: Prefix of folders to search (default: 'apprenticeships')
        subfolder: Subdirectory within folders to search (default: 'supporting-files')

    Returns:
        Path to extracted CSV file, or None if not found
    """
    import zipfile

    all_zip_files = []

    # Check all apprenticeships folders
    folders = glob.glob(f'{folder_prefix}_*')
    for folder in folders:
        search_pattern = os.path.join(folder, subfolder, zip_pattern)
        zip_files = glob.glob(search_pattern)
        all_zip_files.extend(zip_files)

    if not all_zip_files:
        return None

    # Sort zip files by (year_start, year_end, quarter) in descending order
    def sort_key(filepath: str) -> tuple:
        filename = os.path.basename(filepath)
        year_start, year_end, quarter = extract_year_quarter_from_filename(filename)
        return (year_start, year_end, quarter)

    all_zip_files.sort(key=sort_key, reverse=True)
    zip_file = all_zip_files[0]

    # Extract the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        if csv_files:
            extract_path = os.path.dirname(zip_file)
            zip_ref.extract(csv_files[0], extract_path)
            return os.path.join(extract_path, csv_files[0])

    return None


class TableFormatter:
    """
    Generic table formatter supporting multiple output formats.

    This class provides a unified interface for generating tables in various
    formats (Markdown, CSV, TSV, console-friendly) from structured data.
    """

    @staticmethod
    def to_csv(headers: List[str], rows: List[List[Any]]) -> str:
        """
        Format data as CSV using Python's csv module.

        Args:
            headers: List of column headers
            rows: List of row data (each row is a list of values)

        Returns:
            CSV formatted string with proper escaping
        """
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()

    @staticmethod
    def to_tsv(headers: List[str], rows: List[List[Any]]) -> str:
        """
        Format data as TSV (tab-separated values).

        Args:
            headers: List of column headers
            rows: List of row data

        Returns:
            TSV formatted string
        """
        output = StringIO()
        writer = csv.writer(output, delimiter='\t')
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()

    @staticmethod
    def to_markdown(headers: List[str], rows: List[List[Any]]) -> str:
        """
        Format data as Markdown table.

        Args:
            headers: List of column headers
            rows: List of row data

        Returns:
            Markdown table formatted string
        """
        lines = []

        # Header row
        header_line = "| " + " | ".join(str(h) for h in headers) + " |"
        lines.append(header_line)

        # Separator row
        separator = "|" + "|".join("-" * (len(str(h)) + 2) for h in headers) + "|"
        lines.append(separator)

        # Data rows
        for row in rows:
            row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
            lines.append(row_line)

        return '\n'.join(lines)

    @staticmethod
    def to_console_table(headers: List[str], rows: List[List[Any]],
                         column_widths: Optional[List[int]] = None) -> str:
        """
        Format data as console-friendly aligned table.

        Args:
            headers: List of column headers
            rows: List of row data
            column_widths: Optional list of column widths (auto-calculated if not provided)

        Returns:
            Console-friendly table string with aligned columns
        """
        # Calculate column widths if not provided
        if column_widths is None:
            column_widths = [len(str(h)) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(column_widths):
                        column_widths[i] = max(column_widths[i], len(str(cell)))

        lines = []

        # Header
        header_parts = []
        for i, header in enumerate(headers):
            width = column_widths[i] if i < len(column_widths) else len(str(header))
            header_parts.append(f"{str(header):<{width}}")
        header_line = " | ".join(header_parts)
        lines.append(header_line)

        # Separator
        separator_parts = []
        for width in column_widths[:len(headers)]:
            separator_parts.append("-" * width)
        separator = "-|-".join(separator_parts)
        lines.append(separator)

        # Data rows
        for row in rows:
            row_parts = []
            for i, cell in enumerate(row):
                width = column_widths[i] if i < len(column_widths) else len(str(cell))
                # Right-align numbers, left-align text
                cell_str = str(cell)
                if cell_str.replace(',', '').replace('.', '').isdigit():
                    row_parts.append(f"{cell_str:>{width}}")
                else:
                    row_parts.append(f"{cell_str:<{width}}")
            row_line = " | ".join(row_parts)
            lines.append(row_line)

        return '\n'.join(lines)


def read_csv_data(csv_file_path: str, filter_fn: Callable[[Dict[str, str]], bool]) -> List[Dict[str, Any]]:
    """
    Read and filter CSV data with proper error handling.

    Args:
        csv_file_path: Path to the CSV file
        filter_fn: Function that returns True for rows to include

    Returns:
        List of dictionaries containing filtered data

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file has invalid format
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    filtered_data = []

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                if filter_fn(row):
                    filtered_data.append(row)

    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Error decoding CSV file: {e}")

    return filtered_data
