"""Utility functions for the hiollama package."""
from rich import print
from typing import Optional, Dict, Any
from .constants import CHAT_COLORS, MAX_PREVIEW_LENGTH, RAINBOW_COLORS, RAINBOW_TEXT, HEADER_SEPARATOR
from pathlib import Path

def get_chat_color(chat_index: int) -> str:
    """Return the color for a specific chat index."""
    return CHAT_COLORS.get(chat_index, "white")

def format_message_preview(content: Any, max_length: int = MAX_PREVIEW_LENGTH) -> str:
    """Format a message for preview display."""
    if not content:
        return "[Empty]"
    
    if not isinstance(content, str):
        content = str(content)
        
    first_line = content.split('\n')[0]
    has_more = len(first_line) > max_length or len(content.split('\n')) > 1
    return first_line[:max_length] + ('...' if has_more else '')

def print_rainbow_header() -> None:
    """Print the HIOLLAMA! header in rainbow colors."""
    rainbow_text = ""
    for i, char in enumerate(RAINBOW_TEXT):
        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
        rainbow_text += f"[{color}]{char}[/{color}]"
        
    print(f"\n[bold]{rainbow_text}[/bold]\n")

def print_chat_header(chat_index: int) -> str:
    """Print the chat header and return the chat color."""
    chat_color = get_chat_color(chat_index)
    
    # Print rainbow header
    print_rainbow_header()
    
    # Print chat header with color
    print(f"[bold {chat_color}]CHAT {chat_index + 1}{HEADER_SEPARATOR}[/bold {chat_color}]")
    
    return chat_color

def print_message_with_bar(chat_color: str, role: str, content: Any) -> None:
    """Print a message with a colored vertical bar and role prefix."""
    preview = format_message_preview(content)
    prefix = f"{role}: " if role else ""
    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]{prefix}{preview}[/grey42]")

def reset_switch_flags(app_instance) -> None:
    """Reset switch flags on all chat instances."""
    app_instance.switch_requested = False
    
    if hasattr(app_instance, 'chat_instances') and app_instance.chat_instances:
        for chat in app_instance.chat_instances:
            if hasattr(chat, 'switch_requested'):
                chat.switch_requested = False
                
def reset_twist_content(app_instance) -> None:
    """Reset twist content on all chat instances."""
    app_instance.twist_content = None
    
    if hasattr(app_instance, 'chat_instances') and app_instance.chat_instances:
        for chat in app_instance.chat_instances:
            if hasattr(chat, 'twist_content'):
                chat.twist_content = None

# Keeping existing class for file loading
class Utils:
    @staticmethod
    def load_file_as_prompt(filepath, instructions=""):
        """Load a file and format it as a prompt with instructions."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
            
        content = path.read_text(errors='replace')
        if instructions:
            return f"{instructions}\n\n```{path.suffix[1:] if path.suffix else ''}\n{content}\n```"
        else:
            return content