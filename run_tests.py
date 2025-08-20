#!/usr/bin/env python3
"""
Test runner script for ContentGraph MCP Server.

This script provides convenient commands for running tests with different configurations.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔥 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test runner for ContentGraph MCP")
    parser.add_argument(
        "--mode", 
        choices=["unit", "integration", "all", "coverage", "fast"], 
        default="all",
        help="Test mode to run"
    )
    parser.add_argument(
        "--file", 
        help="Run tests for a specific file (e.g., test_models.py)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    success = True
    
    if args.file:
        # Run specific test file
        cmd = base_cmd + [f"tests/{args.file}"]
        success = run_command(cmd, f"Running tests for {args.file}")
    
    elif args.mode == "unit":
        # Run only unit tests
        cmd = base_cmd + ["-m", "unit"]
        success = run_command(cmd, "Running unit tests")
    
    elif args.mode == "integration":
        # Run only integration tests
        cmd = base_cmd + ["-m", "integration"]
        success = run_command(cmd, "Running integration tests")
    
    elif args.mode == "fast":
        # Run tests without coverage (faster)
        cmd = base_cmd + ["--no-cov"]
        success = run_command(cmd, "Running fast tests (no coverage)")
    
    elif args.mode == "coverage":
        # Run tests with detailed coverage
        cmd = base_cmd + [
            "--cov=src", 
            "--cov-report=html", 
            "--cov-report=xml"
        ]
        success = run_command(cmd, "Running tests with coverage")
        
        if success:
            print(f"\n📊 Coverage report generated:")
            print(f"   - HTML: htmlcov/index.html")
            print(f"   - XML: coverage.xml")
    
    else:  # args.mode == "all"
        # Run all tests with coverage
        cmd = base_cmd + [
            "--cov=src", 
            "--cov-report=html", 
            "--cov-report=term-missing"
        ]
        success = run_command(cmd, "Running all tests with coverage")
    
    if success:
        print(f"\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()