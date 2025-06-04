"""General application commands."""
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory
from ..config import ConfigManager
from ..utils import get_chat_color
from rich import print
from rich.prompt import Prompt


def cmd_help(handler) -> CommandResult:
    """Display the help menu using the existing UI manager implementation."""
    handler.app.ui.help_menu()
    return CommandResult(ActionType.CONTINUE)


def cmd_quit(handler) -> CommandResult:
    """Save configuration and exit."""
    return CommandResult(ActionType.QUIT)


def cmd_showvars(handler) -> CommandResult:
    """Display application variables."""
    handler.app.ui.show_variables()
    return CommandResult(ActionType.CONTINUE)


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


def cmd_alias_add(handler, alias: str, command: str) -> CommandResult:
    """Add a new command alias."""
    # Validate that target command exists
    if not registry.get_command(command):
        print(f"[bold red]Error:[/bold red] Command '{command}' does not exist")
        print("[grey50]Use /sys.help to see available commands[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    # Prevent aliases that conflict with existing command names
    if registry.get_command(alias) and alias not in registry.user_aliases:
        print(f"[bold red]Error:[/bold red] '{alias}' is already a command name")
        print("[grey50]Choose a different alias name[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    # Check if alias already exists
    if alias in registry.user_aliases:
        old_command = registry.user_aliases[alias]
        print(f"[yellow]Warning:[/yellow] Alias '{alias}' already exists (points to '{old_command}')")
        confirm = Prompt.ask("Overwrite existing alias?", choices=["y", "n"], default="n")
        if confirm.lower() != "y":
            return CommandResult(ActionType.CONTINUE)
    
    # Add the alias
    success = registry.add_user_alias(alias, command)
    if success:
        print(f"[green]✓ Alias created:[/green] '{alias}' → '{command}'")
        print(f"[grey50]You can now use /{alias} instead of /{command}[/grey50]")
    else:
        print(f"[bold red]Error:[/bold red] Failed to create alias")
    
    return CommandResult(ActionType.CONTINUE)


def cmd_alias_remove(handler, alias: str) -> CommandResult:
    """Remove a command alias."""
    if alias not in registry.user_aliases:
        print(f"[bold red]Error:[/bold red] Alias '{alias}' does not exist")
        print("[grey50]Use /alias.list to see current aliases[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    command = registry.user_aliases[alias]
    success = registry.remove_user_alias(alias)
    
    if success:
        print(f"[green]✓ Alias removed:[/green] '{alias}' (was pointing to '{command}')")
    else:
        print(f"[bold red]Error:[/bold red] Failed to remove alias")
    
    return CommandResult(ActionType.CONTINUE)


def cmd_alias_list(handler) -> CommandResult:
    """List all user-defined command aliases."""
    aliases = registry.list_user_aliases()
    
    if not aliases:
        print("[yellow]No aliases defined[/yellow]")
        print("[grey50]Use /alias.add <alias> <command> to create aliases[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    print(f"[bold cyan]User-Defined Aliases ({len(aliases)}):[/bold cyan]")
    print()
    
    # Sort aliases for consistent display
    for alias in sorted(aliases.keys()):
        command = aliases[alias]
        print(f"  [green]{alias}[/green] → [cyan]{command}[/cyan]")
    
    print()
    print("[grey50]Use /alias.remove <alias> to remove an alias[/grey50]")
    return CommandResult(ActionType.CONTINUE)


def cmd_alias_help(handler) -> CommandResult:
    """Show alias command usage help."""
    print("\n[bold cyan]Alias Management Commands:[/bold cyan]")
    print()
    print("  [bold]/alias.add <alias> <command>[/bold]")
    print("    Create a new alias for an existing command")
    print("    Example: /alias.add t chat.twist")
    print()
    print("  [bold]/alias.remove <alias>[/bold]")
    print("    Remove an existing alias")
    print("    Example: /alias.remove t")
    print()
    print("  [bold]/alias.list[/bold]")
    print("    Show all current aliases")
    print()
    print("[grey50]Aliases let you create shortcuts for frequently used commands[/grey50]")
    return CommandResult(ActionType.CONTINUE)


# New hierarchical system commands
@registry.register("sys.help", "Show this command reference", aliases=["help"], category=CommandCategory.GENERAL)
def cmd_sys_help(handler) -> CommandResult:
    """Show comprehensive command help."""
    return cmd_help(handler)


@registry.register("sys.quit", "Exit and save configuration", aliases=["quit"], category=CommandCategory.GENERAL)
def cmd_sys_quit(handler) -> CommandResult:
    """Exit the application."""
    return cmd_quit(handler)


@registry.register("sys.vars", "Show current system variables", category=CommandCategory.GENERAL)
def cmd_sys_vars(handler) -> CommandResult:
    """Display system variables and settings."""
    return cmd_showvars(handler)


# Alias management commands
@registry.register("alias.add", "Create a new command alias", category=CommandCategory.GENERAL)
def cmd_alias_add_registered(handler, alias: str, command: str) -> CommandResult:
    """Create a new command alias."""
    return cmd_alias_add(handler, alias, command)


@registry.register("alias.remove", "Remove a command alias", category=CommandCategory.GENERAL)
def cmd_alias_remove_registered(handler, alias: str) -> CommandResult:
    """Remove a command alias."""
    return cmd_alias_remove(handler, alias)


@registry.register("alias.list", "List all command aliases", category=CommandCategory.GENERAL)
def cmd_alias_list_registered(handler) -> CommandResult:
    """List all user-defined command aliases."""
    return cmd_alias_list(handler)


@registry.register("alias", "Show alias command help", category=CommandCategory.GENERAL)
def cmd_alias_help_registered(handler) -> CommandResult:
    """Show alias management help."""
    return cmd_alias_help(handler)