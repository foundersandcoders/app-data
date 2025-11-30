#!/usr/bin/env python3
"""
Extract Apprenticeship Starts by Standard for a Specific Provider

This script extracts apprenticeship starts data for a specific provider from the
Department for Education (DfE) apprenticeship data CSV files and presents it as
a table with years as columns and standards as rows.

The most recent year is shown as an annual total if Q4 data is present (indicating the year
is complete). If Q4 is not yet available, the year is broken down into quarterly columns
(Q1, Q2, Q3) to provide more granular insight into current trends. Previous years are always
shown as single annual totals.

Usage:
    python3 provider.py [options] [provider_name] [input_file]

Options:
    --csv, -c       Output in CSV format (suitable for importing into databases)
    --table         Output in table format (console-friendly aligned tables)
    --tsv, -t       Output in tab-separated format (for copy-paste into spreadsheets)
    --help, -h      Show this help message

Arguments:
    provider_name   Provider name to filter. Defaults to "FOUNDERS & CODERS"
    input_file      Path to CSV file. If not specified, automatically finds the most recent file

Output:
    Default: Markdown table format for copy-paste into Notion inline tables
    Shows all standards with 3+ total starts in the most recent year, with others grouped as "All other standards"
    Includes a total row showing all starts across all standards by year
    Most recent year shows quarterly breakdown only if Q4 is not yet available (2024-25 Q1, 2024-25 Q2, etc.)

Examples:
    python3 provider.py                                 # FOUNDERS & CODERS, latest file
    python3 provider.py "QA"                            # QA, latest file
    python3 provider.py "MAKERS ACADEMY" data.csv       # MAKERS ACADEMY, specific file
    python3 provider.py --csv "MULTIVERSE GROUP"        # MULTIVERSE GROUP, CSV format
"""

import sys
from typing import List, Dict, Any

from utils import (
    clean_provider_name,
    parse_positions,
    find_latest_file,
    extract_from_zip_if_needed,
    format_academic_year,
    TableFormatter,
    read_csv_data
)
from config import (
    STARTS_FILE_PATTERN,
    STARTS_ZIP_PATTERN,
    STARTS_MIN_THRESHOLD,
    FIELD_ST_CODE,
    FIELD_PROVIDER_NAME,
    FIELD_YEAR,
    FIELD_STARTS,
    FIELD_START_QUARTER,
    FIELD_STD_FWK_NAME,
    CONSOLE_YEAR_COLUMN_WIDTH
)

# Default provider
DEFAULT_PROVIDER = 'FOUNDERS & CODERS'
CONSOLE_STANDARD_COLUMN_WIDTH = 40


def extract_provider_starts(csv_file_path: str, provider_name: str = DEFAULT_PROVIDER) -> List[Dict[str, Any]]:
    """
    Extract apprenticeship starts data for a specific provider.

    Args:
        csv_file_path: Path to the CSV file containing starts data
        provider_name: The provider name to filter for (e.g., 'FOUNDERS & CODERS')

    Returns:
        List of dictionaries containing filtered starts data

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file has invalid format
    """
    # Clean the target provider name for comparison
    target_provider_clean = clean_provider_name(provider_name)

    def filter_by_provider(row: Dict[str, str]) -> bool:
        """Filter for specific provider."""
        provider = row.get(FIELD_PROVIDER_NAME, '').strip()
        provider_clean = clean_provider_name(provider)
        return provider_clean == target_provider_clean

    raw_data = read_csv_data(csv_file_path, filter_by_provider)

    # Transform to required format
    starts_data = []
    for row in raw_data:
        quarter_str = row.get(FIELD_START_QUARTER, '').strip()
        quarter = parse_positions(quarter_str, default=0) if quarter_str else 0

        starts_data.append({
            'standard_code': row.get(FIELD_ST_CODE, '').strip(),
            'standard_name': row.get(FIELD_STD_FWK_NAME, '').strip(),
            'year': row.get(FIELD_YEAR, '').strip(),
            'quarter': quarter,
            'starts': parse_positions(row.get(FIELD_STARTS, '').strip(), default=0),
            'provider': row.get(FIELD_PROVIDER_NAME, '').strip()
        })

    return starts_data


