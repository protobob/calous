"""Log command formatters."""

from rich import print
from ...constants import Colors, Messages
from .services import LogOperationResult


class LogFormatter:
    """Handles formatting for log command outputs."""
    
    @staticmethod
    def format_enable_result(result: LogOperationResult):
        """Format log enable operation result."""
        if result.success:
            print(f"\n{result.message}")
        else:
            print(f"\n{result.message}")
    
    @staticmethod
    def format_disable_result(result: LogOperationResult):
        """Format log disable operation result."""
        if result.success:
            print(f"\n{result.message}")
        else:
            print(f"\n{result.message}")
    
    @staticmethod
    def format_today_result(result: LogOperationResult):
        """Format today's log display result."""
        if result.success:
            print(f"\n[bold green]{result.message}:[/bold green]")
            print("=" * 60)
            print(result.data)
            print("=" * 60)
        else:
            print(f"\n[bold yellow]{result.message}[/bold yellow]")
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        print(f"\n{Messages.OPERATION_CANCELLED}")
