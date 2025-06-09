"""System command handlers."""
from ...types import CommandResult, ActionType
from ..registry import registry
from .services import SysService
from ..types import CommandCategory


@registry.register("sys.help", "Show this command reference", aliases=["help"], category=CommandCategory.GENERAL)
def cmd_sys_help(handler, category: str = None, command: str = None) -> CommandResult:
    """Show comprehensive command help.
    
    Args:
        category: Optional category name (e.g., 'chat', 'model', 'prompt')
        command: Optional specific command name (e.g., 'chat.switch', 'model.setctx')
    """
    return SysService.show_help(handler, category, command)


@registry.register("sys.quit", "Exit and save configuration", aliases=["quit"], category=CommandCategory.GENERAL)
def cmd_sys_quit(handler) -> CommandResult:
    """Exit the application."""
    return SysService.quit_application(handler)


@registry.register("model.vars", "Show model-related variables", category=CommandCategory.MODEL)
def cmd_model_vars(handler) -> CommandResult:
    """Display model-related variables and settings."""
    return SysService.show_model_variables(handler)


@registry.register("chat.vars", "Show chat-specific variables", category=CommandCategory.NAVIGATION)
def cmd_chat_vars(handler) -> CommandResult:
    """Display chat-specific variables and settings."""
    return SysService.show_chat_variables(handler)


@registry.register("log.vars", "Show logging-related variables", category=CommandCategory.LOGGING)
def cmd_log_vars(handler) -> CommandResult:
    """Display logging-related variables and settings."""
    return SysService.show_log_variables(handler)


@registry.register("sys.help.all", "List all commands by category", category=CommandCategory.GENERAL)
def cmd_sys_help_all(handler) -> CommandResult:
    """Show comprehensive list of all commands by category."""
    return SysService.show_help_all(handler)