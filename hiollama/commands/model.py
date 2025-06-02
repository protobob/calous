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
        # Show current setting and helpful guidance
        current = handler.app.num_ctx
        print(f"\n[bold]Current Context Window:[/bold] {current:,} tokens")
        
        # Show VRAM estimate for current setting if model is selected
        if handler.app.selected_model:
            context_info = handler.app.model.get_context_window_info(handler.app.selected_model)
            if context_info:
                user_context_info = context_info._replace(actual_context=current)
                vram_estimate = handler.app.model.estimate_context_vram_usage(user_context_info)
                if vram_estimate != "unknown":
                    print(f"[bold]Current VRAM Usage:[/bold] {vram_estimate} [grey50](estimated)[/grey50]")
        
        print(f"\n[grey50]Usage:[/grey50] [bold]/setctx NUMBER[/bold] - Set context window size")
        print(f"[grey50]Range:[/grey50] {MIN_NUM_CTX:,} to {MAX_NUM_CTX:,} tokens")
        # Provide recommended settings
        print(f"\n[bold cyan]Recommended Settings:[/bold cyan]")
        print(f"  [green]4,096[/green]  - Standard conversations, low VRAM (~600MB-1GB)")
        print(f"  [yellow]8,192[/yellow]  - Long conversations, moderate VRAM (~1-2GB)")
        print(f"  [orange1]16,384[/orange1] - Extended context, high VRAM (~2-4GB)")
        print(f"  [red]32,768[/red] - Maximum context, very high VRAM (~5-8GB)")
        
        print(f"\n[grey50]Note: Larger contexts use more VRAM and may cause instability or slower performance.[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    # Validate input
    if context_size < MIN_NUM_CTX:
        print(f"\n[bold red]Error:[/bold red] Context size must be at least {MIN_NUM_CTX:,} tokens")
        return CommandResult(ActionType.CONTINUE)
    
    if context_size > MAX_NUM_CTX:
        print(f"\n[bold red]Error:[/bold red] Context size cannot exceed {MAX_NUM_CTX:,} tokens")
        return CommandResult(ActionType.CONTINUE)
    
    # Show VRAM estimate for the requested setting
    vram_warning = ""
    if handler.app.selected_model:
        context_info = handler.app.model.get_context_window_info(handler.app.selected_model)
        if context_info:
            user_context_info = context_info._replace(actual_context=context_size)
            vram_estimate = handler.app.model.estimate_context_vram_usage(user_context_info)
            if vram_estimate != "unknown":
                vram_warning = f" [grey50](~{vram_estimate} VRAM)[/grey50]"
    
    # Provide warnings based on context size
    if context_size > 24576:  # 24k+
        print(f"\n[bold red]Warning:[/bold red] Very large context window ({context_size:,}) may cause:")
        print(f"  • Extremely high VRAM usage{vram_warning}")
        print(f"  • Model instability or incoherent responses")
        print(f"  • Significantly slower performance")
        print(f"  • Potential out-of-memory errors")
        print(f"\n[yellow]Consider using 16k or less for better stability.[/yellow]")
    elif context_size > 16384:  # 16k+
        print(f"\n[bold yellow]Warning:[/bold yellow] Large context window ({context_size:,}) will use significant resources{vram_warning}")
        print(f"  • High VRAM usage may impact performance")
        print(f"  • Some models may become less coherent with very long contexts")
    elif context_size > 8192:  # 8k+
        print(f"\n[yellow]Notice:[/yellow] Moderate context window ({context_size:,}){vram_warning}")
        print(f"  • Good balance of memory and performance for most use cases")
    
    # Set the context size
    handler.app.num_ctx = context_size
    print(f"\n[green]Context window set to {context_size:,} tokens for this chat[/green]")
    print("[grey50]This will take effect on the next message to the model[/grey50]")
    
    return CommandResult(ActionType.CONTINUE)