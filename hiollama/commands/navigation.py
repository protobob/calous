"""Chat navigation commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


def cmd_switch(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Switch to specified chat or cycle to next."""
    target_chat = None
    if chat_number is not None:
        if chat_number < 1:
            print("[bold red]Error:[/bold red] Chat number must be 1 or greater.")
            return CommandResult(ActionType.CONTINUE)
        target_chat = chat_number - 1  # Convert to 0-based index
    
    return CommandResult(ActionType.SWITCH, {"target_chat": target_chat})


def cmd_addchat(handler) -> CommandResult:
    """Add a new chat session dynamically."""
    # Validate maximum chat limit
    from ..constants import MAX_CHATS
    current_num_chats = handler.app.session_manager.num_chats
    
    if current_num_chats >= MAX_CHATS:
        print(f"[bold red]Error:[/bold red] Maximum number of chats ({MAX_CHATS}) reached.")
        return CommandResult(ActionType.CONTINUE)
    
    print(f"[bold green]Adding new chat session...[/bold green] Creating Chat {current_num_chats + 1}")
    return CommandResult(ActionType.ADDCHAT)


def cmd_removechat(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Remove a chat session dynamically."""
    current_num_chats = handler.app.session_manager.num_chats
    
    # Must have at least 1 chat
    if current_num_chats <= 1:
        print("[bold red]Error:[/bold red] Cannot remove the last remaining chat.")
        return CommandResult(ActionType.CONTINUE)
    
    # If no chat number specified, remove the last chat
    if chat_number is None:
        target_index = current_num_chats - 1  # Last chat (0-based)
        chat_number = current_num_chats  # For display (1-based)
    else:
        if chat_number < 1 or chat_number > current_num_chats:
            print(f"[bold red]Error:[/bold red] Chat number must be between 1 and {current_num_chats}.")
            return CommandResult(ActionType.CONTINUE)
        target_index = chat_number - 1  # Convert to 0-based index
    
    print(f"[bold yellow]Removing Chat {chat_number}...[/bold yellow] Configuration will be preserved.")    
    return CommandResult(ActionType.REMOVECHAT, {"target_index": target_index})


def cmd_twist(handler, target_chat: Optional[int] = None) -> CommandResult:
    """Twist last AI response to target chat."""
    # Validate last response exists
    last_response = handler.app.last_response
    if not last_response:
        print("\n[bold red]Error:[/bold red] No previous response to twist.")
        return CommandResult(ActionType.CONTINUE)    # Extract content
    twist_content = last_response.get("message", {}).get("content", "")    
    if not twist_content:
        print("[bold red]Error:[/bold red] Previous response is empty.")
        return CommandResult(ActionType.CONTINUE)

    # With native Ollama API, last_response already contains clean content (no thinking)
    # No need to strip thoughts as the API handles this separation
    clean_twist_content = twist_content
    if not clean_twist_content:
        print("[bold red]Error:[/bold red] No valid content to twist.")
        return CommandResult(ActionType.CONTINUE)# Process target chat
    target_index = None
    if target_chat is not None:
        if target_chat < 1:
            print("[bold red]Error:[/bold red] Target chat number must be 1 or greater.")
            return CommandResult(ActionType.CONTINUE)
        target_index = target_chat - 1  # Convert to 0-based index
    
    return CommandResult(ActionType.TWIST, {
        "content": clean_twist_content,
        "target_chat": target_index
    })


# Hierarchical chat session management commands

@registry.register("chat.add", "Add a new chat session", category=CommandCategory.NAVIGATION)
def cmd_chat_add(handler) -> CommandResult:
    """Add a new chat session using hierarchical command."""
    return cmd_addchat(handler)


@registry.register("chat.switch", "Switch between chat sessions", category=CommandCategory.NAVIGATION)
def cmd_chat_switch(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Switch to specified chat or cycle to next using hierarchical command."""
    return cmd_switch(handler, chat_number)


@registry.register("chat.remove", "Remove a chat session", category=CommandCategory.NAVIGATION)
def cmd_chat_remove(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Remove a chat session using hierarchical command."""
    return cmd_removechat(handler, chat_number)


@registry.register("chat.twist", "Copy AI response to another chat", category=CommandCategory.NAVIGATION)
def cmd_chat_twist(handler, target_chat: Optional[int] = None) -> CommandResult:
    """Twist last AI response to target chat using hierarchical command."""
    return cmd_twist(handler, target_chat)


@registry.register("chat.reset", "Reset current chat to factory defaults", category=CommandCategory.NAVIGATION)
def cmd_chat_reset(handler) -> CommandResult:
    """Reset the current chat to factory defaults with confirmation."""
    # Import the resetchat function from general.py
    from .general import cmd_resetchat
    return cmd_resetchat(handler)