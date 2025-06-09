"""Model management services."""
from typing import Optional, NamedTuple
from ...constants import MIN_NUM_CTX, MAX_NUM_CTX, MIN_TEMPERATURE, MAX_TEMPERATURE


class ContextResult(NamedTuple):
    success: bool
    context_size: int
    vram_estimate: Optional[str] = None
    warning_level: str = "none"  # none, notice, warning, error


class TemperatureResult(NamedTuple):
    success: bool
    temperature: float
    warning_level: str = "none"  # none, notice, warning


class EvaluationResult(NamedTuple):
    enabled: bool
    changed: bool


class ThinkingResult(NamedTuple):
    enabled: bool
    changed: bool


class ModelService:
    """Service for managing model settings and operations."""
    
    def __init__(self, app):
        self.app = app
    
    def select_model(self) -> Optional[str]:
        """Select a model from available models."""
        return self.app.model.select_model()
      
    def update_global_model(self, model_name: str) -> int:
        """Update the model globally across all chats."""
        return self.app.update_global_model(model_name)
    
    def update_global_context(self, context_size: int) -> int:
        """Update the context window globally across all chats."""
        return self.app.update_global_num_ctx(context_size)
    
    def get_current_context(self) -> int:
        """Get the current context window size."""
        return self.app.num_ctx
    
    def set_context_size(self, context_size: int) -> ContextResult:
        """Set the context window size with validation."""
        # Validate input
        if context_size < MIN_NUM_CTX:
            return ContextResult(
                success=False,
                context_size=context_size,
                warning_level="error"
            )
        
        if context_size > MAX_NUM_CTX:
            return ContextResult(
                success=False,
                context_size=context_size,
                warning_level="error"
            )
        
        # Get VRAM estimate
        vram_estimate = None
        if self.app.selected_model:
            context_info = self.app.model.get_context_window_info(self.app.selected_model)
            if context_info:
                user_context_info = context_info._replace(actual_context=context_size)
                vram_estimate = self.app.model.estimate_context_vram_usage(user_context_info)
        
        # Determine warning level
        warning_level = "none"
        if context_size > 24576:  # 24k+
            warning_level = "error"
        elif context_size > 16384:  # 16k+
            warning_level = "warning"
        elif context_size > 8192:  # 8k+
            warning_level = "notice"
          # Set the context size globally
        updated_count = self.update_global_context(context_size)
        
        return ContextResult(
            success=True,
            context_size=context_size,
            vram_estimate=vram_estimate,
            warning_level=warning_level
        )
    
    def get_current_temperature(self) -> float:
        """Get the current temperature setting."""
        return self.app.temperature
    
    def set_temperature(self, temperature: float) -> TemperatureResult:
        """Set the temperature with validation."""
        # Validate input
        if temperature < MIN_TEMPERATURE or temperature > MAX_TEMPERATURE:
            return TemperatureResult(
                success=False,
                temperature=temperature,
                warning_level="error"
            )
        
        # Determine warning level
        warning_level = "none"
        if temperature == 0.0:
            warning_level = "deterministic"
        elif temperature < 0.3:
            warning_level = "low"
        elif temperature > 1.5:
            warning_level = "warning"
        elif temperature > 1.0:
            warning_level = "notice"
        
        # Set the temperature
        self.app.temperature = temperature
        
        return TemperatureResult(
            success=True,
            temperature=temperature,
            warning_level=warning_level
        )
    
    def get_evaluation_display(self) -> bool:
        """Get the current evaluation display setting."""
        return self.app.verbosity
    
    def set_evaluation_display(self, enabled: bool) -> EvaluationResult:
        """Set the evaluation display setting."""
        current = self.app.verbosity
        changed = current != enabled
        self.app.verbosity = enabled
        return EvaluationResult(enabled=enabled, changed=changed)
    
    def get_thinking_mode(self) -> bool:
        """Get the current thinking mode setting."""
        return self.app.thinking_enabled
    
    def set_thinking_mode(self, enabled: bool) -> ThinkingResult:
        """Set the thinking mode setting."""
        current = self.app.thinking_enabled
        changed = current != enabled
        self.app.thinking_enabled = enabled
        return ThinkingResult(enabled=enabled, changed=changed)
