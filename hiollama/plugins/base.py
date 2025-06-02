"""Base classes for HiOllama plugin system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class PluginCapability(Enum):
    """Types of capabilities a plugin can provide."""
    FUNCTION_CALLING = "function_calling"  # LLM tool use
    COMMANDS = "commands"  # User commands
    HOOKS = "hooks"  # Message processing hooks
    UI = "ui"  # Custom display/formatting


class PluginBase(ABC):
    """Base class for all HiOllama plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.capabilities: List[PluginCapability] = []
        self.loaded = False
        self.error = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    def cleanup(self) -> None:
        """Clean up plugin resources. Override if needed."""
        pass
    
    def get_capabilities(self) -> List[PluginCapability]:
        """Return list of capabilities this plugin provides."""
        return self.capabilities.copy()


class FunctionCallingPlugin(PluginBase):
    """Base class for plugins that provide LLM function calling capabilities."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        super().__init__(name, version, description)
        self.capabilities.append(PluginCapability.FUNCTION_CALLING)
    
    @abstractmethod
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Return OpenAI function calling schemas for this plugin."""
        pass
    
    @abstractmethod
    def execute_function(self, function_name: str, **kwargs) -> str:
        """Execute a function call and return the result."""
        pass
    
    def get_function_names(self) -> List[str]:
        """Return list of function names this plugin provides."""
        schemas = self.get_function_schemas()
        return [schema['function']['name'] for schema in schemas]


class CommandPlugin(PluginBase):
    """Base class for plugins that provide user commands."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        super().__init__(name, version, description)
        self.capabilities.append(PluginCapability.COMMANDS)
    
    @abstractmethod
    def get_commands(self) -> Dict[str, Callable]:
        """Return dict of command_name -> command_function mappings."""
        pass
    
    @abstractmethod
    def get_command_help(self) -> Dict[str, str]:
        """Return dict of command_name -> help_text mappings."""
        pass


class HookPlugin(PluginBase):
    """Base class for plugins that provide message processing hooks."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        super().__init__(name, version, description)
        self.capabilities.append(PluginCapability.HOOKS)
    
    def pre_message_hook(self, user_input: str, context: Dict[str, Any]) -> str:
        """Process user input before sending to LLM. Return modified input."""
        return user_input
    
    def post_message_hook(self, response: str, context: Dict[str, Any]) -> str:
        """Process LLM response before displaying. Return modified response."""
        return response
