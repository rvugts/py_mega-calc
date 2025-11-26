# Time Estimation Logic: Spec vs Implementation

## Specification Requirements (from spec.md lines 155-159)

The spec requires time estimation based on these complexity models:

1. **Fibonacci**: $T(n) \propto \log n$
2. **Factorial**: $T(n) \propto n (\log n)^2$
3. **Primes**: Probabilistic, highly variance-dependent. Estimate based on average density $1/\ln(N)$.

## Previous Implementation (Before Fix)

### ✅ Fibonacci - Matched Spec
- **Implementation**: Uses log transformation
  ```python
  log_inputs = [math.log(max(1, n)) for n in inputs]
  predicted = self._linear_regression_predict(log_inputs, times, math.log(max(1, input_value)))
  ```
- **Status**: Correctly implements $T(n) \propto \log n$

### ✅ Factorial - Matched Spec
- **Implementation**: Uses $n (\log n)^2$ transformation
  ```python
  transformed_inputs = [n * (math.log(max(1, n)) ** 2) for n in inputs]
  transformed_value = input_value * (math.log(max(1, input_value)) ** 2)
  predicted = self._linear_regression_predict(transformed_inputs, times, transformed_value)
  ```
- **Status**: Correctly implements $T(n) \propto n (\log n)^2$

### ❌ Primes - Did NOT Match Spec
- **Previous Implementation**: Used simple linear regression with ad-hoc scaling
  ```python
  predicted = self._linear_regression_predict(inputs, times, input_value)
  # Ad-hoc scaling for large inputs
  if input_value > max_benchmark_input * 10:
      log_ratio = math.log(input_value / max_benchmark_input)
      predicted = predicted * (1 + log_ratio * 0.5)
  ```
- **Problem**: 
  - Used linear regression on raw input values ($T(n) \propto n$)
  - Applied ad-hoc log scaling factor instead of proper density-based model
  - Did not use the $1/\ln(N)$ density model from the spec

## Current Implementation (After Fix)

### Primes - Now Matches Spec
- **Implementation**: Uses $n \ln(n)$ transformation based on prime density
  ```python
  # Prime number theorem: density of primes around N is ~1/ln(N)
  # To find Nth prime, need to check ~N*ln(N) numbers
  # So time scales as T(n) ∝ n * ln(n)
  transformed_inputs = [n * math.log(max(1, n)) for n in inputs]
  transformed_value = input_value * math.log(max(1, input_value))
  predicted = self._linear_regression_predict(transformed_inputs, times, transformed_value)
  ```
- **Status**: Now correctly implements density-based estimation using $1/\ln(N)$ model

## Mathematical Justification

The spec's requirement for primes is based on the **Prime Number Theorem**:
- The density of primes around $N$ is approximately $1/\ln(N)$
- To find the $N$-th prime, you need to check approximately $N \ln(N)$ numbers
- Therefore, time complexity scales as $T(n) \propto n \ln(n)$

This is now properly implemented using the same transformation approach as Fibonacci and Factorial:
- Transform inputs using the theoretical complexity model
- Fit linear regression on transformed space
- Predict in transformed space

## Summary

| Calculator | Spec Requirement | Previous Implementation | Current Implementation |
|------------|-----------------|------------------------|----------------------|
| Fibonacci  | $T(n) \propto \log n$ | ✅ Correct | ✅ Correct |
| Factorial  | $T(n) \propto n (\log n)^2$ | ✅ Correct | ✅ Correct |
| Primes     | Based on density $1/\ln(N)$ → $T(n) \propto n \ln(n)$ | ❌ Linear + ad-hoc scaling | ✅ $n \ln(n)$ transformation |

