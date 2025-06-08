#!/usr/bin/env python3
"""
Command-focused test script for HiOllama application.
Tests the core user commands and functionality.
"""

import subprocess
import sys
import time
from pathlib import Path

def test_command(command, expected_outputs, test_name):
    """Test a specific command and check for expected outputs."""
    print(f"🔍 Testing {test_name}...")
    
    try:        # Use PowerShell to send command and quit
        cmd = f'"{command}"; "/sys.quit" | python -m hiollama 1'
        result = subprocess.run(
            ["powershell", "-Command", cmd], 
            capture_output=True, 
            text=True, 
            timeout=20,
            cwd=Path(__file__).parent.parent
        )
        
        output = result.stdout
        
        # Check for expected outputs
        missing = []
        for expected in expected_outputs:
            if expected not in output:
                missing.append(expected)
        
        if not missing:
            print(f"✅ {test_name} - All expected outputs found")
            return True
        else:
            print(f"❌ {test_name} - Missing: {missing}")
            print(f"   Got output: {output[:300]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} - Command timed out")
        return False
    except Exception as e:
        print(f"❌ {test_name} - Error: {e}")
        return False

def main():
    """Test core HiOllama commands."""
    print("🚀 HiOllama Command Testing")
    print("=" * 40)
      # Define command tests
    tests = [        {
            "command": "/sys.help",
            "expected": [
                "System Commands:",
                "/sys.help", "/sys.quit", "/sys.vars",
                "Chat Session Management:",
                "/chat.switch", "/chat.add",
                "Model Control Commands:",
                "/model.switch", "/model.eval",
                "Prompt Management Commands:",
                "/prompt.set", "/prompt.use",
                "History & Logging Commands:",
                "/history.show", "/log.on",
                "File Management Commands:",
                "/file.load"
            ],
            "name": "/sys.help command"
        },
        {
            "command": "/sys.vars",
            "expected": [
                "Selected Model:",
                "Verbosity:",
                "Logging Enabled:",
                "Config Path:",
                "System Prompt:"
            ],
            "name": "/sys.vars command"
        },
        {
            "command": "/prompt.list all",
            "expected": [
                "Chat 1:",
                "Chat 2:"
            ],
            "name": "/prompt.list all command"
        },
        {
            "command": "/model.switch",
            "expected": [
                "Available models:",
                "Currently selected:"
            ],
            "name": "/model.switch command"
        },
        {
            "command": "/history.show", 
            "expected": [
                "No messages in history"
            ],
            "name": "/history.show command (empty)"
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test_command(test["command"], test["expected"], test["name"]):
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 40)
    print(f"📊 Command Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All command tests passed! HiOllama commands are working correctly.")
        return 0
    else:
        print("⚠️  Some command tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
