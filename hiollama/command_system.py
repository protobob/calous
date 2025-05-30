"""Advanced command system with argparse integration and decorator-based registration."""
import argparse
import shlex
import inspect
from typing import Dict, Callable, Any, Optional, List, Union
from dataclasses import dataclass
from rich import print
from .types import CommandResult, ActionType


@dataclass
class CommandDefinition:
    """Definition of a command including its metadata and handler."""
    name: str
    handler: Callable
    description: str
    parser: argparse.ArgumentParser
    aliases: List[str] = None
    category: str = "General"


class CommandCategory:
    """Categories for organizing commands in help output."""
    GENERAL = "General Commands"
    NAVIGATION = "Chat Navigation" 
    MODEL = "Model Management"
    PROMPT = "Prompt Management"
    HISTORY = "Chat History"
    FILE = "File Operations"


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
            
            # Special handling for load command
            if name == "load":
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
            return cmd_def.handler(self, **kwargs)
        except Exception as e:
            print(f"[bold red]Command execution error:[/bold red] {e}")
            return CommandResult(ActionType.CONTINUE)


# Command implementations using the new decorator system

@registry.register("help", "Show this help menu", aliases=["h"], category=CommandCategory.GENERAL)
def cmd_help(handler) -> CommandResult:
    """Display the help menu using the existing UI manager implementation."""
    # Use your beautiful existing help menu instead of generating a new one
    handler.app.ui.help_menu()
    return CommandResult(ActionType.CONTINUE)


@registry.register("quit", "Exit and save configuration", aliases=["q", "exit"], category=CommandCategory.GENERAL)
def cmd_quit(handler) -> CommandResult:
    """Save configuration and exit."""
    # Don't save here - let the session manager handle it
    # Just return the QUIT action
    return CommandResult(ActionType.QUIT)


@registry.register("showvars", "Display current system variables", aliases=["vars"], category=CommandCategory.GENERAL)
def cmd_showvars(handler) -> CommandResult:
    """Display application variables."""
    handler.app.ui.show_variables()
    return CommandResult(ActionType.CONTINUE)


