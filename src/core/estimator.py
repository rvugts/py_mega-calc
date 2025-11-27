"""Benchmarking utility for predicting calculation time.

This module provides regression-based benchmarking to predict calculation
time for large inputs using micro-benchmarks and linear regression.

Dependencies:
    - time: Time measurement
    - math: Mathematical functions for regression
    - typing: Type hints
"""

import math
import time
from typing import Any, Callable, Dict, List, Tuple


class Estimator:
    """Regression-based benchmarking utility for predicting calculation time.

    Runs micro-benchmarks on startup (or on demand) to predict calculation
    time for large inputs. Supports Fibonacci, Factorial, and Prime
    calculations.
    """

    def __init__(self) -> None:
        """Initialize the Estimator."""
        self.benchmark_data: Dict[str, List[Tuple[int, float]]] = {}

    def run_micro_benchmark(
        self,
        calculation_func: Callable[[int], Any],
        input_values: List[int],
    ) -> List[Tuple[int, float]]:
        """Run micro-benchmark for a calculation function.

        Executes the calculation function for each input value and measures
        the execution time.

        :param calculation_func: The calculation function to benchmark
        :type calculation_func: Callable[[int], Any]
        :param input_values: List of input values to test
        :type input_values: List[int]
        :return: List of tuples (input_value, execution_time_seconds)
        :rtype: List[Tuple[int, float]]
        """
        results: List[Tuple[int, float]] = []

        for input_val in input_values:
            try:
                start_time = time.perf_counter()
                calculation_func(input_val)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                results.append((input_val, execution_time))
            except Exception:  # pylint: disable=broad-exception-caught
                # Intentionally catch all exceptions to skip failed benchmarks
                # and continue with remaining input values
                continue

        return results

    def predict_time(
        self, input_value: int, calc_type: str = 'default'
    ) -> float:
        """Predict execution time for a given input value using regression.

        Uses benchmark data to fit a regression model and predict execution
        time. Supports different complexity models:
        - Fibonacci: T(n) ∝ log n
        - Factorial: T(n) ∝ n (log n)²
        - Primes: Probabilistic, density-based

        :param input_value: The input value to predict time for
        :type input_value: int
        :param calc_type: Type of calculation ('fibonacci', 'factorial',
                         'primes', or 'default')
        :type calc_type: str
        :return: Predicted execution time in seconds
        :rtype: float
        :raises ValueError: If no benchmark data is available
        """
        if calc_type not in self.benchmark_data:
            raise ValueError(
                f"No benchmark data available for calculation type: "
                f"{calc_type}"
            )

        benchmark_points = self.benchmark_data[calc_type]

        if len(benchmark_points) < 2:
            return self._simple_extrapolation(
                benchmark_points, input_value
            )

        sorted_points = sorted(benchmark_points, key=lambda x: x[0])
        inputs = [x[0] for x in sorted_points]
        times = [x[1] for x in sorted_points]

        predicted = self._predict_by_type(
            calc_type, inputs, times, input_value
        )

        if predicted < 0.001 and input_value > 1000:
            predicted = max(0.001, predicted)

        return max(0.0, predicted)

    def _simple_extrapolation(
        self, benchmark_points: List[Tuple[int, float]], input_value: int
    ) -> float:
        """Simple extrapolation for insufficient data points.

        :param benchmark_points: Available benchmark data
        :type benchmark_points: List[Tuple[int, float]]
        :param input_value: Input value to predict for
        :type input_value: int
        :return: Predicted time
        :rtype: float
        :raises ValueError: If no benchmark data available
        """
        if len(benchmark_points) == 1:
            n, t = benchmark_points[0]
            if n == 0:
                return t
            return t * (input_value / n)

        raise ValueError("Insufficient benchmark data for prediction")

    def _predict_by_type(
        self,
        calc_type: str,
        inputs: List[int],
        times: List[float],
        input_value: int,
    ) -> float:
        """Predict time based on calculation type.

        :param calc_type: Type of calculation
        :type calc_type: str
        :param inputs: Input values from benchmark
        :type inputs: List[int]
        :param times: Execution times from benchmark
        :type times: List[float]
        :param input_value: Input value to predict for
        :type input_value: int
        :return: Predicted execution time
        :rtype: float
        """
        if calc_type == 'fibonacci':
            log_inputs = [math.log(max(1, n)) for n in inputs]
            log_value = math.log(max(1, input_value))
            return self._linear_regression_predict(
                log_inputs, times, log_value
            )

        if calc_type == 'factorial':
            transformed_inputs = [
                n * (math.log(max(1, n)) ** 2) for n in inputs
            ]
            transformed_value = (
                input_value * (math.log(max(1, input_value)) ** 2)
            )
            return self._linear_regression_predict(
                transformed_inputs, times, transformed_value
            )

        if calc_type == 'primes':
            transformed_inputs = [
                n * math.log(max(1, n)) for n in inputs
            ]
            transformed_value = (
                input_value * math.log(max(1, input_value))
            )
            return self._linear_regression_predict(
                transformed_inputs, times, transformed_value
            )

        return self._linear_regression_predict(inputs, times, input_value)

    def _linear_regression_predict(
        self,
        x_values: List[float],
        y_values: List[float],
        x_predict: float,
    ) -> float:
        """Perform simple linear regression and predict y for given x.

        Uses least squares method: y = a*x + b

        :param x_values: List of x values from benchmark data
        :type x_values: List[float]
        :param y_values: List of y values (times) from benchmark data
        :type y_values: List[float]
        :param x_predict: x value to predict y for
        :type x_predict: float
        :return: Predicted y value
        :rtype: float
        """
        n = len(x_values)
        if n < 2:
            if n == 1 and x_values[0] != 0:
                return y_values[0] * (x_predict / x_values[0])
            return 0.0

        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean)
            for i in range(n)
        )
        denominator = sum(
            (x_values[i] - x_mean) ** 2 for i in range(n)
        )

        if denominator == 0:
            return y_mean

        a = numerator / denominator
        b = y_mean - a * x_mean

        return a * x_predict + b
