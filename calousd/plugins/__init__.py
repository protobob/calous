"""
CALOUS Plugin System

This module provides a comprehensive plugin architecture for CALOUS,
enabling extensible functionality through various plugin types.
"""

from .base import PluginBase, FunctionCallingPlugin, CommandPlugin, HookPlugin, PluginCapability
from .manager import PluginManager
# Import plugin config to make it available as part of the plugins package
from . import plugin_config

__all__ = [
    'PluginBase',
    'FunctionCallingPlugin', 
    'CommandPlugin',
    'HookPlugin',
    'PluginCapability',
    'PluginManager',
    'plugin_config'
]