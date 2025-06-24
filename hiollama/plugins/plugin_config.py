"""
Plugin configuration for HiOllama.

This module controls which plugins are enabled in the HiOllama application.
By default, all plugins are enabled. To restrict which plugins can be loaded,
modify the ENABLED_PLUGINS set below.

Examples:
    # Enable only specific plugins
    ENABLED_PLUGINS = {"dice_roller", "web_search"}
    
    # Enable all plugins (default behavior)
    ENABLED_PLUGINS = None
    
    # Disable all plugins completely
    ENABLED_PLUGINS = set()
"""

# Set of plugin file names (without .py extension) that should be enabled
# Set to None to enable all plugins
# Set to empty set() to disable all plugins
#ENABLED_PLUGINS = None  # {"dice_roller"}
ENABLED_PLUGINS = set()

