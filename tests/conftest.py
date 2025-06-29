"""
Test configuration and shared utilities for CALOUS tests.
"""

import subprocess
import sys
from pathlib import Path

def run_calous_command(cmd, timeout=15):
    """Helper function to run CALOUS commands in tests."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=Path(__file__).parent.parent
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"

def assert_contains(text, expected_items, test_name=""):
    """Assert that text contains all expected items."""
    missing = []
    for expected in expected_items:
        if expected not in text:
            missing.append(expected)
    
    if missing:
        raise AssertionError(f"{test_name} - Missing: {missing}")
    
    return True

# Test configuration
DEFAULT_TIMEOUT = 15
TEST_CHAT_COUNT = 2
