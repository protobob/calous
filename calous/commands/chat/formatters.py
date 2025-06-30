"""Chat command formatters."""
from rich import print as rich_print
from rich.prompt import Prompt
from ...constants import Colors, Messages, Confirmations
from .services import ChatOperationResult, ChatInfo
from ..formatters import CommandFormatter


class ChatFormatter(CommandFormatter):
    """Formatter for chat command outputs."""
    
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
    def format_add_chat_result(result: ChatOperationResult):
        """Format add chat operation result."""
        if result.success:
            message = f"[bold green]Adding new chat session...[/bold green] Creating Chat {result.chat_number}"
            ChatFormatter._output(message)
        else:
            ChatFormatter.print_error(result.error_message)
    
    @staticmethod
    def format_switch_error(error_message: str):
        """Format chat switch error."""
        ChatFormatter.print_error(error_message)
    
    @staticmethod
    def format_remove_error(error_message: str):
        """Format chat remove error."""
        ChatFormatter.print_error(error_message)
    
    @staticmethod
    def format_remove_chat(chat_number: int):
        """Format chat removal message."""
        message = f"[bold yellow]Removing Chat {chat_number}...[/bold yellow] Configuration will be preserved."
        ChatFormatter._output(message)
    
    @staticmethod
    def format_twist_error(error_message: str):
        """Format twist operation error."""
        ChatFormatter.print_error(error_message)
    
    @staticmethod
    def format_reset_warning(chat_info: ChatInfo):
        """Print chat reset warning with colored chat identification."""
        warning_msg = f"\n{Colors.WARNING}Warning:{Colors.RESET} This will {Colors.ERROR}RESET{Colors.RESET} [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] to factory defaults.\n"
        warning_msg += f"This will {Colors.ERROR}CLEAR{Colors.RESET} history, system prompt, and all saved prompts."
        ChatFormatter._output(warning_msg)
    
    @staticmethod
    def format_reset_success(chat_info: ChatInfo):
        """Print chat reset success message."""
        message = f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] reset to factory defaults successfully!"
        ChatFormatter._output(message)
    
    @staticmethod
    def format_reset_error():
        """Print chat reset error message."""
        CommandFormatter._output(f"{Colors.ERROR}Error:{Colors.RESET} Failed to reset chat to defaults.")
    
    @staticmethod
    def confirm_reset() -> bool:
        """Confirm chat reset operation."""
        response = Prompt.ask("\nAre you sure you want to continue?", choices=Confirmations.YES_NO, default=Confirmations.DEFAULT_NO)
        return response.lower() == "y"
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        CommandFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
