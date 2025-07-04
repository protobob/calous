"""Plugin command formatters module."""
from ..formatters import CommandFormatter


class PluginFormatter(CommandFormatter):
    """Specialized formatter for plugin command output."""
    
    @staticmethod
    def _output(message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        session_manager = CommandFormatter._get_session_manager()
        if session_manager and session_manager.socket_mode and session_manager.current_connection:
            session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
    
    @staticmethod
    def plugin_system_not_available():
        """Print plugin system not available message."""
        PluginFormatter._output("[1;31mPlugin system not available[0m")
    
    @staticmethod
    def no_plugins_loaded():
        """Print no plugins loaded message."""
        PluginFormatter._output("[33mNo plugins loaded[0m")
    
    @staticmethod
    def create_plugin_table():
        """Create a simple table header for plugin display."""
        # Return a simple formatted header instead of Rich table
        header = "\n{:<20} {:<10} {:<10} {:<20} {:<30}".format(
            "Plugin", "Version", "Status", "Capabilities", "Description"
        )
        separator = "-" * 90
        return f"{header}\n{separator}"
    
    @staticmethod
    def format_plugin_capabilities(capabilities):
        """Format plugin capabilities for display."""
        formatted = []
        for cap in capabilities:            
            if cap.name == "FUNCTION_CALLING":
                formatted.append("🔧 LLM Tools")
            elif cap.name == "COMMANDS":
                formatted.append("💬 Commands")
            elif cap.name == "HOOKS":
                formatted.append("🔗 Hooks")
            elif cap.name == "UI":
                formatted.append("🎨 UI")
        
        return " ".join(formatted) if formatted else "None"
    
    @staticmethod
    def display_plugin_table(table_header):
        """Display a plugin table using the proper output method."""
        # Display the simple header text
        PluginFormatter._output(table_header)
    
    @staticmethod
    def show_function_calling_plugins(function_plugins):
        """Show function calling plugins."""
        if function_plugins:
            PluginFormatter._output(f"\n[1;36mAvailable LLM Tools:[0m")
            for plugin in function_plugins:
                schemas = plugin.get_function_schemas()
                for schema in schemas:
                    function_info = schema.get('function', {})
                    func_name = function_info.get('name', 'Unknown')
                    func_desc = function_info.get('description', 'No description')
                    PluginFormatter._output(f"  • [1m{func_name}[0m: {func_desc}")
    
    @staticmethod
    def missing_plugin_name():
        """Print missing plugin name error."""
        PluginFormatter._output("[1;31mError:[0m Please specify a plugin name")
        PluginFormatter._output("[90mUsage: /plugin.info <plugin_name>[0m")
    
    @staticmethod
    def plugin_not_found(plugin_name):
        """Print plugin not found error."""
        PluginFormatter._output(f"[1;31mPlugin '{plugin_name}' not found[0m")
        PluginFormatter._output("[90mUse /plugin.list to see available plugins[0m")
    
    @staticmethod
    def show_plugin_details(plugin):
        """Show detailed plugin information."""
        PluginFormatter._output(f"\n[1;36mPlugin Details: {plugin.name}[0m")
        PluginFormatter._output(f"[1mVersion:[0m {getattr(plugin, 'version', '1.0.0')}")
        PluginFormatter._output(f"[1mDescription:[0m {plugin.description}")
        PluginFormatter._output(f"[1mStatus:[0m {'✓ Active' if plugin.is_active else '✗ Inactive'}")
    
    @staticmethod
    def show_plugin_capabilities(capabilities):
        """Show plugin capabilities."""
        PluginFormatter._output(f"[1mCapabilities:[0m")
        for cap in capabilities:        
            if cap.name == "FUNCTION_CALLING":
                PluginFormatter._output("  • 🔧 LLM Tools - Provides capabilities for LLM use")
            elif cap.name == "COMMANDS":
                PluginFormatter._output("  • 💬 Commands - Adds user commands")
            elif cap.name == "HOOKS":
                PluginFormatter._output("  • 🔗 Hooks - Integrates with message processing")
            elif cap.name == "UI":
                PluginFormatter._output("  • 🎨 UI - Modifies user interface")
    
    @staticmethod
    def show_plugin_functions(schemas):
        """Show plugin functions."""
        if schemas:
            PluginFormatter._output(f"\n[1mAvailable LLM Tools:[0m")
            for schema in schemas:
                function_info = schema.get('function', {})
                func_name = function_info.get('name', 'Unknown')
                func_desc = function_info.get('description', 'No description')
                PluginFormatter._output(f"  • [1m{func_name}[0m")
                PluginFormatter._output(f"    {func_desc}")
                
                # Show parameters
                params = function_info.get('parameters', {}).get('properties', {})
                if params:
                    PluginFormatter._output(f"    [2mParameters:[0m")
                    required_params = function_info.get('parameters', {}).get('required', [])
                    for param_name, param_info in params.items():
                        param_type = param_info.get('type', 'unknown')
                        param_desc = param_info.get('description', 'No description')
                        required = param_name in required_params
                        req_marker = " [31m*[0m" if required else ""
                        PluginFormatter._output(f"      - {param_name} ({param_type}){req_marker}: {param_desc}")
    
    @staticmethod
    def reload_warning():
        """Print plugin reload warning."""
        PluginFormatter._output("[1;33mWarning:[0m This will reload all plugins from disk.")
        PluginFormatter._output("Any plugin state will be lost and all plugins will be reinitialized.")
    
    @staticmethod
    def reload_starting():
        """Print plugin reload starting message."""
        PluginFormatter._output("[34mReloading plugins...[0m")
    
    @staticmethod
    def reload_complete():
        """Print plugin reload complete message."""
        PluginFormatter._output("[32m✓[0m Plugin reload complete!")
    
    @staticmethod
    def reload_directory_error():
        """Print plugin reload directory error."""
        PluginFormatter._output("[1;31mError:[0m Could not locate plugin directory")
    
    @staticmethod
    def reload_cancelled():
        """Print plugin reload cancelled message."""
        PluginFormatter._output("Plugin reload cancelled.")
    
    @staticmethod
    def show_plugin_directory(plugin_dir):
        """Show plugin directory path."""
        PluginFormatter._output(f"[90mPlugin directory: {plugin_dir}[0m")
