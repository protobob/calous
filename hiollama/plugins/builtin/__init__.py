"""Built-in plugins for HiOllama.

Note: Plugins are actually discovered and loaded dynamically by scanning Python files
in this directory. The plugin manager looks for classes that inherit from PluginBase.

To control which plugins are enabled:
1. Edit hiollama/plugins/plugin_config.py
2. Set ENABLED_PLUGINS to a set of plugin names you want to enable
   Example: ENABLED_PLUGINS = {"dice_roller"}
3. Set ENABLED_PLUGINS = None to enable all plugins (default)
4. Set ENABLED_PLUGINS = set() to disable all plugins completely

The classes below are primarily for reference and direct imports when needed.


from .dice_roller import DiceRollerPlugin

# Export plugin classes for direct imports
__all__ = [
    'DiceRollerPlugin',
    # Add other plugin class names here as they're created
]
"""