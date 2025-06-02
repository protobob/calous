"""Plugin manager for HiOllama plugin system."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from rich import print

from .base import PluginBase, PluginCapability, FunctionCallingPlugin, CommandPlugin, HookPlugin


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.function_plugins: Dict[str, FunctionCallingPlugin] = {}
        self.command_plugins: Dict[str, CommandPlugin] = {}
        self.hook_plugins: List[HookPlugin] = []
        self.plugin_commands: Dict[str, Callable] = {}
        self.plugin_functions: Dict[str, Callable] = {}
        
    def discover_and_load_plugins(self, plugin_dir: Path) -> None:
        """Discover and load all plugins from the plugin directory."""
        print(f"[DEBUG] Discovering plugins in directory: {plugin_dir}")
        if not plugin_dir.exists():
            print(f"[DEBUG] Plugin directory does not exist: {plugin_dir}")
            return

        # Load built-in plugins
        builtin_dir = plugin_dir / "builtin"
        print(f"[DEBUG] Checking built-in plugins directory: {builtin_dir}")
        if builtin_dir.exists():
            print(f"[DEBUG] Built-in plugins directory exists: {builtin_dir}")
            self._load_plugins_from_directory(builtin_dir)
        else:
            print(f"[DEBUG] Built-in plugins directory does not exist: {builtin_dir}")

        # Load user plugins (future expansion)
        user_dir = plugin_dir / "user"
        print(f"[DEBUG] Checking user plugins directory: {user_dir}")
        if user_dir.exists():
            print(f"[DEBUG] User plugins directory exists: {user_dir}")
            self._load_plugins_from_directory(user_dir)
        else:
            print(f"[DEBUG] User plugins directory does not exist: {user_dir}")
    
    def _load_plugins_from_directory(self, directory: Path) -> None:
        """Load all Python files in a directory as plugins."""
        for plugin_file in directory.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
                
            try:
                self._load_plugin_file(plugin_file)
            except Exception as e:
                print(f"[yellow]Warning:[/yellow] Failed to load plugin {plugin_file.name}: {e}")
    
    def _load_plugin_file(self, plugin_file: Path) -> None:
        """Load a single plugin file."""
        module_name = f"hiollama.plugins.builtin.{plugin_file.stem}"
        
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
                not attr.__name__ in ['FunctionCallingPlugin', 'CommandPlugin', 'HookPlugin']):  # Skip base classes only
                
                # Instantiate and register the plugin
                try:
                    plugin_instance = attr()
                    self.register_plugin(plugin_instance)
                except Exception as e:
                    print(f"[yellow]Warning:[/yellow] Failed to instantiate plugin {attr_name}: {e}")
    
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
                func_plugin = plugin
                self.function_plugins[plugin.name] = func_plugin
                # Register function mappings
                for func_name in func_plugin.get_function_names():
                    self.plugin_functions[func_name] = func_plugin.execute_function
            
            if PluginCapability.COMMANDS in capabilities:
                cmd_plugin = plugin
                self.command_plugins[plugin.name] = cmd_plugin
                # Register command mappings
                commands = cmd_plugin.get_commands()
                self.plugin_commands.update(commands)
            
            if PluginCapability.HOOKS in capabilities:
                self.hook_plugins.append(plugin)
            
            print(f"[green]✓[/green] Loaded plugin: {plugin.name} v{plugin.version}")
            return True
            
        except Exception as e:
            plugin.error = str(e)
            plugin.loaded = False
            self.plugins[plugin.name] = plugin
            print(f"[red]✗[/red] Failed to register plugin {plugin.name}: {e}")
            return False
    
    def get_all_function_schemas(self) -> List[Dict[str, Any]]:
        """Get all function calling schemas from loaded plugins."""
        schemas = []
        for plugin in self.function_plugins.values():
            if plugin.loaded:
                try:
                    schemas.extend(plugin.get_function_schemas())
                except Exception as e:
                    print(f"[yellow]Warning:[/yellow] Error getting schemas from {plugin.name}: {e}")
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
            print(f"[red]Error executing plugin command {command_name}:[/red] {e}")
            return None
    
    def apply_pre_message_hooks(self, user_input: str, context: Dict[str, Any]) -> str:
        """Apply all pre-message hooks to user input."""
        processed_input = user_input
        for hook_plugin in self.hook_plugins:
            if hook_plugin.loaded:
                try:
                    processed_input = hook_plugin.pre_message_hook(processed_input, context)
                except Exception as e:
                    print(f"[yellow]Warning:[/yellow] Error in pre-message hook from {hook_plugin.name}: {e}")
        return processed_input
    
    def apply_post_message_hooks(self, response: str, context: Dict[str, Any]) -> str:
        """Apply all post-message hooks to LLM response."""
        processed_response = response
        for hook_plugin in self.hook_plugins:
            if hook_plugin.loaded:
                try:
                    processed_response = hook_plugin.post_message_hook(processed_response, context)
                except Exception as e:
                    print(f"[yellow]Warning:[/yellow] Error in post-message hook from {hook_plugin.name}: {e}")
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
            func_plugin = plugin
            info["functions"] = func_plugin.get_function_names()
        
        if PluginCapability.COMMANDS in plugin.get_capabilities() and plugin.loaded:
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
                print(f"[yellow]Warning:[/yellow] Error cleaning up {plugin.name}: {e}")
        
        # Clear all registries
        self.plugins.clear()
        self.function_plugins.clear()
        self.command_plugins.clear()
        self.hook_plugins.clear()
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
