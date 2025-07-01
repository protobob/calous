"""UI formatting utilities for alias command output."""
from typing import Dict
from ...constants import Colors, Confirmations
from ..formatters import CommandFormatter


class AliasFormatter(CommandFormatter):
    """Specialized formatter for alias-related output."""
    
    @staticmethod
    def _output(message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        session_manager = CommandFormatter._get_session_manager()
        if session_manager and session_manager.socket_mode and session_manager.current_connection:
            session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
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
        AliasFormatter._output(f"{Colors.WARNING}No aliases defined{Colors.RESET}")
        AliasFormatter._output(f"{Colors.HINT}Use /alias.add <alias> <command> to create aliases{Colors.RESET}")
    
    @staticmethod
    def print_alias_list(aliases: Dict[str, str]):
        """Print formatted list of aliases."""
        AliasFormatter._output(f"{Colors.INFO}User-Defined Aliases ({len(aliases)}):{Colors.RESET}")
        AliasFormatter._output("")
        
        # Sort aliases for consistent display
        for alias in sorted(aliases.keys()):
            command = aliases[alias]
            AliasFormatter._output(f"  {Colors.SUCCESS}{alias}{Colors.RESET} → {Colors.COMMAND}{command}{Colors.RESET}")
        
        AliasFormatter._output("")
        AliasFormatter._output(f"{Colors.HINT}Use /alias.remove <alias> to remove an alias{Colors.RESET}")
    
    @staticmethod
    def print_alias_help():
        """Print alias management help."""
        AliasFormatter._output(f"\n{Colors.INFO}Alias Management Commands:{Colors.RESET}")
        AliasFormatter._output("")
        AliasFormatter._output(f"  [bold]/alias.add <alias> <command>[/bold]")
        AliasFormatter._output("    Create a new alias for an existing command")
        AliasFormatter._output("    Example: /alias.add t chat.twist")
        AliasFormatter._output("")
        AliasFormatter._output(f"  [bold]/alias.remove <alias>[/bold]")
        AliasFormatter._output("    Remove an existing alias")
        AliasFormatter._output("    Example: /alias.remove t")
        AliasFormatter._output("")
        AliasFormatter._output(f"  [bold]/alias.list[/bold]")
        AliasFormatter._output("    Show all current aliases")
        AliasFormatter._output("")
        AliasFormatter._output(f"{Colors.HINT}Aliases let you create shortcuts for frequently used commands{Colors.RESET}")
    
    @staticmethod
    def confirm_alias_overwrite(alias: str, old_command: str) -> bool:
        """Confirm overwriting an existing alias."""
        AliasFormatter.print_warning(f"Alias '{alias}' already exists (points to '{old_command}')")
        return AliasFormatter.confirm_action("Overwrite existing alias?")
