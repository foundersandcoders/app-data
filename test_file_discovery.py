#!/usr/bin/env python3
"""
Tests for file discovery functionality with year/quarter parsing.

Run with: python3 test_file_discovery.py
"""

from utils import extract_year_quarter_from_filename, find_latest_file
import tempfile
import os


def test_year_quarter_extraction():
    """Test extraction of year and quarter from filenames."""
    print("Testing year/quarter extraction...")

    test_cases = [
        # (filename, expected_result)
        ('app-underlying-data-vacancies-202425-q2.csv', (2024, 25, 2)),
        ('app-underlying-data-vacancies-202324-q4.csv', (2023, 24, 4)),
        ('app-underlying-data-vacancies-202425-q1.csv', (2024, 25, 1)),
        ('app-underlying-data-monthly-202425-mar.csv', (2024, 25, 3)),
        ('app-underlying-data-monthly-202324-nov.csv', (2023, 24, 11)),
        ('app-underlying-data-monthly-202425-jan.csv', (2024, 25, 1)),
        ('app-underlying-data-monthly-202425-dec.csv', (2024, 25, 12)),
        ('app-underlying-data-starts-202223-Q3.csv', (2022, 23, 3)),  # Case insensitive
    ]

    passed = 0
    failed = 0

    for filename, expected in test_cases:
        result = extract_year_quarter_from_filename(filename)
        if result == expected:
            print(f"  ✓ {filename}: {result}")
            passed += 1
        else:
            print(f"  ✗ {filename}: got {result}, expected {expected}")
            failed += 1

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return failed == 0


def test_file_sorting():
    """Test that files are sorted correctly by year and quarter."""
    print("\nTesting file sorting logic...")

    # Create test data - various files from different quarters
    test_files = [
        'app-underlying-data-vacancies-202324-q2.csv',  # 2023-24 Q2
        'app-underlying-data-vacancies-202425-q1.csv',  # 2024-25 Q1
        'app-underlying-data-vacancies-202425-q2.csv',  # 2024-25 Q2 (should be latest)
        'app-underlying-data-vacancies-202324-q4.csv',  # 2023-24 Q4
        'app-underlying-data-vacancies-202223-q3.csv',  # 2022-23 Q3
    ]

    # Sort using same logic as find_latest_file
    def sort_key(filename):
        year_start, year_end, quarter = extract_year_quarter_from_filename(filename)
        return (year_start, year_end, quarter)

    sorted_files = sorted(test_files, key=sort_key, reverse=True)

    print(f"  Files sorted (newest first):")
    for f in sorted_files:
        year_info = extract_year_quarter_from_filename(f)
        print(f"    {f} -> {year_info}")

    # The newest should be 2024-25 Q2
    expected_newest = 'app-underlying-data-vacancies-202425-q2.csv'
    if sorted_files[0] == expected_newest:
        print(f"  ✓ Correctly identified newest: {sorted_files[0]}")
        return True
    else:
        print(f"  ✗ Expected {expected_newest}, got {sorted_files[0]}")
        return False


def test_month_sorting():
    """Test that monthly files are sorted correctly."""
    print("\nTesting monthly file sorting...")

    test_files = [
        'app-underlying-data-monthly-202425-jan.csv',  # Jan = 1
        'app-underlying-data-monthly-202425-mar.csv',  # Mar = 3
        'app-underlying-data-monthly-202425-nov.csv',  # Nov = 11 (should be latest)
        'app-underlying-data-monthly-202425-sep.csv',  # Sep = 9
        'app-underlying-data-monthly-202324-dec.csv',  # Previous year
    ]

    def sort_key(filename):
        year_start, year_end, quarter = extract_year_quarter_from_filename(filename)
        return (year_start, year_end, quarter)

    sorted_files = sorted(test_files, key=sort_key, reverse=True)

    print(f"  Monthly files sorted (newest first):")
    for f in sorted_files:
        year_info = extract_year_quarter_from_filename(f)
        print(f"    {f} -> {year_info}")

    # The newest should be 2024-25 Nov (month 11)
    expected_newest = 'app-underlying-data-monthly-202425-nov.csv'
    if sorted_files[0] == expected_newest:
        print(f"  ✓ Correctly identified newest monthly: {sorted_files[0]}")
        return True
    else:
        print(f"  ✗ Expected {expected_newest}, got {sorted_files[0]}")
        return False


def test_cross_year_sorting():
    """Test that files from different academic years sort correctly."""
    print("\nTesting cross-year sorting...")

    test_files = [
        'app-underlying-data-vacancies-202122-q4.csv',  # 2021-22 Q4
        'app-underlying-data-vacancies-202223-q1.csv',  # 2022-23 Q1
        'app-underlying-data-vacancies-202324-q4.csv',  # 2023-24 Q4
        'app-underlying-data-vacancies-202425-q1.csv',  # 2024-25 Q1 (should be latest)
    ]

    def sort_key(filename):
        year_start, year_end, quarter = extract_year_quarter_from_filename(filename)
        return (year_start, year_end, quarter)

    sorted_files = sorted(test_files, key=sort_key, reverse=True)

    print(f"  Cross-year files sorted (newest first):")
    for f in sorted_files:
        year_info = extract_year_quarter_from_filename(f)
        print(f"    {f} -> {year_info}")

    expected_order = [
        'app-underlying-data-vacancies-202425-q1.csv',  # 2024-25 Q1
        'app-underlying-data-vacancies-202324-q4.csv',  # 2023-24 Q4
        'app-underlying-data-vacancies-202223-q1.csv',  # 2022-23 Q1
        'app-underlying-data-vacancies-202122-q4.csv',  # 2021-22 Q4
    ]

    if sorted_files == expected_order:
        print(f"  ✓ Files sorted correctly across years")
        return True
    else:
        print(f"  ✗ Sorting incorrect")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("FILE DISCOVERY TESTS")
    print("=" * 70)

    results = []

    results.append(("Year/Quarter Extraction", test_year_quarter_extraction()))
    results.append(("File Sorting", test_file_sorting()))
    results.append(("Month Sorting", test_month_sorting()))
    results.append(("Cross-Year Sorting", test_cross_year_sorting()))

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    exit(main())
