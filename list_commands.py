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
import hiollama.commands

def main():
    print("=== ALL REGISTERED COMMANDS ===\n")
    
    # Group commands by their actual prefix/namespace
    commands_by_prefix = {}
    
    for name, cmd_def in registry.get_all_commands().items():
        # Extract prefix from command name (e.g., "chat.add" -> "chat")
        if '.' in name:
            prefix = name.split('.')[0]
        else:
            prefix = "system"  # For commands without dots like help, quit
        
        if prefix not in commands_by_prefix:
            commands_by_prefix[prefix] = []
        commands_by_prefix[prefix].append(cmd_def)
    
    # Logical order for command prefixes
    prefix_order = [
        "sys",      # System commands (help, quit, vars)
        "chat",     # Chat management
        "model",    # Model settings
        "persona",  # Persona management
        "prompt",   # Prompt management
        "history",  # History commands
        "log",      # Logging commands
        "file",     # File operations
        "alias",    # Alias management
        "plugin",   # Plugin system
        "system"    # Legacy commands without prefixes
    ]
    
    # Print commands grouped by prefix
    for prefix in prefix_order:
        if prefix in commands_by_prefix:
            print(f"{prefix.upper()} COMMANDS:")
            for cmd_def in sorted(commands_by_prefix[prefix], key=lambda x: x.name):
                aliases_str = f" (aliases: {', '.join(cmd_def.aliases)})" if cmd_def.aliases else ""
                print(f"  /{cmd_def.name}{aliases_str} - {cmd_def.description}")
            print()
    
    # Print any remaining prefixes not in our predefined order
    remaining_prefixes = set(commands_by_prefix.keys()) - set(prefix_order)
    for prefix in sorted(remaining_prefixes):
        print(f"{prefix.upper()} COMMANDS:")
        for cmd_def in sorted(commands_by_prefix[prefix], key=lambda x: x.name):
            aliases_str = f" (aliases: {', '.join(cmd_def.aliases)})" if cmd_def.aliases else ""
            print(f"  /{cmd_def.name}{aliases_str} - {cmd_def.description}")
        print()
    
    print(f"Total commands registered: {len(registry.get_all_commands())}")

if __name__ == "__main__":
    main()
