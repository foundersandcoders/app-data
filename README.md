# DfE Apprenticeship Data Extraction Scripts

This repository contains Python scripts for extracting and analysing apprenticeship data from UK Department for Education (DfE) statistical releases.

## Recent Updates

**Latest**: Intelligent file discovery now automatically selects the most recent data files based on academic year and quarter/month patterns. See [FILE_DISCOVERY.md](FILE_DISCOVERY.md) for details.

**Refactored**: Codebase refactored for improved maintainability, reduced duplication, and better code quality. See [REFACTORING.md](REFACTORING.md) for details.

## Scripts

### vacancies.py

Extracts Software Developer (Level 4) apprenticeship vacancy data from DfE vacancy CSV files and presents it in various formats suitable for analysis.

**Features:**
- **Automatic file discovery**: Finds and uses the most recent vacancy data file
- Filters vacancy data specifically for Software Developer apprenticeships
- Groups data by training provider and employer
- Provides multiple output formats (table, CSV, Markdown, TSV)
- Clean company name processing (removes legal suffixes like "Ltd", "PLC")
- Separates London vs other UK locations
- Aggregates small providers for better data presentation

**Usage:**
```bash
# Automatic discovery (uses most recent file)
python3 vacancies.py [options]

# Specify a file explicitly
python3 vacancies.py [options] [input_file]
```

**Options:**
- `--csv`, `-c`: Output in CSV format (suitable for importing into databases)
- `--table`: Output in table format (console-friendly aligned tables)
- `--tsv`, `-t`: Output in tab-separated format (for copy-paste into spreadsheets)
- `--help`, `-h`: Show help message

**Default behaviour:** Markdown table format using the most recent vacancy file

**Output Format:** Two tables showing:
1. **Providers Table**: Training providers with employer count and total vacancies
2. **Employers Table**: Detailed breakdown with employer, provider, location, and positions

The script intelligently groups data by:
- Detailed breakdown for providers with >10 apprenticeships
- Summary for providers with 4-10 apprenticeships
- Aggregated total for providers with ≤3 apprenticeships

**Examples:**
```bash
python3 vacancies.py                    # Markdown format, latest file
python3 vacancies.py --table            # Console table format
python3 vacancies.py --csv              # CSV format for import
python3 vacancies.py data/file.csv      # Use specific file
```

### starts.py

Extracts apprenticeship starts data for a specific standard and presents it as a league table with years as columns and providers as rows.

**Features:**
- **Automatic file discovery**: Finds and uses the most recent starts data file
- **Quarterly breakdown**: Most recent year is broken down into Q1, Q2, Q3, Q4 columns
- Filters data for any apprenticeship standard code (defaults to ST0116)
- Creates year-over-year comparison tables
- Shows providers with 3+ starts in most recent year separately
- Includes total row showing all starts across providers
- Automatically extracts from zip files if needed

**Usage:**
```bash
# Automatic discovery (uses most recent file)
python3 starts.py [options] [standard_code]

# Specify a file explicitly
python3 starts.py [options] [standard_code] [input_file]
```

**Options:**
- `--csv`, `-c`: Output in CSV format
- `--table`: Output in console table format
- `--tsv`, `-t`: Output in tab-separated format
- `--help`, `-h`: Show help message

**Default Standard:** `ST0116` (Software Developer)

**Output Format:** League table showing:
1. **Total row**: Combined starts across all providers by year and quarter
2. **Major providers**: Providers with 3+ total starts in most recent year
3. **All other providers**: Aggregated smaller providers
4. **Most recent year**: Broken down into Q1, Q2, Q3, Q4 columns for detailed analysis

**Examples:**
```bash
python3 starts.py                       # ST0116 (Software Developer), latest file
python3 starts.py ST0113                # ST0113, latest file
python3 starts.py ST0116 data.csv       # ST0116, specific file
python3 starts.py --table ST0116        # Console table format
python3 starts.py --csv ST0113          # CSV output
```

### monthly.py

Extracts monthly apprenticeship starts data for a specific standard and presents it as a table with years as columns and months as rows (in academic year order: Aug-Jul).

**Features:**
- **Automatic file discovery**: Finds and uses the most recent monthly starts file
- Filters data for any apprenticeship standard code (defaults to ST0116)
- Creates month-by-month comparison across years
- Displays months in academic year order (August to July)
- Includes total row showing annual totals

**Usage:**
```bash
# Automatic discovery (uses most recent file)
python3 monthly.py [options] [standard_code]

# Specify a file explicitly
python3 monthly.py [options] [standard_code] [input_file]
```

**Options:**
- `--csv`, `-c`: Output in CSV format
- `--table`: Output in console table format
- `--tsv`, `-t`: Output in tab-separated format
- `--help`, `-h`: Show help message

**Default Standard:** `ST0116` (Software Developer)

**Examples:**
```bash
python3 monthly.py                      # ST0116, latest file
python3 monthly.py ST0113               # ST0113, latest file
python3 monthly.py ST0116 data.csv      # ST0116, specific file
python3 monthly.py --table ST0113       # ST0113, table format
```

## Intelligent File Discovery

All scripts automatically discover and use the most recent data files based on:
- **Academic year** (e.g., 2024-25 is newer than 2023-24)
- **Quarter/month** (e.g., Q3 is newer than Q2, Nov is newer than Mar)

Files are found in:
1. Current directory
2. `apprenticeships_*/supporting-files/` folders

**Supported filename patterns:**
- Quarterly: `app-underlying-data-{type}-{year}-q{1-4}.csv`
  - Example: `app-underlying-data-vacancies-202425-q2.csv`
