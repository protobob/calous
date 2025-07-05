"""Plugin manager for CALOUS plugin system."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from ..unified_logger import unified_logger
from .base import PluginBase, PluginCapability, FunctionCallingPlugin, CommandPlugin, HookPlugin, ProviderPlugin


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client via callback or log it."""
        # Try to use callback if available (set by session manager)
        if hasattr(self, '_output_callback') and self._output_callback:
            self._output_callback(message, message_type)
        else:
            # Fall back to logging for daemon mode
            # Strip Rich markup for clean logs
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            rich_markup = re.compile(r'\[/?[^\]]*\]')
            clean_message = ansi_escape.sub('', message)
            clean_message = rich_markup.sub('', clean_message)
            unified_logger._write_log_entry("PLUGIN_OUTPUT", clean_message)
    
    def set_output_callback(self, callback):
        """Set a callback function for output (called by session manager)."""
        self._output_callback = callback
    
    def __init__(self, debug: bool = False):
        self.plugins: Dict[str, PluginBase] = {}
        self.function_plugins: Dict[str, FunctionCallingPlugin] = {}
        self.command_plugins: Dict[str, CommandPlugin] = {}
        self.hook_plugins: List[HookPlugin] = []
        self.provider_plugins: Dict[str, ProviderPlugin] = {}
        self.plugin_commands: Dict[str, Callable] = {}
        self.plugin_functions: Dict[str, Callable] = {}
        self.debug = debug
        self._output_callback = None  # Will be set by session manager
        
    def discover_and_load_plugins(self, plugin_dir: Path) -> None:
        """Discover and load all plugins from the plugin directory."""
        if self.debug:
            self._output(f"[DEBUG] Discovering plugins in directory: {plugin_dir}")
        unified_logger.log_plugin_event("DISCOVERY", f"Scanning for plugins in {plugin_dir}")
        
        if not plugin_dir.exists():
            if self.debug:
                self._output(f"[DEBUG] Plugin directory does not exist: {plugin_dir}")
            unified_logger.log_plugin_event("ERROR", f"Plugin directory does not exist: {plugin_dir}")
            return
              
        # Load enabled plugin configuration
        try:
            from calousd.plugins.plugin_config import ENABLED_PLUGINS
            self.enabled_plugin_names = ENABLED_PLUGINS
            
            if self.enabled_plugin_names is None:
                if self.debug:
                    self._output(f"[34mPlugin config:[0m Loading all available plugins (no filtering)")
                unified_logger.log_plugin_event("CONFIG", "Loading all available plugins (no filtering)")
            elif len(self.enabled_plugin_names) == 0:
                if self.debug:
                    self._output(f"[34mPlugin config:[0m All plugins disabled (empty set in config)")
                unified_logger.log_plugin_event("CONFIG", "All plugins disabled (empty set in config)")
            else:
                plugins_list = ', '.join(self.enabled_plugin_names)
                if self.debug:
                    self._output(f"[34mPlugin filtering active:[0m Only loading: {plugins_list}")
                unified_logger.log_plugin_event("CONFIG", f"Only loading these plugins: {plugins_list}")
        except Exception as e:
            self._output(f"[33mWarning:[0m Could not load plugin configuration: {e}")
            unified_logger.log_plugin_event("ERROR", f"Could not load plugin configuration: {e}")
            self.enabled_plugin_names = None  # Load all plugins if config not present

        # Load built-in plugins
        builtin_dir = plugin_dir / "builtin"
        if self.debug:
            self._output(f"[DEBUG] Checking built-in plugins directory: {builtin_dir}")
        unified_logger.log_plugin_event("SCAN", f"Checking built-in plugins directory: {builtin_dir}")
        if builtin_dir.exists():
            if self.debug:
                self._output(f"[DEBUG] Built-in plugins directory exists: {builtin_dir}")
            self._load_plugins_from_directory(builtin_dir)
        else:
            if self.debug:
                self._output(f"[DEBUG] Built-in plugins directory does not exist: {builtin_dir}")
            unified_logger.log_plugin_event("ERROR", f"Built-in plugins directory does not exist: {builtin_dir}")        # Load user plugins (future expansion)
        user_dir = plugin_dir / "user"
        if self.debug:
            self._output(f"[DEBUG] Checking user plugins directory: {user_dir}")
        unified_logger.log_plugin_event("SCAN", f"Checking user plugins directory: {user_dir}")
        if user_dir.exists():
            if self.debug:
                self._output(f"[DEBUG] User plugins directory exists: {user_dir}")
            self._load_plugins_from_directory(user_dir)
        else:
            if self.debug:
                self._output(f"[DEBUG] User plugins directory does not exist: {user_dir}")
            unified_logger.log_plugin_event("INFO", f"User plugins directory does not exist (this is normal): {user_dir}")
            
        # Log a summary of loaded plugins
        self._log_plugin_summary()
    
    def _load_plugins_from_directory(self, directory: Path) -> None:
        """Load all Python files in a directory as plugins."""
        unified_logger.log_plugin_event("SCAN", f"Scanning directory {directory} for plugin files")
        for plugin_file in directory.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
                
            try:
                self._load_plugin_file(plugin_file)
            except Exception as e:
                self._output(f"[33mWarning:[0m Failed to load plugin {plugin_file.name}: {e}")
                unified_logger.log_plugin_event("ERROR", f"Failed to load plugin {plugin_file.name}: {e}")
    
    def _load_plugin_file(self, plugin_file: Path) -> None:
        """Load a single plugin file."""
        # Skip loading if not in enabled list
        if hasattr(self, "enabled_plugin_names") and self.enabled_plugin_names is not None:
            if plugin_file.stem not in self.enabled_plugin_names:
                if self.debug:
                    self._output(f"[34mSkipping disabled plugin:[0m {plugin_file.stem}")
                unified_logger.log_plugin_event("SKIP", f"Skipping disabled plugin: {plugin_file.stem}")
                return
                
        unified_logger.log_plugin_event("LOAD", f"Loading plugin file: {plugin_file.stem}")
        
        # Determine appropriate module name based on plugin location
        if "builtin" in str(plugin_file):
            module_name = f"calousd.plugins.builtin.{plugin_file.stem}"
        elif "user" in str(plugin_file):
            module_name = f"calousd.plugins.user.{plugin_file.stem}"
        else:
            module_name = f"calousd.plugins.{plugin_file.stem}"
        
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {plugin_file}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
          # Look for plugin classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, PluginBase) and 
                attr != PluginBase and
                not attr.__name__ in ['FunctionCallingPlugin', 'CommandPlugin', 'HookPlugin', 'ProviderPlugin']):  # Skip base classes only
                
                # Instantiate and register the plugin
                try:
                    plugin_instance = attr()  # type: ignore # Plugin classes define their own constructors
                    self.register_plugin(plugin_instance)
                except Exception as e:
                    self._output(f"[33mWarning:[0m Failed to instantiate plugin {attr_name}: {e}")
    
    def register_plugin(self, plugin: PluginBase) -> bool:
        """Register a plugin instance."""        
        try:
            # Initialize the plugin
            if not plugin.initialize():
                plugin.error = "Plugin initialization failed"
                self.plugins[plugin.name] = plugin
                return False
            
            plugin.loaded = True
            self.plugins[plugin.name] = plugin
            
            # Register capabilities
            capabilities = plugin.get_capabilities()
            
            if PluginCapability.FUNCTION_CALLING in capabilities:
                if isinstance(plugin, FunctionCallingPlugin):
                    func_plugin = plugin
                    self.function_plugins[plugin.name] = func_plugin
                    # Register function mappings
                    for func_name in func_plugin.get_function_names():
                        self.plugin_functions[func_name] = func_plugin.execute_function
            
            if PluginCapability.COMMANDS in capabilities:
                if isinstance(plugin, CommandPlugin):
                    cmd_plugin = plugin
                    self.command_plugins[plugin.name] = cmd_plugin
                    # Register command mappings
                    commands = cmd_plugin.get_commands()
                    self.plugin_commands.update(commands)
            
            if PluginCapability.HOOKS in capabilities:
                if isinstance(plugin, HookPlugin):
                    self.hook_plugins.append(plugin)
            
            if PluginCapability.PROVIDER in capabilities:
                if isinstance(plugin, ProviderPlugin):
                    provider_name = plugin.get_provider_name()
                    self.provider_plugins[provider_name] = plugin
            
            # Print success message for all loaded plugins
            self._output(f"[32m✓[0m Loaded plugin: {plugin.name} v{plugin.version}")
            unified_logger.log_plugin_event("SUCCESS", f"Loaded plugin: {plugin.name} v{plugin.version}")
            return True
            
        except Exception as e:
            plugin.error = str(e)
            plugin.loaded = False
            self.plugins[plugin.name] = plugin
            self._output(f"[31m✗[0m Failed to register plugin {plugin.name}: {e}")
            unified_logger.log_plugin_event("ERROR", f"Failed to register plugin {plugin.name}: {e}")
            return False
    
    def _log_plugin_summary(self) -> None:
        """Log a summary of loaded plugins to the unified logger."""
        loaded_count = sum(1 for p in self.plugins.values() if p.loaded)
        failed_count = len(self.plugins) - loaded_count
        
        summary = f"Plugin loading complete: {loaded_count} plugins loaded"
        if failed_count > 0:
            summary += f", {failed_count} plugins failed"
            
        if loaded_count > 0:
            summary += ". Loaded plugins:"
            for plugin in self.plugins.values():
                if plugin.loaded:
                    capabilities = [cap.value for cap in plugin.get_capabilities()]
                    summary += f"\n- {plugin.name} v{plugin.version} ({', '.join(capabilities)})"
        else:
            summary += ". No plugins were loaded."
            
        unified_logger.log_plugin_event("SUMMARY", summary)
        unified_logger.add_separator("End of Plugin Loading")

    def get_all_function_schemas(self) -> List[Dict[str, Any]]:
        """Get all function calling schemas from loaded plugins."""
        schemas = []
        for plugin in self.function_plugins.values():
            if plugin.loaded:
                try:
                    schemas.extend(plugin.get_function_schemas())
                except Exception as e:
                    self._output(f"[33mWarning:[0m Error getting schemas from {plugin.name}: {e}")
        return schemas
    
    def execute_function(self, function_name: str, **kwargs) -> str:
        """Execute a plugin function call."""
        if function_name not in self.plugin_functions:
            return f"Error: Unknown function '{function_name}'"
        
        try:
            return self.plugin_functions[function_name](function_name, **kwargs)
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
    
    def execute_command(self, command_name: str, *args, **kwargs):
        """Execute a plugin command."""
        if command_name not in self.plugin_commands:
            return None
        
        try:
            return self.plugin_commands[command_name](*args, **kwargs)
        except Exception as e:
            self._output(f"[31mError executing plugin command {command_name}:[0m {e}")
            return None
    
    def apply_pre_message_hooks(self, user_input: str, context: Dict[str, Any]) -> str:
        """Apply all pre-message hooks to user input."""
        processed_input = user_input
        for hook_plugin in self.hook_plugins:
            if hook_plugin.loaded:
                try:
                    processed_input = hook_plugin.pre_message_hook(processed_input, context)
                except Exception as e:
                    self._output(f"[33mWarning:[0m Error in pre-message hook from {hook_plugin.name}: {e}")
        return processed_input
    
    def apply_post_message_hooks(self, response: str, context: Dict[str, Any]) -> str:
        """Apply all post-message hooks to LLM response."""
        processed_response = response
        for hook_plugin in self.hook_plugins:
            if hook_plugin.loaded:
                try:
                    processed_response = hook_plugin.post_message_hook(processed_response, context)
                except Exception as e:
                    self._output(f"[33mWarning:[0m Error in post-message hook from {hook_plugin.name}: {e}")
        return processed_response
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific plugin."""
        if plugin_name not in self.plugins:
            return None
        
        plugin = self.plugins[plugin_name]
        info = {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "loaded": plugin.loaded,
            "error": plugin.error,
            "capabilities": [cap.value for cap in plugin.get_capabilities()]
        }
        
        # Add capability-specific info
        if PluginCapability.FUNCTION_CALLING in plugin.get_capabilities() and plugin.loaded:
            if isinstance(plugin, FunctionCallingPlugin):
                func_plugin = plugin
                info["functions"] = func_plugin.get_function_names()
        
        if PluginCapability.COMMANDS in plugin.get_capabilities() and plugin.loaded:
            if isinstance(plugin, CommandPlugin):
                cmd_plugin = plugin
                info["commands"] = list(cmd_plugin.get_commands().keys())
        
        return info
    
    def get_all_plugins_info(self) -> List[Dict[str, Any]]:
        """Get information about all plugins."""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "loaded": plugin.loaded,
                "error": plugin.error,
                "capabilities": [cap.value for cap in plugin.get_capabilities()]
            }
            for plugin in self.plugins.values()
        ]
    
    def reload_plugins(self, plugin_dir: Path) -> None:
        """Reload all plugins (for development)."""
        # Cleanup existing plugins
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                self._output(f"[33mWarning:[0m Error cleaning up {plugin.name}: {e}")
        
        # Clear all registries
        self.plugins.clear()
        self.function_plugins.clear()
        self.command_plugins.clear()
        self.hook_plugins.clear()
        self.provider_plugins.clear()
        self.plugin_commands.clear()
        self.plugin_functions.clear()
        
        # Reload plugins
        self.discover_and_load_plugins(plugin_dir)
    
    def get_all_plugins(self) -> List[PluginBase]:
        """Get all loaded plugins."""
        return list(self.plugins.values())
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a specific plugin by name."""
        return self.plugins.get(name)
    
    def get_function_calling_plugins(self) -> List[FunctionCallingPlugin]:
        """Get all function calling plugins."""
        return list(self.function_plugins.values())
    
    def get_command_plugins(self) -> List[CommandPlugin]:
        """Get all command plugins."""
        return list(self.command_plugins.values())
    
    def get_hook_plugins(self) -> List[HookPlugin]:
        """Get all hook plugins."""
        return self.hook_plugins.copy()
    
    def get_provider_plugins(self) -> Dict[str, ProviderPlugin]:
        """Get all provider plugins."""
        return self.provider_plugins.copy()
    
    def get_provider_plugin(self, provider_name: str) -> Optional[ProviderPlugin]:
        """Get a specific provider plugin by name."""
        return self.provider_plugins.get(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """Get names of all available provider plugins."""
        return list(self.provider_plugins.keys())
