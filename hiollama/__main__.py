"""Entry point for the hiollama package."""
from .app import HiOllamaChat
from rich import print
from typing import List, Optional

def setup_chats() -> List[HiOllamaChat]:
    """Initialize and configure chat instances."""
    chats = [HiOllamaChat(), HiOllamaChat()]
    
    # Configure chat instances
    for i, chat in enumerate(chats):
        chat.active_chat_index = i
        chat.chat_instances = chats
    
    return chats

def display_welcome() -> None:
    """Display welcome message for the application."""
    print("\n[bold]Created two chat instances. Use '/switch' to toggle between them.\n"
          "Use '/twist' to send an AI response from one chat as a prompt to the other chat.[/bold]")

def display_chat_header(chat_index: int) -> str:
    """Display the chat header and return the chat color."""
    chat_color = "green" if chat_index == 0 else "blue"
    
    # Print HIOLLAMA! in rainbow colors
    print("\n[bold][red]H[/red][orange1]I[/orange1][yellow1]O[/yellow1][green]L[/green]"
          "[blue]L[/blue][purple]A[/purple][magenta]M[/magenta][red]A[/red][orange1]![/orange1][/bold]\n")
    
    # Print chat header with color
    print(f"[bold {chat_color}]CHAT {chat_index + 1}_____________[/bold {chat_color}]")
    
    return chat_color

def display_chat_context(chat: HiOllamaChat, chat_color: str) -> None:
    """Display the current chat context (system prompt, history)."""
    # Print system prompt with grey color and colored bar
    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]SYS: {chat.system_prompt['content']}[/grey42]")
    
    # Find and display recent messages if they exist
    last_messages = find_last_messages(chat)
    if last_messages.get('user'):
        display_message_preview(chat_color, "YOU", last_messages['user'])
        
    if last_messages.get('assistant'):
        display_message_preview(chat_color, "LLM", last_messages['assistant'])

def find_last_messages(chat):
    """Find the last user and assistant messages in chat history."""
    last_messages = {}
    
    if len(chat.chat_history.history) >= 2:
        # Find the last assistant message first
        for i, msg in enumerate(reversed(chat.chat_history.history)):
            if msg.get("role") == "assistant":
                last_messages['assistant'] = msg
                
                # Then look for the last user message before it
                for umsg in reversed(chat.chat_history.history[:-(i+1)]):
                    if umsg.get("role") == "user":
                        last_messages['user'] = umsg
                        break
                break
    
    return last_messages

def display_message_preview(chat_color, role, message):
    """Display a preview of a message."""
    content = message.get('content', '')
    first_line = content.split('\n')[0]
    preview = first_line[:100] + ('...' if len(first_line) > 100 or len(content.split('\n')) > 1 else '')
    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]{role}: {preview}[/grey42]")

def handle_twist_content(chat: HiOllamaChat, source_index: int) -> None:
    """Process and display twisted content from another chat."""
    twist_content = chat.twist_content
    
    if not twist_content:
        return
        
    # Determine source chat color
    source_chat_color = "green" if source_index == 0 else "blue"
    
    try:
        # Add a header for the twisted content
        print(f"\n[bold {source_chat_color}]TWIST FROM CHAT {source_index + 1}:[/bold {source_chat_color}]")
        
        # Display content preview
        if isinstance(twist_content, str):
            first_line = twist_content.split('\n')[0]
            preview = first_line[:100] + ('...' if len(first_line) > 100 or len(twist_content.split('\n')) > 1 else '')
            print(f"[bold {source_chat_color}]|[/bold {source_chat_color}] [grey42]{preview}[/grey42]")
        else:
            print(f"[bold {source_chat_color}]|[/bold {source_chat_color}] [grey42][italic]Empty content[/italic][/grey42]")
        
        print()  # Add spacing
        
        # Send the twist content to the model
        if twist_content is not None:
            chat.handle_regular_input(twist_content)
            
    except Exception as e:
        print(f"[bold red]Error handling twist content: {e}[/bold red]")
    
    # Clear twist content from both chats
    chat.twist_content = None
    chat.chat_instances[source_index].twist_content = None
    
    # Reset switch flags
    chat.switch_requested = False
    chat.chat_instances[source_index].switch_requested = False

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
    
    # Display welcome and initial context
    display_welcome()
    chats[active_index].ui.clear_screen()
    chat_color = display_chat_header(active_index)
    display_chat_context(chats[active_index], chat_color)
    
    try:
        # Main application loop
        first_run = False  # Already showed header
        while True:
            # Run the active chat until switch is requested
            chats[active_index].active_chat_index = active_index
            chats[active_index].run(break_on_switch=True, skip_header=(not first_run))
            first_run = False
            
            # Switch to the other chat
            active_index = 1 - active_index
            
            # Display the new active chat's context
            chats[active_index].ui.clear_screen()
            chat_color = display_chat_header(active_index)
            display_chat_context(chats[active_index], chat_color)
            
            # Check for and handle any twisted content
            twist_content = getattr(chats[active_index], 'twist_content', None)
            if twist_content:
                handle_twist_content(chats[active_index], 1 - active_index)
                
    except KeyboardInterrupt:
        save_all_configs(chats)

if __name__ == "__main__":
    main()