@registry.register("switch", "Switch between chats", category=CommandCategory.NAVIGATION)
def cmd_switch(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Switch to specified chat or cycle to next."""
    target_chat = None
    if chat_number is not None:
        if chat_number < 1:
            print("[bold red]Error:[/bold red] Chat number must be 1 or greater.")
            return CommandResult(ActionType.CONTINUE)
        target_chat = chat_number - 1  # Convert to 0-based index
    
    return CommandResult(ActionType.SWITCH, {"target_chat": target_chat})


@registry.register("twist", "Copy AI response to another chat", category=CommandCategory.NAVIGATION)
def cmd_twist(handler, target_chat: Optional[int] = None) -> CommandResult:
    """Twist last AI response to target chat."""
    # Validate last response exists
    last_response = handler.app.last_response
    if not last_response:
        print("\n[bold red]Error:[/bold red] No previous response to twist.")
        return CommandResult(ActionType.CONTINUE)

    # Extract content
    twist_content = last_response.get("message", {}).get("content", "")
    if not twist_content:
        print("[bold red]Error:[/bold red] Previous response is empty.")
        return CommandResult(ActionType.CONTINUE)

    # Process target chat
    target_index = None
    if target_chat is not None:
        if target_chat < 1:
            print("[bold red]Error:[/bold red] Chat number must be 1 or greater.")
            return CommandResult(ActionType.CONTINUE)
        target_index = target_chat - 1  # Convert to 0-based index

    return CommandResult(ActionType.TWIST, {
        "content": twist_content,
        "target_chat": target_index
    })


@registry.register("model", "Select a different Ollama model", category=CommandCategory.MODEL)
def cmd_model(handler) -> CommandResult:
    """Select a different model globally."""
    selected = handler.app.model.select_model()
    if selected:
        updated_count = handler.app.update_global_model(selected)
        print(f"Model changed globally to: {selected}")
        print(f"Updated model for {updated_count} chat instance(s).")
    return CommandResult(ActionType.CONTINUE)


@registry.register("toggle_eval", "Toggle evaluation data display", aliases=["eval"], category=CommandCategory.MODEL)
def cmd_toggle_eval(handler) -> CommandResult:
    """Toggle display of evaluation data."""
    handler.app.verbosity = not handler.app.verbosity
    print(f"\nVerbosity is now: {handler.app.verbosity}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("toggle_think", "Toggle AI thought filtering", aliases=["think"], category=CommandCategory.MODEL)
def cmd_toggle_think(handler) -> CommandResult:
    """Toggle filtering of AI thoughts."""
    handler.app.think_filtering = not handler.app.think_filtering
    print(f"\nThink filtering is now: {handler.app.think_filtering}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("system", "Change system prompt", category=CommandCategory.PROMPT)
def cmd_system(handler, prompt: str) -> CommandResult:
    """Change the system prompt."""
    if not prompt.strip():
        print("\n[bold red]Error:[/bold red] System prompt cannot be empty.")
        return CommandResult(ActionType.CONTINUE)

    print(f"\nPrevious System Prompt: [grey50]{handler.app.system_prompt['content']}[/grey50]")
    handler.app.system_prompt = {"role": "system", "content": prompt}
    print(f"System prompt updated to: [grey50]{prompt}[/grey50]")
    return CommandResult(ActionType.CONTINUE)


@registry.register("setprompt", "Save a prompt to a slot", category=CommandCategory.PROMPT)
def cmd_setprompt(handler, slot: int, prompt: str) -> CommandResult:
    """Set a saved prompt."""
    from .constants import MAX_PROMPTS
    
    if not (1 <= slot <= MAX_PROMPTS):
        print(f"[bold red]Error:[/bold red] Slot must be between 1 and {MAX_PROMPTS}.")
        return CommandResult(ActionType.CONTINUE)
    
    if not prompt.strip():
        print("[bold red]Error:[/bold red] Prompt text cannot be empty.")
        return CommandResult(ActionType.CONTINUE)
    
    handler.app.prompts[f"prompt{slot}"] = prompt
    print(f"Prompt{slot} set successfully!")
    handler.app.save_config()
    return CommandResult(ActionType.CONTINUE)


@registry.register("prompt", "Use a saved prompt", category=CommandCategory.PROMPT)
def cmd_prompt(handler, slot: int) -> CommandResult:
    """Use a saved prompt."""
    from .constants import MAX_PROMPTS
    
    if not (1 <= slot <= MAX_PROMPTS):
        print(f"[bold red]Error:[/bold red] Slot must be between 1 and {MAX_PROMPTS}.")
        return CommandResult(ActionType.CONTINUE)
    
    selected_prompt = handler.app.prompts[f"prompt{slot}"]
    if not selected_prompt:
        print(f"Prompt{slot} is empty. Set it first using /setprompt.")
        return CommandResult(ActionType.CONTINUE)
    
    print(f"Using Prompt{slot}: {selected_prompt}")
    handler.app.handle_regular_input(selected_prompt)
    return CommandResult(ActionType.CONTINUE)


@registry.register("showprompt", "Display saved prompts", aliases=["prompts"], category=CommandCategory.PROMPT)
def cmd_showprompt(handler, slot: Optional[int] = None) -> CommandResult:
    """Display saved prompts."""
    from .constants import MAX_PROMPTS
    
    if slot is None:
        # Show all prompts
        print("\n--- Saved Prompts ---")
        for i in range(1, MAX_PROMPTS + 1):
            prompt = handler.app.prompts[f"prompt{i}"]
            print(f"Prompt{i}: {prompt if prompt else '[Empty]'}")
        print("---------------------\n")
    else:
        if not (1 <= slot <= MAX_PROMPTS):
            print(f"[bold red]Error:[/bold red] Slot must be between 1 and {MAX_PROMPTS}.")
            return CommandResult(ActionType.CONTINUE)
        
        prompt = handler.app.prompts[f"prompt{slot}"]
        print(f"\nPrompt{slot}: {prompt if prompt else '[Empty]'}\n")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("clear", "Clear chat history", category=CommandCategory.HISTORY)
def cmd_clear(handler) -> CommandResult:
    """Clear the chat history after confirmation."""
    confirm = input("Are you sure you want to clear the chat history? (y/n): ").strip().lower()
    if confirm in ["y", "yes"]:
        handler.app.chat_history.clear()
        print("\nChat history cleared.")
    else:
        print("\nClear operation canceled.")
    return CommandResult(ActionType.CONTINUE)


@registry.register("history", "Display chat history", aliases=["hist"], category=CommandCategory.HISTORY)
def cmd_history(handler) -> CommandResult:
    """Display the chat history."""
    handler.app.chat_history.print_history()
    return CommandResult(ActionType.CONTINUE)


@registry.register("setmax", "Set maximum history size", category=CommandCategory.HISTORY)
def cmd_setmax(handler, size: int) -> CommandResult:
    """Set maximum chat history size."""
    if not (2 <= size <= 100) or size % 2 != 0:
        print("[bold red]Error:[/bold red] Size must be an even number between 2 and 100.")
        return CommandResult(ActionType.CONTINUE)
    
    handler.app.MAX_HISTORY = size
    print(f"\nMaximum chat history set to {size}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("toggle_log", "Toggle conversation logging", aliases=["log"], category=CommandCategory.HISTORY)
def cmd_toggle_log(handler) -> CommandResult:
    """Toggle logging of chat history."""
    handler.app.logging_enabled = not handler.app.logging_enabled
    print(f"\nLogging is now: {handler.app.logging_enabled}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("load", "Load file as prompt", category=CommandCategory.FILE)
def cmd_load(handler, filepath: str, prompt: List[str]) -> CommandResult:
    """Load a file and send it to the model with prompt."""
    from pathlib import Path
    
    if not Path(filepath).exists():
        print(f"\n[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        return CommandResult(ActionType.CONTINUE)
    
    # Join the prompt list into a single string
    prompt_text = " ".join(prompt)
    
    try:
        from .utils import Utils
        file_prompt = Utils.load_file_as_prompt(filepath, prompt_text)
        print(f"\n[grey50]Sent [italic]{filepath}[/italic] -- hold on, this might take awhile...[/grey50]")
        handler.app.handle_regular_input(file_prompt)
    except Exception as e:
        print(f"\n[bold red]Failed to load file:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)