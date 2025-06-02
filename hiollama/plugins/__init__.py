"""
HiOllama Plugin System

This module provides a comprehensive plugin architecture for HiOllama,
enabling extensible functionality through various plugin types.
"""

from .base import PluginBase, FunctionCallingPlugin, CommandPlugin, HookPlugin, PluginCapability
from .manager import PluginManager

__all__ = [
    'PluginBase',
    'FunctionCallingPlugin', 
    'CommandPlugin',
    'HookPlugin',
    'PluginCapability',
    'PluginManager'
]