def aggregate_starts_by_standard_year(starts_data: List[Dict[str, Any]],
                                      most_recent_year: str = None) -> Dict[str, Dict[str, int]]:
    """
    Aggregate starts data by standard and year, with optional quarterly breakdown for most recent year.

    Args:
        starts_data: List of starts data dictionaries
        most_recent_year: The most recent academic year (e.g., '2024-25').
                          If specified, this year will be broken down by quarters.
                          If None, all years including the most recent will be shown as annual totals.

    Returns:
        Dictionary with standard codes as keys and year/quarter->starts dictionaries as values.
        If most_recent_year is specified, keys for that year will be like '2024-25 Q1', '2024-25 Q2', etc.
        For other years (or all years if most_recent_year is None), keys will be just the year like '2023-24'.
    """
    aggregated = {}

    for record in starts_data:
        standard_key = f"{record['standard_code']} {record['standard_name']}"
        year = record['year']
        quarter = record['quarter']
        starts = record['starts']

        if standard_key not in aggregated:
            aggregated[standard_key] = {}

        # For the most recent year, create quarterly keys
        if most_recent_year and year == most_recent_year and quarter > 0:
            year_key = f"{year} Q{quarter}"
        else:
            year_key = year

        if year_key not in aggregated[standard_key]:
            aggregated[standard_key][year_key] = 0

        aggregated[standard_key][year_key] += starts

    return aggregated


