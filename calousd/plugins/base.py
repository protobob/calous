"""Base classes for CALOUS plugin system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class PluginCapability(Enum):
    """Types of capabilities a plugin can provide."""
    FUNCTION_CALLING = "function_calling"  # LLM tool use
    COMMANDS = "commands"  # User commands
    HOOKS = "hooks"  # Message processing hooks
    UI = "ui"  # Custom display/formatting
    PROVIDER = "provider"  # LLM provider (e.g., Groq, Claude)


class PluginBase(ABC):
    """Base class for all CALOUS plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.capabilities: List[PluginCapability] = []
        self.loaded = False
        self.error: Optional[str] = None
    
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
    
    @property
    def is_active(self) -> bool:
        """Check if plugin is currently active/enabled."""
        return self.loaded and self.error is None


class FunctionCallingPlugin(PluginBase):
    """Base class for plugins that provide LLM function calling capabilities."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        super().__init__(name, version, description)
        self.capabilities.append(PluginCapability.FUNCTION_CALLING)
    
    @abstractmethod
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Return OpenAI function calling schemas for this plugin."""
        pass
    
    def execute_function(self, function_name: str, **kwargs) -> str:
        """Execute a function call and return the result."""
        # Default implementation calls call_function and converts to JSON string
        import json
        result = self.call_function(function_name, kwargs)
        return json.dumps(result, ensure_ascii=False)
    
    @abstractmethod
    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call and return the result as a dictionary."""
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


class ProviderPlugin(PluginBase):
    """Base class for plugins that provide LLM provider capabilities."""
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        super().__init__(name, version, description)
        self.capabilities.append(PluginCapability.PROVIDER)
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this provider (e.g., 'groq', 'claude')."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider."""
        pass
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, Any]], model: str, 
                         stream: bool = True, **kwargs) -> Any:
        """Generate a response using this provider's API."""
        pass
    
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Return True if this provider supports streaming responses."""
        pass
    
    @abstractmethod
    def supports_function_calling(self) -> bool:
        """Return True if this provider supports function calling."""
        pass
    
    def validate_model(self, model: str) -> bool:
        """Check if the given model is valid for this provider."""
        return model in self.get_available_models()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Return information about this provider."""
        return {
            "name": self.get_provider_name(),
            "models": self.get_available_models(),
            "streaming": self.supports_streaming(),
            "function_calling": self.supports_function_calling()
        }
