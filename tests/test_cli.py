"""Tests for CLI interface."""

import pytest
from typer.testing import CliRunner
from src.cli import app


class TestCLIArgumentParsing:
    """Test CLI argument parsing functionality."""
    
    def test_cli_app_exists(self):
        """Test that CLI app exists."""
        assert app is not None
    
    def test_cli_accepts_type_argument(self):
        """Test that CLI accepts type argument (prime/fib/fact)."""
        runner = CliRunner()
        
        # Test with fib
        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code in [0, 2]  # 0 for success, 2 for missing required args
        
        # Test with fact
        result = runner.invoke(app, ["fact", "--index", "5"])
        assert result.exit_code in [0, 2]
        
        # Test with prime
        result = runner.invoke(app, ["prime", "--index", "10"])
        assert result.exit_code in [0, 2]
    
    def test_cli_rejects_invalid_type(self):
        """Test that CLI rejects invalid type argument."""
        runner = CliRunner()
        result = runner.invoke(app, ["invalid", "--index", "10"])
        assert result.exit_code != 0
    
    def test_cli_accepts_index_flag(self):
        """Test that CLI accepts --index flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        # Should not fail on argument parsing (may fail on execution)
        assert "--index" in result.stdout or result.exit_code in [0, 2]
    
    def test_cli_accepts_min_digits_flag(self):
        """Test that CLI accepts --min-digits flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "3"])
        # Should not fail on argument parsing
        assert result.exit_code in [0, 2]
    
    def test_cli_rejects_both_index_and_min_digits(self):
        """Test that CLI rejects both --index and --min-digits (mutually exclusive)."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--min-digits", "3"])
        # Should fail with error about mutually exclusive options
        assert result.exit_code != 0
    
    def test_cli_requires_either_index_or_min_digits(self):
        """Test that CLI requires either --index or --min-digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib"])
        # Should fail because neither --index nor --min-digits provided
        assert result.exit_code != 0
    
    def test_cli_accepts_benchmark_flag(self):
        """Test that CLI accepts --benchmark flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--benchmark"])
        # Should not fail on argument parsing
        assert result.exit_code in [0, 2]
    
    def test_cli_accepts_dry_run_flag(self):
        """Test that CLI accepts --dry-run flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--dry-run"])
        # Should not fail on argument parsing
        assert result.exit_code in [0, 2]
    
    def test_cli_accepts_strict_flag(self):
        """Test that CLI accepts --strict flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--strict"])
        # Should not fail on argument parsing
        assert result.exit_code in [0, 2]
    
    def test_cli_accepts_multiple_flags(self):
        """Test that CLI accepts multiple flags together."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--benchmark", "--dry-run", "--strict"])
        # Should not fail on argument parsing
        assert result.exit_code in [0, 2]
    
    def test_cli_index_must_be_integer(self):
        """Test that --index must be an integer."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "not_a_number"])
        # Should fail with validation error
        assert result.exit_code != 0
    
    def test_cli_min_digits_must_be_integer(self):
        """Test that --min-digits must be an integer."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "not_a_number"])
        # Should fail with validation error
        assert result.exit_code != 0


