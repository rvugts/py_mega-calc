"""Benchmarking utility for predicting calculation time."""

import time
import math
from typing import Callable, List, Dict, Tuple, Any, Optional


class Estimator:
    """Regression-based benchmarking utility for predicting calculation time.
    
    Runs micro-benchmarks on startup (or on demand) to predict calculation time
    for large inputs. Supports Fibonacci, Factorial, and Prime calculations.
    """
    
    def __init__(self):
        """Initialize the Estimator."""
        self.benchmark_data: Dict[str, List[Tuple[int, float]]] = {}
    
    def run_micro_benchmark(
        self, 
        calculation_func: Callable[[int], Any], 
        input_values: List[int]
    ) -> List[Tuple[int, float]]:
        """Run micro-benchmark for a calculation function with given input values.
        
        Executes the calculation function for each input value and measures
        the execution time. Returns a list of (input_value, execution_time) tuples.
        
        Args:
            calculation_func: The calculation function to benchmark (takes int, returns Any)
            input_values: List of input values to test
            
        Returns:
            List of tuples (input_value, execution_time_seconds)
        """
        results = []
        
        for input_val in input_values:
            try:
                start_time = time.perf_counter()
                calculation_func(input_val)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                # Always add results, even if very small (for regression to work)
                results.append((input_val, execution_time))
            except Exception:
                # Skip inputs that cause errors
                continue
        
        return results
    
    def predict_time(self, input_value: int, calc_type: str = 'default') -> float:
        """Predict execution time for a given input value using regression.
        
        Uses benchmark data to fit a regression model and predict execution time.
        Supports different complexity models:
        - Fibonacci: T(n) ∝ log n
        - Factorial: T(n) ∝ n (log n)²
        - Primes: Probabilistic, density-based
        
        Args:
            input_value: The input value to predict time for
            calc_type: Type of calculation ('fibonacci', 'factorial', 'primes', or 'default')
            
        Returns:
            Predicted execution time in seconds
            
        Raises:
            ValueError: If no benchmark data is available for the calculation type
        """
        if calc_type not in self.benchmark_data or not self.benchmark_data[calc_type]:
            raise ValueError(f"No benchmark data available for calculation type: {calc_type}")
        
        benchmark_points = self.benchmark_data[calc_type]
        
        if len(benchmark_points) < 2:
            # Not enough data points, use simple linear extrapolation
            if len(benchmark_points) == 1:
                n, t = benchmark_points[0]
                if n == 0:
                    return t
                return t * (input_value / n)
            else:
                raise ValueError("Insufficient benchmark data for prediction")
        
        # Sort by input value
        sorted_points = sorted(benchmark_points, key=lambda x: x[0])
        inputs = [x[0] for x in sorted_points]
        times = [x[1] for x in sorted_points]
        
        # Choose regression model based on calculation type
        if calc_type == 'fibonacci':
            # T(n) ∝ log n
            # Transform: log_inputs = log(n), fit linear: time = a * log(n) + b
            log_inputs = [math.log(max(1, n)) for n in inputs]
            predicted = self._linear_regression_predict(log_inputs, times, math.log(max(1, input_value)))
        elif calc_type == 'factorial':
            # T(n) ∝ n (log n)²
            # Transform: transformed = n * (log n)², fit linear
            transformed_inputs = [n * (math.log(max(1, n)) ** 2) for n in inputs]
            transformed_value = input_value * (math.log(max(1, input_value)) ** 2)
            predicted = self._linear_regression_predict(transformed_inputs, times, transformed_value)
        elif calc_type == 'primes':
            # Primes: Estimate based on average density 1/ln(N) per spec
            # Prime number theorem: density of primes around N is ~1/ln(N)
            # To find Nth prime, need to check ~N*ln(N) numbers
            # So time scales as T(n) ∝ n * ln(n)
            # Transform: transformed = n * ln(n), fit linear
            transformed_inputs = [n * math.log(max(1, n)) for n in inputs]
            transformed_value = input_value * math.log(max(1, input_value))
            predicted = self._linear_regression_predict(transformed_inputs, times, transformed_value)
        else:
            # Default: simple linear regression
            predicted = self._linear_regression_predict(inputs, times, input_value)
        
        # Ensure prediction is positive and reasonable
        # For very small predictions (< 0.001), use a minimum threshold based on input size
        if predicted < 0.001 and input_value > 1000:
            # For large inputs, ensure minimum estimate
            predicted = max(0.001, predicted)
        
        return max(0.0, predicted)
    
    def _linear_regression_predict(self, x_values: List[float], y_values: List[float], x_predict: float) -> float:
        """Perform simple linear regression and predict y for given x.
        
        Uses least squares method: y = a*x + b
        
        Args:
            x_values: List of x values from benchmark data
            y_values: List of y values (times) from benchmark data
            x_predict: x value to predict y for
            
        Returns:
            Predicted y value
        """
        n = len(x_values)
        if n < 2:
            # Fallback to simple ratio
            if n == 1 and x_values[0] != 0:
                return y_values[0] * (x_predict / x_values[0])
            return 0.0
        
        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        # Calculate slope (a) and intercept (b)
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            # All x values are the same, return mean y
            return y_mean
        
        a = numerator / denominator
        b = y_mean - a * x_mean
        
        # Predict
        return a * x_predict + b

