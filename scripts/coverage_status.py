#!/usr/bin/env python3
"""
Quick coverage status checker for ContentGraph MCP Server.
"""

import subprocess
import sys
from pathlib import Path
import json


def get_coverage_data():
    """Get coverage data from coverage.json if available."""
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        with open(coverage_file) as f:
            return json.load(f)
    return None


def get_coverage_summary():
    """Get coverage summary from coverage command."""
    try:
        result = subprocess.run(
            ["python", "-m", "coverage", "report", "--format=total"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return None


def main():
    print("🔍 ContentGraph MCP Coverage Status")
    print("=" * 40)
    
    # Check if coverage data exists
    coverage_file = Path("coverage.json")
    html_report = Path("htmlcov/index.html")
    xml_report = Path("coverage.xml")
    
    # Get coverage percentage
    coverage_pct = get_coverage_summary()
    
    if coverage_pct is not None:
        print(f"📊 Overall Coverage: {coverage_pct:.1f}%")
        
        if coverage_pct >= 90:
            print("🟢 Excellent coverage!")
        elif coverage_pct >= 80:
            print("🟡 Good coverage")
        elif coverage_pct >= 70:
            print("🟠 Fair coverage - consider adding more tests")
        else:
            print("🔴 Low coverage - needs improvement")
    else:
        print("❌ No coverage data found")
        print("   Run 'make test' to generate coverage data")
    
    print("\n📄 Available Reports:")
    
    if html_report.exists():
        print("✅ HTML Report: htmlcov/index.html")
    else:
        print("❌ HTML Report: Not found")
    
    if xml_report.exists():
        print("✅ XML Report: coverage.xml")
    else:
        print("❌ XML Report: Not found")
    
    if coverage_file.exists():
        print("✅ JSON Report: coverage.json")
    else:
        print("❌ JSON Report: Not found")
    
    print(f"\n🛠️  Quick Commands:")
    print(f"   make test         - Run tests with coverage")
    print(f"   make coverage-html - Generate HTML report")
    print(f"   make coverage-report - Show detailed report")


if __name__ == "__main__":
    main()
