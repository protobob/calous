#!/usr/bin/env python3
"""
Comprehensive test script for CALOUS application.
Tests command-line arguments, validation, and basic functionality.

Usage:
    python test_calous.py          # Run all tests
    python test_calous.py --quick  # Run only fast tests
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

# Add the parent directory to the path to import calous modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from hiollama.constants import APP_VERSION

def run_command(cmd, timeout=10):
    """Run a command with timeout and return result."""
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

def test_help():
    """Test help command."""
    print("🔍 Testing --help command...")
    code, stdout, stderr = run_command("python -m hiollama --help")
    
    if code == 0 and "Hi, Ollama! - Multi-chat AI interface" in stdout:
        print("✅ Help command works")
        return True
    else:
        print(f"❌ Help command failed: {stderr}")
        return False

def test_argument_validation():
    """Test argument validation."""
    print("\n🔍 Testing argument validation...")
    
    # Test invalid number of chats (0)
    code, stdout, stderr = run_command("python -m hiollama 0")
    if code == 1 and "Error: Number of chats must be at least 1" in stdout:
        print("✅ Validates minimum chats (1)")
    else:
        print(f"❌ Failed to validate minimum chats: {stdout}")
        return False
    
    # Test exceeding maximum chats
    code, stdout, stderr = run_command("python -m hiollama 15")
    if code == 1 and "Error: Number of chats cannot exceed 14" in stdout:
        print("✅ Validates maximum chats (14)")
    else:
        print(f"❌ Failed to validate maximum chats: {stdout}")
        return False
    
    # Test custom max-chats override
    code, stdout, stderr = run_command("python -m hiollama 10 --max-chats 5")
    if code == 1 and "Error: Number of chats cannot exceed 5" in stdout:
        print("✅ Validates custom max-chats")
    else:
        print(f"❌ Failed to validate custom max-chats: {stdout}")
        return False
    
    return True

def test_app_startup():
    """Test application startup with different configurations."""
    print("\n🔍 Testing application startup...")    # Test with 1 chat
    print("  Testing 1 chat...")
    code, stdout, stderr = run_command('echo "/quit" | python -m hiollama 1', timeout=15)
    if "HIOLLAMA!" in stdout and APP_VERSION in stdout and "ACTIVE CHATS: ()" in stdout:
        print("✅ 1 chat configuration works")
    else:
        print(f"❌ 1 chat failed: {stdout[:200]}...")
        return False
      # Test with default (flexible number of chats)
    print("  Testing default configuration...")
    code, stdout, stderr = run_command('echo "/quit" | python -m hiollama', timeout=15)
    if "HIOLLAMA!" in stdout and "(/switch [1-" in stdout and "] to change)" in stdout:
        print("✅ Default configuration works")
    else:
        print(f"❌ Default configuration failed: {stdout[:200]}...")
        return False
    
    # Test with maximum (14 chats)
    print("  Testing maximum (14 chats)...")
    code, stdout, stderr = run_command('echo "/quit" | python -m hiollama 14', timeout=15)
    if "HIOLLAMA!" in stdout and "(/switch [1-14] to change)" in stdout:
        print("✅ Maximum 14 chat configuration works")
    else:
        print(f"❌ Maximum configuration failed: {stdout[:200]}...")
        return False
    
    return True

def test_commands():
    """Test various application commands."""
    print("\n🔍 Testing application commands...")
    
    # Test help command
    print("  Testing /help command...")
    code, stdout, stderr = run_command('echo "/help" | python -m hiollama 2', timeout=15)
    if "GLOBAL HELP MENU" in stdout and "General Commands:" in stdout:
        print("✅ /help command works")
    else:
        print(f"❌ /help command failed: {stdout[:200]}...")
        return False
    
    # Test showvars command
    print("  Testing /showvars command...")
    code, stdout, stderr = run_command('echo "/showvars" | python -m hiollama 1', timeout=15)
    if "CHAT 1 VARIABLES" in stdout and "Selected Model:" in stdout:
        print("✅ /showvars command works")
    else:
        print(f"❌ /showvars command failed: {stdout[:200]}...")
        return False
    
    return True

def test_commands_comprehensive():
    """Test all major commands systematically."""
    print("\n🔍 Testing comprehensive command set...")
    
    commands_to_test = [
        ("/help", "GLOBAL HELP MENU"),
        ("/showvars", "Selected Model:"),
        ("/model", "Available models:"),
        ("/history", "Chat history"),  # This might show empty initially
        ("/toggle_log", "Logging"),
        ("/quit", "Exiting and saving")
    ]
    
    for cmd, expected in commands_to_test:
        print(f"  Testing {cmd}...")
        code, stdout, stderr = run_command(f'echo "{cmd}" | python -m hiollama 1', timeout=15)
        if expected in stdout:
            print(f"✅ {cmd} works")
        else:
            print(f"❌ {cmd} failed or returned unexpected output")
            return False
    
    return True

def test_ui_elements():
    """Test UI elements and formatting."""
    print("\n🔍 Testing UI elements...")
    
    # Test that Unicode issue is fixed
    code, stdout, stderr = run_command('echo "/quit" | python -m hiollama 4', timeout=15)
    if ">" in stdout and not "►" in stdout:
        print("✅ Unicode compatibility fixed (using > instead of ►)")
    else:
        print(f"❌ Unicode issue may still exist")
        return False
    
    # Test chat color coding and numbering
    if "> 1:" in stdout and "  2:" in stdout and "  3:" in stdout and "  4:" in stdout:
        print("✅ Chat numbering and active chat marking works")
    else:
        print(f"❌ Chat numbering failed")
        return False
    
    return True

def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="HiOllama Test Suite")
    parser.add_argument('--quick', action='store_true', help='Run only quick tests')
    parser.add_argument('--commands-only', action='store_true', help='Test only commands')
    args = parser.parse_args()
    
    print("🚀 HiOllama Comprehensive Test Suite")
    print("=" * 50)
    
    if args.commands_only:
        tests = [test_commands_comprehensive]
    elif args.quick:
        tests = [test_help, test_argument_validation]
    else:
        tests = [
            test_help,
            test_argument_validation, 
            test_app_startup,
            test_commands,
            test_ui_elements,
            test_commands_comprehensive
        ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test {test.__name__} failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! HiOllama is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
