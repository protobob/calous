"""Log management commands."""
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import LogService
from .formatters import LogFormatter


@registry.register("log.on", "Enable unified logging", category=CommandCategory.HISTORY)
def cmd_log_on(handler) -> CommandResult:
    """Enable unified logging of all chat activities."""
    service = LogService(handler.app)
    result = service.enable_logging()
    LogFormatter.format_enable_result(result)
    return CommandResult(ActionType.CONTINUE)


@registry.register("log.off", "Disable unified logging", category=CommandCategory.HISTORY)
def cmd_log_off(handler) -> CommandResult:
    """Disable unified logging of all chat activities."""
    service = LogService(handler.app)
    result = service.disable_logging()
    LogFormatter.format_disable_result(result)
    return CommandResult(ActionType.CONTINUE)


@registry.register("log.today", "View today's unified log", category=CommandCategory.HISTORY)
def cmd_log_today(handler) -> CommandResult:
    """View the unified log for today."""
    service = LogService(handler.app)
    result = service.get_today_log()
    LogFormatter.format_today_result(result)
    return CommandResult(ActionType.CONTINUE)
