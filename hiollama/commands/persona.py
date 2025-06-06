"""Persona management commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory
from ..persona import PersonaManager
from ..utils import get_chat_color


@registry.register("persona.set", "Set a system prompt at slot 0-9", category=CommandCategory.PROMPT)
def cmd_persona_set(handler, slot: int, content) -> CommandResult:
    """Set a system prompt at slot 0-9."""
    try:
        if not (0 <= slot <= 9):
            print("[bold red]Error:[/bold red] Slot must be between 0 and 9.")
            return CommandResult(ActionType.CONTINUE)
        
        # Handle both single strings and lists (from nargs='+')
        if isinstance(content, list):
            content = ' '.join(content)
        
        if not content.strip():
            print("[bold red]Error:[/bold red] Prompt text cannot be empty.")
            return CommandResult(ActionType.CONTINUE)
        
        handler.app.persona.set_slot(slot, content)
        
        # Get chat color for styling
        chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona slot {slot} set successfully!")
        
        # Save config to persist changes
        handler.app.save_config()
        
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.get", "View contents of a specific slot", category=CommandCategory.PROMPT)
def cmd_persona_get(handler, slot: int) -> CommandResult:
    """View contents of a specific slot."""
    try:
        if not (0 <= slot <= 9):
            print("[bold red]Error:[/bold red] Slot must be between 0 and 9.")
            return CommandResult(ActionType.CONTINUE)
        
        content = handler.app.persona.get_slot(slot)
        
        # Get chat color for styling
        chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
        chat_number = getattr(handler.app, 'active_chat_index', 0) + 1
        
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {chat_number} PERSONA SLOT {slot}[/bold {chat_color}]\n")
        
        if content:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot Content:':<20} [grey70]{content}[/grey70]\n")
        else:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot Content:':<20} [grey70](not set)[/grey70]\n")
        
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.clear", "Clear contents of a specific slot", category=CommandCategory.PROMPT)
def cmd_persona_clear(handler, slot: int) -> CommandResult:
    """Clear contents of a specific slot."""
    try:
        if not (0 <= slot <= 9):
            print("[bold red]Error:[/bold red] Slot must be between 0 and 9.")
            return CommandResult(ActionType.CONTINUE)
        
        if not handler.app.persona.get_slot(slot):
            print(f"[bold yellow]Warning:[/bold yellow] Slot {slot} is already empty.")
            return CommandResult(ActionType.CONTINUE)
        
        handler.app.persona.clear_slot(slot)
        
        # Get chat color for styling
        chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona slot {slot} cleared successfully!")
        
        # Save config to persist changes
        handler.app.save_config()
        
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.name", "Set the persona name", category=CommandCategory.PROMPT)
def cmd_persona_name(handler, name) -> CommandResult:
    """Set the persona name."""
    # Handle both single strings and lists (from nargs='+')
    if isinstance(name, list):
        name = ' '.join(name)
    
    if not name.strip():
        print("[bold red]Error:[/bold red] Persona name cannot be empty.")
        return CommandResult(ActionType.CONTINUE)
    
    handler.app.persona.set_name(name)
    
    # Get chat color for styling
    chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
    print(f"[bold {chat_color}]|[/bold {chat_color}] Persona name set to: [grey70]{name}[/grey70]")
    
    # Save config to persist changes
    handler.app.save_config()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.show", "Show current name + all slot contents", category=CommandCategory.PROMPT)
def cmd_persona_show(handler) -> CommandResult:
    """Show current name + all slot contents."""
    # Get chat color for styling
    chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
    chat_number = getattr(handler.app, 'active_chat_index', 0) + 1
    
    print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {chat_number} PERSONA[/bold {chat_color}]\n")
    
    # Show persona name
    persona_name = handler.app.persona.name
    if persona_name:
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Name:':<20} [grey70]{persona_name}[/grey70]")
    else:
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Name:':<20} [grey70](not set)[/grey70]")
    
    print()  # Empty line for spacing
    
    # Show all slots
    has_content = False
    for slot in range(10):
        content = handler.app.persona.get_slot(slot)
        if content:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot ' + str(slot) + ':':<20} [grey70]{content}[/grey70]")
            has_content = True
        else:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot ' + str(slot) + ':':<20} [grey70](not set)[/grey70]")
    
    print()  # Empty line for spacing
    
    # Show combined prompt if there's content
    if has_content:
        combined = handler.app.persona.get_combined_prompt()
        print(f"[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]COMBINED SYSTEM PROMPT:[/bold {chat_color}]\n")
        print(f"[bold {chat_color}]|[/bold {chat_color}] [grey70]{combined}[/grey70]\n")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.reset", "Clear name and all slot contents", category=CommandCategory.PROMPT)
def cmd_persona_reset(handler) -> CommandResult:
    """Clear name and all slot contents (start fresh)."""
    from rich.prompt import Prompt
    
    try:
        # Get chat info for colored display
        chat_number = getattr(handler.app, 'active_chat_index', 0) + 1
        chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
        
        # Check if there's anything to reset
        if handler.app.persona.is_empty():
            print(f"[bold {chat_color}]|[/bold {chat_color}] Persona is already empty.")
            return CommandResult(ActionType.CONTINUE)
        
        # Ask for confirmation
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]CLEAR[/bold red] [bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] persona.")
        print("This will clear the persona name and all slot contents.")
        
        confirm = Prompt.ask("\nAre you sure you want to continue?", choices=["y", "n"], default="n")
        
        if confirm == 'y':
            handler.app.persona.reset()
            print(f"[bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] persona reset successfully!")
            
            # Save config to persist changes
            handler.app.save_config()
        else:
            print("Reset operation cancelled.")
            
    except KeyboardInterrupt:
        print("\nReset operation cancelled.")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.save", "Save current persona", category=CommandCategory.PROMPT)
def cmd_persona_save(handler) -> CommandResult:
    """Save current persona (uses name as filename)."""
    if not handler.app.persona.name:
        print("[bold red]Error:[/bold red] You must set a persona name before saving.")
        print("Use [bold]/persona.name <name>[/bold] to set a name first.")
        return CommandResult(ActionType.CONTINUE)
    
    if not handler.app.persona.has_content():
        print("[bold yellow]Warning:[/bold yellow] Persona has no slot content to save.")
        return CommandResult(ActionType.CONTINUE)
    
    manager = PersonaManager()
    success = manager.save_persona(handler.app.persona.name, handler.app.persona.slots)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.load", "Load a saved persona by name", category=CommandCategory.PROMPT)
def cmd_persona_load(handler, name) -> CommandResult:
    """Load a saved persona by name."""
    # Handle both single strings and lists (from nargs='+')
    if isinstance(name, list):
        name = ' '.join(name)
    
    if not name.strip():
        print("[bold red]Error:[/bold red] Persona name cannot be empty.")
        return CommandResult(ActionType.CONTINUE)
    
    manager = PersonaManager()
    data = manager.load_persona(name)
    
    if data:
        handler.app.persona.load_from_data(data)
        
        # Get chat color for styling
        chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona '{name}' loaded successfully!")
        
        # Save config to persist changes
        handler.app.save_config()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.list", "List all saved personas", category=CommandCategory.PROMPT)
def cmd_persona_list(handler) -> CommandResult:
    """List all saved personas."""
    manager = PersonaManager()
    personas = manager.list_personas()
    
    # Get chat color for styling
    chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
    
    print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]SAVED PERSONAS[/bold {chat_color}]\n")
    
    if not personas:
        print(f"[bold {chat_color}]|[/bold {chat_color}] [grey70]No saved personas found.[/grey70]\n")
    else:
        for i, persona in enumerate(personas, 1):
            print(f"[bold {chat_color}]|[/bold {chat_color}] {i:>2}. [grey70]{persona}[/grey70]")
        print()  # Empty line for spacing
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("persona.delete", "Delete a saved persona file", category=CommandCategory.PROMPT)
def cmd_persona_delete(handler, name) -> CommandResult:
    """Delete a saved persona."""
    # Handle both single strings and lists (from nargs='+')
    if isinstance(name, list):
        name = ' '.join(name)
    
    if not name.strip():
        print("[bold red]Error:[/bold red] Persona name cannot be empty.")
        return CommandResult(ActionType.CONTINUE)
    
    from rich.prompt import Prompt
      # Ask for confirmation
    print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]DELETE[/bold red] saved persona file '{name}'.")
    print("This action cannot be undone.")
    
    confirm = Prompt.ask("\nAre you sure you want to continue?", choices=["y", "n"], default="n")
    
    if confirm == 'y':
        manager = PersonaManager()
        manager.delete_persona(name)
    else:
        print("Delete operation cancelled.")
    
    return CommandResult(ActionType.CONTINUE)
