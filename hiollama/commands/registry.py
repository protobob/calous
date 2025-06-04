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
        self.user_aliases: Dict[str, str] = {}
        self._load_user_aliases()
    
    def _load_user_aliases(self):
        """Load user-defined aliases from config."""
        try:
            from ..config import ConfigManager
            self.user_aliases = ConfigManager.get_aliases()
        except Exception:
            # Fallback if config not available during import
            self.user_aliases = {}
    
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
        
        # Check user aliases first (they take precedence)
        if name in self.user_aliases:
            return self.commands.get(self.user_aliases[name])
        
        # Check built-in aliases
        if name in self.aliases:
            return self.commands[self.aliases[name]]
        
        return None
    
    def get_all_commands(self) -> Dict[str, CommandDefinition]:
        """Get all registered commands."""
        return self.commands.copy()
    
    def add_user_alias(self, alias: str, command: str) -> bool:
        """Add a user-defined alias and persist to config."""
        # Validate that target command exists
        if not self.get_command(command):
            return False
            
        # Prevent aliases that conflict with existing command names
        if alias in self.commands:
            return False
            
        try:
            from ..config import ConfigManager
            ConfigManager.add_alias(alias, command)
            self.user_aliases[alias] = command
            return True
        except Exception:
            return False
    
    def remove_user_alias(self, alias: str) -> bool:
        """Remove a user-defined alias and update config."""
        if alias not in self.user_aliases:
            return False
            
        try:
            from ..config import ConfigManager
            success = ConfigManager.remove_alias(alias)
            if success:
                del self.user_aliases[alias]
            return success
        except Exception:
            return False
    
    def list_user_aliases(self) -> Dict[str, str]:
        """Get all user-defined aliases."""
        return self.user_aliases.copy()
    
    def refresh_user_aliases(self):
        """Reload user aliases from config."""
        self._load_user_aliases()


# Global registry instance
registry = CommandRegistry()