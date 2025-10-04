#!/usr/bin/env python3
"""
Configuration constants for apprenticeship data analysis scripts.

This module centralizes all magic numbers, thresholds, and configuration
values used across the analysis scripts.
"""

# Provider categorization thresholds for vacancy analysis
VACANCY_LARGE_PROVIDER_THRESHOLD = 10  # Providers with >10 positions get detailed breakdown
VACANCY_MEDIUM_PROVIDER_MIN = 4         # Providers with 4-10 positions get summary
VACANCY_SMALL_PROVIDER_MAX = 3          # Providers with ≤3 positions get aggregated

# Provider categorization thresholds for starts analysis
STARTS_MIN_THRESHOLD = 3                # Minimum starts in most recent year to show provider separately

# Regional analysis thresholds
REGION_MIN_THRESHOLD = 10               # Minimum starts in most recent year to show region separately

# Funding type labels
FUNDING_LEVY = 'Supported by ASA levy funds'
FUNDING_OTHER = 'Other'
FUNDING_LEVY_LABEL = 'Large employers (levy-funded)'
FUNDING_OTHER_LABEL = 'SMEs (other funding)'

# Employers to always show regardless of threshold
ALWAYS_SHOW_PROVIDERS = ['FOUNDERS & CODERS']

# Geographic analysis
LONDON_KEYWORD = 'london'               # Keyword for identifying London locations
NON_LONDON_MIN_POSITIONS = 3            # Minimum positions for non-London employers to show individually

# Default standard codes
DEFAULT_STANDARD_CODE = 'ST0116'        # Software Developer Level 4

# Column widths for console output
CONSOLE_PROVIDER_COLUMN_WIDTH = 40
CONSOLE_EMPLOYER_COLUMN_WIDTH = 40
CONSOLE_TOWN_COLUMN_WIDTH = 15
CONSOLE_POSITIONS_COLUMN_WIDTH = 9
CONSOLE_YEAR_COLUMN_WIDTH = 8
CONSOLE_MONTH_COLUMN_WIDTH = 7

# Column widths for formatted tables
TABLE_PROVIDER_WIDTH = 25
TABLE_EMPLOYER_WIDTH = 40
TABLE_TOWN_WIDTH = 15

# Academic year month order
ACADEMIC_MONTH_ORDER = [
    'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan',
    'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'
]

# File patterns
VACANCY_FILE_PATTERN = 'app-underlying-data-vacancies-*.csv'
STARTS_FILE_PATTERN = 'app-underlying-data-starts-*.csv'
STARTS_ZIP_PATTERN = 'app-underlying-data-starts-*.zip'
MONTHLY_STARTS_FILE_PATTERN = 'app-underlying-data-monthly-starts-*.csv'
UNDERLYING_STARTS_FILE_PATTERN = 'app-underlying-data-starts-*.csv'

# Data folder configuration
APPRENTICESHIPS_FOLDER_PREFIX = 'apprenticeships'
SUPPORTING_FILES_SUBFOLDER = 'supporting-files'

# CSV field names
FIELD_FRAMEWORK_OR_STANDARD_NAME = 'framework_or_standard_name'
FIELD_EMPLOYER_FULL_NAME = 'employer_full_name'
FIELD_PROVIDER_FULL_NAME = 'provider_full_name'
FIELD_PROVIDER_NAME = 'provider_name'
FIELD_VACANCY_TOWN = 'vacancy_town'
FIELD_NUMBER_OF_POSITIONS = 'number_of_positions'
FIELD_ST_CODE = 'st_code'
FIELD_YEAR = 'year'
FIELD_STARTS = 'starts'
FIELD_START_MONTH = 'start_month'
FIELD_START_QUARTER = 'start_quarter'
FIELD_STD_FWK_NAME = 'std_fwk_name'

# Underlying data field names
FIELD_LEARNER_HOME_REGION = 'learner_home_region'
FIELD_DELIVERY_REGION = 'delivery_region'
FIELD_FUNDING_TYPE = 'funding_type'
FIELD_STD_FWK_NAME_UNDERLYING = 'std_fwk_name'

# Filter values
FILTER_SOFTWARE_DEVELOPER = 'Software developer'
