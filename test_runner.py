#!/usr/bin/env python3
"""
Main test runner for HiOllama application.
Convenient entry point for running all tests.

Usage:
    python test_runner.py          # Run all tests
    python test_runner.py --quick  # Run only quick tests
    python test_runner.py cli      # Run only CLI tests
    python test_runner.py commands # Run only command tests
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run tests using the tests directory runner."""
    # Forward all arguments to the tests runner
    test_runner_path = Path(__file__).parent / "tests" / "run_tests.py"
    
    cmd = [sys.executable, str(test_runner_path)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
