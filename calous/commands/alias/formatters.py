"""UI formatting utilities for alias command output."""
from rich import print
from rich.prompt import Prompt
from typing import Dict
from ...constants import Colors, Confirmations
from ..formatters import CommandFormatter


class AliasFormatter(CommandFormatter):
    """Specialized formatter for alias-related output."""
    
    @staticmethod
    def print_alias_created(alias: str, command: str):
        """Print alias creation success message."""
        AliasFormatter.print_success(
            f"Alias created: '{alias}' → '{command}'",
            f"You can now use /{alias} instead of /{command}"
        )
    
    @staticmethod
    def print_alias_updated(alias: str, command: str, old_command: str):
        """Print alias update success message."""
        AliasFormatter.print_success(
            f"Alias updated: '{alias}' → '{command}' (was pointing to '{old_command}')",
            f"You can now use /{alias} for '{command}'"
        )
    
    @staticmethod
    def print_alias_removed(alias: str, command: str):
        """Print alias removal success message."""
        AliasFormatter.print_success(f"Alias removed: '{alias}' (was pointing to '{command}')")
    
    @staticmethod
    def print_no_aliases():
        """Print message when no aliases are defined."""
        print(f"{Colors.WARNING}No aliases defined{Colors.RESET}")
        print(f"{Colors.HINT}Use /alias.add <alias> <command> to create aliases{Colors.RESET}")
    
    @staticmethod
    def print_alias_list(aliases: Dict[str, str]):
        """Print formatted list of aliases."""
        print(f"{Colors.INFO}User-Defined Aliases ({len(aliases)}):{Colors.RESET}")
        print()
        
        # Sort aliases for consistent display
        for alias in sorted(aliases.keys()):
            command = aliases[alias]
            print(f"  {Colors.SUCCESS}{alias}{Colors.RESET} → {Colors.COMMAND}{command}{Colors.RESET}")
        
        print()
        print(f"{Colors.HINT}Use /alias.remove <alias> to remove an alias{Colors.RESET}")
    
    @staticmethod
    def print_alias_help():
        """Print alias management help."""
        print(f"\n{Colors.INFO}Alias Management Commands:{Colors.RESET}")
        print()
        print(f"  [bold]/alias.add <alias> <command>[/bold]")
        print("    Create a new alias for an existing command")
        print("    Example: /alias.add t chat.twist")
        print()
        print(f"  [bold]/alias.remove <alias>[/bold]")
        print("    Remove an existing alias")
        print("    Example: /alias.remove t")
        print()
        print(f"  [bold]/alias.list[/bold]")
        print("    Show all current aliases")
        print()
        print(f"{Colors.HINT}Aliases let you create shortcuts for frequently used commands{Colors.RESET}")
    
    @staticmethod
    def confirm_alias_overwrite(alias: str, old_command: str) -> bool:
        """Confirm overwriting an existing alias."""
        AliasFormatter.print_warning(f"Alias '{alias}' already exists (points to '{old_command}')")
        return AliasFormatter.confirm_action("Overwrite existing alias?")
