"""Command registry with decorator-based registration."""
import argparse
import inspect
import io
import re
import sys
from contextlib import redirect_stdout
from typing import Dict, Optional, List, Union, get_origin, get_args
from .types import CommandDefinition, CommandCategory
from ..unified_logger import unified_logger


class CommandRegistry:
    """Registry for all available commands with decorator-based registration."""
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            unified_logger.info(message, stream='app', component='command_registry_fallback')
    
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
    
    def _strip_rich_tags(self, rich_output: str) -> str:
        """Strip Rich tags and ANSI escape sequences from the output."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', rich_output)
    
    def register(self, name: str, description: str = "", aliases: List[str] = [], 
                category: str = CommandCategory.GENERAL):
        """Decorator for registering commands."""
        def decorator(func):
            # Create argument parser for this command
            parser = argparse.ArgumentParser(
                prog=f"/{name}",
                description=description,
                add_help=False,  # We'll handle help ourselves
                exit_on_error=False  # Don't exit on parse errors
            )            # Special handling for commands that need to capture remaining text
            if name in ["persona.name", "persona.set", "persona.load", "persona.delete", 
                       "context.save", "context.load", "context.delete",
                       "history.save", "history.load", "history.delete"]:
                if name == "persona.name":
                    parser.add_argument("name", nargs='+', help="Persona name (multiple words allowed)")
                elif name == "persona.set":
                    parser.add_argument("slot", type=int, help="Persona slot number (0-9)")
                    parser.add_argument("content", nargs='+', help="Persona content (multiple words allowed)")
                elif name == "persona.load":
                    parser.add_argument("name", nargs='+', help="Persona name to load (multiple words allowed)")
                elif name == "persona.delete":
                    parser.add_argument("name", nargs='+', help="Persona name to delete (multiple words allowed)")
                elif name in ["context.save", "context.load", "context.delete"]:
                    parser.add_argument("name", nargs='+', help="Context name (multiple words allowed)")
                elif name in ["history.save", "history.load", "history.delete"]:
                    parser.add_argument("filename", nargs='+', help="Filename (multiple words allowed)")
            # Special handling for file.load command
            elif name in ["file.load"]:
                parser.add_argument("filepath", type=str, help="File path to load")
                parser.add_argument("prompt", nargs='*', default="", help="Prompt text (no quotes needed)")
            # Special handling for prompt.set command
            elif name == "prompt.set":
                parser.add_argument("slot", type=int, help="Prompt slot number")
                parser.add_argument("prompt", nargs='+', help="Prompt text (multiple words allowed)")
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
                    
                    origin = get_origin(arg_type)
                    if origin is Union:
                        # This is Optional[SomeType]
                        inner_type = get_args(arg_type)[0]
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
            
            def wrapped_handler(*args, **kwargs):
                # Store original stdout
                original_stdout = sys.stdout
                buffer = io.StringIO()
                
                try:
                    # Redirect stdout to capture terminal output
                    sys.stdout = buffer
                    # Execute the original function and get its return value
                    result = func(*args, **kwargs)
                finally:
                    # Restore original stdout
                    sys.stdout = original_stdout
                
                # Get the captured output (keep Rich markup)
                rich_output = buffer.getvalue()
                
                # Send the Rich output to client (let send_to_client handle format conversion)
                if rich_output:
                    self._output(rich_output)
                
                # If the command returned a CommandResult, update its message with Rich markup
                if hasattr(result, 'message') and hasattr(result, 'action'):
                    # Always use Rich output - let send_to_client convert format if needed
                    if rich_output.strip():
                        result.message = rich_output.strip()
                    return result
                else:
                    # Return original result if it's not a CommandResult
                    return result

            # Store command definition
            cmd_def = CommandDefinition(
                name=name,
                handler=wrapped_handler,
                description=description,
                parser=parser,
                aliases=aliases,
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
            # Update commands file for tab completion
            self.write_commands_file()
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
                # Update commands file for tab completion
                self.write_commands_file()
            return success
        except Exception:
            return False
    
    def list_user_aliases(self) -> Dict[str, str]:
        """Get all user-defined aliases."""
        return self.user_aliases.copy()
    
    def refresh_user_aliases(self):
        """Reload user aliases from config."""
        self._load_user_aliases()
    
    def write_commands_file(self):
        """Write all commands to a file for cx_rust tab completion."""
        try:
            from ..constants import COMMANDS_FILE, CALOUS_DIR
            import os
            
            # Ensure directory exists
            os.makedirs(CALOUS_DIR, exist_ok=True)
            
            # Get all commands and sort them
            commands = []
            for name in sorted(self.commands.keys()):
                commands.append(f"/{name}")
            
            # Add aliases
            for alias in sorted(self.aliases.keys()):
                if alias not in [name[1:] for name in commands]:  # Don't duplicate
                    commands.append(f"/{alias}")
            
            # Add user aliases
            for alias in sorted(self.user_aliases.keys()):
                if alias not in [name[1:] for name in commands]:  # Don't duplicate
                    commands.append(f"/{alias}")
            
            # Write to file
            with open(COMMANDS_FILE, 'w') as f:
                f.write('\n'.join(sorted(commands)) + '\n')
                
        except Exception as e:
            # Silently fail - this is not critical functionality
            pass


# Global registry instance
registry = CommandRegistry()