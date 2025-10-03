#!/usr/bin/env python3
"""
Extract Monthly Apprenticeship Starts by Year

This script extracts monthly apprenticeship starts data for a specific standard from the
Department for Education (DfE) apprenticeship data CSV files and presents it as
a table with years as columns and months as rows.

Usage:
    python3 monthly.py [options] [standard_code] [input_file]

Options:
    --csv, -c       Output in CSV format (suitable for importing into databases)
    --table         Output in table format (console-friendly aligned tables)
    --tsv, -t       Output in tab-separated format (for copy-paste into spreadsheets)
    --help, -h      Show this help message

Arguments:
    standard_code   Standard code to filter (e.g., ST0116). Defaults to ST0116 (Software Developer)
    input_file      Path to CSV file. If not specified, automatically finds the most recent file

Output:
    Default: Markdown table format for copy-paste into Notion inline tables
    Shows monthly starts with years as columns and months as rows (Aug-Jul academic year order)

Examples:
    python3 monthly.py                      # ST0116, latest file
    python3 monthly.py ST0113               # ST0113, latest file
    python3 monthly.py ST0116 data.csv      # ST0116, specific file
    python3 monthly.py --table ST0113       # ST0113, table format
"""

import sys
from typing import List, Dict, Any

from utils import (
    parse_positions,
    find_latest_file,
    format_academic_year,
    TableFormatter,
    read_csv_data
)
from config import (
    MONTHLY_STARTS_FILE_PATTERN,
    DEFAULT_STANDARD_CODE,
    ACADEMIC_MONTH_ORDER,
    FIELD_ST_CODE,
    FIELD_YEAR,
    FIELD_STARTS,
    FIELD_START_MONTH,
    FIELD_STD_FWK_NAME,
    CONSOLE_MONTH_COLUMN_WIDTH,
    CONSOLE_YEAR_COLUMN_WIDTH
)


def extract_monthly_starts(csv_file_path: str, standard_code: str = DEFAULT_STANDARD_CODE) -> List[Dict[str, Any]]:
    """
    Extract monthly apprenticeship starts data for a specific standard.

    Args:
        csv_file_path: Path to the CSV file containing monthly starts data
        standard_code: The standard code to filter for (e.g., 'ST0116')

    Returns:
        List of dictionaries containing filtered monthly starts data

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file has invalid format
    """
    def filter_by_standard(row: Dict[str, str]) -> bool:
        """Filter for specific standard code."""
        st_code = row.get(FIELD_ST_CODE, '').strip()
        return st_code == standard_code

    raw_data = read_csv_data(csv_file_path, filter_by_standard)

    # Transform to required format
    monthly_data = []
    for row in raw_data:
        monthly_data.append({
            'year': row.get(FIELD_YEAR, '').strip(),
            'start_month': row.get(FIELD_START_MONTH, '').strip(),
            'starts': parse_positions(row.get(FIELD_STARTS, '').strip(), default=0),
            'standard_code': row.get(FIELD_ST_CODE, '').strip(),
            'standard_name': row.get(FIELD_STD_FWK_NAME, '').strip()
        })

    return monthly_data


