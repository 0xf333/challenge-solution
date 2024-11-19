from enum import Enum
from typing import Final


class ErrorThreshold(float, Enum):
    """
    Classification thresholds for error percentages in formula results.
    Used to rate the reliability of `(n₁ × n₂)/n₃` calculations.

    Attributes
    ----------
    EXCEPTIONAL : float
        Error below 1% indicates exceptional precision
    SUPERIOR : float
        Error below 5% indicates superior consistency
    SATISFACTORY : float
        Error below 10% meets minimum requirements
    """

    EXCEPTIONAL = 1.0
    SUPERIOR = 5.0
    SATISFACTORY = 10.0


class CSVIndex:
    """
    Constants defining the structure and indexing of the input CSV file.

    Attributes
    ----------
    TARGET_ROW : Final[int]
        Row index containing target values for each set
    DATA_START_ROW : Final[int]
        Starting row index for the available numbers data
    SETS_COUNT : Final[int]
        Total number of data sets (A through H)
    COLUMN_STEP : Final[int]
        Step size between columns (accounts for empty columns)
    """

    TARGET_ROW: Final[int] = 3
    DATA_START_ROW: Final[int] = 6
    SETS_COUNT: Final[int] = 8
    COLUMN_STEP: Final[int] = 2


class DisplaySettings:
    """
    Configuration for numerical formatting and display timing.

    Attributes
    ----------
    PAUSE_DURATION : Final[int]
        Duration in seconds to pause between displaying sections
    DECIMAL_PLACES : Final[int]
        Number of decimal places for general number display
    SCIENTIFIC_NOTATION_PLACES : Final[int]
        Precision for numbers in scientific notation
    ERROR_DECIMAL_PLACES : Final[int]
        Precision for error percentage values
    """

    PAUSE_DURATION: Final[int] = 0
    DECIMAL_PLACES: Final[int] = 2
    SCIENTIFIC_NOTATION_PLACES: Final[int] = 2
    ERROR_DECIMAL_PLACES: Final[int] = 4


class StatisticalMetrics:
    """
    Constants for statistical calculations and analysis.

    Attributes
    ----------
    Q1_PERCENTILE : Final[int]
        First quartile (25th percentile) for error distribution
    Q3_PERCENTILE : Final[int]
        Third quartile (75th percentile) for error distribution
    """

    Q1_PERCENTILE: Final[int] = 25
    Q3_PERCENTILE: Final[int] = 75


class TableFormat:
    """
    Format specifications for tabulate table display.

    Attributes
    ----------
    GRID : Final[str]
        Grid format with full borders for detailed data display
    SIMPLE : Final[str]
        Simple format with minimal borders for summary data
    RIGHT_ALIGN : Final[str]
        Right alignment for numerical values in tables
    """

    GRID: Final[str] = "grid"
    SIMPLE: Final[str] = "simple"
    RIGHT_ALIGN: Final[str] = "right"


class DisplayStrings:
    """
    Static string constants used in data presentation.

    Attributes
    ----------
    HEADER_SEPARATOR : Final[str]
        Separator line for section headers
    SET_PREFIX : Final[str]
        Prefix used before set identifiers (A-H)
    TARGET_VALUES_HEADER : Final[str]
        Header text for target values section
    AVAILABLE_NUMBERS_HEADER : Final[str]
        Header text for available numbers section
    """

    HEADER_SEPARATOR: Final[str] = "=" * 60
    SET_PREFIX: Final[str] = "Set "
    TARGET_VALUES_HEADER: Final[str] = "TARGET VALUES"
    AVAILABLE_NUMBERS_HEADER: Final[str] = "AVAILABLE NUMBERS"
