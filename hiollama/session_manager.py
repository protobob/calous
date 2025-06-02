"""Chat session management for Hi, Ollama!"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from rich import print
import os
from .types import ActionType, CommandResult  # Import from types instead
from .utils import get_chat_color, print_rainbow_header, format_message_preview
from .config import ConfigManager
from .constants import DEFAULT_NUM_CHATS, TWIST_PREVIEW_LENGTH, SWITCH_PREVIEW_LENGTH
from .unified_logger import unified_logger

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from .app import HiOllamaChat

class ChatSessionManager:    
    def __init__(self, num_chats: Optional[int] = None):  # Remove hardcoded default
        self.chats: List['HiOllamaChat'] = []
        self.active_chat_index = 0
        # Use constant for default
        self.num_chats = num_chats if num_chats is not None else DEFAULT_NUM_CHATS
        self._initialize_chats()
        
        # Log session start
        model = ConfigManager.get_global_config().get("selected_model", "unknown")
        unified_logger.log_session_start(self.num_chats, model)
          
    def _initialize_chats(self):
        """Initialize all chat instances."""
        # Import here to avoid circular import
        from .app import HiOllamaChat
        self.chats = [HiOllamaChat(i) for i in range(self.num_chats)]  # Use parameter
        
        # Configure chat instances - REMOVED CIRCULAR REFERENCE
        for i, chat in enumerate(self.chats):
            chat.active_chat_index = i
            chat.session_manager = self  # Give chats reference to session manager only
        
        # Share plugin manager across all chats
        if self.chats:
            plugin_manager = self.chats[0].plugin_manager
            for chat in self.chats[1:]:
                chat.plugin_manager = plugin_manager
    
    def get_active_chat(self) -> 'HiOllamaChat':
        """Get the currently active chat instance."""
        return self.chats[self.active_chat_index]
    
    def get_all_chats(self) -> List['HiOllamaChat']:
        """Get all chat instances - for use by other components."""
        return self.chats
    def switch_to_chat(self, target_index: Optional[int] = None) -> bool:
        """Switch to specified chat or next chat if no index provided."""
        previous_chat_index = self.active_chat_index
        
        if target_index is None:
            # Default behavior: switch to next chat (cycling)
            target_index = (self.active_chat_index + 1) % self.num_chats
        
        if 0 <= target_index < self.num_chats:
            if target_index != previous_chat_index:
                # Log the channel switch
                unified_logger.log_channel_switch(previous_chat_index, target_index, "manual")
            self.active_chat_index = target_index
            return True
        
        print(f"\n[bold red]Error:[/bold red] Invalid chat number. Available chats: 1-{self.num_chats}")
        return False
    def twist_to_chat(self, content: str, target_index: Optional[int] = None) -> bool:
        """Twist content to specified chat or next chat if no index provided."""
        source_chat_index = self.active_chat_index
        
        if target_index is None:
            # Default behavior: twist to next chat
            target_index = (self.active_chat_index + 1) % self.num_chats

        if not (0 <= target_index < self.num_chats):
            print(f"\n[bold red]Error:[/bold red] Invalid chat number. Available chats: 1-{self.num_chats}")
            return False

        # Log the twist action
        unified_logger.log_twist_action(source_chat_index, target_index, content)

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
        
        # Use module-level imported get_chat_color
        target_chat_color = get_chat_color(target_index)
        target_chat.ui.display_chat_context(target_chat_color)

        # Display the twist content indicator with SOURCE CHAT COLOR
        # Truncate content and make it single line
        twist_preview = content.replace('\n', ' ').strip()
        if len(twist_preview) > TWIST_PREVIEW_LENGTH:
            twist_preview = twist_preview[:TWIST_PREVIEW_LENGTH] + "..."

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
        
        # Log the model change
        unified_logger.log_model_change(new_model, updated_count)
        
        return updated_count    
    
    def add_chat(self) -> bool:
        """Add a new chat session dynamically."""
        from .app import HiOllamaChat
        
        # Create new chat instance
        new_chat_index = self.num_chats
        new_chat = HiOllamaChat(new_chat_index)
        new_chat.session_manager = self
        
        # Share plugin manager from existing chats
        if self.chats and hasattr(self.chats[0], 'plugin_manager'):
            new_chat.plugin_manager = self.chats[0].plugin_manager
        
        # Add to chats list
        self.chats.append(new_chat)
        
        # Update num_chats
        self.num_chats += 1
        
        # Update global config
        ConfigManager.update_global_config({"num_chats": self.num_chats})
        
        # Log the addition
        unified_logger.log_channel_switch(-1, new_chat_index, "addchat")
        
        print(f"[bold green]✓[/bold green] Chat {new_chat_index + 1} added successfully!")
        return True
        
    def remove_chat(self, target_index: int) -> bool:
        """Remove a chat session dynamically."""
        if target_index < 0 or target_index >= self.num_chats:
            return False
        
        # Save the chat's configuration before removing it
        chat_to_remove = self.chats[target_index]
        try:
            chat_to_remove.save_config()
            print(f"[grey70]Saved configuration for Chat {target_index + 1}[/grey70]")
        except Exception as e:
            print(f"[bold yellow]Warning:[/bold yellow] Could not save config for Chat {target_index + 1}: {e}")
        
        # Remove the chat from the list
        removed_chat = self.chats.pop(target_index)
        
        # Update num_chats
        self.num_chats -= 1
        
        # Update global config (preserves chat configs in unified file)
        ConfigManager.update_global_config({"num_chats": self.num_chats})
        
        # Adjust active_chat_index if necessary
        if self.active_chat_index >= self.num_chats:
            # If we removed the last chat and it was active, switch to the new last chat
            self.active_chat_index = self.num_chats - 1
        elif self.active_chat_index > target_index:
            # If we removed a chat before the active one, adjust the index
            self.active_chat_index -= 1
        
        # Update instance indices for remaining chats
        for i, chat in enumerate(self.chats):
            chat.instance_index = i
            chat.active_chat_index = i
        
        # Log the removal
        unified_logger.log_channel_switch(target_index, -1, "removechat")
        
        print(f"[bold green]✓[/bold green] Chat {target_index + 1} removed successfully!")
        print(f"[grey70]Configuration preserved in unified config file.[/grey70]")
        return True

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
        
        elif result.action == ActionType.ADDCHAT:
            if self.add_chat():
                # Switch to the new chat and display its context
                self.active_chat_index = self.num_chats - 1
                self._display_chat_context()
        
        elif result.action == ActionType.REMOVECHAT:
            data = result.data or {}
            target_index = data.get('target_index', self.num_chats - 1)
            if self.remove_chat(target_index):
                # Display context for the current active chat
                self._display_chat_context()
    
        # CONTINUE action requires no special handling
        return True
    
    def _display_chat_context(self, clear_screen=True):
        """Display context for the active chat."""
        active_chat = self.get_active_chat()
        if clear_screen:
            active_chat.ui.clear_screen()
        
        # Use module-level imported get_chat_color
        chat_color = get_chat_color(self.active_chat_index)
        active_chat.ui.display_chat_context(chat_color)    
    
    def save_all_configs(self):
        """Save configurations for all chat instances."""
        print("\n[bold]Exiting and saving configurations.[/bold]")
        
        # Log session end
        unified_logger.log_session_end()
        
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