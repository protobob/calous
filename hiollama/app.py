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
            
    def run(self):
        """Main application loop."""
        self.ui.clear_screen()
        print(f"\nLoaded config from: {ConfigManager.CONFIG_PATH}\n")
        print(f"Model: {self.selected_model}")

        try:
            while True:
                prompt_text = self.ui.generate_prompt_text()
                user_input = Prompt.ask(prompt_text).strip()

                if self.commands.parse_and_execute(user_input):
                    continue
                else:
                    self.handle_regular_input(user_input)

        except KeyboardInterrupt:
            print("\nInterrupted. Saving config and exiting.")
        finally:
            self.save_config()
