"""General application commands."""
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory
from ..config import ConfigManager
from ..utils import get_chat_color
from rich import print
from rich.prompt import Prompt


@registry.register("help", "Show this help menu", aliases=["h"], category=CommandCategory.GENERAL)
def cmd_help(handler) -> CommandResult:
    """Display the help menu using the existing UI manager implementation."""
    handler.app.ui.help_menu()
    return CommandResult(ActionType.CONTINUE)


@registry.register("quit", "Exit and save configuration", aliases=["q", "exit"], category=CommandCategory.GENERAL)
def cmd_quit(handler) -> CommandResult:
    """Save configuration and exit."""
    return CommandResult(ActionType.QUIT)


@registry.register("showvars", "Display current system variables", aliases=["vars"], category=CommandCategory.GENERAL)
def cmd_showvars(handler) -> CommandResult:
    """Display application variables."""
    handler.app.ui.show_variables()
    return CommandResult(ActionType.CONTINUE)


@registry.register("resetchat", "Reset chat to factory defaults", category=CommandCategory.GENERAL)
def cmd_resetchat(handler) -> CommandResult:
    """Reset the current chat to factory defaults with confirmation."""
    try:
        # Get chat info for colored display
        chat_number = handler.app.instance_index + 1
        chat_color = get_chat_color(handler.app.instance_index)
        
        # Ask for confirmation with colored text
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]RESET[/bold red] [bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] to factory defaults.")
        print("This will [bold red]CLEAR[/bold red] history, system prompt, and all saved prompts.")
        
        confirm = Prompt.ask("\nAre you sure you want to continue?", choices=["y", "n"], default="n")
        
        if confirm == 'y':            # Get the default chat configuration
            default_config = ConfigManager._generate_default_chat_config()
            
            # Update the chat instance with default values
            handler.app.verbosity = default_config["verbosity"]
            handler.app.system_prompt = {
                "role": "system",
                "content": default_config["system_prompt"]
            }
            handler.app.logging_enabled = default_config["logging_enabled"]
            handler.app.thinking_enabled = False  # Default to False for clean output
            handler.app.prompts = default_config["prompts"]
            
            # Clear chat history
            handler.app.chat_history.clear()
            # Save the updated configuration
            handler.app.save_config()
            print(f"[bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] reset to factory defaults successfully!")
        else:
            print("Reset operation cancelled.")
    except KeyboardInterrupt:
        print("\nReset operation cancelled.")
    return CommandResult(ActionType.CONTINUE)