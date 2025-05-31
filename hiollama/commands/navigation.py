"""Chat navigation commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


@registry.register("switch", "Switch between chats", category=CommandCategory.NAVIGATION)
def cmd_switch(handler, chat_number: Optional[int] = None) -> CommandResult:
    """Switch to specified chat or cycle to next."""
    target_chat = None
    if chat_number is not None:
        if chat_number < 1:
            print("[bold red]Error:[/bold red] Chat number must be 1 or greater.")
            return CommandResult(ActionType.CONTINUE)
        target_chat = chat_number - 1  # Convert to 0-based index
    
    return CommandResult(ActionType.SWITCH, {"target_chat": target_chat})


@registry.register("twist", "Copy AI response to another chat", category=CommandCategory.NAVIGATION)
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