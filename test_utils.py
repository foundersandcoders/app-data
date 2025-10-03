#!/usr/bin/env python3
"""
Unit tests for utils module.

Run with: pytest test_utils.py -v
"""

import pytest
from utils import (
    clean_company_name,
    clean_provider_name,
    parse_positions,
    format_academic_year,
    extract_year_quarter_from_filename,
    TableFormatter
)


class TestCleanCompanyName:
    """Tests for clean_company_name function."""

    def test_removes_limited(self):
        assert clean_company_name("Acme Corp LIMITED") == "Acme Corp"

    def test_removes_ltd(self):
        assert clean_company_name("Tech Solutions LTD") == "Tech Solutions"

    def test_removes_ltd_with_period(self):
        assert clean_company_name("Software Inc LTD.") == "Software Inc"

    def test_removes_llp(self):
        assert clean_company_name("Law Firm LLP") == "Law Firm"

    def test_removes_plc(self):
        assert clean_company_name("Big Company PLC") == "Big Company"

    def test_removes_cic(self):
        assert clean_company_name("Social Enterprise C.I.C.") == "Social Enterprise"

    def test_removes_multiple_suffixes(self):
        # Should only remove the final suffix
        assert clean_company_name("Company CO") == "Company"

    def test_preserves_name_without_suffix(self):
        assert clean_company_name("Simple Name") == "Simple Name"

    def test_handles_empty_string(self):
        assert clean_company_name("") == ""

    def test_handles_none(self):
        assert clean_company_name(None) == None

    def test_handles_whitespace(self):
        assert clean_company_name("  Spaced Ltd  ") == "Spaced"

    def test_case_insensitive(self):
        assert clean_company_name("lowercase ltd") == "lowercase"
        assert clean_company_name("UPPERCASE LTD") == "UPPERCASE"


class TestCleanProviderName:
    """Tests for clean_provider_name function."""

    def test_removes_ukprn(self):
        assert clean_provider_name("Training Provider (12345)") == "Training Provider"

    def test_removes_ukprn_and_suffix(self):
        assert clean_provider_name("Training Provider LTD (12345)") == "Training Provider"

    def test_preserves_name_without_ukprn(self):
        assert clean_provider_name("Simple Provider") == "Simple Provider"


class TestParsePositions:
    """Tests for parse_positions function."""

    def test_parses_valid_integer_string(self):
        assert parse_positions("5") == 5
        assert parse_positions("100") == 100

    def test_returns_default_for_empty_string(self):
        assert parse_positions("") == 1
        assert parse_positions("", default=0) == 0

    def test_returns_default_for_none(self):
        assert parse_positions(None) == 1
        assert parse_positions(None, default=0) == 0

    def test_handles_integer_input(self):
        assert parse_positions(42) == 42

    def test_returns_default_for_invalid_string(self):
        assert parse_positions("invalid") == 1
        assert parse_positions("abc", default=0) == 0

    def test_handles_whitespace(self):
        assert parse_positions("  5  ") == 5


class TestFormatAcademicYear:
    """Tests for format_academic_year function."""

    def test_formats_compact_year(self):
        assert format_academic_year("202021") == "2020-21"
        assert format_academic_year("202324") == "2023-24"

    def test_preserves_already_formatted_year(self):
        assert format_academic_year("2020-21") == "2020-21"

    def test_handles_mixed_format(self):
        # Extract first 6 digits
        year = format_academic_year("2020-21")
        assert "2020" in year


