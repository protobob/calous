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
    def show_model_variables(handler) -> CommandResult:
        """Display model-related variables."""
        handler.app.ui.show_model_variables()
        return CommandResult(ActionType.CONTINUE)
    
    @staticmethod
    def show_chat_variables(handler) -> CommandResult:
        """Display chat-specific variables."""
        handler.app.ui.show_chat_variables()
        return CommandResult(ActionType.CONTINUE)
    
    @staticmethod
    def show_log_variables(handler) -> CommandResult:
        """Display logging-related variables."""
        handler.app.ui.show_log_variables()
        return CommandResult(ActionType.CONTINUE)
