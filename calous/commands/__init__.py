"""Command system module."""
from .registry import registry
from .handler import AdvancedCommandHandler

# Import all command modules to trigger @registry.register decorators
from .alias import commands as alias_commands
from .sys import commands as sys_commands
from .model import commands as model_commands
from .chat import commands as chat_commands
from .history import commands as history_commands
from .log import commands as log_commands
from .file import commands as file_commands
from .prompt import commands as prompt_commands
from .plugin import commands as plugin_commands
from .persona import commands as persona_commands

__all__ = ['AdvancedCommandHandler']