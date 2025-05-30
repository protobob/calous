"""Command system module."""
from .registry import registry
from .handler import AdvancedCommandHandler
from .types import CommandDefinition, CommandCategory

# Import all command modules to register them
from . import general
from . import navigation
from . import model
from . import prompt
from . import history
from . import file

__all__ = ['registry', 'AdvancedCommandHandler', 'CommandDefinition', 'CommandCategory']