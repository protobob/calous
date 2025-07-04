"""Prompt command formatters module."""
from ...constants import Colors
from ..formatters import CommandFormatter


class PromptFormatter(CommandFormatter):
    """Formatter for prompt command output."""
    
    @staticmethod
    def _output(message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        session_manager = CommandFormatter._get_session_manager()
        if session_manager and session_manager.socket_mode and session_manager.current_connection:
            session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
    @staticmethod
    def prompt_slot_error(max_prompts: int):
        """Print error for invalid prompt slot."""
        PromptFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Slot must be between 1 and {max_prompts}.")
    
    @staticmethod
    def prompt_empty_error():
        """Print error for empty prompt text."""
        PromptFormatter._output(f"{Colors.ERROR}Error:{Colors.RESET} Prompt text cannot be empty.")
    
    @staticmethod
    def prompt_set_success(slot: int):
        """Print successful prompt set message."""
        PromptFormatter._output(f"Prompt{slot} set successfully!")
    
    @staticmethod
    def prompt_not_set_error(slot: int):
        """Print error for accessing unset prompt."""
        PromptFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Prompt{slot} is not set.")
    
    @staticmethod
    def using_prompt(chat_color: str, slot: int, prompt_text: str):
        """Print message when using a prompt."""
        PromptFormatter._output(f"\n\033[1m{chat_color}|\033[0m Using Prompt {slot}: [37m{prompt_text}[0m")
    
    @staticmethod
    def show_single_prompt(chat_color: str, active_chat_index: int, slot: int, prompt_content: str):
        """Print a single prompt with styling."""
        PromptFormatter._output(f"\n\033[1m{chat_color}|\033[0m \033[1m{chat_color}CHAT {active_chat_index + 1} PROMPT {slot}\033[0m\n")
        PromptFormatter._output(f"\033[1m{chat_color}|\033[0m {'Prompt Content:':<20} [37m{prompt_content}[0m\n")
    
    @staticmethod
    def show_prompt_list_header(chat_color: str, active_chat_index: int):
        """Print header for prompt list."""
        PromptFormatter._output(f"\n\033[1m{chat_color}|\033[0m \033[1m{chat_color}CHAT {active_chat_index + 1} SAVED PROMPTS\033[0m\n")
    
    @staticmethod
    def show_prompt_list_item(chat_color: str, slot: int, content: str):
        """Print a prompt list item."""
        if content:
            PromptFormatter._output(f"\033[1m{chat_color}|\033[0m {'Prompt' + str(slot) + ':':<20} [37m{content}[0m")
        else:
            PromptFormatter._output(f"\033[1m{chat_color}|\033[0m {'Prompt' + str(slot) + ':':<20} [37m(not set)[0m")
    
    @staticmethod
    def add_spacing():
        """Add spacing after output."""
        PromptFormatter._output("")
