"""UI formatting utilities for command output."""
from rich import print
from rich.prompt import Prompt
from typing import Dict, Any, Optional
from ..constants import Colors, Messages, Confirmations
from ..utils import get_chat_color


class CommandFormatter:
    """Utility class for consistent command output formatting."""   
    
    @staticmethod
    def print_error(message: str, hint: str = ""):
        """Print an error message with optional hint."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} {message}")
        if hint:
            print(f"{Colors.HINT}{hint}{Colors.RESET}")
    
    @staticmethod
    def print_success(message: str, hint: str = ""):
        """Print a success message with optional hint."""
        print(f"{Colors.SUCCESS}✓ {message}{Colors.RESET}")
        if hint:
            print(f"{Colors.HINT}{hint}{Colors.RESET}")
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message."""
        print(f"\n{Colors.WARNING}Warning:{Colors.RESET} {message}")
    
    @staticmethod
    def print_info(title: str, items: Dict[str, str] = None):
        """Print an info section with optional items."""
        print(f"\n{Colors.INFO}{title}:{Colors.RESET}")
        print()
        if items:
            for key, value in items.items():
                print(f"  {Colors.SUCCESS}{key}{Colors.RESET} → {Colors.COMMAND}{value}{Colors.RESET}")
    
    @staticmethod
    def confirm_action(message: str, default: str = Confirmations.DEFAULT_NO) -> bool:
        """Ask for user confirmation."""
        response = Prompt.ask(message, choices=Confirmations.YES_NO, default=default)
        return response.lower() == "y"


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


class ChatFormatter(CommandFormatter):
    """Specialized formatter for chat-related output."""
    
    @staticmethod
    def print_reset_warning(chat_number: int, chat_color: str):
        """Print chat reset warning with colored chat identification."""
        print(f"\n{Colors.WARNING}Warning:{Colors.RESET} This will {Colors.ERROR}RESET{Colors.RESET} [bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] to factory defaults.")
        print(f"This will {Colors.ERROR}CLEAR{Colors.RESET} history, system prompt, and all saved prompts.")
    
    @staticmethod
    def print_reset_success(chat_number: int, chat_color: str):
        """Print chat reset success message."""
        print(f"[bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] reset to factory defaults successfully!")
    
    @staticmethod
    def confirm_chat_reset() -> bool:
        """Confirm chat reset operation."""
        return ChatFormatter.confirm_action("\nAre you sure you want to continue?")


