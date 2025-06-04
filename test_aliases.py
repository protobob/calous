#!/usr/bin/env python3
"""Simple test script to verify alias functionality works."""

import sys
from pathlib import Path

# Add the hiollama package to Python path
hiollama_path = Path(__file__).parent / "hiollama"
sys.path.insert(0, str(hiollama_path.parent))

from hiollama.commands.registry import registry
from hiollama.config import ConfigManager

def test_aliases():
    print("=== Testing Alias Functionality ===\n")
    
    # Test 1: Check that alias commands are registered
    print("1. Testing command registration:")
    alias_commands = ["alias", "alias.add", "alias.remove", "alias.list"]
    for cmd in alias_commands:
        cmd_def = registry.get_command(cmd)
        if cmd_def:
            print(f"   ✓ /{cmd} - {cmd_def.description}")
        else:
            print(f"   ✗ /{cmd} - NOT FOUND")
    
    print("\n2. Testing config methods:")
    # Test 2: Test config methods
    try:
        # Test get_aliases
        aliases = ConfigManager.get_aliases()
        print(f"   ✓ get_aliases() returned: {aliases}")
        
        # Test add_alias
        ConfigManager.add_alias("test_alias", "sys.help")
        print("   ✓ add_alias() worked")
        
        # Test list_aliases
        aliases = ConfigManager.list_aliases()
        print(f"   ✓ list_aliases() returned: {aliases}")
        
        # Test remove_alias  
        removed = ConfigManager.remove_alias("test_alias")
        print(f"   ✓ remove_alias() returned: {removed}")
        
    except Exception as e:
        print(f"   ✗ Config error: {e}")
    
    print("\n3. Testing registry methods:")
    # Test 3: Test registry methods
    try:
        # Test that we can find a real command
        real_cmd = registry.get_command("sys.help")
        print(f"   ✓ get_command('sys.help') found: {real_cmd.name if real_cmd else 'None'}")
        
        # Test user alias methods
        aliases = registry.list_user_aliases()
        print(f"   ✓ list_user_aliases() returned: {aliases}")
        
    except Exception as e:
        print(f"   ✗ Registry error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_aliases()
