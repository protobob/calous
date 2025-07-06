"""
Plugin configuration for CALOUS.

This module controls which plugins are enabled in the CALOUS application.
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
#ENABLED_PLUGINS = None  # Enable all
#ENABLED_PLUGINS = set() # Disable All
#ENABLED_PLUGINS = {"calculator_plugin", "mcp_client_plugin"}
ENABLED_PLUGINS = {"groq_provider", "dice_roller"}

