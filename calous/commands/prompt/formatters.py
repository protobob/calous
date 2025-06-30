"""Prompt command formatters module."""
from rich import print as rich_print
from ...constants import Colors
from ..formatters import CommandFormatter


class PromptFormatter(CommandFormatter):
    """Formatter for prompt command output."""
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
    @staticmethod
    def prompt_slot_error(max_prompts: int):
        """Print error for invalid prompt slot."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Slot must be between 1 and {max_prompts}.")
    
    @staticmethod
    def prompt_empty_error():
        """Print error for empty prompt text."""
        CommandFormatter._output(f"{Colors.ERROR}Error:{Colors.RESET} Prompt text cannot be empty.")
    
    @staticmethod
    def prompt_set_success(slot: int):
        """Print successful prompt set message."""
        CommandFormatter._output(f"Prompt{slot} set successfully!")
    
    @staticmethod
    def prompt_not_set_error(slot: int):
        """Print error for accessing unset prompt."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Prompt{slot} is not set.")
    
    @staticmethod
    def using_prompt(chat_color: str, slot: int, prompt_text: str):
        """Print message when using a prompt."""
        CommandFormatter._output(f"\n[bold {chat_color}]|[/bold {chat_color}] Using Prompt {slot}: [grey70]{prompt_text}[/grey70]")
    
    @staticmethod
    def show_single_prompt(chat_color: str, active_chat_index: int, slot: int, prompt_content: str):
        """Print a single prompt with styling."""
        CommandFormatter._output(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {active_chat_index + 1} PROMPT {slot}[/bold {chat_color}]\n")
        CommandFormatter._output(f"[bold {chat_color}]|[/bold {chat_color}] {'Prompt Content:':<20} [grey70]{prompt_content}[/grey70]\n")
    
    @staticmethod
    def show_prompt_list_header(chat_color: str, active_chat_index: int):
        """Print header for prompt list."""
        CommandFormatter._output(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {active_chat_index + 1} SAVED PROMPTS[/bold {chat_color}]\n")
    
    @staticmethod
    def show_prompt_list_item(chat_color: str, slot: int, content: str):
        """Print a prompt list item."""
        if content:
            CommandFormatter._output(f"[bold {chat_color}]|[/bold {chat_color}] {'Prompt' + str(slot) + ':':<20} [grey70]{content}[/grey70]")
        else:
            CommandFormatter._output(f"[bold {chat_color}]|[/bold {chat_color}] {'Prompt' + str(slot) + ':':<20} [grey70](not set)[/grey70]")
