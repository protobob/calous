"""Chat command formatters."""
from ...constants import Colors, Messages, Confirmations
from .services import ChatOperationResult, ChatInfo
from ..formatters import CommandFormatter


class ChatFormatter(CommandFormatter):
    """Formatter for chat command outputs."""
    
    
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
        ChatFormatter._output(f"{Colors.ERROR}Error:{Colors.RESET} Failed to reset chat to defaults.")
    
    @staticmethod
    def confirm_reset() -> bool:
        """Confirm chat reset operation."""
        prompt = "\nAre you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        ChatFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
