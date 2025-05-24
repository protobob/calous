"""Main application class for Hi, Ollama!"""
import ollama
from rich.prompt import Prompt
from rich import print

from .config import ConfigManager
from .commands import CommandHandler
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction

class HiOllamaChat:
    def __init__(self):
        self.config = ConfigManager.load_config()
        
        # Initialize attributes from config
        self.selected_model = self.config.get("selected_model", "qwen3:0.6B")
        self.verbosity = self.config.get("verbosity", True)
        self.think_filtering = self.config.get("think_filtering", True)
        self.MAX_HISTORY = self.config.get("MAX_HISTORY", 20)
        self.system_prompt = {
            "role": "system",
            "content": self.config.get("system_prompt", "You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code.")
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, 11)})
          # For multi-instance support
        self.active_chat_index = 0
        self.chat_instances = []
        self.twist_content = None  # Initialize twist_content attribute
        self.switch_requested = False  # Initialize switch_requested flag
        
        # Initialize components
        self.ui = UIManager(self)
        self.chat_history = ChatHistory(self)
        self.model = ModelInteraction(self)
        self.commands = CommandHandler(self)
        
    def save_config(self):
        """Save the current configuration."""
        self.config["selected_model"] = self.selected_model
        self.config["verbosity"] = self.verbosity
        self.config["think_filtering"] = self.think_filtering
        self.config["MAX_HISTORY"] = self.MAX_HISTORY
        self.config["system_prompt"] = self.system_prompt["content"]
        self.config["logging_enabled"] = self.logging_enabled
        self.config["prompts"] = self.prompts
        ConfigManager.save_config(self.config)
            
    def handle_regular_input(self, user_input):
        """Process regular user input (non-commands)."""
        # Add the user message to history before sending to the model
        self.chat_history.add_message("user", user_input)  
    
        try:
            response = self.ui.run_with_spinner(self.model.talk_to_model, user_input)
            self.model.process_response(user_input, response)
        except ollama.APIError as e:
            print(f"Ollama API Error: {e}")
        except Exception as e:
            print(f"Model Error: {e}")
            
    def run(self, break_on_switch=False, skip_header=False):
        """Main application loop."""
        if not skip_header:
            self.ui.clear_screen()
            print(f"\nLoaded config from: {ConfigManager.CONFIG_PATH}\n")
            print(f"Model: {self.selected_model}")

        try:            
            while True:
                prompt_text = self.ui.generate_prompt_text()
                user_input = Prompt.ask(prompt_text).strip()
                  # Check if we need to switch chats (only happens when switching from the outside)
                if break_on_switch and getattr(self, 'switch_requested', False):
                    # Reset the flag for next time
                    self.switch_requested = False
                    # Also make sure any chat instances we're aware of have their flags reset
                    if hasattr(self, 'chat_instances') and self.chat_instances:
                        for chat in self.chat_instances:
                            if hasattr(chat, 'switch_requested'):
                                chat.switch_requested = False
                    return  # Exit this run loop to switch to another instance
                
                # Check for direct switch command
                if break_on_switch and user_input.strip().lower() == "/switch":
                    return  # Exit this run loop to switch to another instance
                    # Check for direct twist command 
                if break_on_switch and user_input.strip().lower() == "/twist":
                    # Handle directly here to bypass command processing
                    self.commands.cmd_twist()
                    return  # Exit this run loop to switch to another instance
                
                # Special check for quit command (don't continue processing after quit)
                if user_input.strip().lower() == "/quit":
                    self.commands.cmd_quit()  # This will call exit() directly
                    continue  # Skip further processing (this line never executes due to exit())
                
                if self.commands.parse_and_execute(user_input):
                    # If the command handler sets switch_requested flag, handle it
                    if break_on_switch and getattr(self, 'switch_requested', False):
                        return  # Exit this run loop to switch to another instance
                    continue
                else:
                    self.handle_regular_input(user_input)

        except KeyboardInterrupt:
            print("\nInterrupted. Saving config and exiting.")
            raise  # Re-raise to let main handle the exit
        finally:
            self.save_config()
