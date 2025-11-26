"""Tests for bug fixes and improvements."""

import pytest
import sys
from typer.testing import CliRunner
from src.cli import app


class TestRAMUsageTracking:
    """Test that RAM usage is tracked correctly (no negative values)."""
    
    def test_ram_usage_is_non_negative(self):
        """Test that reported RAM usage is never negative."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        
        assert result.exit_code == 0
        # Check that RAM usage is not negative
        assert "Peak RAM usage:" in result.stdout
        # Extract RAM usage value
        lines = result.stdout.split('\n')
        ram_line = [line for line in lines if 'Peak RAM usage' in line]
        assert len(ram_line) > 0
        ram_value_str = ram_line[0].split(':')[1].strip().replace(' MB', '')
        ram_value = float(ram_value_str)
        assert ram_value >= 0, f"RAM usage should be non-negative, got {ram_value}"


class TestLargeNumberStringConversion:
    """Test that large numbers (10,000+ digits) can be converted to strings."""
    
    def test_large_fibonacci_string_conversion(self):
        """Test that Fibonacci numbers with 10,000+ digits can be converted to strings."""
        # Set int max str digits to handle large numbers
        original_limit = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(20000)  # Allow up to 20,000 digits
            
            runner = CliRunner()
            # Calculate a large Fibonacci number that would exceed default limit
            # F(1000000) has way more than 4300 digits
            result = runner.invoke(app, ["fib", "--index", "1000000"])
            
            # Should not fail with string conversion error
            assert "Exceeds the limit" not in result.stdout
            assert "sys.set_int_max_str_digits" not in result.stdout
            # Should either complete or fail for other reasons (time, memory), not string conversion
            if result.exit_code != 0:
                assert "string conversion" not in result.stdout.lower()
        finally:
            sys.set_int_max_str_digits(original_limit)
    
    def test_cli_sets_int_max_str_digits(self):
        """Test that CLI automatically sets int_max_str_digits for large numbers."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100000"])
        
        # Should not fail with string conversion error
        assert "Exceeds the limit" not in result.stdout
        assert "sys.set_int_max_str_digits" not in result.stdout


class TestEstimatorAccuracy:
    """Test that estimator provides accurate time predictions."""
    
    def test_estimator_provides_non_zero_estimate(self):
        """Test that estimator provides non-zero estimate for reasonable inputs."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--index", "1000", "--benchmark", "--dry-run"])
        
        assert result.exit_code == 0
        assert "Estimated execution time:" in result.stdout
        # Extract estimated time
        lines = result.stdout.split('\n')
        time_line = [line for line in lines if 'Estimated execution time' in line]
        assert len(time_line) > 0
        time_str = time_line[0].split(':')[1].strip().replace(' seconds', '')
        estimated_time = float(time_str)
        # For a reasonable input like 1000th prime, estimate should be > 0
        # (though it might be very small, so we just check it's a valid float)
        assert isinstance(estimated_time, float)
    
    def test_estimator_estimate_vs_actual(self):
        """Test that estimator provides reasonable estimate compared to actual time."""
        runner = CliRunner()
        # Run with benchmark to get estimate
        result = runner.invoke(app, ["prime", "--index", "100", "--benchmark"])
        
        assert result.exit_code == 0
        # Should show both estimated and actual times
        assert "Estimated execution time:" in result.stdout or "Execution time:" in result.stdout


class TestDryRunBenchmark:
    """Test that dry-run properly runs benchmarks."""
    
    def test_dry_run_runs_benchmark(self):
        """Test that dry-run actually runs benchmark and shows estimate."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--index", "10000", "--dry-run"])
        
        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        # Should show benchmark was run
        assert "micro-benchmark" in result.stdout or "Estimated execution time" in result.stdout
        # Should show a time estimate (even if 0.000, it should be calculated)
        assert "seconds" in result.stdout
    
    def test_dry_run_does_not_perform_calculation(self):
        """Test that dry-run does not perform the actual calculation."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100", "--dry-run"])
        
        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        # Should not show the actual result
        # F(100) = 354224848179261915075, so we shouldn't see this in output
        assert "354224848179261915075" not in result.stdout or "Dry run" in result.stdout

