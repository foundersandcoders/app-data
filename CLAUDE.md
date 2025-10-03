# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data analysis project for processing UK Department for Education (DfE) apprenticeship statistics. The main focus is extracting and analyzing apprenticeship vacancy data, particularly for software developer positions.

## Key Commands

### Running the analysis scripts

**Vacancy analysis:**
```bash
python3 vacancies.py [options] [input_file]
```
- Default markdown output: `python3 vacancies.py`
- CSV output for databases: `python3 vacancies.py --csv`
- Console table format: `python3 vacancies.py --table`

**Apprenticeship starts analysis:**
```bash
python3 starts.py [options] [input_file] [standard_code]
```
- Default markdown output: `python3 starts.py ST0116`
- Console table format: `python3 starts.py --table ST0116`
- CSV output: `python3 starts.py --csv ST0116`

### Working with different data periods
- **Vacancy data**: Automatically finds most recent `app-underlying-data-vacancies-*.csv` file
- **Starts data**: Automatically finds most recent `app-underlying-data-starts-*.csv` file (extracts from zip if needed)
- **Historical data**: Specify different CSV files from the apprenticeships_YYYY-YY directories

## Data Architecture

### Data Structure
The project works with two main apprenticeship data collections:
- **apprenticeships_2023-24/**: Complete 2023-24 academic year data
- **apprenticeships_2024-25/**: Current 2024-25 academic year data (Q2)

Each collection contains:
- **data/**: ~20 CSV files covering geographic, demographic, provider, and subject analysis
- **supporting-files/**: Underlying raw data and metadata
- **data-guidance/**: Documentation explaining data structure and definitions

### Data Processing Patterns
- **Geographic categorization**: Separates London vs rest of UK
- **Provider-based aggregation**: Groups by training providers with statistical thresholds
- **Company name normalization**: Removes legal suffixes ("LIMITED", "LTD", "PLC", etc.)
- **Position counting**: Handles multiple vacancy formats and aggregates totals

### Output Format Strategy
The main script generates data in multiple formats:
- **Table format**: Human-readable console output with aligned columns
- **CSV format**: Database-ready with proper escaping and aggregation levels
- **Markdown format**: Documentation-ready tables for reports
- **TSV format**: Copy-paste friendly for spreadsheet applications

## Code Patterns

### Data Filtering
The vacancy script filters apprenticeship data by `framework_or_standard_name == 'Software developer'`. The starts script filters by `st_code` field. When creating new extraction scripts, follow this pattern:
1. Use `csv.DictReader` for proper CSV parsing with quote handling
2. Filter by the specific apprenticeship type in the framework/standard name field
3. Apply company name cleaning with the `clean_company_name()` function

### Provider Categorization
Data is intelligently grouped by provider size:
- **Large providers (>10 positions)**: Detailed employer breakdown
- **Medium providers (4-10 positions)**: Summary-level reporting
- **Small providers (≤3 positions)**: Aggregated totals

### Geographic Analysis
London-specific analysis is built into the data processing. The script identifies London locations by checking if 'london' appears in the town field (case-insensitive).

## Data Sources and Updates

Data comes from the DfE's official apprenticeship statistics releases. New data is typically released quarterly. When new data files are added:
1. Update the default file path in the main script if needed
2. Ensure the CSV structure matches expected column names
3. Test with the new data to verify filtering and aggregation logic

## Dependencies

The project uses only Python standard library modules (csv, sys, os, typing). This keeps the environment simple and ensures compatibility across different Python installations (3.6+).