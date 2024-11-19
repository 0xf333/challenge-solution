import pandas as pd
import numpy as np
from tabulate import tabulate
from typing import List, Tuple
import itertools
import statistics
import time
from .constants import (
    ErrorThreshold,
    CSVIndex,
    DisplaySettings,
    StatisticalMetrics,
    TableFormat,
    DisplayStrings,
)


class DatasetAnalyzer:
    """
    Analyzes datasets to find optimal combinations using the `(n₁ × n₂)/n₃` formula.
    Processes CSV files containing multiple sets of numbers and their target values,
    finding the best combinations that minimize percentage error.

    Attributes
    ----------
    df : pd.DataFrame
        DataFrame containing the raw CSV data
    results : dict
        Dictionary storing analysis results for each set

    Methods
    ----------
    #### analyze()
        Performs complete analysis of all datasets and displays results
    #### _display_input_data()
        Shows formatted input data and dataset summary
    #### _parse_dataset() -> dict
        Converts raw CSV into structured dictionary format
    #### _find_best_combination(numbers: List[float], target: float) -> Tuple[float, float, tuple]
        Finds optimal (n₁, n₂, n₃) combination for a given target
    #### _calculate_statistical_metrics(errors: List[float]) -> dict
        Computes statistical measures for error analysis

    Example
    -------
    >>> analyzer = DatasetAnalyzer('dataset.csv')
    >>> analyzer.analyze()
    STEP 0: INPUT DATA VERIFICATION
    ===============================
    [Displays formatted input data]
    ...
    STEP 4: CONCLUSION
    ==================
    [Shows final analysis results]

    Notes
    -----
    The CSV file should have the following structure:
    - Sets arranged in columns (A through H)
    - Target values in row 4
    - Available numbers starting from row 7
    - Empty columns between sets
    """

    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path, header=None, skip_blank_lines=True)
        self.results = {}

    def _display_input_data(self):
        """
        Displays input dataset in tabular format for (n₁ × n₂)/n₃ formula analysis.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Prints formatted tables to stdout with:
            - Target values table
            - Available numbers table
            - Dataset summary statistics

        Output Format
        ------------
        1. Target Values Table:
            - Shows target numbers for sets A-H
            - Each value formatted to 2 decimal places
            - These are the targets for `(n₁ × n₂)/n₃` formula

        2. Available Numbers Table:
            - Lists all numbers per set (A-H)
            - Each number can be used as `n₁`, `n₂`, or `n₃`
            - Values formatted to 2 decimal places
            - Same number can be used multiple times

        3. Summary Statistics:
            - Total sets count
            - Numbers available per set
            - Total available data points
        """

        print("\nSTEP 0: INPUT DATA VERIFICATION")
        print(DisplayStrings.HEADER_SEPARATOR)

        headers = []
        for i in range(CSVIndex.SETS_COUNT):
            set_name = chr(65 + i)
            headers.extend([f"{DisplayStrings.SET_PREFIX}{set_name}", ""])

        target_row = []
        for i in range(
            0, CSVIndex.SETS_COUNT * CSVIndex.COLUMN_STEP, CSVIndex.COLUMN_STEP
        ):
            target = self.df.iloc[CSVIndex.TARGET_ROW, i]
            target_row.extend(
                [f"{float(target):.{DisplaySettings.DECIMAL_PLACES}f}", ""]
            )

        number_rows = []
        for row_idx in range(CSVIndex.DATA_START_ROW, self.df.shape[0]):
            row_data = []
            for col_idx in range(
                0, CSVIndex.SETS_COUNT * CSVIndex.COLUMN_STEP, CSVIndex.COLUMN_STEP
            ):
                val = self.df.iloc[row_idx, col_idx]
                if pd.notna(val) and val != "":
                    row_data.extend(
                        [f"{float(val):.{DisplaySettings.DECIMAL_PLACES}f}", ""]
                    )
                else:
                    row_data.extend(["", ""])
            number_rows.append(row_data)

        all_data = [
            [DisplayStrings.TARGET_VALUES_HEADER]
            + ["" for _ in range(CSVIndex.SETS_COUNT * 2 - 1)],
            target_row,
            [DisplayStrings.AVAILABLE_NUMBERS_HEADER]
            + ["" for _ in range(CSVIndex.SETS_COUNT * 2 - 1)],
        ] + number_rows

        print("\nDataset Structure:")
        print(
            tabulate(
                all_data,
                headers=headers,
                tablefmt=TableFormat.GRID,
                numalign=TableFormat.RIGHT_ALIGN,
            )
        )

        print("\nDataset Summary:")
        print(f"- Number of Sets: {CSVIndex.SETS_COUNT} (A through H)")
        print(f"- Numbers per Set: {len(number_rows)} available values")
        print(f"- Total Data Points: {CSVIndex.SETS_COUNT * len(number_rows)}")

        time.sleep(DisplaySettings.PAUSE_DURATION)

    def _parse_dataset(self) -> dict:
        """
        Transforms CSV data into structured format for `(n₁ × n₂)/n₃` calculations.

        Parameters
        ----------
        None
            Uses class property `self.df` containing CSV data

        Returns
        -------
        dict
            Structured dictionary with:
            - `key` : str
                Set identifier (A through H)
            - `value` : dict
                Contains:
                - `target` : float
                    Value to achieve using `(n₁ × n₂)/n₃`
                - `numbers` : List[float]
                    Available numbers for `n₁`, `n₂`, `n₃`

        Algorithm
        ---------
        1. Iterates columns pairwise (skips blank columns)
        2. For each set:
            - Extracts `target` from row 4
            - Collects numbers from row 7 onwards
            - Converts all values to `float` type

        Example
        -------
        >>> {
                'A': {'target': 309303.86,
                    'numbers': [1580060.07, 957467.65]},
                'B': {'target': 1138706.26,
                    'numbers': [12749507.48, 529430.93]}
            }
        """

        datasets = {}
        for i in range(
            0, CSVIndex.SETS_COUNT * CSVIndex.COLUMN_STEP, CSVIndex.COLUMN_STEP
        ):
            set_name = chr(65 + i // CSVIndex.COLUMN_STEP)
            target = float(self.df.iloc[CSVIndex.TARGET_ROW, i])
            numbers = []
            for val in self.df.iloc[CSVIndex.DATA_START_ROW :, i]:
                if pd.notna(val) and val != "":
                    numbers.append(float(val))
            datasets[set_name] = {"target": target, "numbers": numbers}
        return datasets

    def _find_best_combination(
        self, numbers: List[float], target: float
    ) -> Tuple[float, float, tuple]:
        """
        Finds optimal combination of three numbers for (n₁ × n₂)/n₃ formula.

        Parameters
        ----------
        `numbers` : List[float]
            Pool of available numbers that can be used as n₁, n₂, or n₃.
        `target` : float
            The value to be achieved through the formula.

        Returns
        -------
        Tuple[float, float, tuple]
            A tuple containing:
            - `best_result` : float
                The closest value to target achieved by `(n₁ × n₂)/n₃`
            - `best_error` : float
                Percentage error between result and target
            - `best_combination` : tuple
                The three numbers `(n₁, n₂, n₃)` that produced the best result

        Algorithm
        ---------
        1. Uses itertools.product to test every possible combination
        2. For each `(n₁, n₂, n₃)` combination:
            - Validates `n₃ ≠ 0` to avoid division by zero
            - Calculates `(n₁ × n₂)/n₃`
            - Computes `error = |result - target|/target × 100`
            - Updates best values if current error is lower

        Example
        -------
        >>> target = 100
            result = 99
            error  = |(99-100)/100| × 100 = 1%
        """
        best_error = float("inf")
        best_result = None
        best_combination = None

        for n1, n2, n3 in itertools.product(numbers, repeat=3):
            if n3 == 0:
                continue
            result = (n1 * n2) / n3
            error = abs(result - target) / target * 100

            if error < best_error:
                best_error = error
                best_result = result
                best_combination = (n1, n2, n3)

        return best_result, best_error, best_combination

    def _calculate_statistical_metrics(self, errors: List[float]) -> dict:
        """
        Calculates comprehensive statistical metrics for `(n₁ × n₂)/n₃` formula errors.

        Parameters
        ----------
        `errors` : List[float]
            List of percentage errors from each set's best `(n₁ × n₂)/n₃` result

        Returns
        -------
        dict
            Statistical metrics dictionary containing:
            - `mean` : float
                Average error across all sets
            - `median` : float
                Middle value of sorted errors
            - `std_dev` : float
                Standard deviation of errors
            - `variance` : float
                Variance in error distribution
            - `min`, `max` : float
                Smallest and largest errors
            - `range` : float
                Difference between max and min errors
            - `q1`, `q3` : float
                First and third quartiles
            - `iqr` : float
                Interquartile range (Q3 - Q1)

        Algorithm
        ---------
        1. Central Tendency:
            - Calculates mean using `statistics.mean()`
            - Finds median using `statistics.median()`
        2. Dispersion:
            - Computes standard deviation via `statistics.stdev()`
            - Determines variance using `statistics.variance()`
        3. Range Analysis:
            - Finds min/max values
            - Calculates range as `max - min`
        4. Quartile Analysis:
            - Uses `np.percentile()` for Q1 (25%) and Q3 (75%)
            - Computes IQR as `Q3 - Q1`

        Example
        -------
        >>> errors = [1.2, 2.3, 0.8, 1.5]
            metrics = {
                'mean': 1.45,
                'median': 1.35,
                'std_dev': 0.629,
                ...
            }
        """
        return {
            "mean": statistics.mean(errors),
            "median": statistics.median(errors),
            "std_dev": statistics.stdev(errors),
            "variance": statistics.variance(errors),
            "min": min(errors),
            "max": max(errors),
            "range": max(errors) - min(errors),
            "q1": np.percentile(errors, StatisticalMetrics.Q1_PERCENTILE),
            "q3": np.percentile(errors, StatisticalMetrics.Q3_PERCENTILE),
            "iqr": (
                np.percentile(errors, StatisticalMetrics.Q3_PERCENTILE)
                - np.percentile(errors, StatisticalMetrics.Q1_PERCENTILE)
            ),
        }

    def analyze(self):
        """
        Performs complete analysis of sets using `(n₁ × n₂)/n₃` formula,
        organized in steps.

        Parameters
        ----------
        None
            Uses class instance data loaded from CSV

        Returns
        -------
        None
            Outputs comprehensive analysis results to stdout

        Analysis Steps
        -------------
        1. Input Validation
            - Calls `_display_input_data()` to show:
                - Target values
                - Available numbers
                - Dataset structure

        2. Dataset Analysis
            - For each set (A through H):
                - Gets best `(n₁ × n₂)/n₃` combination
                - Calculates error percentage
                - Stores results in formatted table
                - Headers: Dataset, Target, Result, Error(%), |r - t|

        3. Statistical Analysis
            - Computes metrics using `_calculate_statistical_metrics()`
            - Shows:
                - Central tendency (mean, median)
                - Dispersion (std dev, variance)
                - Range (min, max)
                - Quartile information

        4. Precision Analysis
            - Counts datasets within error thresholds:
                - ε < 1%
                - ε < 5%
                - ε < 10%
            - Shows percentage of sets meeting each threshold

        5. Results Classification
            Rates overall reliability based on max error:
            - `Exceptional` : max error < 1%
            - `Superior` : max error < 5%
            - `Satisfactory` : max error < 10%
            - `Limited` : max error ≥ 10%

        Example Output
        -------------
        >>> Dataset | Target    | Result    | ε (%)  | |r - t|
            Set A   | 3.09e+05  | 3.09e+05  | 0.0012 | 3.72e+00
            ...
            Reliability Rating: Superior
            Maximum Error: 4.8532%
            Mean Error: 2.1245%
        """
        self._display_input_data()

        datasets = self._parse_dataset()
        table_data = []
        all_errors = []

        print("\nSTEP 1: DATASET VALIDATION")
        print(DisplayStrings.HEADER_SEPARATOR)

        for set_name, data in datasets.items():
            result, error, (n1, n2, n3) = self._find_best_combination(
                data["numbers"], data["target"]
            )

            self.results[set_name] = {
                "target": data["target"],
                "result": result,
                "error": error,
            }

            table_data.append(
                [
                    f"{DisplayStrings.SET_PREFIX}{set_name}",
                    f"{data['target']:.{DisplaySettings.SCIENTIFIC_NOTATION_PLACES}e}",
                    f"{result:.{DisplaySettings.SCIENTIFIC_NOTATION_PLACES}e}",
                    f"{error:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}",
                    f"{abs(result - data['target']):.{DisplaySettings.SCIENTIFIC_NOTATION_PLACES}e}",
                ]
            )
            all_errors.append(error)

        print("\nResults:")
        print(
            tabulate(
                table_data,
                headers=["Dataset", "Target (t)", "Result (r)", "ε (%)", "|r - t|"],
                tablefmt=TableFormat.SIMPLE,
                numalign=TableFormat.RIGHT_ALIGN,
            )
        )
        time.sleep(DisplaySettings.PAUSE_DURATION)

        print("\nSTEP 2: STATISTICAL ERROR ANALYSIS")
        print(DisplayStrings.HEADER_SEPARATOR)

        metrics = self._calculate_statistical_metrics(all_errors)

        stats_table = [
            [
                "Central Tendency",
                f"μ = {metrics['mean']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
                f"M = {metrics['median']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
            ],
            [
                "Dispersion",
                f"σ = {metrics['std_dev']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
                f"σ² = {metrics['variance']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}",
            ],
            [
                "Range",
                f"min = {metrics['min']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
                f"max = {metrics['max']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
            ],
            [
                "Quartiles",
                f"Q₁ = {metrics['q1']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
                f"Q₃ = {metrics['q3']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
            ],
        ]
        print("\nDescriptive Statistics:")
        print(tabulate(stats_table, tablefmt=TableFormat.SIMPLE))
        time.sleep(DisplaySettings.PAUSE_DURATION)

        print("\nSTEP 3: PRECISION ANALYSIS")
        print(DisplayStrings.HEADER_SEPARATOR)

        confidence_intervals = [
            (
                ErrorThreshold.EXCEPTIONAL.value,
                sum(1 for e in all_errors if e < ErrorThreshold.EXCEPTIONAL.value),
            ),
            (
                ErrorThreshold.SUPERIOR.value,
                sum(1 for e in all_errors if e < ErrorThreshold.SUPERIOR.value),
            ),
            (
                ErrorThreshold.SATISFACTORY.value,
                sum(1 for e in all_errors if e < ErrorThreshold.SATISFACTORY.value),
            ),
        ]

        tolerance_table = [
            [
                "ε < 1.0%",
                f"{confidence_intervals[0][1]}/{CSVIndex.SETS_COUNT} datasets",
                f"({(confidence_intervals[0][1]/len(all_errors))*100:.1f}%)",
            ],
            [
                "ε < 5.0%",
                f"{confidence_intervals[1][1]}/{CSVIndex.SETS_COUNT} datasets",
                f"({(confidence_intervals[1][1]/len(all_errors))*100:.1f}%)",
            ],
            [
                "ε < 10.0%",
                f"{confidence_intervals[2][1]}/{CSVIndex.SETS_COUNT} datasets",
                f"({(confidence_intervals[2][1]/len(all_errors))*100:.1f}%)",
            ],
        ]
        print("\nError Tolerance Distribution:")
        print(tabulate(tolerance_table, tablefmt=TableFormat.SIMPLE))
        time.sleep(DisplaySettings.PAUSE_DURATION)

        print("\nSTEP 4: CONCLUSION")
        print(DisplayStrings.HEADER_SEPARATOR)

        if metrics["max"] < ErrorThreshold.EXCEPTIONAL.value:
            reliability = "Exceptional"
            notes = "Demonstrates remarkable precision across all datasets"
        elif metrics["max"] < ErrorThreshold.SUPERIOR.value:
            reliability = "Superior"
            notes = "Exhibits excellent consistency across datasets"
        elif metrics["max"] < ErrorThreshold.SATISFACTORY.value:
            reliability = "Satisfactory"
            notes = "Meets all specified precision requirements"
        else:
            reliability = "Limited"
            notes = "Further optimization recommended"

        conclusion_table = [
            ["Reliability Rating:", reliability],
            [
                "Maximum Error (ε_max):",
                f"{metrics['max']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
            ],
            [
                "Mean Error (μ_ε):",
                f"{metrics['mean']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
            ],
            [
                "Standard Deviation (σ_ε):",
                f"{metrics['std_dev']:.{DisplaySettings.ERROR_DECIMAL_PLACES}f}%",
            ],
            ["Assessment:", notes],
        ]
        print("\nFinal Results:")
        print(tabulate(conclusion_table, tablefmt=TableFormat.SIMPLE))
        time.sleep(DisplaySettings.PAUSE_DURATION)
        print()
