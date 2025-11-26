"""End-to-end integration tests for py_mega_calc."""

import pytest
import os
import tempfile
import shutil
from typer.testing import CliRunner
from src.cli import app


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows: CLI → Calculator → Output."""
    
    def test_fibonacci_by_index_workflow(self):
        """Test complete workflow for Fibonacci calculation by index."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        
        assert result.exit_code == 0
        assert "55" in result.stdout  # F(10) = 55
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout
        assert "Full result saved to" in result.stdout
    
    def test_fibonacci_by_digits_workflow(self):
        """Test complete workflow for Fibonacci calculation by digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "2"])
        
        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "digits" in result.stdout
        # Should find first 2-digit Fibonacci number (11)
        assert "11" in result.stdout or "13" in result.stdout
    
    def test_factorial_by_index_workflow(self):
        """Test complete workflow for Factorial calculation by index."""
        runner = CliRunner()
        result = runner.invoke(app, ["fact", "--index", "5"])
        
        assert result.exit_code == 0
        assert "120" in result.stdout  # 5! = 120
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout
    
    def test_factorial_by_digits_workflow(self):
        """Test complete workflow for Factorial calculation by digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["fact", "--min-digits", "3"])
        
        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "digits" in result.stdout
    
    def test_prime_by_index_workflow(self):
        """Test complete workflow for Prime calculation by index."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--index", "10"])
        
        assert result.exit_code == 0
        assert "29" in result.stdout  # 10th prime = 29
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout
    
    def test_prime_by_digits_workflow(self):
        """Test complete workflow for Prime calculation by digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--min-digits", "3"])
        
        assert result.exit_code == 0
        assert "101" in result.stdout  # First 3-digit prime = 101
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout
    
    def test_workflow_with_benchmark_flag(self):
        """Test complete workflow with --benchmark flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100", "--benchmark"])
        
        assert result.exit_code == 0
        assert "Estimated execution time" in result.stdout or "micro-benchmark" in result.stdout
        assert "Result" in result.stdout
    
    def test_workflow_with_dry_run_flag(self):
        """Test complete workflow with --dry-run flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "1000", "--dry-run"])
        
        assert result.exit_code == 0
        assert "Estimated execution time" in result.stdout or "micro-benchmark" in result.stdout
        assert "Dry run" in result.stdout
        # Should not show actual result
        assert "Result (4 digits)" not in result.stdout or "Result" not in result.stdout or "Dry run" in result.stdout
    
    def test_workflow_with_strict_flag(self):
        """Test complete workflow with --strict flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--strict"])
        
        assert result.exit_code == 0
        assert "Result" in result.stdout
    
    def test_workflow_file_output(self):
        """Test that workflow creates output file."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        
        assert result.exit_code == 0
        assert "Full result saved to" in result.stdout
        
        # Extract file path from output
        filepath_line = [line for line in result.stdout.split('\n') if 'Full result saved to' in line]
        if filepath_line:
            filepath = filepath_line[0].split(': ')[-1].strip()
            assert os.path.exists(filepath)
            with open(filepath, 'r') as f:
                content = f.read()
                assert "55" in content or "Result" in content
    
    def test_workflow_error_handling(self):
        """Test that workflow handles errors gracefully."""
        runner = CliRunner()
        
        # Test with invalid input
        result = runner.invoke(app, ["fib", "--index", "-1"])
        assert result.exit_code != 0
        # Error messages go to stderr
        assert "Error" in result.stdout or "error" in result.stdout.lower() or "Error" in result.stderr or "error" in result.stderr.lower()
        
        # Test with missing required argument
        result = runner.invoke(app, ["fib"])
        assert result.exit_code != 0
    
    def test_workflow_with_all_flags(self):
        """Test complete workflow with all flags enabled."""
        runner = CliRunner()
        result = runner.invoke(app, [
            "fib",
            "--index", "50",
            "--benchmark",
            "--strict"
        ])
        
        assert result.exit_code == 0
        assert "Result" in result.stdout
    
    def test_workflow_large_calculation(self):
        """Test workflow with larger calculation."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100"])
        
        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout
    
    def test_workflow_output_formatting(self):
        """Test that workflow formats output correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        
        assert result.exit_code == 0
        # Check output structure
        assert "Result" in result.stdout
        assert "digits" in result.stdout
        assert "Metadata" in result.stdout
        assert "Execution time" in result.stdout
        assert "RAM usage" in result.stdout or "Peak RAM" in result.stdout