def prepare_provider_table_data(starts_data: List[Dict[str, Any]],
                                 min_starts: int = STARTS_MIN_THRESHOLD) -> tuple:
    """
    Prepare data for provider table formatting with conditional quarterly breakdown for most recent year.

    The most recent year is shown as an annual total if Q4 is present (indicating the year is complete).
    If Q4 is not yet available, the year is broken down by quarters.

    Args:
        starts_data: List of starts data dictionaries
        min_starts: Minimum starts in most recent year to show standard separately (not used, kept for compatibility)

    Returns:
        Tuple of (headers, rows, title)
    """
    if not starts_data:
        return (['Standard', 'No data available'], [], 'Unknown Provider')

    provider_name = starts_data[0].get('provider', 'Unknown Provider')
    title = f"{provider_name} starts"

    # First, identify the most recent year (without quarters)
    all_base_years = set(record['year'] for record in starts_data)
    sorted_base_years = sorted(all_base_years)

    if not sorted_base_years:
        return (['Standard', 'No data available'], [], title)

    most_recent_year = sorted_base_years[-1]

    # Check if Q4 is present for the most recent year (indicating the year is complete)
    quarters_in_recent_year = set(
        record['quarter'] for record in starts_data
        if record['year'] == most_recent_year and record['quarter'] > 0
    )
    has_q4 = 4 in quarters_in_recent_year

    # Only do quarterly breakdown if Q4 is not present
    year_for_quarterly_breakdown = None if has_q4 else most_recent_year

    # Aggregate data by standard and year, with quarterly breakdown for most recent year (if not complete)
    aggregated = aggregate_starts_by_standard_year(starts_data, year_for_quarterly_breakdown)

    # Get all year/quarter keys and sort them
    all_year_keys = set()
    for standard_data in aggregated.values():
        all_year_keys.update(standard_data.keys())

    # Sort year keys: regular years first, then quarterly keys
    def sort_key(year_key: str) -> tuple:
        if ' Q' in year_key:
            # Quarterly key like "2024-25 Q1"
            year_part, q_part = year_key.split(' Q')
            return (year_part, int(q_part))
        else:
            # Regular year like "2023-24"
            return (year_key, 0)

    year_keys = sorted(all_year_keys, key=sort_key)

    if not year_keys:
        return (['Standard', 'No data available'], [], title)

    # Identify quarterly keys for most recent year
    quarterly_keys = [key for key in year_keys if key.startswith(most_recent_year) and ' Q' in key]

    # Build final year_keys list with total column before quarterly breakdown (only if we have quarters)
    if quarterly_keys:
        final_year_keys = []
        for key in year_keys:
            # Add non-quarterly keys as they are
            if ' Q' not in key:
                final_year_keys.append(key)
            # For the first quarterly key, add the total column before it
            elif key == quarterly_keys[0]:
                final_year_keys.append(most_recent_year)  # Total column
                final_year_keys.append(key)
            else:
                final_year_keys.append(key)
        year_keys = final_year_keys
    # If no quarterly breakdown, year_keys is already correct

    # Get all standards and sort by most recent year total starts (descending)
    all_standards = []
    for standard, year_data in aggregated.items():
        # Sum all quarterly starts for most recent year (or just the year total if no quarters)
        if quarterly_keys:
            recent_starts = sum(
                starts for key, starts in year_data.items()
                if key.startswith(most_recent_year)
            )
        else:
            recent_starts = year_data.get(most_recent_year, 0)
        all_standards.append((standard, year_data, recent_starts))

    # Sort all standards by most recent year total starts (descending)
    all_standards.sort(key=lambda x: x[2], reverse=True)

    # Calculate totals for each year/quarter key
    year_totals = {}
    for year_key in year_keys:
        if quarterly_keys and year_key == most_recent_year:
            # For the total column, sum all quarterly data
            year_totals[year_key] = sum(
                standard_data.get(q_key, 0)
                for q_key in quarterly_keys
                for _, standard_data, _ in all_standards
            )
        else:
            year_totals[year_key] = sum(
                standard_data.get(year_key, 0)
                for _, standard_data, _ in all_standards
            )

    # Build table data
    headers = ['Standard'] + [format_academic_year(year_key.split(' Q')[0]) + (f" Q{year_key.split(' Q')[1]}" if ' Q' in year_key else '')
                              for year_key in year_keys]
    rows = []

    # Total row
    total_row = ['**Total**'] + [f"**{year_totals.get(year_key, 0)}**" for year_key in year_keys]
    rows.append(total_row)

    # All standards (itemized individually)
    for standard, year_data, _ in all_standards:
        row_values = []
        for year_key in year_keys:
            if quarterly_keys and year_key == most_recent_year:
                # For the total column, sum all quarterly data for this standard
                total_value = sum(year_data.get(q_key, 0) for q_key in quarterly_keys)
                row_values.append(total_value)
            else:
                row_values.append(year_data.get(year_key, 0))
        row = [standard] + row_values
        rows.append(row)

    return (headers, rows, title)


def format_provider_markdown(starts_data: List[Dict[str, Any]], min_starts: int = STARTS_MIN_THRESHOLD) -> str:
    """
    Format provider data as a markdown table with years as columns and standards as rows.

    Args:
        starts_data: List of starts data dictionaries
        min_starts: Minimum starts in most recent year to show standard separately

    Returns:
        Markdown table formatted string with header
    """
    if not starts_data:
        return "No apprenticeship starts data found for the specified provider."

    headers, rows, title = prepare_provider_table_data(starts_data, min_starts)

    output_lines = []
    output_lines.append(f"# {title}")
    output_lines.append("")
    output_lines.append(TableFormatter.to_markdown(headers, rows))

    return '\n'.join(output_lines)


def format_provider_csv(starts_data: List[Dict[str, Any]], min_starts: int = STARTS_MIN_THRESHOLD) -> str:
    """
    Format provider data as CSV.

    Args:
        starts_data: List of starts data dictionaries
        min_starts: Minimum starts in most recent year to show standard separately

    Returns:
        CSV formatted string
    """
    headers, rows, _ = prepare_provider_table_data(starts_data, min_starts)

    # Remove markdown bold formatting from CSV output
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    return TableFormatter.to_csv(headers, cleaned_rows)


