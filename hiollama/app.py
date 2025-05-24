"""Main application class for Hi, Ollama!"""
import ollama
from rich.prompt import Prompt
from rich import print

from .config import ConfigManager
from .commands import CommandHandler
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction
from .utils import reset_switch_flags
from .constants import DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS

class HiOllamaChat:
    def __init__(self, instance_index):
        self.instance_index = instance_index
        self.config = ConfigManager.load_config(instance_index)
        
        # Initialize attributes from config
        self.selected_model = self.config.get("selected_model", DEFAULT_MODEL)
        self.verbosity = self.config.get("verbosity", True)
        self.think_filtering = self.config.get("think_filtering", True)
        self.MAX_HISTORY = self.config.get("MAX_HISTORY", DEFAULT_MAX_HISTORY)
        self.system_prompt = {
            "role": "system",
            "content": self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)})
          
        # For multi-instance support
        self.active_chat_index = instance_index
        self.chat_instances = []
        self.twist_content = None  # Initialize twist_content attribute
        self.switch_requested = False  # Initialize switch_requested flag
        
        # Initialize components
        self.ui = UIManager(self)
        self.chat_history = ChatHistory(self, instance_index)
        self.model = ModelInteraction(self)
        self.commands = CommandHandler(self)
        
        # Initialize last response attribute
        self.last_response = None  # Add this to store the last response
        
    def save_config(self):
        """Save the current configuration."""
        self.config["selected_model"] = self.selected_model
        self.config["verbosity"] = self.verbosity
        self.config["think_filtering"] = self.think_filtering
        self.config["MAX_HISTORY"] = self.MAX_HISTORY
        self.config["system_prompt"] = self.system_prompt["content"]
        self.config["logging_enabled"] = self.logging_enabled
        self.config["prompts"] = self.prompts
        ConfigManager.save_config(self.config, self.instance_index)
            
    def handle_regular_input(self, user_input):
        """Process regular user input (non-commands)."""
        try:
            response = self.ui.run_with_spinner(self.model.talk_to_model, user_input)
            self.model.process_response(user_input, response)
        except ollama.APIError as e:
            print(f"Ollama API Error: {e}")
        except Exception as e:
            print(f"Model Error: {e}")
    
        # Add the user message to history after sending to the model
        self.chat_history.add_message("user", user_input)
        
    def run(self, break_on_switch=False, skip_header=False):
        """Main application loop."""
        # Display header if needed
        if not skip_header:
            self._display_header()

        try:            
            while True:
                # Get user input
                user_input = self._get_user_input()
                
                # Handle chat switching
                if self._should_switch(user_input, break_on_switch):
                    return
                    
                # Handle commands
                if self._handle_commands(user_input, break_on_switch):
                    continue
                    
                # Process regular input
                self.handle_regular_input(user_input)

        except KeyboardInterrupt:
            print("\nInterrupted. Saving config and exiting.")
            raise  # Re-raise to let main handle the exit
        finally:
            self.save_config()

    def _display_header(self):
        """Display the application header."""
        self.ui.clear_screen()
        print(f"\nLoaded config from: {ConfigManager.get_config_path(self.instance_index)}\n")
        print(f"Model: {self.selected_model}")

    def _get_user_input(self):
        """Get user input with prompt."""
        prompt_text = self.ui.generate_prompt_text()
        return Prompt.ask(prompt_text).strip()

    def _should_switch(self, user_input, break_on_switch):
        """Check if we should switch chats."""
        if not break_on_switch:
            return False
            
        # Check if switch requested programmatically
        if getattr(self, 'switch_requested', False):
            reset_switch_flags(self)
            return True
            
        # Check for direct switch command
        if user_input.strip().lower() == "/switch":
            return True
            
        # Check for twist command
        if user_input.strip().lower() == "/twist":
            self.commands.cmd_twist()
            return True
            
        return False

    def _handle_commands(self, user_input, break_on_switch):
        """Handle command processing."""
        # Special check for quit command
        if user_input.strip().lower() == "/quit":
            self.commands.cmd_quit()
            return True
        
        # Process other commands
        if self.commands.parse_and_execute(user_input):
            if break_on_switch and getattr(self, 'switch_requested', False):
                return True
            return True
            
        return False
