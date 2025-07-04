"""Context management commands."""
import re
from pathlib import Path
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import ContextService
from .formatters import ContextFormatter
from ...constants import CONTEXT_DIR


@registry.register("context.save", "Save current context to a file", category=CommandCategory.CONTEXT)
def cmd_context_save(handler, name) -> CommandResult:
    """Save current context (persona, prompts, history) to a file."""
    # Join name parts if it's a list (from nargs='+')
    if isinstance(name, list):
        name = " ".join(name)
    
    # Sanitize filename: only allow alphanumeric, dash, underscore, strip after first dot
    base = re.split(r"[.]", name)[0]
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    
    if not safe_name:
        ContextFormatter.format_save_error("Invalid filename")
        return CommandResult(ActionType.CONTINUE)
    
    service = ContextService(handler.app)
    
    # Check for overwrite
    save_path = CONTEXT_DIR / f"{safe_name}.json"
    
    if save_path.exists():
        ContextFormatter._output(f"\n[33mContext '{safe_name}' already exists[0m")
        if not ContextFormatter.confirm_action("Overwrite?", default="n", app=handler.app):
            ContextFormatter.format_operation_cancelled()
            return CommandResult(ActionType.CONTINUE)
    
    # Save the context
    result = service.save_context(safe_name)
    
    if result.success:
        ContextFormatter.format_save_success(result.data["name"], result.data["filepath"])
    else:
        ContextFormatter.format_save_error(result.error_message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("context.load", "Load context from a file", category=CommandCategory.CONTEXT)
def cmd_context_load(handler, name) -> CommandResult:
    """Load context from a file (overwrites current data)."""
    # Join name parts if it's a list (from nargs='+')
    if isinstance(name, list):
        name = " ".join(name)
    
    # Sanitize filename
    base = re.split(r"[.]", name)[0]
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    
    if not safe_name:
        ContextFormatter.format_load_error("Invalid filename")
        return CommandResult(ActionType.CONTINUE)
    
    service = ContextService(handler.app)
    
    # Check if file exists
    load_path = CONTEXT_DIR / f"{safe_name}.json"
    
    if not load_path.exists():
        ContextFormatter.format_load_error(f"Context '{safe_name}' not found")
        return CommandResult(ActionType.CONTINUE)
    
    # Warn user about overwrite
    ContextFormatter.format_load_warning()
    if not ContextFormatter.confirm_action("Continue?", default="n", app=handler.app):
        ContextFormatter.format_operation_cancelled()
        return CommandResult(ActionType.CONTINUE)
    
    # Load the context
    result = service.load_context(safe_name)
    
    if result.success:
        ContextFormatter.format_load_success(result.data["name"])
    else:
        ContextFormatter.format_load_error(result.error_message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("context.list", "List all saved contexts", category=CommandCategory.CONTEXT)
def cmd_context_list(handler) -> CommandResult:
    """List all saved context files."""
    service = ContextService(handler.app)
    result = service.list_contexts()
    
    if not result.success:
        ContextFormatter.format_load_error(result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    contexts = result.data["contexts"]
    
    if not contexts:
        ContextFormatter.format_no_contexts()
    else:
        ContextFormatter.format_contexts_header()
        for context in contexts:
            ContextFormatter.format_context_item(context["name"], context["size"])
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("context.delete", "Delete a saved context file", category=CommandCategory.CONTEXT)
def cmd_context_delete(handler, name) -> CommandResult:
    """Delete a saved context file."""
    # Join name parts if it's a list (from nargs='+')
    if isinstance(name, list):
        name = " ".join(name)
    
    # Sanitize filename
    base = re.split(r"[.]", name)[0]
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    
    if not safe_name:
        ContextFormatter.format_delete_error("Invalid filename")
        return CommandResult(ActionType.CONTINUE)
    
    service = ContextService(handler.app)
    
    # Check if file exists
    delete_path = CONTEXT_DIR / f"{safe_name}.json"
    
    if not delete_path.exists():
        ContextFormatter.format_delete_error(f"Context '{safe_name}' not found")
        return CommandResult(ActionType.CONTINUE)
    
    # Confirm deletion
    ContextFormatter.format_delete_warning(safe_name)
    if not ContextFormatter.confirm_action("Delete?", default="n", app=handler.app):
        ContextFormatter.format_operation_cancelled()
        return CommandResult(ActionType.CONTINUE)
    
    # Delete the context
    result = service.delete_context(safe_name)
    
    if result.success:
        ContextFormatter.format_delete_success(result.data["name"])
    else:
        ContextFormatter.format_delete_error(result.error_message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("context.help", "Show help for context commands", category=CommandCategory.CONTEXT)
def cmd_context_help(handler) -> CommandResult:
    """Show help for context commands - alias for /sys.help context."""
    handler.app.ui.show_category_help("context")
    return CommandResult(ActionType.CONTINUE)