"""Plugin command services module."""
from typing import Optional, Dict, Any, List
import os
from pathlib import Path


class PluginResult:
    """Result object for plugin operations."""
    
    def __init__(self, success: bool, error_message: str = "", 
                 cancelled: bool = False):
        self.success = success
        self.error_message = error_message
        self.cancelled = cancelled


class PluginService:
    """Service for plugin operations."""
    
    @staticmethod
    def get_plugin_manager(app) -> Optional[Any]:
        """Get the plugin manager from the app."""
        if not hasattr(app, 'plugin_manager') or not app.plugin_manager:
            return None
        return app.plugin_manager
    
    @staticmethod
    def get_all_plugins(app) -> List[Any]:
        """Get all plugins from the plugin manager."""
        plugin_manager = PluginService.get_plugin_manager(app)
        if not plugin_manager:
            return []
        return plugin_manager.get_all_plugins()
    
    @staticmethod
    def get_function_calling_plugins(app) -> List[Any]:
        """Get all function calling plugins from the plugin manager."""
        plugin_manager = PluginService.get_plugin_manager(app)
        if not plugin_manager:
            return []
        return plugin_manager.get_function_calling_plugins()
    
    @staticmethod
    def get_plugin_by_name(app, name: str) -> Optional[Any]:
        """Get a plugin by name."""
        plugin_manager = PluginService.get_plugin_manager(app)
        if not plugin_manager:
            return None
        return plugin_manager.get_plugin(name)
    
    @staticmethod
    def get_plugin_dir(app) -> Optional[Path]:
        """Get the plugin directory from the app."""
        # Get the base calous package directory
        calous_dir = Path(__file__).parent.parent.parent
        
        # The plugins directory is directly under the calous package
        plugins_dir = calous_dir / 'plugins'
        
        if not plugins_dir.exists():
            return None
            
        return plugins_dir
    
    @staticmethod
    def reload_plugins(app) -> PluginResult:
        """Reload all plugins from disk."""
        plugin_manager = PluginService.get_plugin_manager(app)
        if not plugin_manager:
            return PluginResult(success=False, error_message="Plugin system not available")
        
        plugin_dir = PluginService.get_plugin_dir(app)
        if not plugin_dir:
            return PluginResult(success=False, error_message="Could not locate plugin directory")
        
        if not plugin_dir.exists():
            return PluginResult(
                success=False, 
                error_message=f"Plugin directory does not exist: {plugin_dir}"
            )
        
        try:
            # Check for the reload_plugins method
            if not hasattr(plugin_manager, 'reload_plugins'):
                # Fallback to discover_and_load_plugins if reload_plugins doesn't exist
                plugin_manager.plugins.clear()  # Clear existing plugins
                plugin_manager.discover_and_load_plugins(plugin_dir)
            else:
                plugin_manager.reload_plugins(plugin_dir)
                
            return PluginResult(success=True)
        except Exception as e:
            return PluginResult(success=False, error_message=f"Failed to reload plugins: {str(e)}")
