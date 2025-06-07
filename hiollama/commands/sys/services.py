"""System services for handling system-level operations."""
from ...types import CommandResult, ActionType


class SysService:
    """Service class for system operations."""
    
    @staticmethod
    def show_help(handler) -> CommandResult:
        """Display the help menu using the existing UI manager implementation."""
        handler.app.ui.help_menu()
        return CommandResult(ActionType.CONTINUE)
    
    @staticmethod
    def quit_application(handler) -> CommandResult:
        """Save configuration and exit."""
        return CommandResult(ActionType.QUIT)
    
    @staticmethod
    def show_variables(handler) -> CommandResult:
        """Display application variables."""
        handler.app.ui.show_variables()
        return CommandResult(ActionType.CONTINUE)