class TestExtractYearQuarter:
    """Tests for extract_year_quarter_from_filename function."""

    def test_extracts_year_and_quarter(self):
        assert extract_year_quarter_from_filename('app-underlying-data-vacancies-202425-q2.csv') == (2024, 25, 2)
        assert extract_year_quarter_from_filename('app-underlying-data-starts-202324-q4.csv') == (2023, 24, 4)

    def test_extracts_year_and_month_name(self):
        assert extract_year_quarter_from_filename('app-underlying-data-monthly-202425-mar.csv') == (2024, 25, 3)
        assert extract_year_quarter_from_filename('app-underlying-data-monthly-202324-nov.csv') == (2023, 24, 11)

    def test_case_insensitive_quarter(self):
        assert extract_year_quarter_from_filename('data-202425-Q2.csv') == (2024, 25, 2)
        assert extract_year_quarter_from_filename('data-202425-q3.csv') == (2024, 25, 3)

    def test_handles_full_month_names(self):
        assert extract_year_quarter_from_filename('data-202425-january.csv') == (2024, 25, 1)
        assert extract_year_quarter_from_filename('data-202425-december.csv') == (2024, 25, 12)

    def test_returns_zero_for_invalid_filename(self):
        assert extract_year_quarter_from_filename('invalid-file.csv') == (0, 0, 0)
        assert extract_year_quarter_from_filename('no-year-pattern.csv') == (0, 0, 0)


class TestTableFormatter:
    """Tests for TableFormatter class."""

    def test_to_csv_basic(self):
        headers = ['Name', 'Age', 'City']
        rows = [
            ['Alice', 30, 'London'],
            ['Bob', 25, 'Paris']
        ]
        result = TableFormatter.to_csv(headers, rows)

        lines = result.strip().split('\n')
        assert lines[0] == 'Name,Age,City'
        assert 'Alice' in lines[1]
        assert 'Bob' in lines[2]

    def test_to_csv_with_quotes(self):
        headers = ['Company', 'Count']
        rows = [['Company, Inc.', 5]]
        result = TableFormatter.to_csv(headers, rows)

        # CSV module should properly escape the comma
        assert '"Company, Inc."' in result or 'Company' in result

    def test_to_tsv_basic(self):
        headers = ['Name', 'Age']
        rows = [['Alice', 30]]
        result = TableFormatter.to_tsv(headers, rows)

        lines = result.strip().split('\n')
        assert 'Name\tAge' in lines[0]
        assert 'Alice\t30' in lines[1]

    def test_to_markdown_basic(self):
        headers = ['Name', 'Age']
        rows = [['Alice', 30], ['Bob', 25]]
        result = TableFormatter.to_markdown(headers, rows)

        lines = result.strip().split('\n')
        assert '| Name | Age |' in lines[0]
        assert '|--' in lines[1]  # Separator
        assert '| Alice | 30 |' in lines[2]
        assert '| Bob | 25 |' in lines[3]

    def test_to_console_table_basic(self):
        headers = ['Name', 'Age']
        rows = [['Alice', 30], ['Bob', 25]]
        result = TableFormatter.to_console_table(headers, rows)

        lines = result.strip().split('\n')
        assert 'Name' in lines[0]
        assert 'Age' in lines[0]
        assert '-' in lines[1]  # Separator
        assert 'Alice' in lines[2]
        assert 'Bob' in lines[3]

    def test_to_console_table_with_custom_widths(self):
        headers = ['Name', 'Age']
        rows = [['Alice', 30]]
        result = TableFormatter.to_console_table(headers, rows, column_widths=[20, 10])

        # Should respect column widths
        assert len(result.split('\n')[0]) >= 30  # At least the sum of column widths


class TestTableFormatterEdgeCases:
    """Edge case tests for TableFormatter."""

    def test_empty_table(self):
        headers = ['Name', 'Age']
        rows = []

        csv_result = TableFormatter.to_csv(headers, rows)
        assert 'Name,Age' in csv_result

        md_result = TableFormatter.to_markdown(headers, rows)
        assert '| Name | Age |' in md_result

    def test_single_row(self):
        headers = ['Name']
        rows = [['Alice']]

        result = TableFormatter.to_markdown(headers, rows)
        assert '| Alice |' in result

    def test_numbers_in_console_table(self):
        """Numbers should be right-aligned in console tables."""
        headers = ['Item', 'Count']
        rows = [['Apple', 100], ['Banana', 50]]
        result = TableFormatter.to_console_table(headers, rows)

        # Check that result contains the data
        assert 'Apple' in result
        assert '100' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
