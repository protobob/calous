"""History management commands."""
from typing import Optional
from rich import print
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import HistoryService
from .formatters import HistoryFormatter


@registry.register("history.clear", "Clear the current chat history", category=CommandCategory.HISTORY)
def cmd_history_clear(handler) -> CommandResult:
    """Clear the current chat's history with confirmation."""
    service = HistoryService(handler.app)
    chat_info = service.get_chat_info()
    
    # Show warning and ask for confirmation
    HistoryFormatter.format_clear_warning(chat_info)
    
    if HistoryFormatter.confirm_clear():
        service.clear_history()
        HistoryFormatter.format_clear_success(chat_info)
    else:
        HistoryFormatter.format_operation_cancelled()
        
    return CommandResult(ActionType.CONTINUE)


@registry.register("history.show", "View the current chat history", category=CommandCategory.HISTORY)
def cmd_history_show(handler) -> CommandResult:
    """Display chat history."""
    service = HistoryService(handler.app)
    service.display_history()
    return CommandResult(ActionType.CONTINUE)


@registry.register("history.help", "Show help for history commands", category=CommandCategory.HISTORY)
def cmd_history_help(handler) -> CommandResult:
    """Show help for history commands - alias for /sys.help history."""
    handler.app.ui.show_category_help("history")
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.on", "Enable chat history recording", category=CommandCategory.HISTORY)
def cmd_history_on(handler) -> CommandResult:
    """Enable chat history recording for the current chat."""
    service = HistoryService(handler.app)
    chat_info = service.get_chat_info()
    
    # Check if already enabled
    if service.get_history_status():
        HistoryFormatter.format_history_already_enabled(chat_info)
    else:
        service.enable_history()
        HistoryFormatter.format_history_enabled(chat_info)
        
    return CommandResult(ActionType.CONTINUE)


@registry.register("history.off", "Disable chat history recording", category=CommandCategory.HISTORY)
def cmd_history_off(handler) -> CommandResult:
    """Disable chat history recording for the current chat."""
    service = HistoryService(handler.app)
    chat_info = service.get_chat_info()
    
    # Check if already disabled
    if not service.get_history_status():
        HistoryFormatter.format_history_already_disabled(chat_info)
    else:
        service.disable_history()
        HistoryFormatter.format_history_disabled(chat_info)
        
    return CommandResult(ActionType.CONTINUE)
