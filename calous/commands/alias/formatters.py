"""UI formatting utilities for alias command output."""
from rich import print as rich_print
from rich.prompt import Prompt
from typing import Dict
from ...constants import Colors, Confirmations
from ..formatters import CommandFormatter


class AliasFormatter(CommandFormatter):
    """Specialized formatter for alias-related output."""
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
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
        CommandFormatter._output(f"{Colors.WARNING}No aliases defined{Colors.RESET}")
        CommandFormatter._output(f"{Colors.HINT}Use /alias.add <alias> <command> to create aliases{Colors.RESET}")
    
    @staticmethod
    def print_alias_list(aliases: Dict[str, str]):
        """Print formatted list of aliases."""
        CommandFormatter._output(f"{Colors.INFO}User-Defined Aliases ({len(aliases)}):{Colors.RESET}")
        CommandFormatter._output()
        
        # Sort aliases for consistent display
        for alias in sorted(aliases.keys()):
            command = aliases[alias]
            CommandFormatter._output(f"  {Colors.SUCCESS}{alias}{Colors.RESET} → {Colors.COMMAND}{command}{Colors.RESET}")
        
        CommandFormatter._output()
        CommandFormatter._output(f"{Colors.HINT}Use /alias.remove <alias> to remove an alias{Colors.RESET}")
    
    @staticmethod
    def print_alias_help():
        """Print alias management help."""
        CommandFormatter._output(f"\n{Colors.INFO}Alias Management Commands:{Colors.RESET}")
        CommandFormatter._output()
        CommandFormatter._output(f"  [bold]/alias.add <alias> <command>[/bold]")
        CommandFormatter._output("    Create a new alias for an existing command")
        CommandFormatter._output("    Example: /alias.add t chat.twist")
        CommandFormatter._output()
        CommandFormatter._output(f"  [bold]/alias.remove <alias>[/bold]")
        CommandFormatter._output("    Remove an existing alias")
        CommandFormatter._output("    Example: /alias.remove t")
        CommandFormatter._output()
        CommandFormatter._output(f"  [bold]/alias.list[/bold]")
        CommandFormatter._output("    Show all current aliases")
        CommandFormatter._output()
        CommandFormatter._output(f"{Colors.HINT}Aliases let you create shortcuts for frequently used commands{Colors.RESET}")
    
    @staticmethod
    def confirm_alias_overwrite(alias: str, old_command: str) -> bool:
        """Confirm overwriting an existing alias."""
        AliasFormatter.print_warning(f"Alias '{alias}' already exists (points to '{old_command}')")
        return AliasFormatter.confirm_action("Overwrite existing alias?")
