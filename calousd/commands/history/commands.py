"""History management commands."""
from typing import Optional
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
    
    if HistoryFormatter.confirm_action("Are you sure you want to clear all chat history?", app=handler.app):
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

@registry.register("history.vars", "Show history status and message count", category=CommandCategory.HISTORY)
def cmd_history_vars(handler) -> CommandResult:
    """Show chat history recording status and message count."""
    service = HistoryService(handler.app)
    chat_info = service.get_chat_info()
    
    # Get history status and count
    history_enabled = service.get_history_status()
    message_count = len(handler.app.chat_history.history)
    
    HistoryFormatter.format_history_vars(chat_info, history_enabled, message_count)
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


@registry.register("history.save", "Save current chat history to a file", category=CommandCategory.HISTORY)
def cmd_history_save(handler, filename) -> CommandResult:
    """Save the current chat's history to a .jsonl file in ~/calousd/chat_history."""
    from pathlib import Path
    import re
    from ...constants import CHAT_HISTORY_DIR
    from .services import HistoryService
    from .formatters import HistoryFormatter

    # Join filename parts if it's a list (from nargs='+')
    if isinstance(filename, list):
        filename = " ".join(filename)

    # Sanitize filename: only allow alphanumeric, dash, underscore, strip after first dot
    base = re.split(r"[.]", filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    CHAT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    save_path = CHAT_HISTORY_DIR / f"{safe}.jsonl"

    # Check for overwrite
    if save_path.exists():
        HistoryFormatter.format_file_exists_warning(save_path.name)
        if not HistoryFormatter.confirm_action("Overwrite?", default="n", app=handler.app):
            HistoryFormatter.format_operation_cancelled()
            return CommandResult(ActionType.CONTINUE)

    service = HistoryService(handler.app)
    count = service.save_history_to_file(save_path)
    if count > 0:
        HistoryFormatter.format_save_success(save_path, count)
    else:
        HistoryFormatter.format_save_no_messages()
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.load", "Load chat history from a file", category=CommandCategory.HISTORY)
def cmd_history_load(handler, filename) -> CommandResult:
    """Load chat history from a .jsonl file in ~/calousd/chat_history, overwriting current history."""
    from pathlib import Path
    import re
    from ...constants import CHAT_HISTORY_DIR
    from .services import HistoryService
    from .formatters import HistoryFormatter

    # Join filename parts if it's a list (from nargs='+')
    if isinstance(filename, list):
        filename = " ".join(filename)

    # Sanitize filename
    base = re.split(r"[.]", filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    load_path = CHAT_HISTORY_DIR / f"{safe}.jsonl"

    service = HistoryService(handler.app)
    if not load_path.exists():
        HistoryFormatter.format_load_file_not_found(load_path)
        return CommandResult(ActionType.CONTINUE)

    # Warn user about overwrite
    HistoryFormatter.format_load_warning()
    if not HistoryFormatter.confirm_action("Continue?", default="n", app=handler.app):
        HistoryFormatter.format_operation_cancelled()
        return CommandResult(ActionType.CONTINUE)

    count = service.load_history_from_file(load_path)
    HistoryFormatter.format_load_success(load_path, count)
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.list", "List saved chat history files", category=CommandCategory.HISTORY)
def cmd_history_list(handler) -> CommandResult:
    """List all .jsonl files in ~/calousd/chat_history, showing base names only."""
    from ...constants import CHAT_HISTORY_DIR
    if not CHAT_HISTORY_DIR.exists():
        HistoryFormatter.format_no_saved_files()
        return CommandResult(ActionType.CONTINUE)
    files = sorted(CHAT_HISTORY_DIR.glob("*.jsonl"))
    if not files:
        HistoryFormatter.format_no_saved_files()
    else:
        HistoryFormatter.format_saved_files_header()
        for f in files:
            base = f.stem  # filename without extension
            HistoryFormatter.format_saved_file_item(base, f.stat().st_size)
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.delete", "Delete a saved chat history file", category=CommandCategory.HISTORY)
def cmd_history_delete(handler, filename) -> CommandResult:
    """Delete a .jsonl file in ~/calousd/chat_history after Y/N confirmation."""
    from pathlib import Path
    import re
    from ...constants import CHAT_HISTORY_DIR

    # Join filename parts if it's a list (from nargs='+')
    if isinstance(filename, list):
        filename = " ".join(filename)

    # Sanitize filename
    base = re.split(r"[.]+", filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    del_path = CHAT_HISTORY_DIR / f"{safe}.jsonl"

    if not del_path.exists():
        HistoryFormatter.format_delete_file_not_found(del_path)
        return CommandResult(ActionType.CONTINUE)

    HistoryFormatter.format_delete_warning(del_path.name)
    if not HistoryFormatter.confirm_action("Delete?", default="n", app=handler.app):
        HistoryFormatter.format_operation_cancelled()
        return CommandResult(ActionType.CONTINUE)

    try:
        del_path.unlink()
        HistoryFormatter.format_delete_success(del_path.name)
    except Exception as e:
        HistoryFormatter.format_delete_error(str(e))
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.purge", "Purge the most recent N entries from current chat history", category=CommandCategory.HISTORY)
def cmd_history_purge(handler, num_entries: int) -> CommandResult:
    """Purge the most recent N entries from the current chat's history after confirmation."""
    service = HistoryService(handler.app)
    chat_info = service.get_chat_info()
    history = handler.app.chat_history.history
    total = len(history)
    n = max(0, min(num_entries, total))

    if n == 0:
        HistoryFormatter.format_no_messages_to_purge()
        return CommandResult(ActionType.CONTINUE)

    HistoryFormatter.format_purge_warning(chat_info, n)
    
    # Use app.confirm() which handles socket mode properly
    # In socket mode, auto-confirm destructive operations since they're intentional
    if not HistoryFormatter.confirm_action("Are you sure you want to continue?", default="y", app=handler.app):
        # No feedback on cancel, per user request
        return CommandResult(ActionType.CONTINUE)

    # Remove from in-memory history
    del history[-n:]
    handler.app.chat_history.history = history

    # Overwrite the history file with the new history
    import json
    history_file = handler.app.chat_history._get_history_filename()
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            for msg in history:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        HistoryFormatter.format_purge_success(n)
    except Exception as e:
        HistoryFormatter.format_purge_file_error(str(e))
    return CommandResult(ActionType.CONTINUE)
