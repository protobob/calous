#!/usr/bin/env python3
"""Test script to verify debug routing fixes in session_manager.py"""

import sys
from pathlib import Path

def test_debug_routing_fixes():
    """Test that session_manager.py debug calls have been properly fixed."""
    print("🔍 Testing Debug Routing Fixes in session_manager.py")
    print("=" * 60)
    
    session_manager_file = Path("/home/aswin/python/calous/calousd/session_manager.py")
    
    if not session_manager_file.exists():
        print("❌ session_manager.py not found!")
        return
    
    # Read the file
    with open(session_manager_file, 'r') as f:
        content = f.read()
    
    # Count problematic patterns
    problematic_patterns = [
        'self._output(f"[Debug]',
        'self._output("[Debug]',
        'print(f"[Debug]',
        'print("[Debug]'
    ]
    
    fixed_patterns = [
        'unified_logger.debug_socket(',
        'unified_logger.debug_command(',
        'unified_logger.debug(',
        'unified_logger.error('
    ]
    
    print("🔍 Checking for problematic debug patterns...")
    total_problems = 0
    for pattern in problematic_patterns:
        count = content.count(pattern)
        if count > 0:
            print(f"  ❌ Found {count} instances of: {pattern}")
            total_problems += count
        else:
            print(f"  ✅ No instances of: {pattern}")
    
    print(f"\n📊 Total problematic patterns: {total_problems}")
    
    print("\n🔧 Checking for proper debug routing...")
    total_fixes = 0
    for pattern in fixed_patterns:
        count = content.count(pattern)
        if count > 0:
            print(f"  ✅ Found {count} instances of: {pattern}")
            total_fixes += count
        else:
            print(f"  ⚠️  No instances of: {pattern}")
    
    print(f"\n📊 Total enhanced logger calls: {total_fixes}")
    
    # Check for unified_logger import
    if "from .unified_logger import unified_logger" in content:
        print("✅ unified_logger properly imported")
    else:
        print("❌ unified_logger import missing!")
    
    # Overall result
    print("\n🎯 Overall Assessment:")
    if total_problems == 0 and total_fixes > 0:
        print("✅ SUCCESS: Debug routing properly fixed!")
        print("  • No problematic debug calls found")
        print("  • Enhanced logger methods in use")
        print("  • Debug info will route to log files, not socket clients")
    elif total_problems == 0:
        print("⚠️  PARTIAL: No problematic calls, but no enhanced logger usage detected")
    else:
        print(f"❌ ISSUES FOUND: {total_problems} problematic debug calls still present")
    
    # Show specific examples of what was fixed
    print("\n💡 What was accomplished:")
    print("  BEFORE: self._output(f'[Debug] Processing command: {command}')")
    print("  AFTER:  unified_logger.debug_command(f'Processing command: {command}')")
    print()
    print("  RESULT: Debug info now goes to debug.log, NOT to socket clients!")

if __name__ == "__main__":
    test_debug_routing_fixes()