class FileFormatter(CommandFormatter):
    """Specialized formatter for file operation output."""
    
    @staticmethod
    def print_file_not_found(filepath: str, resolved_path: str):
        """Print file not found error with resolved path."""
        FileFormatter.print_error(f"File not found: {filepath}")
        print(f"{Colors.HINT}Resolved path: {resolved_path}{Colors.RESET}")
    
    @staticmethod
    def print_not_a_file(filepath: str):
        """Print error when path is not a file."""
        FileFormatter.print_error(f"Path is not a file: {filepath}")
    
    @staticmethod
    def print_file_too_large(file_size: int, max_size: int):
        """Print error for files that exceed size limit."""
        FileFormatter.print_error(f"File too large ({file_size:,} bytes). Maximum allowed: {max_size:,} bytes")
    
    @staticmethod
    def print_large_file_warning(file_size: int):
        """Print warning for large files."""
        FileFormatter.print_warning(f"Large file ({file_size:,} bytes). This may take a moment to process.")
    
    @staticmethod
    def print_binary_file_warning(extension: str):
        """Print warning for potentially binary files."""
        FileFormatter.print_warning(f"'{extension}' files are typically binary and may not display properly as text.")
    
    @staticmethod
    def print_unknown_extension_notice(extension: str):
        """Print notice for unknown file extensions."""
        print(f"\n{Colors.INFO}Notice:{Colors.RESET} Unknown file type '{extension}'. Attempting to load as text.")
    
    @staticmethod
    def print_no_extension_notice():
        """Print notice for files without extensions."""
        print(f"\n{Colors.INFO}Notice:{Colors.RESET} File has no extension. Attempting to load as text.")
    
    @staticmethod
    def print_content_preview(content: str, preview_length: int = 100):
        """Print a preview of file content."""
        if len(content) > preview_length:
            preview = content[:preview_length] + "..."
            print(f"\n{Colors.HINT}Content preview:\n\n{Colors.RESET}{preview}")
    
    @staticmethod
    def print_file_loaded(filename: str, char_count: int, prompt: str = ""):
        """Print successful file load message."""
        FileFormatter.print_success(f"Loaded file: {filename} ({char_count:,} characters)")
        if prompt.strip():
            print(f"{Colors.HINT}Prompt: {prompt}{Colors.RESET}")
        else:
            print(f"{Colors.HINT}No additional prompt provided{Colors.RESET}")
    
    @staticmethod
    def confirm_large_file_load() -> bool:
        """Confirm loading a large file."""
        return FileFormatter.confirm_action("Continue loading this large file?")
    
    @staticmethod
    def confirm_binary_file_load() -> bool:
        """Confirm loading a potentially binary file."""
        return FileFormatter.confirm_action("Continue loading this file?")
    
    @staticmethod
    def print_operation_cancelled():
        """Print file operation cancelled message."""
        print(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def print_encoding_error():
        """Print error when file cannot be decoded."""
        FileFormatter.print_error("Unable to decode file with any supported encoding")
    
    # Methods called from file.py
    @staticmethod
    def file_size_error(file_size: int, max_size: int):
        """Print error for files that exceed size limit."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} File too large ({file_size:,} bytes). Maximum allowed: {max_size:,} bytes")
    
    @staticmethod
    def large_file_warning(file_size: int):
        """Print warning for large files."""
        print(f"\n{Colors.WARNING}Warning:{Colors.RESET} Large file ({file_size:,} bytes). This may take a moment to process.")
    
    @staticmethod
    def no_extension_notice():
        """Print notice for files without extensions."""
        print(f"\n{Colors.INFO}Notice:{Colors.RESET} File has no extension. Attempting to load as text.")
    
    @staticmethod
    def binary_file_warning(extension: str):
        """Print warning for potentially binary files."""
        print(f"\n{Colors.WARNING}Warning:{Colors.RESET} '{extension}' files are typically binary and may not display properly as text.")
    
    @staticmethod
    def unknown_extension_notice(extension: str):
        """Print notice for unknown file extensions."""
        print(f"\n{Colors.INFO}Notice:{Colors.RESET} Unknown file type '{extension}'. Attempting to load as text.")
    
    @staticmethod
    def content_preview(preview: str):
        """Print a preview of file content."""
        print(f"\n{Colors.HINT}Content preview:\n\n{Colors.RESET}{preview}")
    
    @staticmethod
    def file_not_found_error(filepath: str, resolved_path):
        """Print file not found error with resolved path."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} File not found: {filepath}")
        print(f"{Colors.HINT}Resolved path:{Colors.RESET} {resolved_path}")
    
    @staticmethod
    def not_a_file_error(filepath: str):
        """Print error when path is not a file."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} Path is not a file: {filepath}")
    
    @staticmethod
    def file_load_cancelled():
        """Print file loading cancelled message."""
        print(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def generic_error(message: str):
        """Print generic error message."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} {message}")
    
    @staticmethod
    def file_loaded_success(filename: str, char_count: int, prompt: str = ""):
        """Print successful file load message."""
        print(f"\n{Colors.SUCCESS}✓{Colors.RESET} Loaded file: {filename} ({char_count:,} characters)")
        if prompt.strip():
            print(f"{Colors.HINT}Prompt:{Colors.RESET} {prompt}")
        else:
            print(f"{Colors.HINT}No additional prompt provided{Colors.RESET}")
    
    @staticmethod
    def file_load_error(message: str):
        """Print file loading error."""
        print(f"\n{Colors.ERROR}Error loading file:{Colors.RESET} {message}")


class HandlerFormatter(CommandFormatter):
    """Specialized formatter for command handler output."""
    
    @staticmethod
    def invalid_command_syntax(error: str):
        """Print invalid command syntax error."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} Invalid command syntax: {error}")
    
    @staticmethod
    def empty_command_error():
        """Print empty command error."""
        print(f"\n{Colors.ERROR}Error:{Colors.RESET} Empty command.")
    
    @staticmethod
    def invalid_command(command_name: str):
        """Print invalid command error with help hint."""
        print(f"\n{Colors.ERROR}Invalid command:{Colors.RESET} /{command_name}")
        print(f"{Colors.HINT}Type /help to see available commands.{Colors.RESET}")
    
    @staticmethod
    def command_usage(usage: str):
        """Print command usage information."""
        print(f"{Colors.HINT}Usage: {usage.strip()}{Colors.RESET}")
    
    @staticmethod
    def argument_parse_error(error: str, usage: str):
        """Print argument parsing error with usage."""
        HandlerFormatter.print_error(str(error))
        HandlerFormatter.command_usage(usage)
    
    @staticmethod
    def command_execution_error(error: str):
        """Print command execution error."""
        print(f"\n{Colors.ERROR}Command execution error:{Colors.RESET} {error}")
