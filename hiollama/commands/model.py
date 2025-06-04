"""Model management commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from ..constants import MIN_NUM_CTX, MAX_NUM_CTX, MIN_TEMPERATURE, MAX_TEMPERATURE, DEFAULT_TEMPERATURE
from .registry import registry
from .types import CommandCategory


def cmd_model(handler) -> CommandResult:
    """Select a different model globally."""
    selected = handler.app.model.select_model()
    if selected:
        updated_count = handler.app.update_global_model(selected)
        print(f"Model changed globally to: {selected}")
        print(f"Updated model for {updated_count} chat instance(s).")
    return CommandResult(ActionType.CONTINUE)


def cmd_toggle_eval(handler) -> CommandResult:
    """Toggle display of evaluation data."""
    handler.app.verbosity = not handler.app.verbosity
    print(f"\nVerbosity is now: {handler.app.verbosity}")
    return CommandResult(ActionType.CONTINUE)


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


def cmd_settemp(handler, temperature: Optional[float] = None) -> CommandResult:
    """Set the temperature parameter for the current chat."""
    if temperature is None:
        # Show current setting and helpful guidance
        current = handler.app.temperature
        print(f"\n[bold]Current Temperature:[/bold] {current}")
        
        print(f"\n[grey50]Usage:[/grey50] [bold]/settemp NUMBER[/bold] - Set temperature parameter")
        print(f"[grey50]Range:[/grey50] {MIN_TEMPERATURE} to {MAX_TEMPERATURE}")
        print(f"[grey50]Default:[/grey50] {DEFAULT_TEMPERATURE}")
        
        # Provide guidance on temperature values
        print(f"\n[bold cyan]Temperature Guide:[/bold cyan]")
        print(f"  [blue]0.0[/blue]   - Completely deterministic (always same response)")
        print(f"  [green]0.2[/green]   - Very focused and consistent")
        print(f"  [green]0.4[/green]   - Focused but with some variation")
        print(f"  [yellow]0.7[/yellow]   - Balanced creativity and consistency")
        print(f"  [yellow]{DEFAULT_TEMPERATURE}[/yellow]   - Default Ollama setting (good balance)")
        print(f"  [orange1]1.0[/orange1]   - More creative and varied responses")
        print(f"  [orange1]1.2[/orange1]   - Quite creative, may be less coherent")
        print(f"  [red]1.5+[/red]  - Very creative but potentially chaotic")
        
        print(f"\n[grey50]Lower values = more predictable, higher values = more creative[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    # Validate input
    if temperature < MIN_TEMPERATURE:
        print(f"\n[bold red]Error:[/bold red] Temperature must be at least {MIN_TEMPERATURE}")
        return CommandResult(ActionType.CONTINUE)
    
    if temperature > MAX_TEMPERATURE:
        print(f"\n[bold red]Error:[/bold red] Temperature cannot exceed {MAX_TEMPERATURE}")
        return CommandResult(ActionType.CONTINUE)
    
    # Provide guidance based on temperature value
    if temperature == 0.0:
        print(f"\n[blue]Notice:[/blue] Deterministic mode - responses will be identical for same inputs")
    elif temperature < 0.3:
        print(f"\n[green]Notice:[/green] Very low temperature - responses will be highly consistent")
    elif temperature > 1.5:
        print(f"\n[yellow]Warning:[/yellow] High temperature ({temperature}) may produce:")
        print(f"  • Very creative but potentially incoherent responses")
        print(f"  • Unpredictable or inconsistent behavior")
        print(f"  • Reduced factual accuracy")
    elif temperature > 1.0:
        print(f"\n[yellow]Notice:[/yellow] High temperature ({temperature}) - expect very creative responses")
    
    # Set the temperature
    handler.app.temperature = temperature
    print(f"\n[green]Temperature set to {temperature} for this chat[/green]")
    print("[grey50]This will take effect on the next message to the model[/grey50]")
    
    return CommandResult(ActionType.CONTINUE)


# New hierarchical model commands
@registry.register("model.switch", "Change the current model", category=CommandCategory.MODEL)
def cmd_model_switch(handler) -> CommandResult:
    """Select a different model globally."""
    return cmd_model(handler)


@registry.register("model.setctx", "Set max context window size", category=CommandCategory.MODEL)
def cmd_model_setctx(handler, context_size: Optional[int] = None) -> CommandResult:
    """Set the context window size for the current chat."""
    return cmd_setctx(handler, context_size)


@registry.register("model.eval", "Toggle evaluation display", category=CommandCategory.MODEL)
def cmd_model_eval(handler, state: str) -> CommandResult:
    """Enable or disable evaluation data display."""
    if state.lower() not in ["on", "off"]:
        print("[bold red]Error:[/bold red] State must be 'on' or 'off'")
        print("[grey50]Usage: /model.eval on  or  /model.eval off[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    target_state = state.lower() == "on"
    
    if handler.app.verbosity == target_state:
        print(f"\nEvaluation display is already {'enabled' if target_state else 'disabled'}")
    else:
        handler.app.verbosity = target_state
        print(f"\nEvaluation display is now: {'enabled' if target_state else 'disabled'}")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("model.think", "Toggle thinking display", category=CommandCategory.MODEL)
def cmd_model_think(handler, state: str) -> CommandResult:
    """Enable or disable thinking mode display."""
    if state.lower() not in ["on", "off"]:
        print("[bold red]Error:[/bold red] State must be 'on' or 'off'")
        print("[grey50]Usage: /model.think on  or  /model.think off[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    target_state = state.lower() == "on"
    
    if handler.app.thinking_enabled == target_state:
        print(f"\nThinking mode is already {'enabled' if target_state else 'disabled'}")
    else:
        handler.app.thinking_enabled = target_state
        status = "enabled" if target_state else "disabled"
        print(f"\nThinking mode is now: {status}")
        if target_state:
            print("[grey50]Model reasoning will be shown during responses but filtered from history and twist operations[/grey50]")
        else:
            print("[grey50]Model reasoning will be hidden for clean output[/grey50]")
    
    return CommandResult(ActionType.CONTINUE)