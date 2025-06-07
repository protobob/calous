"""History command formatters."""

from rich import print
from rich.prompt import Prompt
from ...constants import Colors, Messages, Confirmations


class HistoryFormatter:
    """Handles formatting for history command outputs."""
    
    @staticmethod
    def format_clear_warning(chat_info):
        """Print history clear warning with colored chat identification."""
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]CLEAR[/bold red] [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history.")
        print("All conversation history will be permanently deleted.")
    
    @staticmethod
    def format_clear_success(chat_info):
        """Print history clear success message."""
        print(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history cleared successfully!")
    
    @staticmethod
    def confirm_clear() -> bool:
        """Confirm history clear operation."""
        response = Prompt.ask("\nAre you sure you want to continue?", choices=Confirmations.YES_NO, default=Confirmations.DEFAULT_NO)
        return response.lower() == "y"
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        print(f"\n{Messages.OPERATION_CANCELLED}")