- Monthly: `app-underlying-data-{type}-{year}-{month}.csv`
  - Example: `app-underlying-data-monthly-202425-mar.csv`

See [FILE_DISCOVERY.md](FILE_DISCOVERY.md) for complete documentation.

## Code Architecture

The project uses a modular architecture with shared utilities:

- **`vacancies.py`**, **`starts.py`**, **`monthly.py`** - Main analysis scripts
- **`utils.py`** - Shared utilities (name cleaning, file discovery, table formatting)
- **`config.py`** - Configuration constants (thresholds, field names, patterns)
- **`test_utils.py`** - Unit tests for utility functions
- **`test_file_discovery.py`** - Tests for file discovery logic

## Data Sources

These scripts work with CSV files downloaded from the DfE's apprenticeship statistics releases:
- [Apprenticeship and traineeships statistics](https://www.gov.uk/government/statistics/apprenticeship-and-traineeships-statistics)

Download the "Underlying data" files and place them in:
- Root directory, or
- `apprenticeships_YYYY-YY/supporting-files/` folders

Scripts automatically find and use the most recent files.

## Output Formats

All scripts support multiple output formats optimised for different use cases:

| Format | Use Case | Option |
|--------|----------|--------|
| **Markdown** | Documentation, reports, Notion inline tables | Default |
| **CSV** | Import into databases, spreadsheets | `--csv` |
| **TSV** | Copy-paste into existing tables | `--tsv` |
| **Table** | Console viewing, terminal output | `--table` |

## Requirements

**Runtime:**
- Python 3.6+
- Standard library only (no external dependencies)

**Development (optional):**
```bash
pip3 install -r requirements.txt
```

Includes:
- pytest - for running tests
- mypy - for type checking (optional)
- black - for code formatting (optional)
- flake8 - for linting (optional)

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python3 test_utils.py
python3 test_file_discovery.py

# Or with pytest (if installed)
pytest test_*.py -v
```

## Configuration

Thresholds and settings can be adjusted in `config.py`:

```python
# Provider categorisation thresholds
VACANCY_LARGE_PROVIDER_THRESHOLD = 10  # Providers with >10 positions
VACANCY_MEDIUM_PROVIDER_MIN = 4        # Providers with 4-10 positions
VACANCY_SMALL_PROVIDER_MAX = 3         # Providers with ≤3 positions

# Starts analysis
STARTS_MIN_THRESHOLD = 3               # Minimum starts to show separately

# Standard codes
DEFAULT_STANDARD_CODE = 'ST0116'       # Software Developer Level 4
```

## Documentation

- **README.md** (this file) - Overview and usage
- **CLAUDE.md** - Instructions for Claude Code development
- **REFACTORING.md** - Details of refactoring improvements
- **FILE_DISCOVERY.md** - Intelligent file discovery documentation
- **requirements.txt** - Development dependencies

## Examples

### Typical Workflow

```bash
# 1. Download latest DfE data files
# Place in root or apprenticeships_2024-25/supporting-files/

# 2. Run analysis scripts (automatically use latest files)
python3 vacancies.py --table
python3 starts.py ST0116 --csv
python3 monthly.py --tsv

# 3. Output can be redirected to files
python3 vacancies.py --csv > vacancies_output.csv
python3 starts.py --table ST0116 > starts_report.txt
```

### Analysing Different Standards

```bash
# Software Developer (Level 4)
python3 starts.py ST0116
python3 monthly.py ST0116

# Data Analyst (Level 4)
python3 starts.py ST0118
python3 monthly.py ST0118

# Cyber Security Technologist (Level 3)
python3 starts.py ST0622
python3 monthly.py ST0622
```

### Historical Data Analysis

```bash
# Use specific older file
python3 vacancies.py apprenticeships_2023-24/supporting-files/app-underlying-data-vacancies-202324-q4.csv

# Compare different quarters
python3 starts.py ST0116 app-data-starts-202324-q4.csv > q4_2023.txt
python3 starts.py ST0116 app-data-starts-202425-q2.csv > q2_2024.txt
diff q4_2023.txt q2_2024.txt
```

## Troubleshooting

### "No vacancy/starts data files found"

**Solution:**
1. Ensure files are named correctly: `app-underlying-data-{type}-{year}-{quarter}.csv`
2. Check files are in root directory or `apprenticeships_*/supporting-files/`
3. Verify year format: `202425` not `2024-25`

### Script uses wrong file

**Debug:**
```python
from utils import find_latest_file
print(find_latest_file('app-underlying-data-vacancies-*.csv'))
```

**Solution:** Specify file explicitly:
```bash
python3 vacancies.py path/to/specific/file.csv
```

### No data in output

**Check:**
1. Verify standard code is correct (e.g., `ST0116` not `ST116`)
2. Ensure CSV file contains data for the specified standard
3. Check CSV field names match expected format

## Contributing

When modifying the code:

1. Add configuration to `config.py` (not hardcoded in scripts)
2. Add shared logic to `utils.py`
3. Write tests for new functionality
4. Use type hints on all functions
5. Follow the coding standards in `CLAUDE.md`

## Licence

This code is provided for analysing publicly available DfE apprenticeship statistics.

## Contact

For questions about the DfE data:
- [DfE Apprenticeship Statistics](https://www.gov.uk/government/statistics/apprenticeship-and-traineeships-statistics)

For issues with these scripts:
- Review the documentation files in this repository
- Check the test files for usage examples
