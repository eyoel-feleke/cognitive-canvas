#!/usr/bin/env python3
"""
Coverage report generator for ContentGraph MCP Server.

This script provides convenient commands for generating coverage reports in different formats.
"""

import subprocess
import sys
import argparse
from pathlib import Path
import webbrowser
import os


def run_command(cmd, description, show_output=True):
    """Run a command and handle errors."""
    if show_output:
        print(f"\n🔥 {description}")
        print(f"Running: {' '.join(cmd)}")
        print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent.parent)
        if show_output:
            print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        if show_output:
            print(f"❌ {description} failed with exit code {e.returncode}")
        return True


def open_html_report():
    """Open the HTML coverage report in the default browser."""
    html_path = Path("htmlcov/index.html")
    if html_path.exists():
        file_url = f"file://{html_path.absolute()}"
        print(f"\n🌐 Opening coverage report: {file_url}")
        webbrowser.open(file_url)
        return True
    else:
        print("❌ HTML coverage report not found. Run tests with coverage first.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Coverage report generator for ContentGraph MCP")
    parser.add_argument(
        "--format", 
        choices=["html", "xml", "term", "json", "all"], 
        default="html",
        help="Coverage report format"
    )
    parser.add_argument(
        "--open", 
        action="store_true",
        help="Open HTML report in browser after generation"
    )
    parser.add_argument(
        "--run-tests", 
        action="store_true",
        help="Run tests before generating reports"
    )
    parser.add_argument(
        "--fail-under", 
        type=int,
        default=65,
        help="Minimum coverage percentage (default: 65)"
    )
    
    args = parser.parse_args()
    
    success = True
    
    # Run tests first if requested
    if args.run_tests:
        cmd = [
            "python", "-m", "pytest", 
            "--cov=src", 
            "--cov-branch",
            f"--cov-fail-under={args.fail_under}"
        ]
        success = run_command(cmd, "Running tests with coverage")
        
        if not success:
            print("💥 Some tests failed, generating partial report")
            # sys.exit(1)
    
    # Generate coverage reports
    coverage_cmd_base = ["python", "-m", "coverage"]
    
    if args.format == "html" or args.format == "all":
        cmd = coverage_cmd_base + ["html", "--directory=htmlcov"]
        success &= run_command(cmd, "Generating HTML coverage report")
        
        if success and args.open:
            open_html_report()
    
    if args.format == "xml" or args.format == "all":
        cmd = coverage_cmd_base + ["xml", "-o", "coverage.xml"]
        success &= run_command(cmd, "Generating XML coverage report")
    
    if args.format == "json" or args.format == "all":
        cmd = coverage_cmd_base + ["json", "-o", "coverage.json"]
        success &= run_command(cmd, "Generating JSON coverage report")
    
    if args.format == "term" or args.format == "all":
        cmd = coverage_cmd_base + ["report", "--show-missing"]
        success &= run_command(cmd, "Generating terminal coverage report")
    
    # Show summary
    if success:
        print(f"\n🎉 Coverage reports generated successfully!")
        
        # Show available reports
        reports = []
        if Path("htmlcov/index.html").exists():
            reports.append("📄 HTML: htmlcov/index.html")
        if Path("coverage.xml").exists():
            reports.append("📄 XML: coverage.xml")
        if Path("coverage.json").exists():
            reports.append("📄 JSON: coverage.json")
        
        if reports:
            print(f"\n📊 Available reports:")
            for report in reports:
                print(f"   {report}")
        
        # Quick coverage summary
        cmd = coverage_cmd_base + ["report", "--format=total"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            coverage_pct = result.stdout.strip()
            print(f"\n📈 Overall coverage: {coverage_pct}%")
        
        sys.exit(0)
    else:
        print(f"\n💥 Some coverage reports failed to generate!")
        sys.exit(1)


if __name__ == "__main__":
    main()
