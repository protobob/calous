"""Chat management commands."""
from typing import Optional
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import ChatService
from .formatters import ChatFormatter



@registry.register("chat.switch", "Switch between chat sessions", category=CommandCategory.NAVIGATION)
def cmd_chat_switch(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Switch to specified chat or cycle to next."""
    service = ChatService(handler.app)
    result = service.validate_switch(chat_number)
    
    if not result.success:
        ChatFormatter.format_switch_error(result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    return CommandResult(ActionType.SWITCH, {"target_chat": result.target_index})




@registry.register("chat.twist", "Copy AI response to another chat", category=CommandCategory.NAVIGATION)
def cmd_chat_twist(handler, target_chat: Optional[int] = None) -> CommandResult:
    """Twist last AI response to target chat."""
    service = ChatService(handler.app)
    result = service.validate_twist(target_chat)
    
    if not result.success:
        ChatFormatter.format_twist_error(result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    return CommandResult(ActionType.TWIST, {
        "content": result.content,
        "target_chat": result.target_index
    })


@registry.register("chat.reset", "Reset current chat to factory defaults", category=CommandCategory.NAVIGATION)
def cmd_chat_reset(handler) -> CommandResult:
    """Reset the current chat to factory defaults with confirmation."""
    service = ChatService(handler.app)
    
    # Get chat info for display
    chat_info = service.get_chat_info()
    
    # Show warning and ask for confirmation
    ChatFormatter.format_reset_warning(chat_info)
    
    if ChatFormatter.confirm_action("Are you sure you want to reset this chat to factory defaults?", app=handler.app):
        # Perform the reset
        success = service.reset_to_defaults()
        
        if success:
            ChatFormatter.format_reset_success(chat_info)
        else:
            ChatFormatter.format_reset_error()
    else:
        ChatFormatter.format_operation_cancelled()
        
    return CommandResult(ActionType.CONTINUE)


@registry.register("chat.help", "Show help for chat commands", category=CommandCategory.NAVIGATION)
def cmd_chat_help(handler) -> CommandResult:
    """Show help for chat commands - alias for /sys.help chat."""
    handler.app.ui.show_category_help("chat")
    return CommandResult(ActionType.CONTINUE)

@registry.register("chat.vars", "Show chat-specific variables", category=CommandCategory.NAVIGATION)
def cmd_chat_vars(handler) -> CommandResult:
    """Display chat-specific variables and settings."""
    service = ChatService(handler.app)
    service.show_chat_variables()
    return CommandResult(ActionType.CONTINUE)

