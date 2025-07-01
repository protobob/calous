"""UI formatting utilities for command output."""
from typing import Dict, Any, Optional
from ..constants import Colors, Messages, Confirmations
from ..utils import get_chat_color


class CommandFormatter:
    """Utility class for consistent command output formatting."""   
    
    @staticmethod
    def _get_session_manager():
        """Get session manager from current context."""
        # This will be set by commands when they initialize
        return getattr(CommandFormatter, '_session_manager', None)
    
    @staticmethod
    def _output(message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        session_manager = CommandFormatter._get_session_manager()
        if session_manager and session_manager.socket_mode and session_manager.current_connection:
            session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
    @staticmethod
    def print_error(message: str, hint: str = ""):
        """Print an error message with optional hint."""
        error_msg = f"\n{Colors.ERROR}Error:{Colors.RESET} {message}"
        if hint:
            error_msg += f"\n{Colors.HINT}{hint}{Colors.RESET}"
        CommandFormatter._output(error_msg, "error")
    
    @staticmethod
    def print_success(message: str, hint: str = ""):
        """Print a success message with optional hint."""
        success_msg = f"{Colors.SUCCESS}✓ {message}{Colors.RESET}"
        if hint:
            success_msg += f"\n{Colors.HINT}{hint}{Colors.RESET}"
        CommandFormatter._output(success_msg)
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message."""
        warning_msg = f"\n{Colors.WARNING}Warning:{Colors.RESET} {message}"
        CommandFormatter._output(warning_msg)
    
    @staticmethod
    def print_info(title: str, items: Optional[Dict[str, str]] = None):
        """Print an info section with optional items."""
        info_msg = f"\n{Colors.INFO}{title}:{Colors.RESET}\n"
        if items:
            for key, value in items.items():
                info_msg += f"  {Colors.SUCCESS}{key}{Colors.RESET} → {Colors.COMMAND}{value}{Colors.RESET}\n"
        CommandFormatter._output(info_msg)
    
    @staticmethod
    def confirm_action(message: str, default: str = Confirmations.DEFAULT_NO, app=None) -> bool:
        """Ask for user confirmation."""
        if app and hasattr(app, 'confirm'):
            # Check if we should use interactive confirmations in socket mode
            if hasattr(app, 'session_manager') and app.session_manager and app.session_manager.socket_mode:
                # Check if client supports interactive confirmations
                if hasattr(app.session_manager, 'supports_confirmations') and app.session_manager.supports_confirmations:
                    return app.session_manager.request_confirmation(message, default)
                else:
                    # Fall back to auto-confirm for non-interactive clients
                    default_bool = default == "y"
                    return app.confirm(message, default=default_bool)
            else:
                # Regular confirmation for non-socket mode
                default_bool = default == "y" 
                return app.confirm(message, default=default_bool)
        else:
            # Simple input-based confirmation without rich
            choices_str = "/".join(Confirmations.YES_NO)
            prompt = f"{message} ({choices_str}) [{default}]: "
            response = input(prompt).strip().lower()
            if not response:
                response = default
            return response.lower() == "y"


class ChatFormatter(CommandFormatter):
    """Specialized formatter for chat-related output."""
    
    @staticmethod
    def print_reset_warning(chat_number: int, chat_color: str):
        """Print chat reset warning with colored chat identification."""
        CommandFormatter._output(f"\n{Colors.WARNING}Warning:{Colors.RESET} This will {Colors.ERROR}RESET{Colors.RESET} [bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] to factory defaults.")
        CommandFormatter._output(f"This will {Colors.ERROR}CLEAR{Colors.RESET} history, system prompt, and all saved prompts.")
    
    @staticmethod
    def print_reset_success(chat_number: int, chat_color: str):
        """Print chat reset success message."""
        CommandFormatter._output(f"[bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] reset to factory defaults successfully!")
    
    @staticmethod
    def confirm_chat_reset() -> bool:
        """Confirm chat reset operation."""
        return CommandFormatter.confirm_action("\nAre you sure you want to continue?")


class FileFormatter(CommandFormatter):
    """Specialized formatter for file operation output."""
    
    @staticmethod
    def print_file_not_found(filepath: str, resolved_path: str):
        """Print file not found error with resolved path."""
        FileFormatter.print_error(f"File not found: {filepath}")
        CommandFormatter._output(f"{Colors.HINT}Resolved path: {resolved_path}{Colors.RESET}")
    
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
        CommandFormatter._output(f"\n{Colors.INFO}Notice:{Colors.RESET} Unknown file type '{extension}'. Attempting to load as text.")
    
    @staticmethod
    def print_no_extension_notice():
        """Print notice for files without extensions."""
        CommandFormatter._output(f"\n{Colors.INFO}Notice:{Colors.RESET} File has no extension. Attempting to load as text.")
    
    @staticmethod
    def print_content_preview(content: str, preview_length: int = 100):
        """Print a preview of file content."""
        if len(content) > preview_length:
            preview = content[:preview_length] + "..."
            CommandFormatter._output(f"\n{Colors.HINT}Content preview:\n\n{Colors.RESET}{preview}")
    
    @staticmethod
    def print_file_loaded(filename: str, char_count: int, prompt: str = ""):
        """Print successful file load message."""
        FileFormatter.print_success(f"Loaded file: {filename} ({char_count:,} characters)")
        if prompt.strip():
            CommandFormatter._output(f"{Colors.HINT}Prompt: {prompt}{Colors.RESET}")
        else:
            CommandFormatter._output(f"{Colors.HINT}No additional prompt provided{Colors.RESET}")
    
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
        CommandFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def print_encoding_error():
        """Print error when file cannot be decoded."""
        FileFormatter.print_error("Unable to decode file with any supported encoding")
    
    # Methods called from file.py
    @staticmethod
    def file_size_error(file_size: int, max_size: int):
        """Print error for files that exceed size limit."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} File too large ({file_size:,} bytes). Maximum allowed: {max_size:,} bytes")
    
    @staticmethod
    def large_file_warning(file_size: int):
        """Print warning for large files."""
        CommandFormatter._output(f"\n{Colors.WARNING}Warning:{Colors.RESET} Large file ({file_size:,} bytes). This may take a moment to process.")
    
    @staticmethod
    def no_extension_notice():
        """Print notice for files without extensions."""
        CommandFormatter._output(f"\n{Colors.INFO}Notice:{Colors.RESET} File has no extension. Attempting to load as text.")
    
    @staticmethod
    def binary_file_warning(extension: str):
        """Print warning for potentially binary files."""
        CommandFormatter._output(f"\n{Colors.WARNING}Warning:{Colors.RESET} '{extension}' files are typically binary and may not display properly as text.")
    
    @staticmethod
    def unknown_extension_notice(extension: str):
        """Print notice for unknown file extensions."""
        CommandFormatter._output(f"\n{Colors.INFO}Notice:{Colors.RESET} Unknown file type '{extension}'. Attempting to load as text.")
    
    @staticmethod
    def content_preview(preview: str):
        """Print a preview of file content."""
        CommandFormatter._output(f"\n{Colors.HINT}Content preview:\n\n{Colors.RESET}{preview}")
    
    @staticmethod
    def file_not_found_error(filepath: str, resolved_path):
        """Print file not found error with resolved path."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} File not found: {filepath}")
        CommandFormatter._output(f"{Colors.HINT}Resolved path:{Colors.RESET} {resolved_path}")
    
    @staticmethod
    def not_a_file_error(filepath: str):
        """Print error when path is not a file."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Path is not a file: {filepath}")
    
    @staticmethod
    def file_load_cancelled():
        """Print file loading cancelled message."""
        CommandFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def generic_error(message: str):
        """Print generic error message."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} {message}")
    
    @staticmethod
    def file_loaded_success(filename: str, char_count: int, prompt: str = ""):
        """Print successful file load message."""
        CommandFormatter._output(f"\n{Colors.SUCCESS}✓{Colors.RESET} Loaded file: {filename} ({char_count:,} characters)")
        if prompt.strip():
            CommandFormatter._output(f"{Colors.HINT}Prompt:{Colors.RESET} {prompt}")
        else:
            CommandFormatter._output(f"{Colors.HINT}No additional prompt provided{Colors.RESET}")
    
    @staticmethod
    def file_load_error(message: str):
        """Print file loading error."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error loading file:{Colors.RESET} {message}")


class HandlerFormatter(CommandFormatter):
    """Specialized formatter for command handler output."""
    
    @staticmethod
    def invalid_command_syntax(error: str):
        """Print invalid command syntax error."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Invalid command syntax: {error}")
    
    @staticmethod
    def empty_command_error():
        """Print empty command error."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Empty command.")
    
    @staticmethod
    def invalid_command(command_name: str):
        """Print invalid command error with help hint."""
        CommandFormatter._output(f"\n{Colors.ERROR}Invalid command:{Colors.RESET} /{command_name}")
        CommandFormatter._output(f"{Colors.HINT}Type /help to see available commands.{Colors.RESET}")
    
    @staticmethod
    def command_usage(usage: str):
        """Print command usage information."""
        CommandFormatter._output(f"{Colors.HINT}Usage: {usage.strip()}{Colors.RESET}")
    
    @staticmethod
    def argument_parse_error(error: str, usage: str):
        """Print argument parsing error with usage."""
        HandlerFormatter.print_error(str(error))
        HandlerFormatter.command_usage(usage)
    
    @staticmethod
    def command_execution_error(error: str):
        """Print command execution error."""
        CommandFormatter._output(f"\n{Colors.ERROR}Command execution error:{Colors.RESET} {error}")