def format_provider_table(starts_data: List[Dict[str, Any]], min_starts: int = STARTS_MIN_THRESHOLD) -> str:
    """
    Format provider data as a console-friendly table.

    Args:
        starts_data: List of starts data dictionaries
        min_starts: Minimum starts in most recent year to show standard separately

    Returns:
        Formatted table string
    """
    if not starts_data:
        return "No apprenticeship starts data found for the specified provider."

    headers, rows, title = prepare_provider_table_data(starts_data, min_starts)

    # Remove markdown formatting for console output
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    output_lines = []
    output_lines.append(title.upper())
    output_lines.append("=" * 80)
    output_lines.append("")

    # Calculate column widths
    column_widths = [CONSOLE_STANDARD_COLUMN_WIDTH]
    for _ in range(len(headers) - 1):
        column_widths.append(CONSOLE_YEAR_COLUMN_WIDTH)

    output_lines.append(TableFormatter.to_console_table(headers, cleaned_rows, column_widths))

    return '\n'.join(output_lines)


def format_provider_tsv(starts_data: List[Dict[str, Any]], min_starts: int = STARTS_MIN_THRESHOLD) -> str:
    """
    Format provider data as TSV.

    Args:
        starts_data: List of starts data dictionaries
        min_starts: Minimum starts in most recent year to show standard separately

    Returns:
        TSV formatted string
    """
    headers, rows, _ = prepare_provider_table_data(starts_data, min_starts)

    # Remove markdown formatting
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    return TableFormatter.to_tsv(headers, cleaned_rows)


def main():
    """Main function to run the provider starts extraction."""
    # Find the most recent starts file
    default_file = find_latest_file(STARTS_FILE_PATTERN)

    # If not found, try extracting from zip
    if not default_file:
        default_file = extract_from_zip_if_needed(STARTS_ZIP_PATTERN)

    if not default_file:
        print("Error: No starts data files found in apprenticeships_* folders")
        print("Please ensure you have downloaded apprenticeship data from the DfE website")
        sys.exit(1)

    # Handle command line arguments
    output_format = 'markdown'  # 'markdown', 'console', 'csv', or 'tsv'
    csv_file_path = default_file
    provider_name = DEFAULT_PROVIDER

    # Parse arguments: [options] [provider_name] [input_file]
    positional_args = []

    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(__doc__)
            return
        elif arg in ['--csv', '-c']:
            output_format = 'csv'
        elif arg in ['--table']:
            output_format = 'console'
        elif arg in ['--tsv', '-t']:
            output_format = 'tsv'
        elif not arg.startswith('-'):
            positional_args.append(arg)

    # First positional arg is provider name, second is file path
    if len(positional_args) >= 1:
        # Check if it looks like a file path
        if positional_args[0].endswith('.csv') or '/' in positional_args[0]:
            csv_file_path = positional_args[0]
        else:
            provider_name = positional_args[0]
            if len(positional_args) >= 2:
                csv_file_path = positional_args[1]

    try:
        if output_format == 'console':
            print(f"Extracting apprenticeship starts for {provider_name} from: {csv_file_path}")
            print()

        # Extract starts data
        starts_data = extract_provider_starts(csv_file_path, provider_name)

        # Display summary
        if output_format == 'console':
            total_records = len(starts_data)
            total_starts = sum(record['starts'] for record in starts_data)
            print(f"Found {total_records} records with {total_starts} total starts for {provider_name}")
            print()

        # Display output in requested format
        if output_format == 'csv':
            csv_output = format_provider_csv(starts_data)
            print(csv_output)
        elif output_format == 'tsv':
            tsv_output = format_provider_tsv(starts_data)
            print(tsv_output)
        elif output_format == 'console':
            table_output = format_provider_table(starts_data)
            print(table_output)
        else:  # markdown
            markdown_output = format_provider_markdown(starts_data)
            print(markdown_output)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure the CSV file exists or provide the correct path.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
