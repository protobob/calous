"""System services for handling system-level operations."""
from ...types import CommandResult, ActionType
from ..registry import registry


class SysService:
    """Service class for system operations."""
    
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
    def show_help(handler, category: str = None, command: str = None) -> CommandResult:
        """Display the help menu with optional category or command filtering.
        
        Args:
            category: Optional category name for category-specific help
            command: Optional command name for command-specific help
        """
        if command:
            # Show help for specific command
            handler.app.ui.show_command_help(command)
        elif category:
            # Handle special "all" category to show comprehensive help
            if category.lower() == "all":
                handler.app.ui.help_menu_all()
            else:
                # Show help for specific category
                handler.app.ui.show_category_help(category)
        else:
            # Show streamlined help menu
            handler.app.ui.help_menu()
        return CommandResult(ActionType.CONTINUE)
    
    @staticmethod
    def quit_application(handler) -> CommandResult:
        """Save configuration and exit."""
        # Prevent quit command in socket/non-interactive mode
        if getattr(handler.app, 'non_interactive', False):
            from rich import print as rich_print
            CommandFormatter._output(f"\n[bold red]Error:[/bold red] Quit command not available in socket mode")
            return CommandResult(ActionType.CONTINUE)
        
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
    
    @staticmethod
    def show_help_all(handler) -> CommandResult:
        """Display comprehensive help menu with all commands."""
        handler.app.ui.help_menu_all()
        return CommandResult(ActionType.CONTINUE)
