"""Model command formatters."""
from typing import Optional
from rich import print as rich_print
from ...constants import MIN_NUM_CTX, MAX_NUM_CTX, MIN_TEMPERATURE, MAX_TEMPERATURE, DEFAULT_TEMPERATURE
from .services import ContextResult, TemperatureResult, EvaluationResult, ThinkingResult


class ModelFormatter:
    """Formatter for model command outputs."""
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
    @staticmethod
    def format_model_changed(model_name: str, updated_count: int):
        """Format model change confirmation."""
        CommandFormatter._output(f"Model changed globally to: {model_name}")
        CommandFormatter._output(f"Updated model for {updated_count} chat instance(s).")
    
    @staticmethod
    def format_current_context(current_context: int, selected_model: Optional[str], service):
        """Format current context information display."""
        CommandFormatter._output(f"\n[bold]Current Context Window:[/bold] {current_context:,} tokens")
        
        # Show VRAM estimate for current setting if model is selected
        if selected_model:
            context_info = service.app.model.get_context_window_info(selected_model)
            if context_info:
                user_context_info = context_info._replace(actual_context=current_context)
                vram_estimate = service.app.model.estimate_context_vram_usage(user_context_info)
                if vram_estimate != "unknown":
                    CommandFormatter._output(f"[bold]Current VRAM Usage:[/bold] {vram_estimate} [grey50](estimated)[/grey50]")
        
        CommandFormatter._output(f"\n[grey50]Usage:[/grey50] [bold]/model.setctx NUMBER[/bold] - Set context window size")
        CommandFormatter._output(f"[grey50]Range:[/grey50] {MIN_NUM_CTX:,} to {MAX_NUM_CTX:,} tokens")
        
        # Provide recommended settings
        CommandFormatter._output(f"\n[bold cyan]Recommended Settings:[/bold cyan]")
        CommandFormatter._output(f"  [green]4,096[/green]  - Standard conversations, low VRAM (~600MB-1GB)")
        CommandFormatter._output(f"  [yellow]8,192[/yellow]  - Long conversations, moderate VRAM (~1-2GB)")
        CommandFormatter._output(f"  [orange1]16,384[/orange1] - Extended context, high VRAM (~2-4GB)")
        CommandFormatter._output(f"  [red]32,768[/red] - Maximum context, very high VRAM (~5-8GB)")
        
        CommandFormatter._output(f"\n[grey50]Note: Larger contexts use more VRAM and may cause instability or slower performance.[/grey50]")
    
    @staticmethod
    def format_context_result(result: ContextResult):
        """Format context setting result."""
        if not result.success:
            if result.context_size < MIN_NUM_CTX:
                CommandFormatter._output(f"\n[bold red]Error:[/bold red] Context size must be at least {MIN_NUM_CTX:,} tokens")
            elif result.context_size > MAX_NUM_CTX:
                CommandFormatter._output(f"\n[bold red]Error:[/bold red] Context size cannot exceed {MAX_NUM_CTX:,} tokens")
            return
        
        vram_warning = ""
        if result.vram_estimate and result.vram_estimate != "unknown":
            vram_warning = f" [grey50](~{result.vram_estimate} VRAM)[/grey50]"
        
        # Show warnings based on context size
        if result.warning_level == "error":  # 24k+
            CommandFormatter._output(f"\n[bold red]Warning:[/bold red] Very large context window ({result.context_size:,}) may cause:")
            CommandFormatter._output(f"  • Extremely high VRAM usage{vram_warning}")
            CommandFormatter._output(f"  • Model instability or incoherent responses")
            CommandFormatter._output(f"  • Significantly slower performance")
            CommandFormatter._output(f"  • Potential out-of-memory errors")
            CommandFormatter._output(f"\n[yellow]Consider using 16k or less for better stability.[/yellow]")
        elif result.warning_level == "warning":  # 16k+
            CommandFormatter._output(f"\n[bold yellow]Warning:[/bold yellow] Large context window ({result.context_size:,}) will use significant resources{vram_warning}")
            CommandFormatter._output(f"  • High VRAM usage may impact performance")
            CommandFormatter._output(f"  • Some models may become less coherent with very long contexts")
        elif result.warning_level == "notice":  # 8k+
            CommandFormatter._output(f"\n[yellow]Notice:[/yellow] Moderate context window ({result.context_size:,}){vram_warning}")
            CommandFormatter._output(f"  • Good balance of memory and performance for most use cases")        
        # Success message
        CommandFormatter._output(f"\n[green]Context window set to {result.context_size:,} tokens globally[/green]")
        CommandFormatter._output("[grey50]This will take effect on the next message to the model[/grey50]")
    
    @staticmethod
    def format_current_temperature(current_temperature: float):
        """Format current temperature information display."""
        CommandFormatter._output(f"\n[bold]Current Temperature:[/bold] {current_temperature}")
        
        CommandFormatter._output(f"\n[grey50]Usage:[/grey50] [bold]/model.settemp NUMBER[/bold] - Set temperature parameter")
        CommandFormatter._output(f"[grey50]Range:[/grey50] {MIN_TEMPERATURE} to {MAX_TEMPERATURE}")
        CommandFormatter._output(f"[grey50]Default:[/grey50] {DEFAULT_TEMPERATURE}")
        
        # Provide guidance on temperature values
        CommandFormatter._output(f"\n[bold cyan]Temperature Guide:[/bold cyan]")
        CommandFormatter._output(f"  [blue]0.0[/blue]   - Completely deterministic (always same response)")
        CommandFormatter._output(f"  [green]0.2[/green]   - Very focused and consistent")
        CommandFormatter._output(f"  [green]0.4[/green]   - Focused but with some variation")
        CommandFormatter._output(f"  [yellow]0.7[/yellow]   - Balanced creativity and consistency")
        CommandFormatter._output(f"  [yellow]{DEFAULT_TEMPERATURE}[/yellow]   - Default Ollama setting (good balance)")
        CommandFormatter._output(f"  [orange1]1.0[/orange1]   - More creative and varied responses")
        CommandFormatter._output(f"  [orange1]1.2[/orange1]   - Quite creative, may be less coherent")
        CommandFormatter._output(f"  [red]1.5+[/red]  - Very creative but potentially chaotic")
        
        CommandFormatter._output(f"\n[grey50]Lower values = more predictable, higher values = more creative[/grey50]")
    
    @staticmethod
    def format_temperature_result(result: TemperatureResult):
        """Format temperature setting result."""
        if not result.success:
            CommandFormatter._output(f"\n[bold red]Error:[/bold red] Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}")
            return
        
        # Provide guidance based on temperature value
        if result.warning_level == "deterministic":
            CommandFormatter._output(f"\n[blue]Notice:[/blue] Deterministic mode - responses will be identical for same inputs")
        elif result.warning_level == "low":
            CommandFormatter._output(f"\n[green]Notice:[/green] Very low temperature - responses will be highly consistent")
        elif result.warning_level == "warning":
            CommandFormatter._output(f"\n[yellow]Warning:[/yellow] High temperature ({result.temperature}) may produce:")
            CommandFormatter._output(f"  • Very creative but potentially incoherent responses")
            CommandFormatter._output(f"  • Unpredictable or inconsistent behavior")
            CommandFormatter._output(f"  • Reduced factual accuracy")
        elif result.warning_level == "notice":
            CommandFormatter._output(f"\n[yellow]Notice:[/yellow] High temperature ({result.temperature}) - expect very creative responses")
        
        # Success message
        CommandFormatter._output(f"\n[green]Temperature set to {result.temperature} for this chat[/green]")
        CommandFormatter._output("[grey50]This will take effect on the next message to the model[/grey50]")
    
    @staticmethod
    def format_invalid_state_error(command_type: str):
        """Format invalid state parameter error."""
        CommandFormatter._output("[bold red]Error:[/bold red] State must be 'on' or 'off'")
        CommandFormatter._output(f"[grey50]Usage: /model.{command_type} on  or  /model.{command_type} off[/grey50]")
    
    @staticmethod
    def format_evaluation_state(result: EvaluationResult):
        """Format evaluation display state change."""
        if result.changed:
            CommandFormatter._output(f"\nEvaluation display is now: {'enabled' if result.enabled else 'disabled'}")
        else:
            CommandFormatter._output(f"\nEvaluation display is already {'enabled' if result.enabled else 'disabled'}")
    
    @staticmethod
    def format_thinking_state(result: ThinkingResult):
        """Format thinking mode state change."""
        if result.changed:
            status = "enabled" if result.enabled else "disabled"
            CommandFormatter._output(f"\nThinking mode is now: {status}")
            if result.enabled:
                CommandFormatter._output("[grey50]Model reasoning will be shown during responses but filtered from history and twist operations[/grey50]")
            else:
                CommandFormatter._output("[grey50]Model reasoning will be hidden for clean output[/grey50]")
        else:
            CommandFormatter._output(f"\nThinking mode is already {'enabled' if result.enabled else 'disabled'}")
    
    @staticmethod
    def format_evaluation_toggled(result: EvaluationResult):
        """Format evaluation display toggle result."""
        CommandFormatter._output(f"\nVerbosity is now: {result.enabled}")
    
    @staticmethod
    def format_thinking_toggled(result: ThinkingResult):
        """Format thinking mode toggle result."""
        status = "enabled" if result.enabled else "disabled"
        CommandFormatter._output(f"\nThinking mode is now: {status}")
        if result.enabled:
            CommandFormatter._output("[grey50]Model reasoning will be shown during responses but filtered from history and twist operations[/grey50]")
        else:
            CommandFormatter._output("[grey50]Model reasoning will be hidden for clean output[/grey50]")
