"""Command system module."""
from .registry import registry
from .handler import AdvancedCommandHandler

# Import all command modules to trigger @registry.register decorators
from . import general
from . import navigation  
from . import model
from . import prompt
from . import history
from . import file
from . import plugins
from . import persona

__all__ = ['AdvancedCommandHandler']