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
    
    print("\n[bold]Created two chat instances. Use '/switch' to toggle between them.[/bold]")
    
    # Display initial context by simulating a switch to chat 0
    chats[active_index].ui.clear_screen()
    chat_color = "green"  # Chat 0 is green
    
    # Print chat header with color
    print(f"\n[bold {chat_color}]CHAT {active_index + 1}_____________[/bold {chat_color}]")
    
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
            
            # Print chat header with color
            print(f"\n[bold {chat_color}]CHAT {active_index + 1}_____________[/bold {chat_color}]")
            
            # Print this chat's system prompt with grey color and colored bar
            print(f"[bold {chat_color}]|[/bold {chat_color}] [grey42]SYS: {chats[active_index].system_prompt['content']}[/grey42]")
            
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
    
    except KeyboardInterrupt:
        print("\n[bold]Exiting and saving configurations.[/bold]")
        for chat in chats:
            try:
                chat.save_config()
            except:
                pass

if __name__ == "__main__":
    main()