"""General application commands."""
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory
from .alias_service import AliasService
from .chat_service import ChatService
from .formatters import AliasFormatter, ChatFormatter
from ..constants import Messages


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
        # Get chat info for display
        chat_info = ChatService.get_chat_info(handler.app)
        
        # Show warning and ask for confirmation
        ChatFormatter.print_reset_warning(chat_info["number"], chat_info["color"])
        
        if ChatFormatter.confirm_chat_reset():
            # Perform the reset
            success = ChatService.reset_chat_to_defaults(handler.app)
            
            if success:
                ChatFormatter.print_reset_success(chat_info["number"], chat_info["color"])
            else:
                ChatFormatter.print_error("Failed to reset chat configuration")
        else:
            print(Messages.OPERATION_CANCELLED)
            
    except KeyboardInterrupt:
        print(f"\n{Messages.OPERATION_CANCELLED}")
        
    return CommandResult(ActionType.CONTINUE)


@registry.register("alias.add", "Create a new command alias", category=CommandCategory.GENERAL)
def cmd_alias_add(handler, alias: str, command: str) -> CommandResult:
    """Add a new command alias."""
    # Check if alias already exists and get confirmation if needed
    exists, old_command = AliasService.check_existing_alias(alias)
    if exists:
        if not AliasFormatter.confirm_alias_overwrite(alias, old_command):
            return CommandResult(ActionType.CONTINUE)
    
    result = AliasService.add_alias(alias, command)
    
    if result.success:
        if exists:
            AliasFormatter.print_alias_updated(alias, command, old_command)
        else:
            AliasFormatter.print_alias_created(alias, command)
    else:
        # Handle different error cases
        if "does not exist" in result.message:
            AliasFormatter.print_error(result.message, "Use /sys.help to see available commands")
        elif "already a command name" in result.message:
            AliasFormatter.print_error(result.message, "Choose a different alias name")
        else:
            AliasFormatter.print_error(result.message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("alias.remove", "Remove a command alias", category=CommandCategory.GENERAL)
def cmd_alias_remove(handler, alias: str) -> CommandResult:
    """Remove a command alias."""
    result = AliasService.remove_alias(alias)
    
    if result.success:
        AliasFormatter.print_alias_removed(result.data["alias"], result.data["command"])
    else:
        if "does not exist" in result.message:
            AliasFormatter.print_error(result.message, "Use /alias.list to see current aliases")
        else:
            AliasFormatter.print_error(result.message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("alias.list", "List all command aliases", category=CommandCategory.GENERAL)
def cmd_alias_list(handler) -> CommandResult:
    """List all user-defined command aliases."""
    result = AliasService.list_aliases()
    
    if result.data["aliases"]:
        AliasFormatter.print_alias_list(result.data["aliases"])
    else:
        AliasFormatter.print_no_aliases()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("alias", "Show alias command help", category=CommandCategory.GENERAL)
def cmd_alias_help(handler) -> CommandResult:
    """Show alias command usage help."""
    AliasFormatter.print_alias_help()
    return CommandResult(ActionType.CONTINUE)


# System commands with hierarchical naming
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