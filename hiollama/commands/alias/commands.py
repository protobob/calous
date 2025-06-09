"""Alias management commands."""
from typing import Optional
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import AliasService
from .formatters import AliasFormatter


@registry.register("alias.add", "Create a new command alias", category=CommandCategory.ALIAS)
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


@registry.register("alias.remove", "Remove a command alias", category=CommandCategory.ALIAS)
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


@registry.register("alias.list", "List all command aliases", category=CommandCategory.ALIAS)
def cmd_alias_list(handler) -> CommandResult:
    """List all user-defined command aliases."""
    result = AliasService.list_aliases()
    
    if result.data["aliases"]:
        AliasFormatter.print_alias_list(result.data["aliases"])
    else:
        AliasFormatter.print_no_aliases()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("alias.help", "Show help for alias commands", category=CommandCategory.ALIAS)
def cmd_alias_help(handler) -> CommandResult:
    """Show help for alias commands - alias for /sys.help alias."""
    handler.app.ui.show_category_help("alias")
    return CommandResult(ActionType.CONTINUE)