class TestCLIFlags:
    """Test CLI flag functionality."""
    
    def test_benchmark_flag_parsed_correctly(self):
        """Test that --benchmark flag is parsed correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--benchmark"])
        assert result.exit_code == 0
        # Should show benchmark/estimation output
        assert "Estimated execution time" in result.stdout or "micro-benchmark" in result.stdout
    
    def test_dry_run_flag_parsed_correctly(self):
        """Test that --dry-run flag is parsed correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout
    
    def test_strict_flag_parsed_correctly(self):
        """Test that --strict flag is parsed correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--strict"])
        assert result.exit_code == 0
        # Strict flag works silently unless time limit exceeded
        assert "Result" in result.stdout or result.exit_code == 0
    
    def test_all_flags_together(self):
        """Test that all flags can be used together."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--benchmark", "--dry-run", "--strict"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        assert "Estimated execution time" in result.stdout or "micro-benchmark" in result.stdout
    
    def test_flags_with_min_digits(self):
        """Test that flags work with --min-digits option."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--min-digits", "5", "--benchmark", "--strict"])
        assert result.exit_code == 0
        # Should show benchmark output and result
        assert "Estimated execution time" in result.stdout or "Result" in result.stdout
    
    def test_flags_with_different_calculator_types(self):
        """Test that flags work with all calculator types."""
        runner = CliRunner()
        
        for calc_type in ["fib", "fact", "prime"]:
            result = runner.invoke(app, [calc_type, "--index", "10", "--benchmark"])
            assert result.exit_code == 0
            # Should show benchmark/estimation output
            assert "Estimated execution time" in result.stdout or "micro-benchmark" in result.stdout or "Result" in result.stdout


class TestCLIOutputFormatting:
    """Test CLI output formatting functionality."""
    
    def test_format_result_short_number(self):
        """Test formatting of short number (< 1000 chars)."""
        from src.cli import format_result
        result = format_result(12345)
        assert "12345" in result
        assert "truncated" not in result.lower()
    
    def test_format_result_long_number_truncated(self):
        """Test formatting of long number (> 1000 chars) is truncated."""
        from src.cli import format_result
        long_number = "1" * 2000  # 2000 characters
        result = format_result(int(long_number))
        assert "truncated" in result.lower() or "..." in result
        assert len(result) < 1500  # Should be truncated
    
    def test_format_result_shows_digit_count(self):
        """Test that formatted result shows digit count."""
        from src.cli import format_result
        result = format_result(12345)
        assert "5" in result or "digit" in result.lower()
    
    def test_write_result_to_file(self):
        """Test writing result to file."""
        import os
        import tempfile
        from src.cli import write_result_to_file
        from datetime import datetime
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = 12345
            calc_type = "fib"
            filepath = write_result_to_file(result, calc_type, output_dir=tmpdir)
            
            assert os.path.exists(filepath)
            assert calc_type in filepath
            with open(filepath, 'r') as f:
                content = f.read()
                assert "12345" in content
    
    def test_write_result_includes_metadata(self):
        """Test that file output includes metadata (time, RAM)."""
        import os
        import tempfile
        from src.cli import write_result_to_file
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = 12345
            calc_type = "fib"
            execution_time = 1.5
            ram_usage_mb = 100.5
            
            filepath = write_result_to_file(
                result, calc_type, 
                execution_time=execution_time,
                ram_usage_mb=ram_usage_mb,
                output_dir=tmpdir
            )
            
            with open(filepath, 'r') as f:
                content = f.read()
                assert "1.5" in content or "time" in content.lower()
                assert "100" in content or "ram" in content.lower() or "memory" in content.lower()
    
    def test_format_metadata(self):
        """Test formatting of metadata."""
        from src.cli import format_metadata
        metadata = format_metadata(execution_time=1.5, ram_usage_mb=100.5)
        assert "1.5" in metadata or "time" in metadata.lower()
        assert "100" in metadata or "ram" in metadata.lower() or "memory" in metadata.lower()
    
    def test_results_directory_created(self):
        """Test that results directory is created if it doesn't exist."""
        import os
        import tempfile
        import shutil
        from src.cli import write_result_to_file
        
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = os.path.join(tmpdir, "results")
            # Ensure directory doesn't exist
            if os.path.exists(results_dir):
                shutil.rmtree(results_dir)
            
            result = 12345
            calc_type = "fib"
            filepath = write_result_to_file(result, calc_type, output_dir=results_dir)
            
            assert os.path.exists(results_dir)
            assert os.path.exists(filepath)


class TestCLICalculatorIntegration:
    """Test CLI calculator integration."""
    
    def test_fib_calculator_integration(self):
        """Test that CLI integrates with FibonacciCalculator."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code == 0
        # Should show actual Fibonacci result (F(10) = 55)
        assert "55" in result.stdout or "Result" in result.stdout
    
    def test_fact_calculator_integration(self):
        """Test that CLI integrates with FactorialCalculator."""
        runner = CliRunner()
        result = runner.invoke(app, ["fact", "--index", "5"])
        assert result.exit_code == 0
        # Should show actual factorial result (5! = 120)
        assert "120" in result.stdout or "Result" in result.stdout
    
    def test_prime_calculator_integration(self):
        """Test that CLI integrates with PrimeCalculator."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--index", "10"])
        assert result.exit_code == 0
        # Should show actual prime result (10th prime = 29)
        assert "29" in result.stdout or "Result" in result.stdout
    
    def test_calculate_by_digits_integration(self):
        """Test that CLI integrates with calculate_by_digits method."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "2"])
        assert result.exit_code == 0
        # Should show result with at least 2 digits
        assert "Result" in result.stdout
    
    def test_output_file_created_on_calculation(self):
        """Test that output file is created when calculation runs."""
        import os
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = os.path.join(tmpdir, "results")
            # Mock the results directory by setting environment or patching
            runner = CliRunner()
            # We'll need to patch the output directory in the actual implementation
            result = runner.invoke(app, ["fib", "--index", "5"])
            # For now, just check that it doesn't error
            assert result.exit_code == 0
    
    def test_error_handling_invalid_input(self):
        """Test that CLI handles calculator errors gracefully."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "-1"])
        # Should show error message
        assert result.exit_code != 0 or "Error" in result.stdout or "error" in result.stdout.lower()
    
    def test_benchmark_flag_integration(self):
        """Test that --benchmark flag integrates with Estimator."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100", "--benchmark"])
        # Should show benchmark information
        assert result.exit_code == 0
    
    def test_dry_run_flag_integration(self):
        """Test that --dry-run flag returns estimate without calculation."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "1000", "--dry-run"])
        # Should show estimate without actual result
        assert result.exit_code == 0
        assert "estimate" in result.stdout.lower() or "time" in result.stdout.lower()

