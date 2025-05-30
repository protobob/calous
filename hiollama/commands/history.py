"""Chat history management commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


@registry.register("clear", "Clear chat history", category=CommandCategory.HISTORY)
def cmd_clear(handler) -> CommandResult:
    """Clear the current chat's history."""
    handler.app.chat_history.clear()
    print("Chat history cleared.")
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
        
    except Exception as e:
        print(f"[bold red]Error exporting history:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)

@registry.register("setmax", "Set maximum history size", category=CommandCategory.HISTORY)
def cmd_setmax(handler, size: int) -> CommandResult:
    """Set maximum chat history size."""
    if not (2 <= size <= 100) or size % 2 != 0:
        print("[bold red]Error:[/bold red] Size must be an even number between 2 and 100.")
        return CommandResult(ActionType.CONTINUE)
    
    handler.app.MAX_HISTORY = size
    
    # Trim history if it's longer than the new limit
    if len(handler.app.chat_history.history) > size:
        handler.app.chat_history.history = handler.app.chat_history.history[-size:]
    
    print(f"\nMaximum chat history set to {size}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("toggle_log", "Toggle conversation logging", aliases=["log"], category=CommandCategory.HISTORY)
def cmd_toggle_log(handler) -> CommandResult:
    """Toggle logging of chat history."""
    handler.app.logging_enabled = not handler.app.logging_enabled
    print(f"\nLogging is now: {handler.app.logging_enabled}")
    return CommandResult(ActionType.CONTINUE)