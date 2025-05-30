"""Utility functions for the hiollama package."""
from rich import print
from typing import Optional, Dict, Any
from .constants import MAX_PREVIEW_LENGTH, RAINBOW_COLORS, EXTENDED_RAINBOW_COLORS, RAINBOW_TEXT, HEADER_SEPARATOR, APP_VERSION
from pathlib import Path

def get_chat_color(chat_index: int) -> str:
    """Return the color for a specific chat index using extended rainbow progression."""
    return EXTENDED_RAINBOW_COLORS[chat_index % len(EXTENDED_RAINBOW_COLORS)]

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
    """Print the HIOLLAMA! header in rainbow colors with the version below."""
    rainbow_text = ""
    for i, char in enumerate(RAINBOW_TEXT):
        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
        rainbow_text += f"[{color}]{char}[/{color}]"
    
    # Print the rainbow header
    print(f"\n[bold]{rainbow_text}[/bold]")
    
    # Print the version below the header in darker grey
    print(f"[grey30]v.{APP_VERSION}[/grey30]\n")

def print_chat_header(chat_index: int) -> str:
    """Print the chat header and return the chat color."""
    chat_color = get_chat_color(chat_index)
    
    # Print chat header with color
    print(f"[bold {chat_color}]CHAT {chat_index + 1}{HEADER_SEPARATOR}[/bold {chat_color}]")
    
    return chat_color

def print_message_with_bar(chat_color: str, role: str, content: Any) -> None:
    """Print a message with a colored vertical bar and role prefix."""
    preview = format_message_preview(content)
    prefix = f"{role}: " if role else ""
    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]{prefix}{preview}[/grey42]")

def find_last_messages(chat_history) -> Dict[str, Any]:
    """Find the last user and assistant messages in chat history."""
    last_messages = {}

    # Iterate through the chat history in reverse to find the last assistant and user messages
    for msg in reversed(chat_history.history):
        if not last_messages.get('assistant') and msg.get("role") == "assistant":
            last_messages['assistant'] = msg
        elif not last_messages.get('user') and msg.get("role") == "user":
            last_messages['user'] = msg
        
        # Stop searching if both messages are found
        if last_messages.get('assistant') and last_messages.get('user'):
            break

    return last_messages

# Keeping existing class for file loading
class Utils:
    @staticmethod
    def load_file_as_prompt(filepath, instructions=""):
        """Load a file and format it as a prompt with instructions."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"\nFile not found: {filepath}")
            
        content = path.read_text(errors='replace')
        if instructions:
            return f"{instructions}\n\n```{path.suffix[1:] if path.suffix else ''}\n{content}\n```"
        else:
            return content