"""Entry point for the hiollama package."""
from .app import HiOllamaChat
from rich import print
from typing import List, Dict, Any, Optional
import os
from .utils import (
    get_chat_color, print_chat_header, print_message_with_bar, 
    reset_twist_content, reset_switch_flags, format_message_preview,
    print_rainbow_header
)
from .constants import DEFAULT_NUM_CHATS
from .config import ConfigManager

def display_startup_header():
    """Display the application startup header."""
    # Clear screen first
    os.system('cls' if os.name == 'nt' else 'clear')
    print_rainbow_header()
    #print(f"Loaded config from: {ConfigManager.get_config_path(0)}\n")

def setup_chats(num_chats: int = DEFAULT_NUM_CHATS) -> List[HiOllamaChat]:
    """Initialize and configure chat instances."""
    chats = [HiOllamaChat(i) for i in range(num_chats)]
    
    # Configure chat instances
    for i, chat in enumerate(chats):
        chat.active_chat_index = i
        chat.chat_instances = chats
    
    return chats

def handle_twist_content(chat: HiOllamaChat, source_index: int) -> None:
    """Process and display twisted content from another chat."""
    twist_content = chat.twist_content
    
    if not twist_content:
        return
        
    # Determine source chat color
    source_chat_color = get_chat_color(source_index)
    
    try:
        # Add a header for the twisted content
        print(f"\n[bold {source_chat_color}]TWIST FROM CHAT {source_index + 1}:[/bold {source_chat_color}]")
        
        # Display content preview using the utility function
        if isinstance(twist_content, str):
            print_message_with_bar(source_chat_color, "", twist_content)
        else:
            print_message_with_bar(source_chat_color, "", "[italic]Empty content[/italic]")
        
        print()  # Add spacing
        
        # Send the twist content to the model
        if twist_content is not None:
            chat.handle_regular_input(twist_content)
            
    except Exception as e:
        print(f"[bold red]Error handling twist content: {e}[/bold red]")
    
    # Clear twist content and switch flags from both chats
    reset_twist_content(chat)
    reset_switch_flags(chat)

def save_all_configs(chats: List[HiOllamaChat]) -> None:
    """Save configurations for all chat instances."""
    print("\n[bold]Exiting and saving configurations.[/bold]")
    for chat in chats:
        try:
            chat.save_config()
        except Exception as e:
            print(f"Error saving config: {e}")

def initialize_chat_context(chats: List[HiOllamaChat], active_index: int) -> None:
    """Initialize and display the context for the active chat."""
    chats[active_index].ui.clear_screen()
    chats[active_index].ui.display_chat_context("")  # Pass empty string since header is handled internally

def run_application_loop(chats: List[HiOllamaChat], active_index: int) -> None:
    """Run the main application loop."""
    first_run = True
    while True:
        # For first run, show context without clearing screen (preserve startup header)
        if first_run:
            chats[active_index].ui.display_chat_context("")  # Pass empty string since header is handled internally
        
        # Run the active chat until a switch is requested
        chats[active_index].active_chat_index = active_index
        chats[active_index].run(break_on_switch=True, skip_header=True)
        first_run = False

        # Switch to the other chat
        active_index = 1 - active_index

        # Display the new active chat's context (this will clear screen for subsequent switches)
        initialize_chat_context(chats, active_index)

        # Handle any twisted content
        handle_twist_if_present(chats, active_index)

def handle_twist_if_present(chats: List[HiOllamaChat], active_index: int) -> None:
    """Check for and handle any twisted content."""
    twist_content = getattr(chats[active_index], 'twist_content', None)
    if twist_content:
        handle_twist_content(chats[active_index], 1 - active_index)

def main():
    """Main application entry point."""
    # Display startup header
    display_startup_header()
    
    # Setup chat instances
    chats = setup_chats()
    active_index = 0

    try:
        # Main application loop - first run will show initial context after header
        run_application_loop(chats, active_index)
    except KeyboardInterrupt:
        save_all_configs(chats)