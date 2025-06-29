"""Persona command formatters module."""
from rich import print
from rich.prompt import Prompt
from ..formatters import CommandFormatter
from ...utils import get_chat_color


class PersonaFormatter(CommandFormatter):
    """Specialized formatter for persona command output."""
    
    @staticmethod
    def get_chat_context(app):
        """Get chat color and number for styling."""
        chat_number = getattr(app, 'active_chat_index', 0) + 1
        chat_color = get_chat_color(getattr(app, 'active_chat_index', 0))
        return chat_color, chat_number
    
    @staticmethod
    def slot_validation_error(message: str):
        """Print slot validation error."""
        print(f"[bold red]Error:[/bold red] {message}")
    
    @staticmethod
    def content_validation_error(message: str):
        """Print content validation error."""
        print(f"[bold red]Error:[/bold red] {message}")
    
    @staticmethod
    def slot_set_success(slot: int, chat_color: str):
        """Print slot set success message."""
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona slot {slot} set successfully!")
    
    @staticmethod
    def show_slot_content(slot: int, content: str, chat_color: str, chat_number: int):
        """Show content of a specific slot."""
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {chat_number} PERSONA SLOT {slot}[/bold {chat_color}]\n")
        
        if content:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot Content:':<20} [grey70]{content}[/grey70]\n")
        else:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot Content:':<20} [grey70](not set)[/grey70]\n")
    
    @staticmethod
    def slot_already_empty_warning(slot: int):
        """Print warning that slot is already empty."""
        print(f"[bold yellow]Warning:[/bold yellow] Slot {slot} is already empty.")
    
    @staticmethod
    def slot_clear_success(slot: int, chat_color: str):
        """Print slot clear success message."""
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona slot {slot} cleared successfully!")
    
    @staticmethod
    def name_set_success(name: str, chat_color: str):
        """Print name set success message."""
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona name set to: [grey70]{name}[/grey70]")
    
    @staticmethod
    def show_persona_overview(persona_info: dict, chat_color: str, chat_number: int):
        """Show complete persona overview."""
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {chat_number} PERSONA[/bold {chat_color}]\n")
        
        # Show persona name
        persona_name = persona_info['name']
        if persona_name:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Name:':<20} [grey70]{persona_name}[/grey70]")
        else:
            print(f"[bold {chat_color}]|[/bold {chat_color}] {'Name:':<20} [grey70](not set)[/grey70]")
        
        print()  # Empty line for spacing
        
        # Show all slots
        slots = persona_info['slots']
        for slot in range(10):
            content = slots.get(slot, "")
            if content:
                print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot ' + str(slot) + ':':<20} [grey70]{content}[/grey70]")
            else:
                print(f"[bold {chat_color}]|[/bold {chat_color}] {'Slot ' + str(slot) + ':':<20} [grey70](not set)[/grey70]")
        
        print()  # Empty line for spacing
        
        # Show combined prompt if there's content
        if persona_info['has_content'] and persona_info['combined_prompt']:
            combined = persona_info['combined_prompt']
            print(f"[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]COMBINED SYSTEM PROMPT:[/bold {chat_color}]\n")
            print(f"[bold {chat_color}]|[/bold {chat_color}] [grey70]{combined}[/grey70]\n")
    
    @staticmethod
    def persona_already_empty(chat_color: str):
        """Print message that persona is already empty."""
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona is already empty.")
    
    @staticmethod
    def reset_warning(chat_color: str, chat_number: int):
        """Show reset warning and get confirmation."""
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]CLEAR[/bold red] [bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] persona.")
        print("This will clear the persona name and all slot contents.")
        return Prompt.ask("\nAre you sure you want to continue?", choices=["y", "n"], default="n")
    
    @staticmethod
    def reset_success(chat_color: str, chat_number: int):
        """Print reset success message."""
        print(f"[bold {chat_color}]CHAT {chat_number}[/bold {chat_color}] persona reset successfully!")
    
    @staticmethod
    def operation_cancelled():
        """Print operation cancelled message."""
        print("Operation cancelled.")
    
    @staticmethod
    def save_name_required_error():
        """Print error that name is required for saving."""
        print("[bold red]Error:[/bold red] You must set a persona name before saving.")
        print("Use [bold]/persona.name <n>[/bold] to set a name first.")
    
    @staticmethod
    def save_no_content_warning():
        """Print warning that there's no content to save."""
        print("[bold yellow]Warning:[/bold yellow] Persona has no slot content to save.")
    
    @staticmethod
    def load_success(name: str, chat_color: str):
        """Print load success message."""
        print(f"[bold {chat_color}]|[/bold {chat_color}] Persona '{name}' loaded successfully!")
    
    @staticmethod
    def show_persona_list(personas: list, chat_color: str):
        """Show list of saved personas."""
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]SAVED PERSONAS[/bold {chat_color}]\n")
        
        if not personas:
            print(f"[bold {chat_color}]|[/bold {chat_color}] [grey70]No saved personas found.[/grey70]\n")
        else:
            for i, persona in enumerate(personas, 1):
                print(f"[bold {chat_color}]|[/bold {chat_color}] {i:>2}. [grey70]{persona}[/grey70]")
            print()  # Empty line for spacing
    
    @staticmethod
    def delete_warning(name: str):
        """Show delete warning and get confirmation."""
        print(f"\n[bold yellow]Warning:[/bold yellow] This will [bold red]DELETE[/bold red] saved persona file '{name}'.")
        print("This action cannot be undone.")
        return Prompt.ask("\nAre you sure you want to continue?", choices=["y", "n"], default="n")
    
    @staticmethod
    def delete_cancelled():
        """Print delete cancelled message."""
        print("Delete operation cancelled.")
    
    @staticmethod
    def reset_cancelled():
        """Print reset cancelled message."""
        print("Reset operation cancelled.")
    
    @staticmethod
    def keyboard_interrupt_error():
        """Print keyboard interrupt error."""
        print("\nOperation cancelled.")
    
    @staticmethod
    def generic_error(message: str):
        """Print generic error message."""
        print(f"[bold red]Error:[/bold red] {message}")
