"""Command parsing and execution services."""
import shlex
from typing import List, Dict, Any, Optional, Tuple
from ..types import CommandResult, ActionType
from .types import CommandDefinition
from .formatters import HandlerFormatter
from ..unified_logger import unified_logger


class CommandParsingService:
    """Service for parsing and preparing command execution."""
    
    @staticmethod
    def parse_command_input(user_input: str) -> Optional[Tuple[str, List[str]]]:
        """Parse user input into command name and arguments.
        
        Returns:
            Tuple of (command_name, args) or None if parsing fails
        """
        if not user_input.startswith('/'):
            return None
        
        # Remove leading slash and parse command line
        try:
            # Use shlex to properly handle quoted arguments
            tokens = shlex.split(user_input[1:])
        except ValueError as e:
            HandlerFormatter.invalid_command_syntax(str(e))
            return None
        
        if not tokens:
            HandlerFormatter.empty_command_error()
            return None
        
        command_name = tokens[0].lower()
        args = tokens[1:]
        
        return command_name, args
    
    @staticmethod
    def validate_command(command_name: str, registry) -> Optional[CommandDefinition]:
        """Validate command exists and return its definition.
        
        Returns:
            CommandDefinition if valid, None otherwise
        """
        cmd_def = registry.get_command(command_name)
        if not cmd_def:
            HandlerFormatter.invalid_command(command_name)
            return None
        
        return cmd_def
    
    @staticmethod
    def parse_command_arguments(cmd_def: CommandDefinition, args: List[str]) -> Optional[Dict[str, Any]]:
        """Parse command arguments using the command's parser.
        
        Returns:
            Parsed arguments as dict, or None if parsing fails
        """
        try:
            parsed_args = cmd_def.parser.parse_args(args)
            return vars(parsed_args)
        except SystemExit:
            # Argparse tried to exit - show usage
            HandlerFormatter.command_usage(cmd_def.parser.format_usage())
            return None
        except Exception as e:
            HandlerFormatter.argument_parse_error(str(e), cmd_def.parser.format_usage())
            return None
    
    @staticmethod
    def apply_special_command_handling(cmd_def: CommandDefinition, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply special handling for specific commands that need argument processing.
        
        Returns:
            Modified kwargs dict
        """
        # Special handling for commands with nargs='+'
        if cmd_def.name in ["file.load"]:
            if "prompt" in kwargs and isinstance(kwargs["prompt"], list):
                kwargs["prompt"] = " ".join(kwargs["prompt"])
        
        # Add more special handling here as needed
        return kwargs


class CommandExecutionService:
    """Service for executing commands and logging."""
    
    @staticmethod
    def execute_command(handler, cmd_def: CommandDefinition, kwargs: Dict[str, Any], 
                       command_name: str, args: List[str]) -> CommandResult:
        """Execute a command with proper logging and error handling.
        
        Returns:
            CommandResult from the executed command
        """
        try:
            # Log command execution
            unified_logger.log_command_execution(
                handler.app.instance_index, 
                f"/{command_name} {' '.join(args)}" if args else f"/{command_name}"
            )
            
            # Execute the command
            return cmd_def.handler(handler, **kwargs)
            
        except Exception as e:
            HandlerFormatter.command_execution_error(str(e))
            return CommandResult(ActionType.CONTINUE)
