"""History command formatters."""

from ...constants import Colors, Messages, Confirmations
from ..formatters import CommandFormatter


class HistoryFormatter(CommandFormatter):
    """Handles formatting for history command outputs."""
    
    @staticmethod
    def format_clear_warning(chat_info):
        """Print history clear warning with colored chat identification."""
        HistoryFormatter._output(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]CLEAR[/bold red] [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history.")
        HistoryFormatter._output("All conversation history will be permanently deleted.")
    
    @staticmethod
    def format_clear_success(chat_info):
        """Print history clear success message."""
        HistoryFormatter._output(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history cleared successfully!")
    
    @staticmethod
    def confirm_clear() -> bool:
        """Confirm history clear operation."""
        prompt = "\nAre you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        HistoryFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def format_history_enabled(chat_info):
        """Print history enabled message."""
        HistoryFormatter._output(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording [bold green]ENABLED[/bold green]")
    
    @staticmethod
    def format_history_disabled(chat_info):
        """Print history disabled message."""
        HistoryFormatter._output(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording [bold red]DISABLED[/bold red]")
    
    @staticmethod
    def format_history_already_enabled(chat_info):
        """Print history already enabled message."""
        HistoryFormatter._output(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording is already [bold green]ENABLED[/bold green]")
    
    @staticmethod
    def format_history_already_disabled(chat_info):
        """Print history already disabled message."""
        HistoryFormatter._output(f"[bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history recording is already [bold red]DISABLED[/bold red]")
    
    @staticmethod
    def format_purge_warning(chat_info, n):
        HistoryFormatter._output(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]DELETE[/bold red] the [bold]{n}[/bold] most recent message(s) from [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history.")
        HistoryFormatter._output("This cannot be undone.")

    @staticmethod
    def confirm_purge() -> bool:
        from ...constants import Confirmations
        prompt = "Are you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"

    @staticmethod
    def format_purge_success(n):
        HistoryFormatter._output(f"[green]Purged {n} message(s) from chat history.[/green]")

    @staticmethod
    def format_no_messages_to_purge():
        HistoryFormatter._output(f"[yellow]\nNo messages to purge.[/yellow]")
    
    @staticmethod
    def format_file_exists_warning(filename: str):
        """Print warning when save file already exists."""
        HistoryFormatter._output(f"\n[yellow]File {filename} already exists.[/yellow]")
    
    @staticmethod
    def format_save_success(filepath, count: int):
        """Print save success message."""
        HistoryFormatter._output(f"\n[green]Chat history saved to {filepath} ({count} messages).[/green]")
    
    @staticmethod
    def format_save_no_messages():
        """Print message when no messages to save."""
        HistoryFormatter._output(f"\n[yellow]No messages to save. File not created.[/yellow]")
    
    @staticmethod
    def format_load_file_not_found(filepath):
        """Print file not found error for load."""
        HistoryFormatter._output(f"\n[red]File not found: {filepath}[/red]")
    
    @staticmethod
    def format_load_warning():
        """Print load overwrite warning."""
        HistoryFormatter._output("\n[yellow]Warning: Loading will overwrite current chat history in memory.[/yellow]")
    
    @staticmethod
    def format_load_success(filepath, count: int):
        """Print load success message."""
        HistoryFormatter._output(f"\n[green]Loaded {count} messages from {filepath} into current chat history.[/green]")
    
    @staticmethod
    def format_no_saved_files():
        """Print message when no saved files found."""
        HistoryFormatter._output("\n[yellow]No saved chat history files found.[/yellow]")
    
    @staticmethod
    def format_saved_files_header():
        """Print header for saved files list."""
        HistoryFormatter._output("\n[bold]Saved chat history files:[/bold]")
    
    @staticmethod
    def format_saved_file_item(filename: str, size: int):
        """Print saved file item."""
        HistoryFormatter._output(f"  [cyan]{filename}[/cyan]  ({size} bytes)")
    
    @staticmethod
    def format_delete_file_not_found(filepath):
        """Print file not found error for delete."""
        HistoryFormatter._output(f"\n[red]File not found: {filepath}[/red]")
    
    @staticmethod
    def format_delete_warning(filename: str):
        """Print delete confirmation warning."""
        HistoryFormatter._output(f"\n[yellow]Are you sure you want to delete {filename}? This cannot be undone.[/yellow]")
    
    @staticmethod
    def format_delete_success(filename: str):
        """Print delete success message."""
        HistoryFormatter._output(f"\n[green]Deleted {filename}.[/green]")
    
    @staticmethod
    def format_delete_error(error: str):
        """Print delete error message."""
        HistoryFormatter._output(f"\n[red]Error deleting file: {error}[/red]")
    
    @staticmethod
    def format_purge_file_error(error: str):
        """Print purge file update error."""
        HistoryFormatter._output(f"[red]Error updating history file: {error}[/red]")
    
    @staticmethod
    def format_history_vars(chat_info, history_enabled: bool, message_count: int):
        """Print history variables information."""
        status_text = "[bold green]ENABLED[/bold green]" if history_enabled else "[bold red]DISABLED[/bold red]"
        
        HistoryFormatter._output(f"\n[bold {chat_info.color}]|[/bold {chat_info.color}] [bold {chat_info.color}]CHAT {chat_info.number} HISTORY VARIABLES[/bold {chat_info.color}]\n")
        HistoryFormatter._output(f"[bold {chat_info.color}]|[/bold {chat_info.color}] {'Recording Status:':<20} {status_text}")
        HistoryFormatter._output(f"[bold {chat_info.color}]|[/bold {chat_info.color}] {'Message Count:':<20} [grey70]{message_count}[/grey70]")
        HistoryFormatter._output("")
