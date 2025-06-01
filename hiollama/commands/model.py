"""Model management commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from ..constants import MIN_NUM_CTX, MAX_NUM_CTX
from .registry import registry
from .types import CommandCategory


@registry.register("model", "Select a different Ollama model", category=CommandCategory.MODEL)
def cmd_model(handler) -> CommandResult:
    """Select a different model globally."""
    selected = handler.app.model.select_model()
    if selected:
        updated_count = handler.app.update_global_model(selected)
        print(f"Model changed globally to: {selected}")
        print(f"Updated model for {updated_count} chat instance(s).")
    return CommandResult(ActionType.CONTINUE)


@registry.register("toggle_eval", "Toggle evaluation data display", aliases=["eval"], category=CommandCategory.MODEL)
def cmd_toggle_eval(handler) -> CommandResult:
    """Toggle display of evaluation data."""
    handler.app.verbosity = not handler.app.verbosity
    print(f"\nVerbosity is now: {handler.app.verbosity}")
    return CommandResult(ActionType.CONTINUE)


@registry.register("toggle_think", "Toggle thinking mode display", aliases=["think"], category=CommandCategory.MODEL)
def cmd_toggle_think(handler) -> CommandResult:
    """Toggle thinking mode - when enabled, shows model reasoning during responses."""
    handler.app.thinking_enabled = not handler.app.thinking_enabled
    status = "enabled" if handler.app.thinking_enabled else "disabled"
    print(f"\nThinking mode is now: {status}")
    if handler.app.thinking_enabled:
        print("[grey50]Model reasoning will be shown during responses but filtered from history and twist operations[/grey50]")
    else:
        print("[grey50]Model reasoning will be hidden for clean output[/grey50]")
    return CommandResult(ActionType.CONTINUE)


@registry.register("setctx", "Set context window size", category=CommandCategory.MODEL)
def cmd_setctx(handler, context_size: Optional[int] = None) -> CommandResult:
    """Set the context window size for the current chat."""
    if context_size is None:
        # Show current setting
        current = handler.app.num_ctx
        print(f"[bold]Context Window:[/bold] {current:,} tokens")
        print(f"\n[grey50]Usage:[/grey50] [bold]/setctx NUMBER[/bold] - Set context window size")
        print(f"[grey50]Range:[/grey50] {MIN_NUM_CTX:,} to {MAX_NUM_CTX:,} tokens")
        return CommandResult(ActionType.CONTINUE)
    
    # Validate input
    if context_size < MIN_NUM_CTX:
        print(f"\n[bold red]Error:[/bold red] Context size must be at least {MIN_NUM_CTX:,} tokens")
        return CommandResult(ActionType.CONTINUE)
    
    if context_size > MAX_NUM_CTX:
        print(f"\n[bold red]Error:[/bold red] Context size cannot exceed {MAX_NUM_CTX:,} tokens")
        return CommandResult(ActionType.CONTINUE)
    
    # Warn about large context windows
    if context_size > 16384:  # 16k
        print(f"\n[bold yellow]Warning:[/bold yellow] Large context windows (>{16384:,}) may use significant VRAM and slow performance")
    
    # Set the context size
    handler.app.num_ctx = context_size
    print(f"\nContext window set to {context_size:,} tokens for this chat")
    print("[grey50]This will take effect on the next message to the model[/grey50]")
    
    return CommandResult(ActionType.CONTINUE)