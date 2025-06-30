"""Command handler for parsing and executing commands."""
from ..types import CommandResult, ActionType
from .registry import registry
from .command_service import CommandParsingService, CommandExecutionService
from .formatters import CommandFormatter


class AdvancedCommandHandler:
    """Advanced command handler with argparse integration."""
    
    def __init__(self, app):
        self.app = app
        self.registry = registry
        
        # Inject session manager into formatter for output routing
        if hasattr(app, 'session_manager') and app.session_manager:
            CommandFormatter._session_manager = app.session_manager
        else:
            CommandFormatter._session_manager = None
    
    def parse_and_execute(self, user_input: str) -> CommandResult:
        """Parse and execute commands with full argparse support."""
        # Parse command input
        parsed_input = CommandParsingService.parse_command_input(user_input)
        if not parsed_input:
            return CommandResult(ActionType.CONTINUE)
        
        command_name, args = parsed_input
        
        # Validate command exists
        cmd_def = CommandParsingService.validate_command(command_name, self.registry)
        if not cmd_def:
            return CommandResult(ActionType.CONTINUE)
        
        # Parse command arguments
        kwargs = CommandParsingService.parse_command_arguments(cmd_def, args)
        if kwargs is None:
            return CommandResult(ActionType.CONTINUE)
        
        # Apply special command handling
        kwargs = CommandParsingService.apply_special_command_handling(cmd_def, kwargs)
        
        # Execute command
        return CommandExecutionService.execute_command(self, cmd_def, kwargs, command_name, args)