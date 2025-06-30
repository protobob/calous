"""Persona commands module."""
from rich import print as rich_print

from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import PersonaService
from .formatters import PersonaFormatter


@registry.register("persona.set", "Set a system prompt at slot 0-9", category=CommandCategory.PERSONA)
def cmd_persona_set(handler, slot: int, content) -> CommandResult:
    """Set a system prompt at slot 0-9."""
    formatter = PersonaFormatter()
    
    # Validate slot
    slot_result = PersonaService.validate_slot(slot)
    if not slot_result.success:
        formatter.slot_validation_error(slot_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Validate and process content
    content_result = PersonaService.validate_content(content)
    if not content_result.success:
        formatter.content_validation_error(content_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Set the slot
    set_result = PersonaService.set_persona_slot(handler.app, slot, content_result.data)
    if not set_result.success:
        formatter.generic_error(set_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Show success message
    chat_color, _ = formatter.get_chat_context(handler.app)
    formatter.slot_set_success(slot, chat_color)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.get", "View contents of a specific slot", category=CommandCategory.PERSONA)
def cmd_persona_get(handler, slot: int) -> CommandResult:
    """View contents of a specific slot."""
    formatter = PersonaFormatter()
    
    # Validate slot
    slot_result = PersonaService.validate_slot(slot)
    if not slot_result.success:
        formatter.slot_validation_error(slot_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Get slot content
    get_result = PersonaService.get_persona_slot(handler.app, slot)
    if not get_result.success:
        formatter.generic_error(get_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Show slot content
    chat_color, chat_number = formatter.get_chat_context(handler.app)
    formatter.show_slot_content(slot, get_result.data, chat_color, chat_number)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.clear", "Clear contents of a specific slot", category=CommandCategory.PERSONA)
def cmd_persona_clear(handler, slot: int) -> CommandResult:
    """Clear contents of a specific slot."""
    formatter = PersonaFormatter()
    
    # Validate slot
    slot_result = PersonaService.validate_slot(slot)
    if not slot_result.success:
        formatter.slot_validation_error(slot_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Clear the slot
    clear_result = PersonaService.clear_persona_slot(handler.app, slot)
    if not clear_result.success:
        if "already empty" in clear_result.error_message:
            formatter.slot_already_empty_warning(slot)
        else:
            formatter.generic_error(clear_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Show success message
    chat_color, _ = formatter.get_chat_context(handler.app)
    formatter.slot_clear_success(slot, chat_color)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.name", "Set the persona name", category=CommandCategory.PERSONA)
def cmd_persona_name(handler, name) -> CommandResult:
    """Set the persona name."""
    formatter = PersonaFormatter()
    
    # Validate and process name
    name_result = PersonaService.validate_name(name)
    if not name_result.success:
        formatter.content_validation_error(name_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Set the name
    set_result = PersonaService.set_persona_name(handler.app, name_result.data)
    if not set_result.success:
        formatter.generic_error(set_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Show success message
    chat_color, _ = formatter.get_chat_context(handler.app)
    formatter.name_set_success(name_result.data, chat_color)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.show", "Show current name + all slot contents", category=CommandCategory.PERSONA)
def cmd_persona_show(handler) -> CommandResult:
    """Show current name + all slot contents."""
    formatter = PersonaFormatter()
    
    # Get persona information
    info_result = PersonaService.get_persona_info(handler.app)
    if not info_result.success:
        formatter.generic_error(info_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Show persona overview
    chat_color, chat_number = formatter.get_chat_context(handler.app)
    formatter.show_persona_overview(info_result.data, chat_color, chat_number)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.reset", "Clear name and all slot contents", category=CommandCategory.PERSONA)
def cmd_persona_reset(handler) -> CommandResult:
    """Clear name and all slot contents (start fresh)."""
    formatter = PersonaFormatter()
    
    try:
        # Get chat context
        chat_color, chat_number = formatter.get_chat_context(handler.app)
        
        # Check if there's anything to reset
        if handler.app.persona.is_empty():
            formatter.persona_already_empty(chat_color)
            return CommandResult(ActionType.CONTINUE)
        
        # Ask for confirmation
        confirm = formatter.reset_warning(chat_color, chat_number)
        
        if confirm == 'y':
            # Reset persona
            reset_result = PersonaService.reset_persona(handler.app)
            if reset_result.success:
                formatter.reset_success(chat_color, chat_number)
            else:
                formatter.generic_error(reset_result.error_message)
        else:
            formatter.reset_cancelled()
            
    except KeyboardInterrupt:
        formatter.keyboard_interrupt_error()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.save", "Save current persona", category=CommandCategory.PERSONA)
def cmd_persona_save(handler) -> CommandResult:
    """Save current persona (uses name as filename)."""
    formatter = PersonaFormatter()
    
    # Attempt to save
    save_result = PersonaService.save_persona(handler.app)
    
    if not save_result.success:
        if "name before saving" in save_result.error_message:
            formatter.save_name_required_error()
        elif "no slot content" in save_result.error_message:
            formatter.save_no_content_warning()
        else:
            formatter.generic_error(save_result.error_message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.load", "Load a saved persona by name", category=CommandCategory.PERSONA)
def cmd_persona_load(handler, name) -> CommandResult:
    """Load a saved persona by name."""
    formatter = PersonaFormatter()
    
    # Validate and process name
    name_result = PersonaService.validate_name(name)
    if not name_result.success:
        formatter.content_validation_error(name_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Load the persona
    load_result = PersonaService.load_persona(handler.app, name_result.data)
    if load_result.success:
        chat_color, _ = formatter.get_chat_context(handler.app)
        formatter.load_success(load_result.data, chat_color)
    else:
        formatter.generic_error(load_result.error_message)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.list", "List all saved personas", category=CommandCategory.PERSONA)
def cmd_persona_list(handler) -> CommandResult:
    """List all saved personas."""
    formatter = PersonaFormatter()
    
    # Get persona list
    list_result = PersonaService.list_personas()
    if not list_result.success:
        formatter.generic_error(list_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Show the list
    chat_color, _ = formatter.get_chat_context(handler.app)
    formatter.show_persona_list(list_result.data, chat_color)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.delete", "Delete a saved persona file", category=CommandCategory.PERSONA)
def cmd_persona_delete(handler, name) -> CommandResult:
    """Delete a saved persona."""
    formatter = PersonaFormatter()
    
    # Validate and process name
    name_result = PersonaService.validate_name(name)
    if not name_result.success:
        formatter.content_validation_error(name_result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Ask for confirmation
    confirm = formatter.delete_warning(name_result.data)
    
    if confirm == 'y':
        # Delete the persona
        delete_result = PersonaService.delete_persona(name_result.data)
        if not delete_result.success:
            formatter.generic_error(delete_result.error_message)
    else:
        formatter.delete_cancelled()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.help", "Show help for persona commands", category=CommandCategory.PERSONA)
def cmd_persona_help(handler) -> CommandResult:
    """Show help for persona commands - alias for /sys.help persona."""
    handler.app.ui.show_category_help("persona")
    return CommandResult(ActionType.CONTINUE)
