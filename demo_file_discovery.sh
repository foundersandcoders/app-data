#!/bin/bash
# Demo script showing intelligent file discovery

echo "======================================================"
echo "INTELLIGENT FILE DISCOVERY DEMONSTRATION"
echo "======================================================"
echo ""

echo "Available vacancy files (across all locations):"
echo "------------------------------------------------"
find . -name "app-underlying-data-vacancies-*.csv" -type f 2>/dev/null | while read file; do
    python3 -c "
from utils import extract_year_quarter_from_filename
import os
filename = os.path.basename('$file')
year_start, year_end, quarter = extract_year_quarter_from_filename(filename)
print(f'  {filename}')
print(f'    → Academic year: {year_start}-{year_end}, Quarter: {quarter}')
"
done

echo ""
echo "Selected file (automatic discovery):"
echo "------------------------------------------------"
python3 -c "
from utils import find_latest_file
latest = find_latest_file('app-underlying-data-vacancies-*.csv')
print(f'  {latest}')
print(f'  ✓ This file will be used by default')
"

echo ""
echo "======================================================"
echo "How it works:"
echo "======================================================"
echo "1. All matching files are found across directories"
echo "2. Each filename is parsed for year and quarter"
echo "3. Files are sorted: newest year > highest quarter"
echo "4. The most recent file is selected automatically"
echo ""
echo "Run 'python3 vacancies.py' to use the selected file"
echo "======================================================"
