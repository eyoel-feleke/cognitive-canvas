"""
Pytest configuration file.

This file contains pytest-specific configurations and setup.
"""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test component interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that may take longer to run"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'unit' marker to test files that start with 'test_' and contain 'unit'
        if "unit" in item.nodeid.lower():
            item.add_marker("unit")
        
        # Add 'integration' marker to test files that contain 'integration'
        if "integration" in item.nodeid.lower():
            item.add_marker("integration")
        
        # Add 'slow' marker to tests that might be slow
        if any(keyword in item.nodeid.lower() for keyword in ["embedding", "openai", "large"]):
            item.add_marker("slow")