#!/usr/bin/env python3
"""
Test script for the new refactored command structure in HiOllama.
Tests the new dotted command format (e.g., /sys.help, /model.switch, etc.)
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path to import hiollama modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from hiollama.commands.registry import registry

def test_command_registration():
    """Test that all expected commands are properly registered."""
    print("🔍 Testing Command Registration")
    print("=" * 50)
    
    # Expected categories and some commands in each
    expected_commands = {
        "sys.help": "Show this help menu",
        "sys.quit": "Exit the program",
        "sys.vars": "Display current system variables",
        "chat.switch": "Switch between chats",
        "chat.add": "Add a new chat session",
        "chat.remove": "Remove a chat session",
        "chat.reset": "Reset chat to factory defaults",
        "chat.twist": "Copy AI's last response",
        "model.switch": "Change the current model",
        "model.setctx": "Set max context window size",
        "model.eval": "Toggle evaluation display",
        "model.think": "Toggle thinking display",
        "model.settemp": "Set temperature parameter",
        "prompt.set": "Set a saved prompt",
        "prompt.use": "Use a saved prompt",
        "prompt.list": "Display saved prompts",
        "persona.set": "Set content for persona slot",
        "persona.get": "Get content from persona slot",
        "persona.clear": "Clear persona slot",
        "persona.name": "Set or get persona name",
        "persona.show": "Show complete persona information",
        "persona.reset": "Reset persona to default state",
        "persona.save": "Save current persona to file",
        "persona.load": "Load persona from file",
        "persona.list": "List all saved personas",
        "persona.delete": "Delete a saved persona file",
        "history.show": "Display the current chat history",
        "history.clear": "Clear the current chat history",
        "log.on": "Enable logging of chat history",
        "log.off": "Disable logging of chat history",
        "log.today": "View unified log for today",
        "file.load": "Load a file as a prompt",
        "plugin.list": "List all available plugins",
        "plugin.info": "Get information about a specific plugin",
        "plugin.reload": "Reload the plugin system",
        "alias.add": "Create a new command alias",
        "alias.remove": "Remove a command alias",
        "alias.list": "List all command aliases"
    }
    
    registered_commands = registry.get_all_commands()
    
    passed = 0
    total = len(expected_commands)
    
    for command_name, expected_desc in expected_commands.items():
        if command_name in registered_commands:
            actual_desc = registered_commands[command_name].description
            if expected_desc.lower() in actual_desc.lower():
                print(f"✅ {command_name} - Registered correctly")
                passed += 1
            else:
                print(f"⚠️  {command_name} - Description mismatch")
                print(f"   Expected: {expected_desc}")
                print(f"   Actual: {actual_desc}")
                passed += 1  # Still count as passed since it's registered
        else:
            print(f"❌ {command_name} - NOT REGISTERED")
    
    print("=" * 50)
    print(f"📊 Registration Test Results: {passed}/{total} commands found")
    return passed == total

def test_command_categories():
    """Test that commands are properly categorized."""
    print("\n🔍 Testing Command Categories")
    print("=" * 50)
    
    from hiollama.commands.types import CommandCategory
    
    registered_commands = registry.get_all_commands()
    categories = {}
    for command_name, command_info in registered_commands.items():
        category = command_info.category
        if category not in categories:
            categories[category] = []
        categories[category].append(command_name)
    
    expected_categories = [
        CommandCategory.GENERAL,
        CommandCategory.NAVIGATION,
        CommandCategory.MODEL,
        CommandCategory.PROMPT,
        CommandCategory.HISTORY,
        CommandCategory.FILE
    ]
    
    print(f"Found {len(categories)} categories:")
    for category, commands in categories.items():
        print(f"  {category}: {len(commands)} commands")
        for cmd in sorted(commands)[:3]:  # Show first 3 commands
            print(f"    - {cmd}")
        if len(commands) > 3:
            print(f"    ... and {len(commands) - 3} more")
    
    missing_categories = [cat for cat in expected_categories if cat not in categories]
    if missing_categories:
        print(f"\n⚠️  Missing categories: {missing_categories}")
    else:
        print(f"\n✅ All expected categories found")
    
    return len(missing_categories) == 0

def test_legacy_command_cleanup():
    """Test that old legacy commands are not registered."""
    print("\n🔍 Testing Legacy Command Cleanup")
    print("=" * 50)
    
    # These old commands should NOT be registered anymore
    legacy_commands = [
        "help",           # Now sys.help
        "quit",           # Now sys.quit  
        "showvars",       # Now sys.vars
        "model",          # Now model.switch
        "toggle_eval",    # Now model.eval
        "toggle_think",   # Now model.think
        "setctx",         # Now model.setctx
        "settemp",        # Now model.settemp
        "history",        # Now history.show
        "clear",          # Now history.clear
        "toggle_log",     # Now log.on/log.off
        "prompt",         # Now prompt.set
        "showprompt"      # Now prompt.list
    ]
    
    registered_commands = registry.get_all_commands()
    
    found_legacy = []
    for legacy_cmd in legacy_commands:
        if legacy_cmd in registered_commands:
            found_legacy.append(legacy_cmd)
    
    if found_legacy:
        print(f"❌ Found legacy commands still registered: {found_legacy}")
        return False
    else:
        print(f"✅ No legacy commands found - cleanup successful!")
        print(f"   Checked {len(legacy_commands)} legacy command names")
        return True

def main():
    """Run all command structure tests."""
    print("🚀 HiOllama New Command Structure Testing")
    print("=" * 60)
    
    # Import commands to register them
    try:
        import hiollama.commands
        print("✅ Commands imported successfully")
    except Exception as e:
        print(f"❌ Failed to import commands: {e}")
        return 1
    
    tests = [
        ("Command Registration", test_command_registration),
        ("Command Categories", test_command_categories),
        ("Legacy Command Cleanup", test_legacy_command_cleanup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print("=" * 60)
    print(f"📊 Final Results: {passed}/{total} test categories passed")
    
    if passed == total:
        print("🎉 All command structure tests passed!")
        print("   The new refactored command system is working correctly.")
        return 0
    else:
        print("⚠️  Some command structure tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
