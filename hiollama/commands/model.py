"""Model management commands."""
from rich import print
from ..types import CommandResult, ActionType
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


@registry.register("toggle_think", "Toggle AI thought filtering", aliases=["think"], category=CommandCategory.MODEL)
def cmd_toggle_think(handler) -> CommandResult:
    """Toggle filtering of AI thoughts."""
    handler.app.think_filtering = not handler.app.think_filtering
    print(f"\nThink filtering is now: {handler.app.think_filtering}")
    return CommandResult(ActionType.CONTINUE)