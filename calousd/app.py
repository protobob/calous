"""Main application class for Hi, Ollama!"""

import socket
import sys
import os
import json
import signal
from datetime import datetime

from .config import ConfigManager
from .commands.handler import AdvancedCommandHandler  # Fixed import path
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction
from .persona import Persona
from .constants import DEFAULT_MODEL, DEFAULT_PROVIDER, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS, DEFAULT_NUM_CTX, DEFAULT_TEMPERATURE
from .types import CommandResult, ActionType
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_manager import ChatSessionManager
    from .plugins.manager import PluginManager

SOCKET_PATH = "/tmp/calous.sock"

class Chat:

    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode and self.session_manager.current_connection:
            self.session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
    def __init__(self, instance_index):
        self.instance_index = instance_index
        # Load configs from unified system
        self.config = ConfigManager.get_chat_config(instance_index)
        global_config = ConfigManager.get_global_config()
        self.selected_model = global_config.get("selected_model", DEFAULT_MODEL)
        self.selected_provider = global_config.get("selected_provider", DEFAULT_PROVIDER)
        self.verbosity = self.config.get("verbosity", True)

        # Initialize persona system
        self.persona = Persona()
        persona_data = self.config.get("persona", {})
        if persona_data:
            self.persona.load_from_data(persona_data)
        else:
            old_system_prompt = self.config.get("system_prompt", "")
            if old_system_prompt and old_system_prompt != DEFAULT_SYSTEM_PROMPT:
                self.persona.set_slot(0, old_system_prompt)

        self.system_prompt = {
            "role": "system",
            "content": self.persona.get_combined_prompt()
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.thinking_enabled = self.config.get("thinking_enabled", False)
        self.history_enabled = self.config.get("history_enabled", True)
        self.num_ctx = ConfigManager.get_global_num_ctx()
        self.temperature = self.config.get("temperature", DEFAULT_TEMPERATURE)
        self.keep_alive = ConfigManager.get_keep_alive()  # Load global keep_alive setting
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)})
        self.active_chat_index = instance_index
        self.session_manager: Optional['ChatSessionManager'] = None
        self.plugin_manager: Optional['PluginManager'] = None  # Will be set by session manager

        self.ui = UIManager(self)
        self.chat_history = ChatHistory(self, instance_index)
        self.model = ModelInteraction(self)
        self.commands = AdvancedCommandHandler(self)
        self.last_response = None

    def update_global_model(self, new_model):
        if self.session_manager:
            return self.session_manager.update_global_model(new_model)
        else:
            ConfigManager.update_global_config({"selected_model": new_model})
            self.selected_model = new_model
            return 1

    def update_global_num_ctx(self, new_num_ctx):
        if self.session_manager:
            return self.session_manager.update_global_num_ctx(new_num_ctx)
        else:
            ConfigManager.set_global_num_ctx(new_num_ctx)
            self.num_ctx = new_num_ctx
            return 1

    def save_config(self):
        self.system_prompt["content"] = self.persona.get_combined_prompt()
        chat_config = {
            "verbosity": self.verbosity,
            "persona": self.persona.to_dict(),
            "logging_enabled": self.logging_enabled,
            "thinking_enabled": self.thinking_enabled,
            "history_enabled": self.history_enabled,
            "temperature": self.temperature,
            "prompts": self.prompts
        }
        ConfigManager.update_chat_config(self.instance_index, chat_config)
        ConfigManager.update_global_config({"selected_model": self.selected_model})

    def process_input(self, user_input: str):
        if user_input.startswith('/'):
            return self.commands.parse_and_execute(user_input)
        if self.plugin_manager:
            processed_input = self.plugin_manager.apply_pre_message_hooks(user_input, context={})
        else:
            processed_input = user_input
        if processed_input != user_input and processed_input.startswith("[shell:"):
            self.ui.display_shell_output(processed_input)
            return CommandResult(ActionType.CONTINUE)
        # Process regular input (non-commands)
        self.handle_regular_input(processed_input)
        return CommandResult(ActionType.CONTINUE)

    def handle_regular_input(self, user_input, images=None):
        self.chat_history.add_message("user", user_input)
        try:
            response = self.model.talk_to_model(user_input, images=images)
            # Store the last response for twist operations
            self.last_response = response
        except Exception as e:
            self._output(f"[1;31mError processing input:[0m {e}")

    def confirm(self, question, default=True):
        """Prompt the user for confirmation via socket or direct input."""
        default_choice = "y" if default else "n"
        response = input(f"{question} (y/n) [{default_choice}]: ")
        return response.lower() == "y" if response else default
