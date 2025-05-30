#!/usr/bin/env python3
"""
CLI argument and validation tests for HiOllama application.
Tests command-line interface functionality.
"""

import subprocess
import sys
from pathlib import Path

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

def test_valid_configurations():
    """Test valid command line configurations."""
    print("\n🔍 Testing valid configurations...")
    
    # Test default configuration
    code, stdout, stderr = run_command("python -m hiollama --help")
    if code == 0:
        print("✅ Default configuration valid")
    else:
        print("❌ Default configuration invalid")
        return False
    
    # Test custom max-chats
    code, stdout, stderr = run_command("python -m hiollama --max-chats 10 --help")
    if code == 0:
        print("✅ Custom max-chats configuration valid")
    else:
        print("❌ Custom max-chats configuration invalid")
        return False
    
    return True

def main():
    """Run CLI tests."""
    print("🚀 HiOllama CLI Test Suite")
    print("=" * 40)
    
    tests = [
        test_help,
        test_argument_validation,
        test_valid_configurations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test {test.__name__} failed!")
    
    print("\n" + "=" * 40)
    print(f"📊 CLI Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CLI tests passed!")
        return 0
    else:
        print("⚠️  Some CLI tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