def aggregate_monthly_data(monthly_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Aggregate monthly starts data by year and month.

    Args:
        monthly_data: List of monthly data dictionaries

    Returns:
        Dictionary with years as keys and month->starts dictionaries as values
    """
    aggregated = {}

    for record in monthly_data:
        year = record['year']
        # Extract month name from start_month (e.g., "01 Aug" or "01-Aug" -> "Aug")
        start_month = record['start_month']
        if start_month:
            # Handle both "01 Aug" and "01-Aug" formats
            month_name = start_month.replace('-', ' ').split()[-1]
        else:
            month_name = 'Unknown'
        starts = record['starts']

        if year not in aggregated:
            aggregated[year] = {}

        if month_name not in aggregated[year]:
            aggregated[year][month_name] = 0

        aggregated[year][month_name] += starts

    return aggregated


def prepare_monthly_table_data(monthly_data: List[Dict[str, Any]]) -> tuple:
    """
    Prepare data for monthly table formatting.

    Args:
        monthly_data: List of monthly data dictionaries

    Returns:
        Tuple of (headers, rows, standard_name)
    """
    if not monthly_data:
        return (['Month', 'No data available'], [], 'Unknown Standard')

    standard_code = monthly_data[0].get('standard_code', 'ST0000')
    standard_name = monthly_data[0].get('standard_name', 'Unknown Standard')
    title = f"{standard_code} {standard_name} monthly starts"

    # Aggregate data by year and month
    aggregated = aggregate_monthly_data(monthly_data)

    # Get all years and sort them
    years = sorted(aggregated.keys())

    if not years:
        return (['Month', 'No data available'], [], title)

    # Build table data
    headers = ['Month'] + [format_academic_year(year) for year in years]
    rows = []

    # Month rows in academic year order (Aug-Jul)
    for month in ACADEMIC_MONTH_ORDER:
        row = [month] + [aggregated[year].get(month, 0) for year in years]
        rows.append(row)

    # Calculate totals row
    total_row = ['**Total**'] + [f"**{sum(aggregated[year].values())}**" for year in years]
    rows.append(total_row)

    return (headers, rows, title)


def format_monthly_markdown(monthly_data: List[Dict[str, Any]]) -> str:
    """
    Format monthly data as a markdown table with years as columns and months as rows.

    Args:
        monthly_data: List of monthly data dictionaries

    Returns:
        Markdown table formatted string with header
    """
    if not monthly_data:
        return "No monthly apprenticeship starts data found for the specified standard."

    headers, rows, title = prepare_monthly_table_data(monthly_data)

    output_lines = []
    output_lines.append(f"# {title}")
    output_lines.append("")
    output_lines.append(TableFormatter.to_markdown(headers, rows))

    return '\n'.join(output_lines)


def format_monthly_csv(monthly_data: List[Dict[str, Any]]) -> str:
    """
    Format monthly data as CSV.

    Args:
        monthly_data: List of monthly data dictionaries

    Returns:
        CSV formatted string
    """
    headers, rows, _ = prepare_monthly_table_data(monthly_data)

    # Remove markdown formatting
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    return TableFormatter.to_csv(headers, cleaned_rows)


def format_monthly_table(monthly_data: List[Dict[str, Any]]) -> str:
    """
    Format monthly data as a console-friendly table.

    Args:
        monthly_data: List of monthly data dictionaries

    Returns:
        Formatted table string
    """
    if not monthly_data:
        return "No monthly apprenticeship starts data found for the specified standard."

    headers, rows, title = prepare_monthly_table_data(monthly_data)

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
    column_widths = [CONSOLE_MONTH_COLUMN_WIDTH]
    for _ in range(len(headers) - 1):
        column_widths.append(CONSOLE_YEAR_COLUMN_WIDTH)

    output_lines.append(TableFormatter.to_console_table(headers, cleaned_rows, column_widths))

    return '\n'.join(output_lines)


def format_monthly_tsv(monthly_data: List[Dict[str, Any]]) -> str:
    """
    Format monthly data as TSV.

    Args:
        monthly_data: List of monthly data dictionaries

    Returns:
        TSV formatted string
    """
    headers, rows, _ = prepare_monthly_table_data(monthly_data)

    # Remove markdown formatting
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    return TableFormatter.to_tsv(headers, cleaned_rows)


def main():
    """Main function to run the monthly starts extraction."""
    # Find the most recent monthly starts file
    default_file = find_latest_file(MONTHLY_STARTS_FILE_PATTERN)

    if not default_file:
        print("Error: No monthly starts data files found in apprenticeships_* folders")
        print("Please ensure you have downloaded apprenticeship data from the DfE website")
        sys.exit(1)

    # Handle command line arguments
    output_format = 'markdown'  # 'markdown', 'console', 'csv', or 'tsv'
    csv_file_path = default_file
    standard_code = DEFAULT_STANDARD_CODE

    # Parse arguments: [options] [standard_code] [input_file]
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

    # First positional arg is standard code, second is file path
    if len(positional_args) >= 1:
        if positional_args[0].startswith('ST') and len(positional_args[0]) >= 5:
            standard_code = positional_args[0]
            if len(positional_args) >= 2:
                csv_file_path = positional_args[1]
        else:
            # If first arg doesn't look like a standard code, treat it as a file
            csv_file_path = positional_args[0]

    try:
        if output_format == 'console':
            print(f"Extracting monthly starts for {standard_code} from: {csv_file_path}")
            print()

        # Extract monthly data
        monthly_data = extract_monthly_starts(csv_file_path, standard_code)

        # Display summary
        if output_format == 'console':
            total_records = len(monthly_data)
            total_starts = sum(record['starts'] for record in monthly_data)
            print(f"Found {total_records} records with {total_starts} total starts for {standard_code}")
            if monthly_data:
                print(f"Standard: {monthly_data[0]['standard_name']}")
            print()

        # Display output in requested format
        if output_format == 'csv':
            csv_output = format_monthly_csv(monthly_data)
            print(csv_output)
        elif output_format == 'tsv':
            tsv_output = format_monthly_tsv(monthly_data)
            print(tsv_output)
        elif output_format == 'console':
            table_output = format_monthly_table(monthly_data)
            print(table_output)
        else:  # markdown
            markdown_output = format_monthly_markdown(monthly_data)
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
