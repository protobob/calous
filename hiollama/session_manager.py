"""Chat session management for Hi, Ollama!"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from rich import print
import os
from .app import HiOllamaChat
from .utils import get_chat_color, print_rainbow_header, format_message_preview
from .config import ConfigManager

class ActionType(Enum):
    CONTINUE = "continue"
    SWITCH = "switch"
    TWIST = "twist"
    QUIT = "quit"

@dataclass
class CommandResult:
    action: ActionType
    data: Optional[Dict[str, Any]] = None

class ChatSessionManager:
    def __init__(self, num_chats: Optional[int] = None):
        self.chats: List[HiOllamaChat] = []
        self.active_chat_index = 0
        # Use config value if num_chats not explicitly provided
        self.num_chats = num_chats if num_chats is not None else ConfigManager.get_num_chats()
        self._initialize_chats()
        
    def _initialize_chats(self):
        """Initialize all chat instances."""
        self.chats = [HiOllamaChat(i) for i in range(self.num_chats)]
        
        # Configure chat instances - REMOVED CIRCULAR REFERENCE
        for i, chat in enumerate(self.chats):
            chat.active_chat_index = i
            # REMOVED: chat.chat_instances = self.chats  # This was the circular reference
            chat.session_manager = self  # Give chats reference to session manager only
    
    def get_active_chat(self) -> HiOllamaChat:
        """Get the currently active chat instance."""
        return self.chats[self.active_chat_index]
    
    def get_all_chats(self) -> List[HiOllamaChat]:
        """Get all chat instances - for use by other components."""
        return self.chats
    
    def switch_to_chat(self, target_index: Optional[int] = None) -> bool:
        """Switch to specified chat or next chat if no index provided."""
        if target_index is None:
            # Default behavior: switch to next chat (cycling)
            target_index = (self.active_chat_index + 1) % self.num_chats
        
        if 0 <= target_index < self.num_chats:
            self.active_chat_index = target_index
            return True
        
        print(f"\n[bold red]Error:[/bold red] Invalid chat number. Available chats: 1-{self.num_chats}")
        return False
    
    def twist_to_chat(self, content: str, target_index: Optional[int] = None) -> bool:
        """Twist content to specified chat or next chat if no index provided."""
        if target_index is None:
            # Default behavior: twist to next chat
            target_index = (self.active_chat_index + 1) % self.num_chats

        if not (0 <= target_index < self.num_chats):
            print(f"\n[bold red]Error:[/bold red] Invalid chat number. Available chats: 1-{self.num_chats}")
            return False

        # Display twist preview from source chat
        source_color = get_chat_color(self.active_chat_index)
        target_color = get_chat_color(target_index)

        preview = format_message_preview(content, 50)
        print(f"[bold {source_color}]↪ Twisting to Chat {target_index + 1}: "
              f"[/bold {source_color}][italic {target_color}]\"{preview}\"[/italic {target_color}]")

        # Switch to target chat FIRST
        self.active_chat_index = target_index

        # Clear screen and show FULL context for the target chat (including chat summary)
        target_chat = self.chats[target_index]
        target_chat.ui.clear_screen()
        
        # Use the full display_chat_context which includes both overview AND chat summary
        target_chat.ui.display_chat_context("")

        # Display the twist content indicator with SOURCE CHAT COLOR
        # Truncate content to 100 characters and make it single line
        twist_preview = content.replace('\n', ' ').strip()
        if len(twist_preview) > 100:
            twist_preview = twist_preview[:100] + "..."

        # Use SOURCE_COLOR instead of target_color for the TWIST CONTENT display
        print(f"\n[bold {source_color}]|[/bold {source_color}] [bold {source_color}]TWIST CONTENT:[/bold {source_color}]")
        print(f"[bold {source_color}]|[/bold {source_color}] [grey70]{twist_preview}[/grey70]\n")

        # Send the content as a prompt (which will trigger AI response)
        target_chat.handle_regular_input(content)

        return True
    
    def update_global_model(self, new_model):
        """Update the selected model globally across all instances."""
        # Update global config
        ConfigManager.update_global_config({"selected_model": new_model})
        
        # Update all chat instances
        updated_count = 0
        for chat in self.chats:
            chat.selected_model = new_model
            updated_count += 1
        
        return updated_count
    
    def process_command_result(self, result: CommandResult) -> bool:
        """Process a command result and take appropriate action.
        
        Returns:
            True if the main loop should continue, False if it should exit
        """
        if result.action == ActionType.QUIT:
            self.save_all_configs()
            return False
        
        elif result.action == ActionType.SWITCH:
            data = result.data or {}
            target_index = data.get('target_chat')
            if self.switch_to_chat(target_index):
                self._display_chat_context()
        
        elif result.action == ActionType.TWIST:
            data = result.data or {}
            content = data.get('content', '')
            target_index = data.get('target_chat')
            
            if content:
                self.twist_to_chat(content, target_index)
                # Remove the duplicate _display_chat_context() call here
                # twist_to_chat() already handles the display
    
        # CONTINUE action requires no special handling
        return True
    
    def _display_chat_context(self, clear_screen=True):
        """Display context for the active chat."""
        active_chat = self.get_active_chat()
        if clear_screen:
            active_chat.ui.clear_screen()
        active_chat.ui.display_chat_context("")

    def save_all_configs(self):
        """Save configurations for all chat instances."""
        print("\n[bold]Exiting and saving configurations.[/bold]")
        for chat in self.chats:
            try:
                chat.save_config()
            except Exception as e:
                print(f"\nError saving config: {e}")
    
    def run(self):
        """Run the main application loop."""
        # Display startup header
        self._display_startup_header()
        
        # Show initial context WITHOUT clearing the screen
        self._display_chat_context(clear_screen=False)
        
        try:
            while True:
                active_chat = self.get_active_chat()
                
                # Get user input
                user_input = active_chat.ui.get_user_input()
                
                # Process input and get result
                result = active_chat.process_input(user_input)
                
                # Handle the result
                if not self.process_command_result(result):
                    break  # Exit the application
                    
        except KeyboardInterrupt:
            self.save_all_configs()
            import os
            os._exit(0)
    
    def _display_startup_header(self):
        """Display the application startup header."""
        os.system('cls' if os.name == 'nt' else 'clear')
        from .utils import print_rainbow_header
        print_rainbow_header()