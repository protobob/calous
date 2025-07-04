"""Log command formatters."""

from ...constants import Colors, Messages
from .services import LogOperationResult
from ..formatters import CommandFormatter


class LogFormatter(CommandFormatter):
    """Handles formatting for log command outputs."""
    
    @staticmethod
    def _output(message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        session_manager = CommandFormatter._get_session_manager()
        if session_manager and session_manager.socket_mode and session_manager.current_connection:
            session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
    @staticmethod
    def format_enable_result(result: LogOperationResult):
        """Format log enable operation result."""
        if result.success:
            LogFormatter._output(f"\n{result.message}")
        else:
            LogFormatter._output(f"\n{result.message}")
    
    @staticmethod
    def format_disable_result(result: LogOperationResult):
        """Format log disable operation result."""
        if result.success:
            LogFormatter._output(f"\n{result.message}")
        else:
            LogFormatter._output(f"\n{result.message}")
    
    @staticmethod
    def format_today_result(result: LogOperationResult):
        """Format today's log display result."""
        if result.success:
            LogFormatter._output(f"\n[1;32m{result.message}:[0m")
            LogFormatter._output("=" * 60)
            LogFormatter._output(result.data)
            LogFormatter._output("=" * 60)
        else:
            LogFormatter._output(f"\n[1;33m{result.message}[0m")
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        LogFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
