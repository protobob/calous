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




@registry.register("sys.help.all", "List all commands by category", category=CommandCategory.GENERAL)
def cmd_sys_help_all(handler) -> CommandResult:
    """Show comprehensive list of all commands by category."""
    return SysService.show_help_all(handler)