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
    
    @staticmethod
    def format_history_enabled(chat_info):
        """Print history enabled message."""
        print(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording [bold green]ENABLED[/bold green]")
    
    @staticmethod
    def format_history_disabled(chat_info):
        """Print history disabled message."""
        print(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording [bold red]DISABLED[/bold red]")
    
    @staticmethod
    def format_history_already_enabled(chat_info):
        """Print history already enabled message."""
        print(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording is already [bold green]ENABLED[/bold green]")
    
    @staticmethod
    def format_history_already_disabled(chat_info):
        """Print history already disabled message."""
        print(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording is already [bold red]DISABLED[/bold red]")
    
    @staticmethod
    def format_purge_warning(chat_info, n):
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]DELETE[/bold red] the [bold]{n}[/bold] most recent message(s) from [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history.")
        print("This cannot be undone.")

    @staticmethod
    def confirm_purge() -> bool:
        from ...constants import Confirmations
        from rich.prompt import Prompt
        response = Prompt.ask("Are you sure you want to continue?", choices=Confirmations.YES_NO, default=Confirmations.DEFAULT_NO)
        return response.lower() == "y"

    @staticmethod
    def format_purge_success(n):
        print(f"[green]Purged {n} message(s) from chat history.[/green]")

    @staticmethod
    def format_no_messages_to_purge():
        print(f"[yellow]\nNo messages to purge.[/yellow]")
