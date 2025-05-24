"""Entry point for the hiollama package."""
from .app import HiOllamaChat
from rich import print

def main():
    # Create two chat instances
    chats = [HiOllamaChat(), HiOllamaChat()]
    active_index = 0
    
    for chat in chats:
        # Pass active index and chat list to both instances
        chat.active_chat_index = active_index
        chat.chat_instances = chats
    
    print("\n[bold]Created two chat instances. Use '/switch' to toggle between them.\nUse '/twist' to send an AI response from one chat as a prompt to the other chat.[/bold]")
    # Display initial context by simulating a switch to chat 0
    chats[active_index].ui.clear_screen()
    chat_color = "green"  # Chat 0 is green
    
    # Print HIOLLAMA! in rainbow colors - fixed markup
    print("\n[bold][red]H[/red][orange1]I[/orange1][yellow1]O[/yellow1][green]L[/green][blue]L[/blue][purple]A[/purple][magenta]M[/magenta][red]A[/red][orange1]![/orange1][/bold]\n")
    
    # Print chat header with color
    print(f"[bold {chat_color}]CHAT {active_index + 1}_____________[/bold {chat_color}]")
    
    # Print this chat's system prompt with grey color and colored bar
    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]SYS: {chats[active_index].system_prompt['content']}[/grey42]")
    
    # First run flag - already showed header so set to False
    first_run = False
    
    try:
        # Start with chat[0]
        while True:
            chats[active_index].active_chat_index = active_index
            chats[active_index].run(break_on_switch=True, skip_header=(not first_run))
            first_run = False  # After first run, don't show header again
            # Toggle between 0 and 1
            active_index = 1 - active_index
            # Clear screen when switching
            chats[active_index].ui.clear_screen()
            
            # Color based on chat number
            chat_color = "green" if active_index == 0 else "blue"
            
            # Print HIOLLAMA! in rainbow colors - fixed markup
            print("\n[bold][red]H[/red][orange1]I[/orange1][yellow1]O[/yellow1][green]L[/green][blue]L[/blue][purple]A[/purple][magenta]M[/magenta][red]A[/red][orange1]![/orange1][/bold]\n")
            
            # Print chat header with color
            print(f"[bold {chat_color}]CHAT {active_index + 1}_____________[/bold {chat_color}]")
            # Print this chat's system prompt with grey color and colored bar
            print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]SYS: {chats[active_index].system_prompt['content']}[/grey42]")
            
            # Add a more robust check for twist_content
            twist_content = None
            if hasattr(chats[active_index], 'twist_content') and chats[active_index].twist_content:
                twist_content = chats[active_index].twist_content
            
            # Find the last user message and assistant response
            last_user_msg = None
            last_assistant_msg = None
            
            if len(chats[active_index].chat_history.history) >= 2:
                # First find the last assistant message
                for i, msg in enumerate(reversed(chats[active_index].chat_history.history)):
                    if msg.get("role") == "assistant":
                        last_assistant_msg = msg
                        # Now look for the user message that came before it
                        for umsg in reversed(chats[active_index].chat_history.history[:-(i+1)]):
                            if umsg.get("role") == "user":
                                last_user_msg = umsg
                                break
                        break
                
                # Print the user's last message with grey color and colored bar
                if last_user_msg:
                    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]YOU: {last_user_msg.get('content')}[/grey42]")
                # Print the AI's response with grey color and colored bar
                if last_assistant_msg:
                    print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]LLM: {last_assistant_msg.get('content')}[/grey42]")
                
            # If we have twist content, send it to the model
            if twist_content:
                # Determine source chat color (opposite of current chat color)
                source_chat_index = 1 - active_index
                source_chat_color = "green" if source_chat_index == 0 else "blue"
                try:
                    # Add a header similar to the CHAT header style
                    print(f"\n[bold {source_chat_color}]TWIST FROM CHAT {source_chat_index + 1}_____________[/bold {source_chat_color}]")
                    
                    # Format the preview to make it clear it came from another chat, using the vertical bar style
                    if twist_content is not None and isinstance(twist_content, str):
                        # Get just the first line (or up to 100 chars if no newline)
                        first_line = twist_content.split('\n')[0]
                        preview = first_line[:100] + ('...' if len(first_line) > 100 or len(twist_content.split('\n')) > 1 else '')
                        # Use same format as SYS/YOU/LLM messages with grey text and colored bar
                        print(f"[bold {source_chat_color}]|[/bold {source_chat_color}] [grey42]{preview}[/grey42]")
                    else:
                        print(f"[bold {source_chat_color}]|[/bold {source_chat_color}] [grey42][italic]Empty content[/italic][/grey42]")
                    
                    # Add a small separator underneath
                    print()
                    
                except Exception as e:
                    print(f"[bold red]Error formatting twist content preview: {e}[/bold red]")
                
                # Use the handle_regular_input method to ensure consistent processing
                if twist_content is not None:
                    chats[active_index].handle_regular_input(twist_content)
                # Clear the twist content regardless
                chats[active_index].twist_content = None
                chats[1-active_index].twist_content = None
                # Also reset any switch_requested flags
                chats[active_index].switch_requested = False
                chats[1-active_index].switch_requested = False
    
    except KeyboardInterrupt:
        print("\n[bold]Exiting and saving configurations.[/bold]")
        for chat in chats:
            try:
                chat.save_config()
            except:
                pass

if __name__ == "__main__":
    main()