#!/usr/bin/env python3
"""Script to list all registered commands in HiOllama."""

import sys
from pathlib import Path

# Add the hiollama package to Python path
hiollama_path = Path(__file__).parent / "hiollama"
sys.path.insert(0, str(hiollama_path.parent))

from hiollama.commands.registry import registry
from hiollama.commands.types import CommandCategory

# Import all command modules to trigger registration
import hiollama.commands.general
import hiollama.commands.model
import hiollama.commands.prompt
import hiollama.commands.history
import hiollama.commands.navigation
import hiollama.commands.file
import hiollama.commands.plugins

def main():
    print("=== ALL REGISTERED COMMANDS ===\n")
    
    # Group commands by category
    commands_by_category = {}
    
    for name, cmd_def in registry.get_all_commands().items():
        category = cmd_def.category
        if category not in commands_by_category:
            commands_by_category[category] = []
        commands_by_category[category].append(cmd_def)
    
    # Print commands by category
    for category in [CommandCategory.GENERAL, CommandCategory.MODEL, CommandCategory.PROMPT, 
                    CommandCategory.HISTORY, CommandCategory.NAVIGATION, CommandCategory.FILE]:
        if category in commands_by_category:
            print(f"{category.upper()} COMMANDS:")
            for cmd_def in sorted(commands_by_category[category], key=lambda x: x.name):
                aliases_str = f" (aliases: {', '.join(cmd_def.aliases)})" if cmd_def.aliases else ""
                print(f"  /{cmd_def.name}{aliases_str} - {cmd_def.description}")
            print()
    
    print(f"Total commands registered: {len(registry.get_all_commands())}")

if __name__ == "__main__":
    main()
