"""Entry point for the hiollama package."""
from .app import HiOllamaChat
from rich import print
from typing import List, Dict, Any, Optional
from .utils import (
    get_chat_color, print_chat_header, print_message_with_bar, 
    reset_twist_content, reset_switch_flags, format_message_preview
)

def setup_chats() -> List[HiOllamaChat]:
    """Initialize and configure chat instances."""
    chats = [HiOllamaChat(0), HiOllamaChat(1)]
    
    # Configure chat instances - no need for separate registration
    for i, chat in enumerate(chats):
        chat.active_chat_index = i
        chat.chat_instances = chats
    
    return chats

def find_last_messages(chat: HiOllamaChat) -> Dict[str, Any]:
    """Find the last user and assistant messages in chat history."""
    last_messages = {}

    # Iterate through the chat history in reverse to find the last assistant and user messages
    for msg in reversed(chat.chat_history.history):
        if not last_messages.get('assistant') and msg.get("role") == "assistant":
            last_messages['assistant'] = msg
        elif not last_messages.get('user') and msg.get("role") == "user":
            last_messages['user'] = msg
        
        # Stop searching if both messages are found
        if last_messages.get('assistant') and last_messages.get('user'):
            break

    return last_messages

def display_chat_context(chat: HiOllamaChat, chat_color: str) -> None:
    """Display the current chat context (system prompt, history)."""
    # Print system prompt with grey color and colored bar
    print_message_with_bar(chat_color, "SYS", chat.system_prompt['content'])
    
    # Display the last user message
    last_messages = find_last_messages(chat)
    if last_messages.get('user'):
            print_message_with_bar(chat_color, "YOU", last_messages['user'].get('content', ''))
    
    # Display the last assistant message
    last_messages = find_last_messages(chat)
    if last_messages.get('assistant'):
        print_message_with_bar(chat_color, "LLM", last_messages['assistant'].get('content', ''))

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

def main():
    """Main application entry point."""
    # Setup chat instances
    chats = setup_chats()
    active_index = 0

    # Display welcome message and initial context
    initialize_chat_context(chats, active_index)

    try:
        # Main application loop
        run_application_loop(chats, active_index)
    except KeyboardInterrupt:
        save_all_configs(chats)


def initialize_chat_context(chats: List[HiOllamaChat], active_index: int) -> None:
    """Initialize and display the context for the active chat."""
    chats[active_index].ui.clear_screen()
    chat_color = print_chat_header(active_index)
    display_chat_context(chats[active_index], chat_color)


def run_application_loop(chats: List[HiOllamaChat], active_index: int) -> None:
    """Run the main application loop."""
    first_run = True
    while True:
        # Run the active chat until a switch is requested
        chats[active_index].active_chat_index = active_index
        chats[active_index].run(break_on_switch=True, skip_header=(not first_run))
        first_run = False

        # Switch to the other chat
        active_index = 1 - active_index

        # Display the new active chat's context
        initialize_chat_context(chats, active_index)

        # Handle any twisted content
        handle_twist_if_present(chats, active_index)


def handle_twist_if_present(chats: List[HiOllamaChat], active_index: int) -> None:
    """Check for and handle any twisted content."""
    twist_content = getattr(chats[active_index], 'twist_content', None)
    if twist_content:
        handle_twist_content(chats[active_index], 1 - active_index)