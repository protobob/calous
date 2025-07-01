"""Model command formatters."""
from typing import Optional
from ...constants import MIN_NUM_CTX, MAX_NUM_CTX, MIN_TEMPERATURE, MAX_TEMPERATURE, DEFAULT_TEMPERATURE
from .services import ContextResult, TemperatureResult, EvaluationResult, ThinkingResult
from ..formatters import CommandFormatter


class ModelFormatter(CommandFormatter):
    """Formatter for model command outputs."""
    
    @staticmethod
    def format_model_changed(model_name: str, updated_count: int):
        """Format model change confirmation."""
        ModelFormatter._output(f"Model changed globally to: {model_name}")
        ModelFormatter._output(f"Updated model for {updated_count} chat instance(s).")
    
    @staticmethod
    def format_invalid_model_selection(model_selection: str):
        """Format invalid model selection error."""
        ModelFormatter._output(f"\n[bold red]Invalid model selection:[/bold red] {model_selection}")
        ModelFormatter._output("[grey50]Use /model.switch to see available models[/grey50]")
    
    @staticmethod
    def format_current_context(current_context: int, selected_model: Optional[str], service):
        """Format current context information display."""
        ModelFormatter._output(f"\n[bold]Current Context Window:[/bold] {current_context:,} tokens")
        
        # Show VRAM estimate for current setting if model is selected
        if selected_model:
            context_info = service.app.model.get_context_window_info(selected_model)
            if context_info:
                user_context_info = context_info._replace(actual_context=current_context)
                vram_estimate = service.app.model.estimate_context_vram_usage(user_context_info)
                if vram_estimate != "unknown":
                    ModelFormatter._output(f"[bold]Current VRAM Usage:[/bold] {vram_estimate} [grey50](estimated)[/grey50]")
        
        ModelFormatter._output(f"\n[grey50]Usage:[/grey50] [bold]/model.setctx NUMBER[/bold] - Set context window size")
        ModelFormatter._output(f"[grey50]Range:[/grey50] {MIN_NUM_CTX:,} to {MAX_NUM_CTX:,} tokens")
        
        # Provide recommended settings
        ModelFormatter._output(f"\n[bold cyan]Recommended Settings:[/bold cyan]")
        ModelFormatter._output(f"  [green]4,096[/green]  - Standard conversations, low VRAM (~600MB-1GB)")
        ModelFormatter._output(f"  [yellow]8,192[/yellow]  - Long conversations, moderate VRAM (~1-2GB)")
        ModelFormatter._output(f"  [orange1]16,384[/orange1] - Extended context, high VRAM (~2-4GB)")
        ModelFormatter._output(f"  [red]32,768[/red] - Maximum context, very high VRAM (~5-8GB)")
        
        ModelFormatter._output(f"\n[grey50]Note: Larger contexts use more VRAM and may cause instability or slower performance.[/grey50]")
    
    @staticmethod
    def format_context_result(result: ContextResult):
        """Format context setting result."""
        if not result.success:
            if result.context_size < MIN_NUM_CTX:
                ModelFormatter._output(f"\n[bold red]Error:[/bold red] Context size must be at least {MIN_NUM_CTX:,} tokens")
            elif result.context_size > MAX_NUM_CTX:
                ModelFormatter._output(f"\n[bold red]Error:[/bold red] Context size cannot exceed {MAX_NUM_CTX:,} tokens")
            return
        
        vram_warning = ""
        if result.vram_estimate and result.vram_estimate != "unknown":
            vram_warning = f" [grey50](~{result.vram_estimate} VRAM)[/grey50]"
        
        # Show warnings based on context size
        if result.warning_level == "error":  # 24k+
            ModelFormatter._output(f"\n[bold red]Warning:[/bold red] Very large context window ({result.context_size:,}) may cause:")
            ModelFormatter._output(f"  • Extremely high VRAM usage{vram_warning}")
            ModelFormatter._output(f"  • Model instability or incoherent responses")
            ModelFormatter._output(f"  • Significantly slower performance")
            ModelFormatter._output(f"  • Potential out-of-memory errors")
            ModelFormatter._output(f"\n[yellow]Consider using 16k or less for better stability.[/yellow]")
        elif result.warning_level == "warning":  # 16k+
            ModelFormatter._output(f"\n[bold yellow]Warning:[/bold yellow] Large context window ({result.context_size:,}) will use significant resources{vram_warning}")
            ModelFormatter._output(f"  • High VRAM usage may impact performance")
            ModelFormatter._output(f"  • Some models may become less coherent with very long contexts")
        elif result.warning_level == "notice":  # 8k+
            ModelFormatter._output(f"\n[yellow]Notice:[/yellow] Moderate context window ({result.context_size:,}){vram_warning}")
            ModelFormatter._output(f"  • Good balance of memory and performance for most use cases")        
        # Success message
        ModelFormatter._output(f"\n[green]Context window set to {result.context_size:,} tokens globally[/green]")
        ModelFormatter._output("[grey50]This will take effect on the next message to the model[/grey50]")
    
    @staticmethod
    def format_current_temperature(current_temperature: float):
        """Format current temperature information display."""
        ModelFormatter._output(f"\n[bold]Current Temperature:[/bold] {current_temperature}")
        
        ModelFormatter._output(f"\n[grey50]Usage:[/grey50] [bold]/model.settemp NUMBER[/bold] - Set temperature parameter")
        ModelFormatter._output(f"[grey50]Range:[/grey50] {MIN_TEMPERATURE} to {MAX_TEMPERATURE}")
        ModelFormatter._output(f"[grey50]Default:[/grey50] {DEFAULT_TEMPERATURE}")
        
        # Provide guidance on temperature values
        ModelFormatter._output(f"\n[bold cyan]Temperature Guide:[/bold cyan]")
        ModelFormatter._output(f"  [blue]0.0[/blue]   - Completely deterministic (always same response)")
        ModelFormatter._output(f"  [green]0.2[/green]   - Very focused and consistent")
        ModelFormatter._output(f"  [green]0.4[/green]   - Focused but with some variation")
        ModelFormatter._output(f"  [yellow]0.7[/yellow]   - Balanced creativity and consistency")
        ModelFormatter._output(f"  [yellow]{DEFAULT_TEMPERATURE}[/yellow]   - Default Ollama setting (good balance)")
        ModelFormatter._output(f"  [orange1]1.0[/orange1]   - More creative and varied responses")
        ModelFormatter._output(f"  [orange1]1.2[/orange1]   - Quite creative, may be less coherent")
        ModelFormatter._output(f"  [red]1.5+[/red]  - Very creative but potentially chaotic")
        
        ModelFormatter._output(f"\n[grey50]Lower values = more predictable, higher values = more creative[/grey50]")
    
    @staticmethod
    def format_temperature_result(result: TemperatureResult):
        """Format temperature setting result."""
        if not result.success:
            ModelFormatter._output(f"\n[bold red]Error:[/bold red] Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}")
            return
        
        # Provide guidance based on temperature value
        if result.warning_level == "deterministic":
            ModelFormatter._output(f"\n[blue]Notice:[/blue] Deterministic mode - responses will be identical for same inputs")
        elif result.warning_level == "low":
            ModelFormatter._output(f"\n[green]Notice:[/green] Very low temperature - responses will be highly consistent")
        elif result.warning_level == "warning":
            ModelFormatter._output(f"\n[yellow]Warning:[/yellow] High temperature ({result.temperature}) may produce:")
            ModelFormatter._output(f"  • Very creative but potentially incoherent responses")
            ModelFormatter._output(f"  • Unpredictable or inconsistent behavior")
            ModelFormatter._output(f"  • Reduced factual accuracy")
        elif result.warning_level == "notice":
            ModelFormatter._output(f"\n[yellow]Notice:[/yellow] High temperature ({result.temperature}) - expect very creative responses")
        
        # Success message
        ModelFormatter._output(f"\n[green]Temperature set to {result.temperature} for this chat[/green]")
        ModelFormatter._output("[grey50]This will take effect on the next message to the model[/grey50]")
    
    @staticmethod
    def format_invalid_state_error(command_type: str):
        """Format invalid state parameter error."""
        ModelFormatter._output("[bold red]Error:[/bold red] State must be 'on' or 'off'")
        ModelFormatter._output(f"[grey50]Usage: /model.{command_type} on  or  /model.{command_type} off[/grey50]")
    
    @staticmethod
    def format_evaluation_state(result: EvaluationResult):
        """Format evaluation display state change."""
        if result.changed:
            ModelFormatter._output(f"\nEvaluation display is now: {'enabled' if result.enabled else 'disabled'}")
        else:
            ModelFormatter._output(f"\nEvaluation display is already {'enabled' if result.enabled else 'disabled'}")
    
    @staticmethod
    def format_thinking_state(result: ThinkingResult):
        """Format thinking mode state change."""
        if result.changed:
            status = "enabled" if result.enabled else "disabled"
            ModelFormatter._output(f"\nThinking mode is now: {status}")
            if result.enabled:
                ModelFormatter._output("[grey50]Model reasoning will be shown during responses but filtered from history and twist operations[/grey50]")
            else:
                ModelFormatter._output("[grey50]Model reasoning will be hidden for clean output[/grey50]")
        else:
            ModelFormatter._output(f"\nThinking mode is already {'enabled' if result.enabled else 'disabled'}")
    
    @staticmethod
    def format_evaluation_toggled(result: EvaluationResult):
        """Format evaluation display toggle result."""
        ModelFormatter._output(f"\nVerbosity is now: {result.enabled}")
    
    @staticmethod
    def format_thinking_toggled(result: ThinkingResult):
        """Format thinking mode toggle result."""
        status = "enabled" if result.enabled else "disabled"
        ModelFormatter._output(f"\nThinking mode is now: {status}")
        if result.enabled:
            ModelFormatter._output("[grey50]Model reasoning will be shown during responses but filtered from history and twist operations[/grey50]")
        else:
            ModelFormatter._output("[grey50]Model reasoning will be hidden for clean output[/grey50]")
