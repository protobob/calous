#!/usr/bin/env python3
"""
Test runner for the CALOUS application.
Provides convenient access to all test suites.

Usage:
    python run_tests.py          # Run all tests
    python run_tests.py --quick  # Run only fast tests  
    python run_tests.py cli      # Run only CLI tests
    python run_tests.py commands # Run only command tests
    python run_tests.py full     # Run full integration tests
"""

import sys
import argparse
from pathlib import Path

# Add tests directory to path
sys.path.insert(0, str(Path(__file__).parent))

import test_cli
import test_config
import test_integration

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="CALOUS Test Runner")
    parser.add_argument('suite', nargs='?', default='all', 
                       choices=['all', 'cli', 'config', 'integration', 'quick'],
                       help='Test suite to run')
    parser.add_argument('--quick', action='store_true', 
                       help='Run only quick tests')
    
    args = parser.parse_args()
    
    print("🚀 CALOUS Test Runner")
    print("=" * 50)
    
    total_passed = 0
    total_tests = 0
    
    if args.suite in ['all', 'cli'] or args.quick:
        print("\n📋 Running CLI Tests...")
        result = test_cli.main()
        total_passed += (1 if result == 0 else 0)
        total_tests += 1
    
    if args.suite in ['all', 'config'] or args.quick:
        print("\n📋 Running Configuration Tests...")
        result = test_config.main()
        total_passed += (1 if result == 0 else 0)
        total_tests += 1
    
    if args.suite in ['all', 'integration'] and not args.quick:
        print("\n📋 Running Integration Tests...")
        result = test_integration.main()
        total_passed += (1 if result == 0 else 0)
        total_tests += 1
    
    if args.suite == 'quick':
        print("\n📋 Quick tests completed (CLI + Configuration)")
    
    print("\n" + "=" * 50)
    print(f"🏆 Overall Results: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 All test suites passed! CALOUS is working correctly.")
        return 0
    else:
        print("⚠️  Some test suites failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
