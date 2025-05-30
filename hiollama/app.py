"""Main application class for Hi, Ollama!"""
from rich.prompt import Prompt
from rich import print

from .config import ConfigManager
from .commands.handler import AdvancedCommandHandler  # Fixed import path
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction
from .constants import DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS
from .types import CommandResult, ActionType
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_manager import ChatSessionManager

class HiOllamaChat:
    
    def __init__(self, instance_index):
        self.instance_index = instance_index
        
        # Load configs from unified system
        self.config = ConfigManager.get_chat_config(instance_index)
        global_config = ConfigManager.get_global_config()
        
        # Initialize attributes from config
        self.selected_model = global_config.get("selected_model", DEFAULT_MODEL)
        self.verbosity = self.config.get("verbosity", True)
        self.think_filtering = self.config.get("think_filtering", True)
        self.MAX_HISTORY = self.config.get("MAX_HISTORY", DEFAULT_MAX_HISTORY)
        self.system_prompt = {
            "role": "system",
            "content": self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)})
          
        # For multi-instance support (simplified - no circular references)
        self.active_chat_index = instance_index
        self.session_manager = None  # Will be set by SessionManager
        
        # Initialize components
        self.ui = UIManager(self)
        self.chat_history = ChatHistory(self, instance_index)
        self.model = ModelInteraction(self)
        self.commands = AdvancedCommandHandler(self)  # Direct instantiation
        
        # Initialize last response attribute
        self.last_response = None
    
    def update_global_model(self, new_model):
        """Update the selected model globally across all instances via session manager."""
        # Delegate to session manager which has access to all chats
        if self.session_manager:
            return self.session_manager.update_global_model(new_model)
        else:
            # Fallback for standalone operation (shouldn't happen in normal use)
            ConfigManager.update_global_config({"selected_model": new_model})
            self.selected_model = new_model
            return 1
    def save_config(self):
        """Save the current configuration."""
        # Update instance-specific config
        chat_config = {
            "verbosity": self.verbosity,
            "think_filtering": self.think_filtering,
            "MAX_HISTORY": self.MAX_HISTORY,
            "system_prompt": self.system_prompt["content"],
            "logging_enabled": self.logging_enabled,
            "prompts": self.prompts
        }
        ConfigManager.update_chat_config(self.instance_index, chat_config)
        
        # Update global config with current model
        ConfigManager.update_global_config({"selected_model": self.selected_model})
    
    def process_input(self, user_input: str):
        """Process user input and return a CommandResult."""
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
            response = self.model.talk_to_model(user_input)
            # Streaming handles its own processing including history and logging
        except Exception as e:
            print(f"[bold red]Error processing input:[/bold red] {e}")
