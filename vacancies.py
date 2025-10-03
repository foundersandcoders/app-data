#!/usr/bin/env python3
"""
Extract Software Developer (Level 4) Apprenticeship Vacancies

This script extracts apprenticeship vacancy data for Software Developer positions
from the Department for Education (DfE) apprenticeship data CSV files.

Usage:
    python3 vacancies.py [options] [input_file]

Options:
    --csv, -c       Output in CSV format (suitable for importing into Notion databases)
    --table         Output in table format (console-friendly aligned tables)
    --tsv, -t       Output in tab-separated format (for copy-paste into Notion tables)
    --help, -h      Show this help message

If no input file is specified, it will automatically find the most recent vacancy data file
from the available apprenticeships_YYYY-YY folders.

Output:
    Default: Markdown table format for copy-paste into Notion inline tables
    --csv: CSV format suitable for importing into Notion databases
    --table: Console-friendly aligned tables

    Content includes:
    - Detailed breakdown for providers with >10 apprenticeships (Provider, Employer, Town, Positions)
    - Summary for providers with 4-10 apprenticeships
    - Aggregated total for providers with ≤3 apprenticeships
"""

import sys
from typing import List, Dict, Any

from utils import (
    clean_company_name,
    parse_positions,
    find_latest_file,
    TableFormatter,
    read_csv_data
)
from config import (
    VACANCY_FILE_PATTERN,
    VACANCY_LARGE_PROVIDER_THRESHOLD,
    VACANCY_MEDIUM_PROVIDER_MIN,
    VACANCY_SMALL_PROVIDER_MAX,
    LONDON_KEYWORD,
    NON_LONDON_MIN_POSITIONS,
    FILTER_SOFTWARE_DEVELOPER,
    FIELD_FRAMEWORK_OR_STANDARD_NAME,
    FIELD_EMPLOYER_FULL_NAME,
    FIELD_PROVIDER_FULL_NAME,
    FIELD_VACANCY_TOWN,
    FIELD_NUMBER_OF_POSITIONS,
    CONSOLE_PROVIDER_COLUMN_WIDTH,
    CONSOLE_EMPLOYER_COLUMN_WIDTH,
    CONSOLE_TOWN_COLUMN_WIDTH,
    CONSOLE_POSITIONS_COLUMN_WIDTH,
    TABLE_PROVIDER_WIDTH,
    TABLE_EMPLOYER_WIDTH,
    TABLE_TOWN_WIDTH
)


