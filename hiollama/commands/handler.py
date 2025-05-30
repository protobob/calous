"""Command handler for parsing and executing commands."""
import shlex
from rich import print
from ..types import CommandResult, ActionType
from .registry import registry


class AdvancedCommandHandler:
    """Advanced command handler with argparse integration."""
    
    def __init__(self, app):
        self.app = app
        self.registry = registry
    
    def parse_and_execute(self, user_input: str) -> CommandResult:
        """Parse and execute commands with full argparse support."""
        if not user_input.startswith('/'):
            return CommandResult(ActionType.CONTINUE)
        
        # Remove leading slash and parse command line
        try:
            # Use shlex to properly handle quoted arguments
            tokens = shlex.split(user_input[1:])
        except ValueError as e:
            print(f"[bold red]Error:[/bold red] Invalid command syntax: {e}")
            return CommandResult(ActionType.CONTINUE)
        
        if not tokens:
            print("[bold red]Error:[/bold red] Empty command.")
            return CommandResult(ActionType.CONTINUE)
        
        command_name = tokens[0].lower()
        args = tokens[1:]
        
        # Get command definition
        cmd_def = self.registry.get_command(command_name)
        if not cmd_def:
            print(f"[bold red]Invalid command:[/bold red] /{command_name}")
            print("[grey50]Type /help to see available commands.[/grey50]")
            return CommandResult(ActionType.CONTINUE)
        
        # Parse arguments
        try:
            parsed_args = cmd_def.parser.parse_args(args)
        except SystemExit:
            # Argparse tried to exit - show usage
            print(f"[grey50]Usage: {cmd_def.parser.format_usage().strip()}[/grey50]")
            return CommandResult(ActionType.CONTINUE)
        except Exception as e:
            print(f"[bold red]Error:[/bold red] {e}")
            print(f"[grey50]Usage: {cmd_def.parser.format_usage().strip()}[/grey50]")
            return CommandResult(ActionType.CONTINUE)
        
        # Execute command
        try:
            # Convert parsed args to kwargs
            kwargs = vars(parsed_args)
            
            # Special handling for commands with nargs='+'
            if cmd_def.name in ["system", "setprompt", "load"]:
                if "prompt" in kwargs and isinstance(kwargs["prompt"], list):
                    kwargs["prompt"] = " ".join(kwargs["prompt"])
            
            return cmd_def.handler(self, **kwargs)
        except Exception as e:
            print(f"[bold red]Command execution error:[/bold red] {e}")
            return CommandResult(ActionType.CONTINUE)