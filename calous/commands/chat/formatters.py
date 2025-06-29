"""Chat command formatters."""
from rich import print
from rich.prompt import Prompt
from ...constants import Colors, Messages, Confirmations
from .services import ChatOperationResult, ChatInfo


class ChatFormatter:
    """Formatter for chat command outputs."""
    
    @staticmethod
    def format_add_chat_result(result: ChatOperationResult):
        """Format add chat operation result."""
        if result.success:
            print(f"[bold green]Adding new chat session...[/bold green] Creating Chat {result.chat_number}")
        else:
            print(f"[bold red]Error:[/bold red] {result.error_message}")
    
    @staticmethod
    def format_switch_error(error_message: str):
        """Format chat switch error."""
        print(f"[bold red]Error:[/bold red] {error_message}")
    
    @staticmethod
    def format_remove_error(error_message: str):
        """Format chat remove error."""
        print(f"[bold red]Error:[/bold red] {error_message}")
    
    @staticmethod
    def format_remove_chat(chat_number: int):
        """Format chat removal message."""
        print(f"[bold yellow]Removing Chat {chat_number}...[/bold yellow] Configuration will be preserved.")
    
    @staticmethod
    def format_twist_error(error_message: str):
        """Format twist operation error."""
        print(f"\n[bold red]Error:[/bold red] {error_message}")
    
    @staticmethod
    def format_reset_warning(chat_info: ChatInfo):
        """Print chat reset warning with colored chat identification."""
        print(f"\n{Colors.WARNING}Warning:{Colors.RESET} This will {Colors.ERROR}RESET{Colors.RESET} [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] to factory defaults.")
        print(f"This will {Colors.ERROR}CLEAR{Colors.RESET} history, system prompt, and all saved prompts.")
    
    @staticmethod
    def format_reset_success(chat_info: ChatInfo):
        """Print chat reset success message."""
        print(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] reset to factory defaults successfully!")
    
    @staticmethod
    def format_reset_error():
        """Print chat reset error message."""
        print(f"{Colors.ERROR}Error:{Colors.RESET} Failed to reset chat to defaults.")
    
    @staticmethod
    def confirm_reset() -> bool:
        """Confirm chat reset operation."""
        response = Prompt.ask("\nAre you sure you want to continue?", choices=Confirmations.YES_NO, default=Confirmations.DEFAULT_NO)
        return response.lower() == "y"
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        print(f"\n{Messages.OPERATION_CANCELLED}")