def extract_software_developer_vacancies(csv_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract Software Developer apprenticeship vacancies from CSV data.

    Args:
        csv_file_path: Path to the CSV file containing vacancy data

    Returns:
        List of dictionaries containing filtered vacancy data

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file has invalid format
    """
    def filter_software_developer(row: Dict[str, str]) -> bool:
        """Filter for Software Developer apprenticeships."""
        framework_name = row.get(FIELD_FRAMEWORK_OR_STANDARD_NAME, '').strip()
        return framework_name == FILTER_SOFTWARE_DEVELOPER

    raw_data = read_csv_data(csv_file_path, filter_software_developer)

    # Transform to required format
    vacancies = []
    for row in raw_data:
        employer_name = row.get(FIELD_EMPLOYER_FULL_NAME, '').strip()
        provider_name = row.get(FIELD_PROVIDER_FULL_NAME, '').strip()

        vacancy_data = {
            'employer': employer_name,
            'provider': provider_name,
            'employer_clean': clean_company_name(employer_name),
            'provider_clean': clean_company_name(provider_name),
            'town': row.get(FIELD_VACANCY_TOWN, '').strip(),
            'positions': row.get(FIELD_NUMBER_OF_POSITIONS, '').strip()
        }
        vacancies.append(vacancy_data)

    return vacancies


def aggregate_by_provider(vacancies: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate vacancy data by provider.

    Args:
        vacancies: List of vacancy dictionaries

    Returns:
        Dictionary mapping provider names to aggregated statistics
    """
    provider_stats = {}

    for vacancy in vacancies:
        provider_clean = vacancy['provider_clean']
        employer_clean = vacancy['employer_clean']

        if provider_clean not in provider_stats:
            provider_stats[provider_clean] = {
                'employers': set(),
                'total_positions': 0
            }

        provider_stats[provider_clean]['employers'].add(employer_clean)
        positions = parse_positions(vacancy['positions'])
        provider_stats[provider_clean]['total_positions'] += positions

    return provider_stats


def format_providers_table(vacancies: List[Dict[str, Any]], output_format: str = 'markdown') -> str:
    """
    Format vacancy data as a providers table with Provider, Employers count, and Vacancies.

    Args:
        vacancies: List of vacancy dictionaries
        output_format: 'markdown', 'csv', 'tsv', or 'console'

    Returns:
        Formatted providers table string
    """
    if not vacancies:
        return "No Software Developer apprenticeship vacancies found."

    # Aggregate by provider
    provider_stats = aggregate_by_provider(vacancies)

    # Convert to sorted list
    provider_list = []
    for provider, stats in provider_stats.items():
        provider_list.append({
            'provider': provider,
            'employers_count': len(stats['employers']),
            'total_positions': stats['total_positions']
        })

    provider_list.sort(key=lambda x: x['total_positions'], reverse=True)

    # Prepare table data
    headers = ['Provider', 'Employers', 'Vacancies']
    rows = [
        [p['provider'], p['employers_count'], p['total_positions']]
        for p in provider_list
    ]

    # Format based on output type
    if output_format == 'csv':
        return TableFormatter.to_csv(headers, rows)
    elif output_format == 'tsv':
        return TableFormatter.to_tsv(headers, rows)
    elif output_format == 'console':
        output_lines = []
        output_lines.append("PROVIDERS TABLE")
        output_lines.append("=" * 60)
        output_lines.append("")
        output_lines.append(TableFormatter.to_console_table(headers, rows,
                           [CONSOLE_PROVIDER_COLUMN_WIDTH, 10, CONSOLE_POSITIONS_COLUMN_WIDTH]))
        return '\n'.join(output_lines)
    else:  # markdown
        return TableFormatter.to_markdown(headers, rows)


def aggregate_employers_by_location(vacancies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate employer data and categorize by location (London vs non-London).

    Args:
        vacancies: List of vacancy dictionaries

    Returns:
        Dictionary with aggregated employer statistics
    """
    total_uk_positions = 0
    london_positions = 0
    employer_aggregates = {}

    for vacancy in vacancies:
        employer_clean = vacancy['employer_clean']
        provider_clean = vacancy['provider_clean']
        town = vacancy['town']
        positions = parse_positions(vacancy['positions'])

        total_uk_positions += positions

        # Determine if London
        is_london = (LONDON_KEYWORD in town.lower() if town else False)
        if is_london:
            london_positions += positions

        # Aggregate by employer-provider-town combination
        key = (employer_clean, provider_clean, town)
        if key not in employer_aggregates:
            employer_aggregates[key] = {
                'employer': employer_clean,
                'provider': provider_clean,
                'town': town,
                'positions': 0,
                'is_london': is_london
            }
        employer_aggregates[key]['positions'] += positions

    # Separate by location
    london_employers = []
    other_location_employers = []

    for data in employer_aggregates.values():
        if data['is_london']:
            london_employers.append(data)
        elif data['positions'] >= NON_LONDON_MIN_POSITIONS:
            other_location_employers.append(data)

    # Sort by positions (descending)
    london_employers.sort(key=lambda x: x['positions'], reverse=True)
    other_location_employers.sort(key=lambda x: x['positions'], reverse=True)

    # Calculate remaining
    accounted_positions = london_positions + sum(emp['positions'] for emp in other_location_employers)
    remaining_positions = total_uk_positions - accounted_positions

    return {
        'total_uk': total_uk_positions,
        'london_total': london_positions,
        'london_employers': london_employers,
        'other_employers': other_location_employers,
        'remaining': remaining_positions
    }


def format_employers_table(vacancies: List[Dict[str, Any]], output_format: str = 'markdown') -> str:
    """
    Format vacancy data as an employers table with special structure.

    Args:
        vacancies: List of vacancy dictionaries
        output_format: 'markdown', 'csv', 'tsv', or 'console'

    Returns:
        Formatted employers table string
    """
    if not vacancies:
        return "No Software Developer apprenticeship vacancies found."

    stats = aggregate_employers_by_location(vacancies)

    # Prepare table data
    headers = ['Employer', 'Provider', 'Town', 'Positions']
    rows = []

    # UK and London totals
    rows.append(['UK total', 'All providers', 'UK', stats['total_uk']])
    rows.append(['London total', 'All providers', 'London', stats['london_total']])
    rows.append(['', '', '', ''])  # Spacing row

    # London employers
    for emp in stats['london_employers']:
        rows.append([
            emp['employer'],
            emp['provider'],
            emp['town'] if emp['town'] else 'London',
            emp['positions']
        ])

    if stats['london_employers']:
        rows.append(['', '', '', ''])  # Spacing row

    # Other location employers
    for emp in stats['other_employers']:
        rows.append([
            emp['employer'],
            emp['provider'],
            emp['town'] if emp['town'] else '',
            emp['positions']
        ])

    if stats['other_employers']:
        rows.append(['', '', '', ''])  # Spacing row

    # All other employers
    if stats['remaining'] > 0:
        rows.append(['All other employers', 'All providers', 'Rest of UK', stats['remaining']])

    # Format based on output type
    if output_format == 'csv':
        return TableFormatter.to_csv(headers, rows)
    elif output_format == 'tsv':
        return TableFormatter.to_tsv(headers, rows)
    elif output_format == 'console':
        output_lines = []
        output_lines.append("EMPLOYERS TABLE")
        output_lines.append("=" * 80)
        output_lines.append("")
        output_lines.append(TableFormatter.to_console_table(headers, rows,
                           [CONSOLE_EMPLOYER_COLUMN_WIDTH, TABLE_PROVIDER_WIDTH,
                            CONSOLE_TOWN_COLUMN_WIDTH, CONSOLE_POSITIONS_COLUMN_WIDTH]))
        return '\n'.join(output_lines)
    else:  # markdown
        return TableFormatter.to_markdown(headers, rows)


def format_csv_output(vacancies: List[Dict[str, Any]]) -> str:
    """
    Format vacancy data as CSV for easy import into Notion or Excel.
    Implements the special hierarchical format with provider categorization.

    Args:
        vacancies: List of vacancy dictionaries

    Returns:
        CSV formatted string
    """
    if not vacancies:
        return TableFormatter.to_csv(['Provider', 'Employer', 'Town', 'Positions'], [])

    # Group by provider
    provider_groups = {}
    for vacancy in vacancies:
        provider = vacancy['provider']
        if provider not in provider_groups:
            provider_groups[provider] = []
        provider_groups[provider].append(vacancy)

    # Calculate totals and categorize
    provider_totals = {}
    for provider, provider_vacancies in provider_groups.items():
        total_positions = sum(parse_positions(v['positions']) for v in provider_vacancies)
        provider_totals[provider] = {
            'total_positions': total_positions,
            'vacancies': provider_vacancies
        }

    # Sort and categorize providers
    sorted_providers = sorted(provider_totals.items(), key=lambda x: x[1]['total_positions'], reverse=True)

    detailed_providers = []  # >10 positions
    medium_providers = []    # 4-10 positions
    small_providers = []     # ≤3 positions

    for provider, data in sorted_providers:
        if data['total_positions'] > VACANCY_LARGE_PROVIDER_THRESHOLD:
            detailed_providers.append((provider, data))
        elif data['total_positions'] >= VACANCY_MEDIUM_PROVIDER_MIN:
            medium_providers.append((provider, data))
        else:
            small_providers.append((provider, data))

    rows = []

    # Process detailed providers
    for provider, data in detailed_providers:
        # Aggregate by employer and town
        employer_aggregates = {}
        for vacancy in data['vacancies']:
            key = (vacancy['employer'], vacancy['town'])
            if key not in employer_aggregates:
                employer_aggregates[key] = {
                    'employer': vacancy['employer'],
                    'town': vacancy['town'],
                    'total_positions': 0
                }
            employer_aggregates[key]['total_positions'] += parse_positions(vacancy['positions'])

        # Identify multi-vacancy vs single-vacancy employers
        employer_totals = {}
        for (employer, _), agg_data in employer_aggregates.items():
            if employer not in employer_totals:
                employer_totals[employer] = 0
            employer_totals[employer] += agg_data['total_positions']

        multi_vacancy_employers = []
        other_employers_positions = 0
        other_employers_count = 0

        for agg_data in employer_aggregates.values():
            if employer_totals[agg_data['employer']] == 1:
                other_employers_positions += agg_data['total_positions']
                other_employers_count += 1
            else:
                multi_vacancy_employers.append(agg_data)

        # Sort multi-vacancy employers
        multi_vacancy_employers.sort(key=lambda x: (-x['total_positions'], x['employer']))

        # Add rows
        for agg_data in multi_vacancy_employers:
            town = agg_data['town'] if agg_data['town'] != 'NULL' else ''
            rows.append([provider, agg_data['employer'], town, agg_data['total_positions']])

        # Add other employers line
        if other_employers_count > 0:
            employer_word = "employer" if other_employers_count == 1 else "employers"
            rows.append([provider, f"{other_employers_count} other {employer_word}", "", other_employers_positions])

        # Add subtotal
        rows.append([f"{provider} SUBTOTAL", "", "", data['total_positions']])

    # Process medium providers
    for provider, data in medium_providers:
        rows.append([provider, "(multiple employers)", "", data['total_positions']])

    # Process small providers aggregate
    if small_providers:
        total_small_positions = sum(data['total_positions'] for _, data in small_providers)
        small_provider_count = len(small_providers)
        provider_word = "provider" if small_provider_count == 1 else "providers"
        rows.append([f"{small_provider_count} other {provider_word}", "(various employers)", "", total_small_positions])

    return TableFormatter.to_csv(['Provider', 'Employer', 'Town', 'Positions'], rows)


def main():
    """Main function to run the vacancy extraction."""
    # Find the most recent vacancy file
    default_file = find_latest_file(VACANCY_FILE_PATTERN)

    if not default_file:
        print("Error: No vacancy data files found in apprenticeships_* folders")
        print("Please ensure you have downloaded apprenticeship data from the DfE website")
        sys.exit(1)

    # Handle command line arguments
    output_format = 'markdown'  # 'markdown', 'table', 'csv', or 'tsv'
    csv_file_path = default_file

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
            csv_file_path = arg

    try:
        if output_format == 'console':
            print(f"Extracting Software Developer apprenticeship vacancies from: {csv_file_path}")
            print()

        # Extract vacancy data
        vacancies = extract_software_developer_vacancies(csv_file_path)

        # Display summary
        if output_format == 'console':
            print(f"Found {len(vacancies)} Software Developer apprenticeship vacancies")
            print()

        # Display output in requested format
        if output_format == 'csv':
            # Special CSV format with hierarchical structure
            print(format_csv_output(vacancies))
        else:
            # Standard two-table format for other outputs
            providers_table = format_providers_table(vacancies, output_format)
            employers_table = format_employers_table(vacancies, output_format)

            print(providers_table)
            print()
            print()
            print(employers_table)

        # Display summary statistics (only for console format)
        if vacancies and output_format == 'console':
            print()
            print("Summary:")
            print(f"- Total vacancies: {len(vacancies)}")

            total_positions = sum(parse_positions(v['positions']) for v in vacancies)
            print(f"- Total positions available: {total_positions}")

            towns = set(v['town'] for v in vacancies if v['town'] and v['town'] != 'NULL')
            if towns:
                print(f"- Locations: {len(towns)} unique towns/cities")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure the CSV file exists in the current directory or provide the correct path.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
