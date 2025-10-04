#!/usr/bin/env python3
"""
Extract Apprenticeship Starts by Region and Employer Size

This script extracts apprenticeship starts data for a specific standard from the
Department for Education (DfE) underlying apprenticeship data CSV files and presents
it as a combined view showing major regions broken down by employer size (funding type).

The output shows:
- London (large employers)
- London (SMEs)
- North West (large employers)
- North West (SMEs)
- South East (large employers)
- South East (SMEs)
- All other regions (large employers)
- All other regions (SMEs)
- Total large employers (all regions)
- Total SMEs (all regions)
- Grand total (all employers, all regions)

Usage:
    python3 combined.py [options] [standard_code] [input_file]

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
    Most recent year shows quarterly breakdown (2024-25 Q1, 2024-25 Q2, etc.)

Examples:
    python3 combined.py                       # ST0116, latest file with quarterly breakdown
    python3 combined.py ST0113                # ST0113, latest file with quarterly breakdown
    python3 combined.py ST0116 data.csv       # ST0116, specific file
    python3 combined.py --csv ST0113          # ST0113, CSV format
"""

import sys
from typing import List, Dict, Any

from utils import (
    find_latest_file,
    format_academic_year,
    TableFormatter,
    read_csv_data,
    parse_positions
)
from config import (
    UNDERLYING_STARTS_FILE_PATTERN,
    DEFAULT_STANDARD_CODE,
    FIELD_ST_CODE,
    FIELD_LEARNER_HOME_REGION,
    FIELD_FUNDING_TYPE,
    FIELD_YEAR,
    FIELD_STARTS,
    FIELD_START_QUARTER,
    FIELD_STD_FWK_NAME_UNDERLYING,
    FUNDING_LEVY,
    FUNDING_OTHER,
    FUNDING_LEVY_LABEL,
    FUNDING_OTHER_LABEL,
    CONSOLE_PROVIDER_COLUMN_WIDTH,
    CONSOLE_YEAR_COLUMN_WIDTH
)


