"""Main application class for Hi, Ollama!"""
from rich.prompt import Prompt
from rich import print

from .config import ConfigManager
from .commands import CommandHandler
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction
from .constants import DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS

class HiOllamaChat:
    # Class-level global configuration
    _global_config = None
    
    def __init__(self, instance_index):
        self.instance_index = instance_index
        self.config = ConfigManager.load_config(instance_index)
        
        # Load global config if not already loaded
        if HiOllamaChat._global_config is None:
            HiOllamaChat._global_config = ConfigManager.load_global_config()
        
        # Initialize attributes from config
        self.selected_model = HiOllamaChat._global_config.get("selected_model", DEFAULT_MODEL)
        self.verbosity = self.config.get("verbosity", True)
        self.think_filtering = self.config.get("think_filtering", True)
        self.MAX_HISTORY = self.config.get("MAX_HISTORY", DEFAULT_MAX_HISTORY)
        self.system_prompt = {
            "role": "system",
            "content": self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)})
          
        # For multi-instance support (simplified - no switch state)
        self.active_chat_index = instance_index
        self.chat_instances = []
        self.session_manager = None  # Will be set by SessionManager
        
        # Initialize components
        self.ui = UIManager(self)
        self.chat_history = ChatHistory(self, instance_index)
        self.model = ModelInteraction(self)
        self.commands = CommandHandler(self)
        
        # Initialize last response attribute
        self.last_response = None
    
    def update_global_model(self, new_model):
        """Update the selected model globally across all instances."""
        if HiOllamaChat._global_config is None:
            HiOllamaChat._global_config = ConfigManager.load_global_config()
        
        HiOllamaChat._global_config["selected_model"] = new_model
        ConfigManager.save_global_config(HiOllamaChat._global_config)
        
        # Update all existing instances using chat_instances
        updated_count = 0
        for instance in self.chat_instances:
            if instance is not None:
                instance.selected_model = new_model
                updated_count += 1
        
        return updated_count
        
    def save_config(self):
        """Save the current configuration."""
        # Save instance-specific config (excluding selected_model)
        self.config["verbosity"] = self.verbosity
        self.config["think_filtering"] = self.think_filtering
        self.config["MAX_HISTORY"] = self.MAX_HISTORY
        self.config["system_prompt"] = self.system_prompt["content"]
        self.config["logging_enabled"] = self.logging_enabled
        self.config["prompts"] = self.prompts
        ConfigManager.save_config(self.config, self.instance_index)
        
        # Save global config (selected_model)
        if HiOllamaChat._global_config is not None:
            HiOllamaChat._global_config["selected_model"] = self.selected_model
            ConfigManager.save_global_config(HiOllamaChat._global_config)
    
    def process_input(self, user_input: str):
        """Process user input and return a CommandResult."""
        from .session_manager import CommandResult, ActionType
        
        # Handle commands
        if user_input.startswith('/'):
            return self.commands.parse_and_execute(user_input)
        
        # Handle regular input
        self.handle_regular_input(user_input)
        return CommandResult(ActionType.CONTINUE)
    
    def handle_regular_input(self, user_input):
        """Process regular user input (non-commands)."""
        # Add the user message to history BEFORE sending to the model
        self.chat_history.add_message("user", user_input)
    
        try:
            response = self.ui.run_with_spinner(self.model.talk_to_model, user_input)
            self.model.process_response(user_input, response)
        except Exception as e:
            print(f"Model Error: {e}")
