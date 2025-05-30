"""General application commands."""
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


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