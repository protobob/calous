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
