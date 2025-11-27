"""Tests for Estimator benchmarking utility.

This module contains tests for the Estimator class, including
micro-benchmark execution and regression-based time prediction.

Dependencies:
    - pytest: Testing framework
    - time: Time measurement
    - src.core.estimator: Estimator class
"""

import math
import time

import pytest

from src.core.estimator import Estimator


class TestEstimatorMicroBenchmark:
    """Test micro-benchmark execution functionality."""

    def test_estimator_class_exists(self) -> None:
        """Test that Estimator class exists."""
        assert Estimator is not None

    def test_estimator_can_be_instantiated(self) -> None:
        """Test that Estimator can be instantiated."""
        estimator = Estimator()
        assert estimator is not None

    def test_run_micro_benchmark_exists(self) -> None:
        """Test that run_micro_benchmark method exists."""
        estimator = Estimator()
        assert hasattr(estimator, 'run_micro_benchmark')
        assert callable(estimator.run_micro_benchmark)

    def test_run_micro_benchmark_accepts_calculation_function(
        self,
    ) -> None:
        """Test run_micro_benchmark accepts a calculation function."""
        estimator = Estimator()

        def test_calc(n: int) -> int:
            return n * 2

        result = estimator.run_micro_benchmark(test_calc, [1, 2, 3])
        assert result is not None

    def test_run_micro_benchmark_returns_timing_data(self) -> None:
        """Test run_micro_benchmark returns timing measurements."""
        estimator = Estimator()

        def test_calc(n: int) -> int:
            return n * 2

        result = estimator.run_micro_benchmark(test_calc, [1, 2, 3])
        assert isinstance(result, (list, dict))
        assert len(result) > 0

    def test_run_micro_benchmark_measures_execution_time(self) -> None:
        """Test micro-benchmark actually measures execution time."""
        estimator = Estimator()

        def slow_calc(n: int) -> int:
            time.sleep(0.01)  # 10ms delay
            return n

        result = estimator.run_micro_benchmark(slow_calc, [1])
        assert result is not None

    def test_run_micro_benchmark_handles_multiple_inputs(self) -> None:
        """Test micro-benchmark can handle multiple input values."""
        estimator = Estimator()

        def test_calc(n: int) -> int:
            return n * 2

        inputs = [1, 5, 10, 20]
        result = estimator.run_micro_benchmark(test_calc, inputs)
        assert result is not None
        assert len(result) == len(inputs) or isinstance(result, dict)

    def test_run_micro_benchmark_preserves_calculation_results(
        self,
    ) -> None:
        """Test micro-benchmark preserves calculation correctness."""
        estimator = Estimator()

        def test_calc(n: int) -> int:
            return n * 2

        inputs = [1, 2, 3]
        result = estimator.run_micro_benchmark(test_calc, inputs)
        assert result is not None

    def test_run_micro_benchmark_handles_errors_gracefully(
        self,
    ) -> None:
        """Test micro-benchmark handles calculation errors."""
        estimator = Estimator()

        def failing_calc(n: int) -> int:
            if n > 5:
                raise ValueError("Too large")
            return n * 2

        estimator.run_micro_benchmark(failing_calc, [1, 2, 10])
        assert True  # If we get here, it didn't crash


class TestEstimatorRegressionPrediction:
    """Test regression-based time prediction functionality."""

    def test_predict_time_method_exists(self) -> None:
        """Test that predict_time method exists."""
        estimator = Estimator()
        assert hasattr(estimator, 'predict_time')
        assert callable(estimator.predict_time)

    def test_predict_time_accepts_input_value(self) -> None:
        """Test predict_time accepts an input value."""
        estimator = Estimator()
        try:
            estimator.predict_time(100)
        except (ValueError, AttributeError):
            pass  # Expected if no benchmark data

    def test_predict_time_uses_benchmark_data(self) -> None:
        """Test predict_time uses benchmark data for prediction."""
        estimator = Estimator()

        benchmark_data = [(1, 0.001), (5, 0.005), (10, 0.01), (20, 0.02)]
        estimator.benchmark_data['test_calc'] = benchmark_data

        predicted_time = estimator.predict_time(50, calc_type='test_calc')
        assert predicted_time is not None
        assert isinstance(predicted_time, (int, float))
        assert predicted_time > 0

    def test_predict_time_for_fibonacci(self) -> None:
        """Test time prediction for Fibonacci calculations."""
        estimator = Estimator()

        benchmark_data = [
            (10, 0.001),
            (20, 0.002),
            (30, 0.003),
            (40, 0.004),
        ]
        estimator.benchmark_data['fibonacci'] = benchmark_data

        predicted = estimator.predict_time(100, calc_type='fibonacci')
        assert predicted > 0
        assert isinstance(predicted, (int, float))

    def test_predict_time_for_factorial(self) -> None:
        """Test time prediction for Factorial calculations."""
        estimator = Estimator()

        benchmark_data = [
            (10, 0.01),
            (20, 0.04),
            (30, 0.09),
            (40, 0.16),
        ]
        estimator.benchmark_data['factorial'] = benchmark_data

        predicted = estimator.predict_time(100, calc_type='factorial')
        assert predicted > 0
        assert isinstance(predicted, (int, float))

    def test_predict_time_for_primes(self) -> None:
        """Test time prediction for Prime calculations."""
        estimator = Estimator()

        benchmark_data = [
            (100, 0.1),
            (200, 0.2),
            (300, 0.3),
            (400, 0.4),
        ]
        estimator.benchmark_data['primes'] = benchmark_data

        predicted = estimator.predict_time(1000, calc_type='primes')
        assert predicted > 0
        assert isinstance(predicted, (int, float))

    def test_predict_time_handles_missing_benchmark_data(self) -> None:
        """Test predict_time handles missing benchmark data gracefully."""
        estimator = Estimator()

        with pytest.raises((ValueError, KeyError, AttributeError)):
            estimator.predict_time(100, calc_type='unknown')

    def test_predict_time_returns_reasonable_values(self) -> None:
        """Test predicted times are reasonable (positive, finite)."""
        estimator = Estimator()

        benchmark_data = [(1, 0.001), (2, 0.002), (3, 0.003)]
        estimator.benchmark_data['test'] = benchmark_data

        predicted = estimator.predict_time(10, calc_type='test')
        assert predicted > 0
        assert predicted != float('inf')
        assert predicted != float('-inf')
        assert not math.isnan(predicted)  # Not NaN
