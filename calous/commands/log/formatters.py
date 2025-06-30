"""Log command formatters."""

from rich import print as rich_print
from ...constants import Colors, Messages
from .services import LogOperationResult


class LogFormatter:
    """Handles formatting for log command outputs."""
    
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
    def format_enable_result(result: LogOperationResult):
        """Format log enable operation result."""
        if result.success:
            CommandFormatter._output(f"\n{result.message}")
        else:
            CommandFormatter._output(f"\n{result.message}")
    
    @staticmethod
    def format_disable_result(result: LogOperationResult):
        """Format log disable operation result."""
        if result.success:
            CommandFormatter._output(f"\n{result.message}")
        else:
            CommandFormatter._output(f"\n{result.message}")
    
    @staticmethod
    def format_today_result(result: LogOperationResult):
        """Format today's log display result."""
        if result.success:
            CommandFormatter._output(f"\n[bold green]{result.message}:[/bold green]")
            CommandFormatter._output("=" * 60)
            CommandFormatter._output(result.data)
            CommandFormatter._output("=" * 60)
        else:
            CommandFormatter._output(f"\n[bold yellow]{result.message}[/bold yellow]")
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        CommandFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
