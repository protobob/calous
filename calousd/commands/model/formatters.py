"""Model command formatters."""
from typing import Optional
from ...constants import MIN_NUM_CTX, MAX_NUM_CTX, MIN_TEMPERATURE, MAX_TEMPERATURE, DEFAULT_TEMPERATURE, Colors
from .services import ContextResult, TemperatureResult, EvaluationResult, ThinkingResult, ToolUseResult
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
        ModelFormatter._output(f"\n[1;31mInvalid model selection:[0m {model_selection}")
        ModelFormatter._output("[90mUse /model.switch to see available models[0m")
    
    @staticmethod
    def format_current_context(current_context: int, selected_model: Optional[str], service):
        """Format current context information display."""
        ModelFormatter._output(f"\n[1mCurrent Context Window:[0m {current_context:,} tokens")
        
        # Show VRAM estimate for current setting if model is selected
        if selected_model:
            context_info = service.app.model.get_context_window_info(selected_model)
            if context_info:
                user_context_info = context_info._replace(actual_context=current_context)
                vram_estimate = service.app.model.estimate_context_vram_usage(user_context_info)
                if vram_estimate != "unknown":
                    ModelFormatter._output(f"[1mCurrent VRAM Usage:[0m {vram_estimate} [90m(estimated)[0m")
        
        ModelFormatter._output(f"\n[90mUsage:[0m [1m/model.setctx NUMBER[0m - Set context window size")
        ModelFormatter._output(f"[90mRange:[0m {MIN_NUM_CTX:,} to {MAX_NUM_CTX:,} tokens")
        
        # Provide recommended settings
        ModelFormatter._output(f"\n[1;36mRecommended Settings:[0m")
        ModelFormatter._output(f"  [32m4,096[0m  - Standard conversations, low VRAM (~600MB-1GB)")
        ModelFormatter._output(f"  [33m8,192[0m  - Long conversations, moderate VRAM (~1-2GB)")
        ModelFormatter._output(f"  [38;5;208m16,384[0m - Extended context, high VRAM (~2-4GB)")
        ModelFormatter._output(f"  [31m32,768[0m - Maximum context, very high VRAM (~5-8GB)")
        
        ModelFormatter._output(f"\n[90mNote: Larger contexts use more VRAM and may cause instability or slower performance.[0m")
    
    @staticmethod
    def format_context_result(result: ContextResult):
        """Format context setting result."""
        if not result.success:
            if result.context_size < MIN_NUM_CTX:
                ModelFormatter._output(f"\n[1;31mError:[0m Context size must be at least {MIN_NUM_CTX:,} tokens")
            elif result.context_size > MAX_NUM_CTX:
                ModelFormatter._output(f"\n[1;31mError:[0m Context size cannot exceed {MAX_NUM_CTX:,} tokens")
            return
        
        vram_warning = ""
        if result.vram_estimate and result.vram_estimate != "unknown":
            vram_warning = f" [90m(~{result.vram_estimate} VRAM)[0m"
        
        # Show warnings based on context size
        if result.warning_level == "error":  # 24k+
            ModelFormatter._output(f"\n[1;31mWarning:[0m Very large context window ({result.context_size:,}) may cause:")
            ModelFormatter._output(f"  • Extremely high VRAM usage{vram_warning}")
            ModelFormatter._output(f"  • Model instability or incoherent responses")
            ModelFormatter._output(f"  • Significantly slower performance")
            ModelFormatter._output(f"  • Potential out-of-memory errors")
            ModelFormatter._output(f"\n[33mConsider using 16k or less for better stability.[0m")
        elif result.warning_level == "warning":  # 16k+
            ModelFormatter._output(f"\n[1;33mWarning:[0m Large context window ({result.context_size:,}) will use significant resources{vram_warning}")
            ModelFormatter._output(f"  • High VRAM usage may impact performance")
            ModelFormatter._output(f"  • Some models may become less coherent with very long contexts")
        elif result.warning_level == "notice":  # 8k+
            ModelFormatter._output(f"\n[33mNotice:[0m Moderate context window ({result.context_size:,}){vram_warning}")
            ModelFormatter._output(f"  • Good balance of memory and performance for most use cases")        
        # Success message
        ModelFormatter._output(f"\n[32mContext window set to {result.context_size:,} tokens globally[0m")
        ModelFormatter._output("[90mThis will take effect on the next message to the model[0m")
    
    @staticmethod
    def format_current_temperature(current_temperature: float):
        """Format current temperature information display."""
        ModelFormatter._output(f"\n[1mCurrent Temperature:[0m {current_temperature}")
        
        ModelFormatter._output(f"\n[90mUsage:[0m [1m/model.settemp NUMBER[0m - Set temperature parameter")
        ModelFormatter._output(f"[90mRange:[0m {MIN_TEMPERATURE} to {MAX_TEMPERATURE}")
        ModelFormatter._output(f"[90mDefault:[0m {DEFAULT_TEMPERATURE}")
        
        # Provide guidance on temperature values
        ModelFormatter._output(f"\n[1;36mTemperature Guide:[0m")
        ModelFormatter._output(f"  [34m0.0[0m   - Completely deterministic (always same response)")
        ModelFormatter._output(f"  [32m0.2[0m   - Very focused and consistent")
        ModelFormatter._output(f"  [32m0.4[0m   - Focused but with some variation")
        ModelFormatter._output(f"  [33m0.7[0m   - Balanced creativity and consistency")
        ModelFormatter._output(f"  [33m{DEFAULT_TEMPERATURE}[0m   - Default Ollama setting (good balance)")
        ModelFormatter._output(f"  [38;5;208m1.0[0m   - More creative and varied responses")
        ModelFormatter._output(f"  [38;5;208m1.2[0m   - Quite creative, may be less coherent")
        ModelFormatter._output(f"  [31m1.5+[0m  - Very creative but potentially chaotic")
        
        ModelFormatter._output(f"\n[90mLower values = more predictable, higher values = more creative[0m")
    
    @staticmethod
    def format_temperature_result(result: TemperatureResult):
        """Format temperature setting result."""
        if not result.success:
            ModelFormatter._output(f"\n[1;31mError:[0m Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}")
            return
        
        # Provide guidance based on temperature value
        if result.warning_level == "deterministic":
            ModelFormatter._output(f"\n[34mNotice:[0m Deterministic mode - responses will be identical for same inputs")
        elif result.warning_level == "low":
            ModelFormatter._output(f"\n[32mNotice:[0m Very low temperature - responses will be highly consistent")
        elif result.warning_level == "warning":
            ModelFormatter._output(f"\n[33mWarning:[0m High temperature ({result.temperature}) may produce:")
            ModelFormatter._output(f"  • Very creative but potentially incoherent responses")
            ModelFormatter._output(f"  • Unpredictable or inconsistent behavior")
            ModelFormatter._output(f"  • Reduced factual accuracy")
        elif result.warning_level == "notice":
            ModelFormatter._output(f"\n[33mNotice:[0m High temperature ({result.temperature}) - expect very creative responses")
        
        # Success message
        ModelFormatter._output(f"\n[32mTemperature set to {result.temperature} for this chat[0m")
        ModelFormatter._output("[90mThis will take effect on the next message to the model[0m")
    
    @staticmethod
    def format_invalid_state_error(command_type: str):
        """Format invalid state parameter error."""
        ModelFormatter._output("[1;31mError:[0m State must be 'on' or 'off'")
        ModelFormatter._output(f"[90mUsage: /model.{command_type} on  or  /model.{command_type} off[0m")
    
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
                ModelFormatter._output("[90mModel reasoning will be shown during responses but filtered from history and twist operations[0m")
            else:
                ModelFormatter._output("[90mModel reasoning will be hidden for clean output[0m")
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
            ModelFormatter._output("[90mModel reasoning will be shown during responses but filtered from history and twist operations[0m")
        else:
            ModelFormatter._output("[90mModel reasoning will be hidden for clean output[0m")
    
    @staticmethod
    def format_tooluse_state(result: ToolUseResult):
        """Format tool use mode state change."""
        if result.changed:
            status = "enabled" if result.enabled else "disabled"
            ModelFormatter._output(f"\nTool use is now: {status}")
            if result.enabled:
                ModelFormatter._output(f"{Colors.HINT}Model can now call function plugins when appropriate{Colors.RESET}")
            else:
                ModelFormatter._output(f"{Colors.HINT}Model will not use function plugins{Colors.RESET}")
        else:
            ModelFormatter._output(f"\nTool use is already {'enabled' if result.enabled else 'disabled'}")
