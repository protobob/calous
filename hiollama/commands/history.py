"""Chat history management commands."""
from typing import Optional
from rich import print
from rich.prompt import Prompt
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory
from ..unified_logger import unified_logger
from ..utils import get_chat_color


@registry.register("clear", "Clear chat history", category=CommandCategory.HISTORY)
def cmd_clear(handler) -> CommandResult:
    """Clear the current chat's history with confirmation."""
    try:
        # Get chat info for colored display
        chat_number = handler.app.instance_index + 1
        chat_color = get_chat_color(handler.app.instance_index)
        
        # Ask for confirmation with colored text
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]CLEAR[/bold red] [bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] history.")
        print("All conversation history will be permanently deleted.")
        
        confirm = Prompt.ask("\nAre you sure you want to continue?", choices=["y", "n"], default="n")
        if confirm == 'y':
            handler.app.chat_history.clear()
            print(f"[bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] history cleared successfully!")
        else:
            print("Clear operation cancelled.")
    except KeyboardInterrupt:
        print("\nClear operation cancelled.")
    return CommandResult(ActionType.CONTINUE)


@registry.register("history", "Show chat history", aliases=["hist"], category=CommandCategory.HISTORY)
def cmd_history(handler) -> CommandResult:
    """Display chat history."""
    handler.app.chat_history.print_history()
    return CommandResult(ActionType.CONTINUE)


@registry.register("export", "Export chat history", category=CommandCategory.HISTORY)
def cmd_export(handler, filename: Optional[str] = None) -> CommandResult:
    """Export chat history to a file."""
    import json
    from datetime import datetime
    from pathlib import Path
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_export_{timestamp}.json"
    
    try:
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        export_path = Path(filename)
        
        # Get full history
        history = handler.app.chat_history.history
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "model": handler.app.selected_model,
            "system_prompt": handler.app.system_prompt,
            "history": history
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Chat history exported to: {export_path.absolute()}")
        
        # Log the export action
        unified_logger.log_export_action(handler.app.instance_index, str(export_path))
        
    except Exception as e:
        print(f"[bold red]Error exporting history:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)




@registry.register("toggle_log", "Toggle unified logging", aliases=["log"], category=CommandCategory.HISTORY)
def cmd_toggle_log(handler) -> CommandResult:
    """Toggle unified logging of all chat activities."""
    enabled = unified_logger.toggle_logging()
    print(f"\nUnified logging is now: {'enabled' if enabled else 'disabled'}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("unified_log", "View unified log for today", aliases=["viewlog"], category=CommandCategory.HISTORY)
def cmd_unified_log(handler) -> CommandResult:
    """View the unified log for today."""
    from pathlib import Path
    from datetime import datetime
    from ..constants import LOG_DIR
    
    today_log = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.txt"
    
    if not today_log.exists():
        print(f"\n[bold yellow]No unified log found for today.[/bold yellow]")
        print(f"Log would be created at: {today_log}")
        return CommandResult(ActionType.CONTINUE)
    
    try:
        with open(today_log, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        if not content:
            print(f"\n[bold yellow]Unified log exists but is empty.[/bold yellow]")
            return CommandResult(ActionType.CONTINUE)
        
        print(f"\n[bold green]Unified Log for {datetime.now().strftime('%Y-%m-%d')}:[/bold green]")
        print("=" * 60)
        print(content)
        print("=" * 60)
        
    except Exception as e:
        print(f"[bold red]Error reading unified log:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)