"""Command registry with decorator-based registration."""
import argparse
import inspect
from typing import Dict, Optional, List, Union
from .types import CommandDefinition, CommandCategory


class CommandRegistry:
    """Registry for all available commands with decorator-based registration."""
    
    def __init__(self):
        self.commands: Dict[str, CommandDefinition] = {}
        self.aliases: Dict[str, str] = {}
    
    def register(self, name: str, description: str = "", aliases: List[str] = None, 
                category: str = CommandCategory.GENERAL):
        """Decorator for registering commands."""
        def decorator(func):
            # Create argument parser for this command
            parser = argparse.ArgumentParser(
                prog=f"/{name}",
                description=description,
                add_help=False,  # We'll handle help ourselves
                exit_on_error=False  # Don't exit on parse errors
            )
            
            # Special handling for commands that need to capture remaining text
            if name in ["system", "setprompt"]:
                if name == "system":
                    parser.add_argument("prompt", nargs='+', help="System prompt text (no quotes needed)")
                elif name == "setprompt":
                    parser.add_argument("slot", type=int, help="Prompt slot number")
                    parser.add_argument("prompt", nargs='+', help="Prompt text (no quotes needed)")            # Special handling for load command
            elif name in ["load", "file.load"]:
                parser.add_argument("filepath", type=str, help="File path to load")
                parser.add_argument("prompt", nargs='+', help="Prompt text (no quotes needed)")
            else:
                # Regular argument parsing for other commands
                sig = inspect.signature(func)
                for param_name, param in sig.parameters.items():
                    if param_name in ['self', 'handler', 'args', 'kwargs']:
                        continue
                        
                    # Determine argument properties from annotations and defaults
                    if param.annotation != inspect.Parameter.empty:
                        arg_type = param.annotation
                    else:
                        arg_type = str
                    
                    # Handle Optional types
                    if hasattr(arg_type, '__origin__') and arg_type.__origin__ is Union:
                        # This is Optional[SomeType]
                        inner_type = arg_type.__args__[0]
                        parser.add_argument(
                            param_name,
                            type=inner_type,
                            nargs='?',
                            help=f"{param_name} (optional)"
                        )
                    elif param.default != inspect.Parameter.empty:
                        # Optional argument with default
                        if param.default is None:
                            # Positional optional argument
                            parser.add_argument(
                                param_name,
                                type=arg_type,
                                nargs='?',
                                default=None,
                                help=f"{param_name} (optional)"
                            )
                        else:
                            # Named optional argument
                            parser.add_argument(
                                f"--{param_name}",
                                type=arg_type,
                                default=param.default,
                                help=f"{param_name} (default: {param.default})"
                            )
                    else:
                        # Required argument
                        parser.add_argument(
                            param_name,
                            type=arg_type,
                            help=f"{param_name} (required)"
                        )
            
            # Store command definition
            cmd_def = CommandDefinition(
                name=name,
                handler=func,
                description=description,
                parser=parser,
                aliases=aliases or [],
                category=category
            )
            
            self.commands[name] = cmd_def
            
            # Register aliases
            if aliases:
                for alias in aliases:
                    self.aliases[alias] = name
            
            return func
        return decorator
    
    def get_command(self, name: str) -> Optional[CommandDefinition]:
        """Get command definition by name or alias."""
        # Check direct name first
        if name in self.commands:
            return self.commands[name]
        
        # Check aliases
        if name in self.aliases:
            return self.commands[self.aliases[name]]
        
        return None
    
    def get_all_commands(self) -> Dict[str, CommandDefinition]:
        """Get all registered commands."""
        return self.commands.copy()


# Global registry instance
registry = CommandRegistry()