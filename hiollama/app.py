"""Main application class for Hi, Ollama!"""
from rich.prompt import Prompt
from rich import print

from .config import ConfigManager
from .commands.handler import AdvancedCommandHandler  # Fixed import path
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction
from .persona import Persona
from .constants import DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS, DEFAULT_NUM_CTX, DEFAULT_TEMPERATURE
from .types import CommandResult, ActionType
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_manager import ChatSessionManager

class Chat:
    
    def __init__(self, instance_index):
        self.instance_index = instance_index
          # Load configs from unified system
        self.config = ConfigManager.get_chat_config(instance_index)
        global_config = ConfigManager.get_global_config()        # Initialize attributes from config
        self.selected_model = global_config.get("selected_model", DEFAULT_MODEL)
        self.verbosity = self.config.get("verbosity", True)
        
        # Initialize persona system (replaces old system_prompt)
        self.persona = Persona()
        
        # Load persona from config if exists
        persona_data = self.config.get("persona", {})
        if persona_data:
            self.persona.load_from_data(persona_data)
        else:
            # Migrate old system_prompt to persona if it exists
            old_system_prompt = self.config.get("system_prompt", "")
            if old_system_prompt and old_system_prompt != DEFAULT_SYSTEM_PROMPT:
                self.persona.set_slot(0, old_system_prompt)
        
        # Keep system_prompt for backwards compatibility in model interaction
        self.system_prompt = {
            "role": "system", 
            "content": self.persona.get_combined_prompt()
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.thinking_enabled = self.config.get("thinking_enabled", False)  # Default to False for clean output
        self.history_enabled = self.config.get("history_enabled", True)  # Default to True for normal operation
        self.num_ctx = ConfigManager.get_global_num_ctx()  # Use global context window
        self.temperature = self.config.get("temperature", DEFAULT_TEMPERATURE)
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)})# For multi-instance support (simplified - no circular references)
        self.active_chat_index = instance_index
        self.session_manager = None  # Will be set by SessionManager
        self.plugin_manager = None  # Will be injected by SessionManager
        
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
    
    def update_global_num_ctx(self, new_num_ctx):
        """Update the context window globally across all instances via session manager."""
        # Delegate to session manager which has access to all chats
        if self.session_manager:
            return self.session_manager.update_global_num_ctx(new_num_ctx)
        else:
            # Fallback for standalone operation (shouldn't happen in normal use)
            ConfigManager.set_global_num_ctx(new_num_ctx)
            self.num_ctx = new_num_ctx
            return 1
    
    def save_config(self):
        """Save the current configuration."""        
        # Update system_prompt content from persona before saving
        self.system_prompt["content"] = self.persona.get_combined_prompt()
          # Update instance-specific config        
        chat_config = {
            "verbosity": self.verbosity,
            "persona": self.persona.to_dict(),  # Save persona instead of system_prompt
            "logging_enabled": self.logging_enabled,
            "thinking_enabled": self.thinking_enabled,
            "history_enabled": self.history_enabled,
            "temperature": self.temperature,
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
    
    def handle_regular_input(self, user_input, images=None):
        """Process regular user input (non-commands)."""
        # Add the user message to history BEFORE sending to the model
        self.chat_history.add_message("user", user_input)
    
        try:
            response = self.model.talk_to_model(user_input, images=images)
            # Streaming handles its own processing including history and logging
        except Exception as e:
            print(f"[bold red]Error processing input:[/bold red] {e}")
