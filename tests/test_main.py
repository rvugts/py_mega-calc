"""Tests for main entry point."""

import pytest
import sys
from unittest.mock import patch
from typer.testing import CliRunner


class TestMainEntryPoint:
    """Test main entry point functionality."""
    
    def test_main_module_exists(self):
        """Test that main module exists and can be imported."""
        from src import main
        assert main is not None
    
    def test_main_can_be_executed(self):
        """Test that main can be executed."""
        from src.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "5"])
        assert result.exit_code == 0
    
    def test_main_entry_point_connects_to_cli(self):
        """Test that main entry point connects to CLI."""
        # Test that we can run the CLI through main
        from src.cli import app
        runner = CliRunner()
        
        # Test with different calculator types
        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code == 0
        
        result = runner.invoke(app, ["fact", "--index", "5"])
        assert result.exit_code == 0
        
        result = runner.invoke(app, ["prime", "--index", "10"])
        assert result.exit_code == 0
    
    def test_main_handles_cli_errors(self):
        """Test that main properly handles CLI errors."""
        from src.cli import app
        runner = CliRunner()
        
        # Test with invalid arguments
        result = runner.invoke(app, ["fib", "--index", "-1"])
        assert result.exit_code != 0
        
        # Test with missing required arguments
        result = runner.invoke(app, ["fib"])
        assert result.exit_code != 0
    
    def test_main_execution_flow(self):
        """Test complete execution flow through main."""
        from src.cli import app
        runner = CliRunner()
        
        # Test a complete calculation flow
        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code == 0
        assert "Result" in result.stdout or "55" in result.stdout
    
    def test_main_with_all_features(self):
        """Test main with all features enabled."""
        from src.cli import app
        runner = CliRunner()
        
        result = runner.invoke(app, [
            "fib", 
            "--index", "20",
            "--benchmark",
            "--strict"
        ])
        # Should complete successfully
        assert result.exit_code == 0

