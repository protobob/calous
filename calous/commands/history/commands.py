"""History management commands."""
from typing import Optional
from rich import print as rich_print
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
    
    if handler.app.confirm("Are you sure you want to clear all chat history?"):
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


@registry.register("history.save", "Save current chat history to a file", category=CommandCategory.HISTORY)
def cmd_history_save(handler, filename: str) -> CommandResult:
    """Save the current chat's history to a .jsonl file in ~/calous/chat_history."""
    from pathlib import Path
    import re
    from ...constants import CALOUS_DIR
    from .services import HistoryService
    from .formatters import HistoryFormatter
    from rich.prompt import Confirm

    # Sanitize filename: only allow alphanumeric, dash, underscore, strip after first dot
    base = re.split(r"[.]", filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    save_dir = Path.home() / "calous" / "chat_history"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{safe}.jsonl"

    # Check for overwrite
    if save_path.exists():
        self._output(f"\n[yellow]File {save_path.name} already exists.[/yellow]")
        if not Confirm.ask("Overwrite?", default=False):
            self._output("\n[cyan]Operation cancelled.[/cyan]")
            return CommandResult(ActionType.CONTINUE)

    service = HistoryService(handler.app)
    count = service.save_history_to_file(save_path)
    if count > 0:
        self._output(f"\n[green]Chat history saved to {save_path} ({count} messages).[/green]")
    else:
        self._output(f"\n[yellow]No messages to save. File not created.[/yellow]")
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.load", "Load chat history from a file", category=CommandCategory.HISTORY)
def cmd_history_load(handler, filename: str) -> CommandResult:
    """Load chat history from a .jsonl file in ~/calous/chat_history, overwriting current history."""
    from pathlib import Path
    import re
    from ...constants import CALOUS_DIR
    from .services import HistoryService
    from .formatters import HistoryFormatter

    # Sanitize filename
    base = re.split(r"[.]", filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    load_dir = Path.home() / "calous" / "chat_history"
    load_path = load_dir / f"{safe}.jsonl"

    service = HistoryService(handler.app)
    if not load_path.exists():
        self._output(f"\n[red]File not found: {load_path}[/red]")
        return CommandResult(ActionType.CONTINUE)

    # Warn user about overwrite
    self._output("\n[yellow]Warning: Loading will overwrite current chat history in memory.[/yellow]")
    from rich.prompt import Confirm
    if not Confirm.ask("Continue?", default=False):
        self._output("\n[cyan]Operation cancelled.[/cyan]")
        return CommandResult(ActionType.CONTINUE)

    count = service.load_history_from_file(load_path)
    self._output(f"\n[green]Loaded {count} messages from {load_path} into current chat history.[/green]")
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.list", "List saved chat history files", category=CommandCategory.HISTORY)
def cmd_history_list(handler) -> CommandResult:
    """List all .jsonl files in ~/calous/chat_history, showing base names only."""
    from pathlib import Path
    list_dir = Path.home() / "calous" / "chat_history"
    if not list_dir.exists():
        self._output("\n[yellow]No saved chat history files found.[/yellow]")
        return CommandResult(ActionType.CONTINUE)
    files = sorted(list_dir.glob("*.jsonl"))
    if not files:
        self._output("\n[yellow]No saved chat history files found.[/yellow]")
    else:
        self._output("\n[bold]Saved chat history files:[/bold]")
        for f in files:
            base = f.stem  # filename without extension
            self._output(f"  [cyan]{base}[/cyan]  ({f.stat().st_size} bytes)")
    return CommandResult(ActionType.CONTINUE)

@registry.register("history.delete", "Delete a saved chat history file", category=CommandCategory.HISTORY)
def cmd_history_delete(handler, filename: str) -> CommandResult:
    """Delete a .jsonl file in ~/calous/chat_history after Y/N confirmation."""
    from pathlib import Path
    import re
    from rich.prompt import Confirm

    # Sanitize filename
    base = re.split(r"[.]+", filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    del_dir = Path.home() / "calous" / "chat_history"
    del_path = del_dir / f"{safe}.jsonl"

    if not del_path.exists():
        self._output(f"\n[red]File not found: {del_path}[/red]")
        return CommandResult(ActionType.CONTINUE)

    self._output(f"\n[yellow]Are you sure you want to delete {del_path.name}? This cannot be undone.[/yellow]")
    if not Confirm.ask("Delete?", default=False):
        self._output("\n[cyan]Operation cancelled.[/cyan]")
        return CommandResult(ActionType.CONTINUE)

    try:
        del_path.unlink()
        self._output(f"\n[green]Deleted {del_path.name}.[/green]")
    except Exception as e:
        self._output(f"\n[red]Error deleting file: {e}[/red]")
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
        self._output(f"[yellow]No messages to purge.[/yellow]")
        return CommandResult(ActionType.CONTINUE)

    self._output(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]DELETE[/bold red] the [bold]{n}[/bold] most recent message(s) from [bold {chat_info.color}]CHAT {chat_info.number}[/bold {chat_info.color}] history.")
    self._output("This cannot be undone.")
    
    # Use app.confirm() which handles socket mode properly
    # In socket mode, auto-confirm destructive operations since they're intentional
    if not handler.app.confirm("Are you sure you want to continue?", default=True):
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
        self._output(f"[green]Purged {n} message(s) from chat history.[/green]")
    except Exception as e:
        self._output(f"[red]Error updating history file: {e}[/red]")
    return CommandResult(ActionType.CONTINUE)
