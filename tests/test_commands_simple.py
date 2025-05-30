#!/usr/bin/env python3
"""
Simplified command test script for HiOllama application.
Tests the core user commands that we know work.
"""

import subprocess
import sys
from pathlib import Path

def test_single_command(command, expected_text, test_name):
    """Test a single command and check for specific expected text."""
    print(f"🔍 Testing {test_name}...")
    
    try:
        # Test the command manually like we did before
        cmd = f'echo "{command}" | python -m hiollama 1'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=Path(__file__).parent.parent
        )
        
        output = result.stdout
        
        if expected_text in output:
            print(f"✅ {test_name} works - Found '{expected_text}'")
            return True
        else:
            print(f"❌ {test_name} failed - Could not find '{expected_text}'")
            print(f"   Output preview: {output[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} timed out")
        return False
    except Exception as e:
        print(f"❌ {test_name} error: {e}")
        return False

def main():
    """Test core HiOllama commands."""
    print("🚀 HiOllama Simple Command Testing")
    print("=" * 45)
    
    # Test commands we know work
    tests = [
        ("/help", "GLOBAL HELP MENU", "/help command"),
        ("/showvars", "CHAT 1 VARIABLES", "/showvars command"),
        ("/quit", "Exiting and saving", "/quit command")
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expected, name in tests:
        if test_single_command(command, expected, name):
            passed += 1
        print()
    
    print("=" * 45)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All command tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
