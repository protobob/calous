"""Persona command formatters module."""
from ..formatters import CommandFormatter
from ...utils import get_chat_color


class PersonaFormatter(CommandFormatter):
    """Specialized formatter for persona command output."""
    
    @staticmethod
    def _output(message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        session_manager = CommandFormatter._get_session_manager()
        if session_manager and session_manager.socket_mode and session_manager.current_connection:
            session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
    @staticmethod
    def get_chat_context(app):
        """Get chat color and number for styling."""
        chat_number = getattr(app, 'active_chat_index', 0) + 1
        chat_color = get_chat_color(getattr(app, 'active_chat_index', 0))
        return chat_color, chat_number
    
    @staticmethod
    def slot_validation_error(message: str):
        """Print slot validation error."""
        PersonaFormatter._output(f"[1;31mError:[0m {message}")
    
    @staticmethod
    def content_validation_error(message: str):
        """Print content validation error."""
        PersonaFormatter._output(f"[1;31mError:[0m {message}")
    
    @staticmethod
    def slot_set_success(slot: int, chat_color: str):
        """Print slot set success message."""
        PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m Persona slot {slot} set successfully!")
    
    @staticmethod
    def show_slot_content(slot: int, content: str, chat_color: str, chat_number: int):
        """Show content of a specific slot."""
        PersonaFormatter._output(f"\n\033[1m{chat_color}|\033[0m \033[1m{chat_color}CHAT {chat_number} PERSONA SLOT {slot}\033[0m\n")
        
        if content:
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {'Slot Content:':<20} [37m{content}[0m\n")
        else:
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {'Slot Content:':<20} [37m(not set)[0m\n")
    
    @staticmethod
    def slot_already_empty_warning(slot: int):
        """Print warning that slot is already empty."""
        PersonaFormatter._output(f"[1;33mWarning:[0m Slot {slot} is already empty.")
    
    @staticmethod
    def slot_clear_success(slot: int, chat_color: str):
        """Print slot clear success message."""
        PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m Persona slot {slot} cleared successfully!")
    
    @staticmethod
    def name_set_success(name: str, chat_color: str):
        """Print name set success message."""
        PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m Persona name set to: [37m{name}[0m")
    
    @staticmethod
    def show_persona_overview(persona_info: dict, chat_color: str, chat_number: int):
        """Show complete persona overview."""
        PersonaFormatter._output(f"\n\033[1m{chat_color}|\033[0m \033[1m{chat_color}CHAT {chat_number} PERSONA\033[0m\n")
        
        # Show persona name
        persona_name = persona_info['name']
        if persona_name:
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {'Name:':<20} [37m{persona_name}[0m")
        else:
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {'Name:':<20} [37m(not set)[0m")
        
        PersonaFormatter._output("")  # Empty line for spacing
        
        # Show all slots
        slots = persona_info['slots']
        for slot in range(10):
            content = slots.get(slot, "")
            if content:
                PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {'Slot ' + str(slot) + ':':<20} [37m{content}[0m")
            else:
                PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {'Slot ' + str(slot) + ':':<20} [37m(not set)[0m")
        
        PersonaFormatter._output("")  # Empty line for spacing
        
        # Show combined prompt if there's content
        if persona_info['has_content'] and persona_info['combined_prompt']:
            combined = persona_info['combined_prompt']
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m \033[1m{chat_color}COMBINED SYSTEM PROMPT:\033[0m\n")
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m [37m{combined}[0m\n")
    
    @staticmethod
    def persona_already_empty(chat_color: str):
        """Print message that persona is already empty."""
        PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m Persona is already empty.")
    
    @staticmethod
    def reset_warning(chat_color: str, chat_number: int):
        """Show reset warning and get confirmation."""
        PersonaFormatter._output(f"\n[1;33mWarning:[0m This will [1;31mCLEAR[0m \033[1m{chat_color}CHAT {chat_number}\033[0m persona.")
        PersonaFormatter._output("This will clear the persona name and all slot contents.")
        prompt = "\nAre you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"
    
    @staticmethod
    def reset_success(chat_color: str, chat_number: int):
        """Print reset success message."""
        PersonaFormatter._output(f"\033[1m{chat_color}CHAT {chat_number}\033[0m persona reset successfully!")
    
    @staticmethod
    def operation_cancelled():
        """Print operation cancelled message."""
        PersonaFormatter._output("Operation cancelled.")
    
    @staticmethod
    def save_name_required_error():
        """Print error that name is required for saving."""
        PersonaFormatter._output("[1;31mError:[0m You must set a persona name before saving.")
        PersonaFormatter._output("Use [1m/persona.name <n>[0m to set a name first.")
    
    @staticmethod
    def save_no_content_warning():
        """Print warning that there's no content to save."""
        PersonaFormatter._output("[1;33mWarning:[0m Persona has no slot content to save.")
    
    @staticmethod
    def load_success(name: str, chat_color: str):
        """Print load success message."""
        PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m Persona '{name}' loaded successfully!")
    
    @staticmethod
    def show_persona_list(personas: list, chat_color: str):
        """Show list of saved personas."""
        PersonaFormatter._output(f"\n\033[1m{chat_color}|\033[0m \033[1m{chat_color}SAVED PERSONAS\033[0m\n")
        
        if not personas:
            PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m [37mNo saved personas found.[0m\n")
        else:
            for i, persona in enumerate(personas, 1):
                PersonaFormatter._output(f"\033[1m{chat_color}|\033[0m {i:>2}. [37m{persona}[0m")
            PersonaFormatter._output("")  # Empty line for spacing
    
    @staticmethod
    def delete_warning(name: str):
        """Show delete warning and get confirmation."""
        PersonaFormatter._output(f"\n[1;33mWarning:[0m This will [1;31mDELETE[0m saved persona file '{name}'.")
        PersonaFormatter._output("This action cannot be undone.")
        prompt = "\nAre you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"
    
    @staticmethod
    def delete_cancelled():
        """Print delete cancelled message."""
        PersonaFormatter._output("Delete operation cancelled.")
    
    @staticmethod
    def reset_cancelled():
        """Print reset cancelled message."""
        PersonaFormatter._output("Reset operation cancelled.")
    
    @staticmethod
    def keyboard_interrupt_error():
        """Print keyboard interrupt error."""
        PersonaFormatter._output("\nOperation cancelled.")
    
    @staticmethod
    def generic_error(message: str):
        """Print generic error message."""
        PersonaFormatter._output(f"[1;31mError:[0m {message}")
