"""System command handlers."""
from ...types import CommandResult, ActionType
from ..registry import registry
from .services import SysService
from ..types import CommandCategory


@registry.register("sys.help", "Show this command reference", aliases=["help"], category=CommandCategory.GENERAL)
def cmd_sys_help(handler) -> CommandResult:
    """Show comprehensive command help."""
    return SysService.show_help(handler)


@registry.register("sys.quit", "Exit and save configuration", aliases=["quit"], category=CommandCategory.GENERAL)
def cmd_sys_quit(handler) -> CommandResult:
    """Exit the application."""
    return SysService.quit_application(handler)


@registry.register("sys.vars", "Show current system variables", category=CommandCategory.GENERAL)
def cmd_sys_vars(handler) -> CommandResult:
    """Display system variables and settings."""
    return SysService.show_variables(handler)