def extract_combined_starts(csv_file_path: str, standard_code: str = DEFAULT_STANDARD_CODE) -> List[Dict[str, Any]]:
    """
    Extract apprenticeship starts data by region and funding type for a specific standard.

    Args:
        csv_file_path: Path to the underlying CSV file containing starts data
        standard_code: The standard code to filter for (e.g., 'ST0116')

    Returns:
        List of dictionaries containing filtered combined starts data

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
    starts_data = []
    for row in raw_data:
        region = row.get(FIELD_LEARNER_HOME_REGION, '').strip()
        funding_type = row.get(FIELD_FUNDING_TYPE, '').strip()
        quarter_str = row.get(FIELD_START_QUARTER, '').strip()
        quarter = parse_positions(quarter_str, default=0) if quarter_str else 0

        # Map funding types to readable labels
        if funding_type == FUNDING_LEVY:
            funding_label = 'Large employers'
        elif funding_type == FUNDING_OTHER:
            funding_label = 'SMEs'
        else:
            funding_label = funding_type  # Keep original if unknown

        starts_data.append({
            'region': region,
            'funding_type': funding_label,
            'funding_type_raw': funding_type,
            'year': row.get(FIELD_YEAR, '').strip(),
            'quarter': quarter,
            'starts': parse_positions(row.get(FIELD_STARTS, '').strip(), default=0),
            'standard_code': row.get(FIELD_ST_CODE, '').strip(),
            'standard_name': row.get(FIELD_STD_FWK_NAME_UNDERLYING, '').strip()
        })

    return starts_data


def aggregate_starts_by_region_funding_year(starts_data: List[Dict[str, Any]],
                                             most_recent_year: str = None) -> Dict[tuple, Dict[str, int]]:
    """
    Aggregate starts data by region, funding type, and year.

    Args:
        starts_data: List of starts data dictionaries
        most_recent_year: The most recent academic year (e.g., '2024-25').
                          If specified, this year will be broken down by quarters.

    Returns:
        Dictionary with (region, funding_type) tuples as keys and year/quarter->starts dictionaries as values.
    """
    aggregated = {}

    for record in starts_data:
        region = record['region']
        funding_type = record['funding_type']
        year = record['year']
        quarter = record['quarter']
        starts = record['starts']

        key = (region, funding_type)
        if key not in aggregated:
            aggregated[key] = {}

        # For the most recent year, create quarterly keys
        if most_recent_year and year == most_recent_year and quarter > 0:
            year_key = f"{year} Q{quarter}"
        else:
            year_key = year

        if year_key not in aggregated[key]:
            aggregated[key][year_key] = 0

        aggregated[key][year_key] += starts

    return aggregated


def prepare_combined_table_data(starts_data: List[Dict[str, Any]]) -> tuple:
    """
    Prepare data for combined table with major regions split by funding type.

    Args:
        starts_data: List of starts data dictionaries

    Returns:
        Tuple of (headers, rows, title)
    """
    if not starts_data:
        return (['Region / Employer Size', 'No data available'], [], 'Unknown Standard')

    standard_code = starts_data[0].get('standard_code', 'ST0000')
    standard_name = starts_data[0].get('standard_name', 'Unknown Standard')
    title = f"{standard_code} {standard_name} starts by region and employer size"

    # Identify the most recent year
    all_base_years = set(record['year'] for record in starts_data)
    sorted_base_years = sorted(all_base_years)

    if not sorted_base_years:
        return (['Region / Employer Size', 'No data available'], [], standard_name)

    most_recent_year = sorted_base_years[-1]

    # Aggregate data
    aggregated = aggregate_starts_by_region_funding_year(starts_data, most_recent_year)

    # Get all year/quarter keys and sort them
    all_year_keys = set()
    for region_funding_data in aggregated.values():
        all_year_keys.update(region_funding_data.keys())

    # Sort year keys
    def sort_key(year_key: str) -> tuple:
        if ' Q' in year_key:
            year_part, q_part = year_key.split(' Q')
            return (year_part, int(q_part))
        else:
            return (year_key, 0)

    year_keys = sorted(all_year_keys, key=sort_key)

    if not year_keys:
        return (['Region / Employer Size', 'No data available'], [], standard_name)

    # Identify quarterly keys for most recent year
    quarterly_keys = [key for key in year_keys if key.startswith(most_recent_year) and ' Q' in key]

    # Build final year_keys list with total column before quarterly breakdown
    final_year_keys = []
    for key in year_keys:
        if ' Q' not in key:
            final_year_keys.append(key)
        elif key == quarterly_keys[0]:
            final_year_keys.append(most_recent_year)
            final_year_keys.append(key)
        else:
            final_year_keys.append(key)

    year_keys = final_year_keys

    # Define major regions and row order
    major_regions = ['London', 'North West', 'South East']
    funding_types = ['Large employers', 'SMEs']

    # Build rows in specified order
    headers = ['Region / Employer Size'] + [format_academic_year(year_key.split(' Q')[0]) +
                                            (f" Q{year_key.split(' Q')[1]}" if ' Q' in year_key else '')
                                            for year_key in year_keys]
    rows = []

    # Grand total row
    grand_total_values = []
    for year_key in year_keys:
        if year_key == most_recent_year:
            total = sum(
                data.get(q_key, 0)
                for q_key in quarterly_keys
                for data in aggregated.values()
            )
        else:
            total = sum(
                data.get(year_key, 0)
                for data in aggregated.values()
            )
        grand_total_values.append(total)

    grand_total_row = ['**Grand Total**'] + [f"**{val}**" for val in grand_total_values]
    rows.append(grand_total_row)

    # Major regions broken down by funding type
    for region in major_regions:
        for funding_type in funding_types:
            key = (region, funding_type)
            year_data = aggregated.get(key, {})

            row_values = []
            for year_key in year_keys:
                if year_key == most_recent_year:
                    total_value = sum(year_data.get(q_key, 0) for q_key in quarterly_keys)
                    row_values.append(total_value)
                else:
                    row_values.append(year_data.get(year_key, 0))

            row_label = f"{region} ({funding_type.lower()})"
            row = [row_label] + row_values
            rows.append(row)

    # All other regions broken down by funding type
    for funding_type in funding_types:
        row_values = []
        for year_key in year_keys:
            if year_key == most_recent_year:
                total = sum(
                    data.get(q_key, 0)
                    for q_key in quarterly_keys
                    for (reg, fund), data in aggregated.items()
                    if fund == funding_type and reg not in major_regions
                )
            else:
                total = sum(
                    data.get(year_key, 0)
                    for (reg, fund), data in aggregated.items()
                    if fund == funding_type and reg not in major_regions
                )
            row_values.append(total)

        row_label = f"All other regions ({funding_type.lower()})"
        row = [row_label] + row_values
        rows.append(row)

    # Total by funding type (all regions)
    for funding_type in funding_types:
        row_values = []
        for year_key in year_keys:
            if year_key == most_recent_year:
                total = sum(
                    data.get(q_key, 0)
                    for q_key in quarterly_keys
                    for (reg, fund), data in aggregated.items()
                    if fund == funding_type
                )
            else:
                total = sum(
                    data.get(year_key, 0)
                    for (reg, fund), data in aggregated.items()
                    if fund == funding_type
                )
            row_values.append(total)

        row_label = f"**Total {funding_type.lower()}**"
        row = [row_label] + [f"**{val}**" for val in row_values]
        rows.append(row)

    return (headers, rows, title)


def format_combined_markdown(starts_data: List[Dict[str, Any]]) -> str:
    """
    Format combined starts data as a markdown table.

    Args:
        starts_data: List of starts data dictionaries

    Returns:
        Markdown table formatted string with header
    """
    if not starts_data:
        return "No apprenticeship starts data found for the specified standard."

    headers, rows, title = prepare_combined_table_data(starts_data)

    output_lines = []
    output_lines.append(f"# {title}")
    output_lines.append("")
    output_lines.append(TableFormatter.to_markdown(headers, rows))

    return '\n'.join(output_lines)


def format_combined_csv(starts_data: List[Dict[str, Any]]) -> str:
    """
    Format combined starts data as CSV.

    Args:
        starts_data: List of starts data dictionaries

    Returns:
        CSV formatted string
    """
    headers, rows, _ = prepare_combined_table_data(starts_data)

    # Remove markdown bold formatting from CSV output
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    return TableFormatter.to_csv(headers, cleaned_rows)


def format_combined_table(starts_data: List[Dict[str, Any]]) -> str:
    """
    Format combined starts data as a console-friendly table.

    Args:
        starts_data: List of starts data dictionaries

    Returns:
        Formatted table string
    """
    if not starts_data:
        return "No apprenticeship starts data found for the specified standard."

    headers, rows, title = prepare_combined_table_data(starts_data)

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
    column_widths = [CONSOLE_PROVIDER_COLUMN_WIDTH]
    for _ in range(len(headers) - 1):
        column_widths.append(CONSOLE_YEAR_COLUMN_WIDTH)

    output_lines.append(TableFormatter.to_console_table(headers, cleaned_rows, column_widths))

    return '\n'.join(output_lines)


def format_combined_tsv(starts_data: List[Dict[str, Any]]) -> str:
    """
    Format combined starts data as TSV.

    Args:
        starts_data: List of starts data dictionaries

    Returns:
        TSV formatted string
    """
    headers, rows, _ = prepare_combined_table_data(starts_data)

    # Remove markdown formatting
    cleaned_rows = []
    for row in rows:
        cleaned_row = [str(cell).replace('**', '') for cell in row]
        cleaned_rows.append(cleaned_row)

    return TableFormatter.to_tsv(headers, cleaned_rows)


def main():
    """Main function to run the combined starts extraction."""
    # Find the most recent underlying starts file
    default_file = find_latest_file(UNDERLYING_STARTS_FILE_PATTERN)

    if not default_file:
        print("Error: No underlying starts data files found in apprenticeships_* folders")
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
            print(f"Extracting combined regional and funding apprenticeship starts for {standard_code} from: {csv_file_path}")
            print()

        # Extract combined starts data
        starts_data = extract_combined_starts(csv_file_path, standard_code)

        # Display summary
        if output_format == 'console':
            total_records = len(starts_data)
            total_starts = sum(record['starts'] for record in starts_data)
            print(f"Found {total_records} records with {total_starts} total starts for {standard_code}")
            if starts_data:
                print(f"Standard: {starts_data[0]['standard_name']}")
            print()

        # Display output in requested format
        if output_format == 'csv':
            csv_output = format_combined_csv(starts_data)
            print(csv_output)
        elif output_format == 'tsv':
            tsv_output = format_combined_tsv(starts_data)
            print(tsv_output)
        elif output_format == 'console':
            table_output = format_combined_table(starts_data)
            print(table_output)
        else:  # markdown
            markdown_output = format_combined_markdown(starts_data)
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
