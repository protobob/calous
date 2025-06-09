"""Model management commands."""
from typing import Optional
from rich import print
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import ModelService
from .formatters import ModelFormatter


@registry.register("model.switch", "Change the current model", category=CommandCategory.MODEL)
def cmd_model_switch(handler) -> CommandResult:
    """Select a different model globally."""
    service = ModelService(handler.app)
    selected = service.select_model()
    if selected:
        updated_count = service.update_global_model(selected)
        ModelFormatter.format_model_changed(selected, updated_count)
    return CommandResult(ActionType.CONTINUE)


@registry.register("model.setctx", "Set max context window size", category=CommandCategory.MODEL)
def cmd_model_setctx(handler, context_size: Optional[int] = None) -> CommandResult:
    """Set the context window size for the current chat."""
    service = ModelService(handler.app)
    formatter = ModelFormatter()
    
    if context_size is None:
        # Show current setting and helpful guidance
        formatter.format_current_context(service.get_current_context(), handler.app.selected_model, service)
        return CommandResult(ActionType.CONTINUE)
    
    # Validate and set context size
    result = service.set_context_size(context_size)
    formatter.format_context_result(result)
    return CommandResult(ActionType.CONTINUE)


@registry.register("model.eval", "Toggle evaluation display", category=CommandCategory.MODEL)
def cmd_model_eval(handler, state: str) -> CommandResult:
    """Enable or disable evaluation data display."""
    if state.lower() not in ["on", "off"]:
        ModelFormatter.format_invalid_state_error("eval")
        return CommandResult(ActionType.CONTINUE)
    
    service = ModelService(handler.app)
    target_state = state.lower() == "on"
    result = service.set_evaluation_display(target_state)
    ModelFormatter.format_evaluation_state(result)
    return CommandResult(ActionType.CONTINUE)


@registry.register("model.think", "Toggle thinking display", category=CommandCategory.MODEL)
def cmd_model_think(handler, state: str) -> CommandResult:
    """Enable or disable thinking mode display."""
    if state.lower() not in ["on", "off"]:
        ModelFormatter.format_invalid_state_error("think")
        return CommandResult(ActionType.CONTINUE)
    
    service = ModelService(handler.app)
    target_state = state.lower() == "on"
    result = service.set_thinking_mode(target_state)
    ModelFormatter.format_thinking_state(result)
    return CommandResult(ActionType.CONTINUE)


@registry.register("model.settemp", "Set temperature parameter", category=CommandCategory.MODEL)
def cmd_model_settemp(handler, temperature: Optional[float] = None) -> CommandResult:
    """Set the temperature parameter for the current chat."""
    service = ModelService(handler.app)
    formatter = ModelFormatter()
    
    if temperature is None:
        # Show current setting and helpful guidance
        formatter.format_current_temperature(service.get_current_temperature())
        return CommandResult(ActionType.CONTINUE)
    
    # Validate and set temperature
    result = service.set_temperature(temperature)
    formatter.format_temperature_result(result)
    return CommandResult(ActionType.CONTINUE)


@registry.register("model.help", "Show help for model commands", category=CommandCategory.MODEL)
def cmd_model_help(handler) -> CommandResult:
    """Show help for model commands - alias for /sys.help model."""
    handler.app.ui.show_category_help("model")
    return CommandResult(ActionType.CONTINUE)


