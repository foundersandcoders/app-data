# Intelligent File Discovery

## Overview

The scripts now intelligently discover and select the most recent data files based on academic year and quarter/month patterns in filenames.

## How It Works

### Filename Parsing

The system extracts three key pieces of information from filenames:
- **Academic Year**: e.g., `202425` → 2024-25
- **Quarter**: e.g., `q2` → Quarter 2
- **Month**: e.g., `mar` → March (month 3)

### Sorting Logic

Files are sorted by:
1. **Academic year** (descending) - newer years first
2. **Quarter/month** (descending) - later quarters/months first

### Examples

**Quarterly files (vacancies, starts):**
```
app-underlying-data-vacancies-202425-q3.csv  ← Selected (2024-25 Q3)
app-underlying-data-vacancies-202425-q2.csv  (2024-25 Q2)
app-underlying-data-vacancies-202425-q1.csv  (2024-25 Q1)
app-underlying-data-vacancies-202324-q4.csv  (2023-24 Q4)
```

**Monthly files:**
```
app-underlying-data-monthly-202425-nov.csv   ← Selected (2024-25 Nov = month 11)
app-underlying-data-monthly-202425-mar.csv   (2024-25 Mar = month 3)
app-underlying-data-monthly-202425-jan.csv   (2024-25 Jan = month 1)
app-underlying-data-monthly-202324-dec.csv   (2023-24 Dec = month 12)
```

## Supported Formats

### Year Formats
- `202425` → 2024-25
- `202324` → 2023-24
- Any 6-digit pattern: `YYYYYY`

### Quarter Formats
- `q1`, `Q1` → Quarter 1
- `q2`, `Q2` → Quarter 2
- `q3`, `Q3` → Quarter 3
- `q4`, `Q4` → Quarter 4
- Case-insensitive

### Month Formats

**Short names:**
- `jan`, `feb`, `mar`, `apr`, `may`, `jun`
- `jul`, `aug`, `sep`, `oct`, `nov`, `dec`

**Full names:**
- `january`, `february`, `march`, etc.
- Case-insensitive

## Usage

### Automatic Discovery

All scripts automatically find the most recent file:

```bash
# Finds latest vacancy file
python3 vacancies.py

# Finds latest starts file
python3 starts.py ST0116

# Finds latest monthly file
python3 monthly.py
```

### Manual File Selection

You can still specify a file explicitly:

```bash
python3 vacancies.py apprenticeships_2023-24/supporting-files/app-underlying-data-vacancies-202324-q4.csv
```

## Search Locations

Files are searched in the following order:
1. **Current directory** (root level)
2. **Apprenticeships folders** (`apprenticeships_*/supporting-files/`)

All matching files are found, then sorted to select the most recent.

## Examples in Practice

### Scenario 1: New Quarter Released

Before (root directory):
```
app-underlying-data-vacancies-202425-q1.csv
```

After downloading Q2 data:
```
app-underlying-data-vacancies-202425-q1.csv
app-underlying-data-vacancies-202425-q2.csv  ← Now selected automatically
```

The script now uses Q2 data without any code changes.

### Scenario 2: New Academic Year

Before:
```
apprenticeships_2023-24/supporting-files/app-underlying-data-starts-202324-q4.csv
```

After downloading 2024-25 data:
```
apprenticeships_2023-24/supporting-files/app-underlying-data-starts-202324-q4.csv
apprenticeships_2024-25/supporting-files/app-underlying-data-starts-202425-q1.csv  ← Now selected
```

The script automatically switches to the new academic year.

### Scenario 3: Monthly Updates

```
app-underlying-data-monthly-202425-jan.csv
app-underlying-data-monthly-202425-feb.csv
app-underlying-data-monthly-202425-mar.csv  ← Selected (most recent)
```

Each month's release is automatically detected.

## Testing

Comprehensive tests verify the file discovery logic:

```bash
# Run file discovery tests
python3 test_file_discovery.py
```

Tests cover:
- ✓ Year/quarter extraction from filenames
- ✓ Correct sorting of quarterly files
- ✓ Correct sorting of monthly files
- ✓ Cross-year comparisons
- ✓ Case-insensitive parsing

## Technical Details

### Key Functions

**`extract_year_quarter_from_filename(filename)`**
- Parses filename to extract (year_start, year_end, quarter/month)
- Returns `(2024, 25, 2)` for `app-underlying-data-vacancies-202425-q2.csv`
- Returns `(2024, 25, 3)` for `app-underlying-data-monthly-202425-mar.csv`

**`find_latest_file(pattern)`**
- Searches for all files matching the pattern
- Sorts by year and quarter/month
- Returns path to most recent file

### Implementation

Located in `utils.py`:
```python
def extract_year_quarter_from_filename(filename: str) -> tuple:
    """Extract academic year and quarter from filename."""
    # Extracts year pattern (e.g., 202425)
    # Extracts quarter (q1-q4) or month name
    # Returns (year_start, year_end, quarter_or_month_num)

def find_latest_file(file_pattern: str) -> Optional[str]:
    """Find most recent file matching pattern."""
    # Searches root and apprenticeships folders
    # Sorts by (year_start, year_end, quarter)
    # Returns newest file path
```

## Benefits

### For Users
- ✅ No manual file path updates needed
- ✅ Scripts automatically use latest data
- ✅ Works across academic years seamlessly
- ✅ Handles quarterly and monthly releases

### For Developers
- ✅ Centralized logic in `utils.py`
- ✅ Comprehensive test coverage
- ✅ Clear, documented functions
- ✅ Easy to extend for new patterns

## Backwards Compatibility

✅ Fully compatible with existing workflows:
- Scripts still accept explicit file paths
- File patterns unchanged
- Output formats unchanged
- Command-line options unchanged

## Future Enhancements

Potential improvements:
- Add support for weekly releases
- Add file version detection
- Add data completeness checking
- Add automatic download of latest files

## Troubleshooting

### Script uses wrong file

**Check**: Run with explicit file path to verify:
```bash
python3 vacancies.py path/to/specific/file.csv
```

**Debug**: Test the discovery logic:
```python
from utils import find_latest_file
print(find_latest_file('app-underlying-data-vacancies-*.csv'))
```

### No files found

**Error**: `Error: No vacancy data files found`

**Solutions**:
1. Check files are named correctly: `app-underlying-data-{type}-{year}-{quarter}.csv`
2. Check files are in `apprenticeships_*/supporting-files/` or root directory
3. Verify year format: `202425` not `2024-25`

### Wrong quarter selected

**Check**: Verify filename format matches expected pattern:
- Quarter: `q1`, `q2`, `q3`, `q4` (case-insensitive)
- Month: `jan`, `feb`, `mar`, etc. (lowercase in filename)

## Related Files

- `utils.py` - Implementation of file discovery logic
- `test_file_discovery.py` - Comprehensive test suite
- `test_utils.py` - Unit tests including year/quarter extraction
- `vacancies.py`, `starts.py`, `monthly.py` - Scripts using file discovery

## Questions?

For issues or questions about file discovery:
1. Check this document
2. Review `test_file_discovery.py` for examples
3. Check `utils.py` docstrings for function details
