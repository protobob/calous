"""Plugin command formatters module."""
from rich import print
from rich.table import Table
from ..formatters import CommandFormatter


class PluginFormatter(CommandFormatter):
    """Specialized formatter for plugin command output."""
    
    @staticmethod
    def plugin_system_not_available():
        """Print plugin system not available message."""
        print("[bold red]Plugin system not available[/bold red]")
    
    @staticmethod
    def no_plugins_loaded():
        """Print no plugins loaded message."""
        print("[yellow]No plugins loaded[/yellow]")
    
    @staticmethod
    def create_plugin_table():
        """Create a table for plugin display."""
        table = Table(title="CALOUS Plugins")
        table.add_column("Plugin", style="cyan", no_wrap=True)
        table.add_column("Version", style="dim")
        table.add_column("Status", style="green")
        table.add_column("Capabilities", style="blue")
        table.add_column("Description", style="white")
        return table
    
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
    def show_function_calling_plugins(function_plugins):
        """Show function calling plugins."""
        if function_plugins:
            print(f"\n[bold cyan]Available LLM Tools:[/bold cyan]")
            for plugin in function_plugins:
                schemas = plugin.get_function_schemas()
                for schema in schemas:
                    function_info = schema.get('function', {})
                    func_name = function_info.get('name', 'Unknown')
                    func_desc = function_info.get('description', 'No description')
                    print(f"  • [bold]{func_name}[/bold]: {func_desc}")
    
    @staticmethod
    def missing_plugin_name():
        """Print missing plugin name error."""
        print("[bold red]Error:[/bold red] Please specify a plugin name")
        print("[grey50]Usage: /plugin.info <plugin_name>[/grey50]")
    
    @staticmethod
    def plugin_not_found(plugin_name):
        """Print plugin not found error."""
        print(f"[bold red]Plugin '{plugin_name}' not found[/bold red]")
        print("[grey50]Use /plugin.list to see available plugins[/grey50]")
    
    @staticmethod
    def show_plugin_details(plugin):
        """Show detailed plugin information."""
        print(f"\n[bold cyan]Plugin Details: {plugin.name}[/bold cyan]")
        print(f"[bold]Version:[/bold] {getattr(plugin, 'version', '1.0.0')}")
        print(f"[bold]Description:[/bold] {plugin.description}")
        print(f"[bold]Status:[/bold] {'✓ Active' if plugin.is_active else '✗ Inactive'}")
    
    @staticmethod
    def show_plugin_capabilities(capabilities):
        """Show plugin capabilities."""
        print(f"[bold]Capabilities:[/bold]")
        for cap in capabilities:        
            if cap.name == "FUNCTION_CALLING":
                print("  • 🔧 LLM Tools - Provides capabilities for LLM use")
            elif cap.name == "COMMANDS":
                print("  • 💬 Commands - Adds user commands")
            elif cap.name == "HOOKS":
                print("  • 🔗 Hooks - Integrates with message processing")
            elif cap.name == "UI":
                print("  • 🎨 UI - Modifies user interface")
    
    @staticmethod
    def show_plugin_functions(schemas):
        """Show plugin functions."""
        if schemas:
            print(f"\n[bold]Available LLM Tools:[/bold]")
            for schema in schemas:
                function_info = schema.get('function', {})
                func_name = function_info.get('name', 'Unknown')
                func_desc = function_info.get('description', 'No description')
                print(f"  • [bold]{func_name}[/bold]")
                print(f"    {func_desc}")
                
                # Show parameters
                params = function_info.get('parameters', {}).get('properties', {})
                if params:
                    print(f"    [dim]Parameters:[/dim]")
                    required_params = function_info.get('parameters', {}).get('required', [])
                    for param_name, param_info in params.items():
                        param_type = param_info.get('type', 'unknown')
                        param_desc = param_info.get('description', 'No description')
                        required = param_name in required_params
                        req_marker = " [red]*[/red]" if required else ""
                        print(f"      - {param_name} ({param_type}){req_marker}: {param_desc}")
    
    @staticmethod
    def reload_warning():
        """Print plugin reload warning."""
        print("[bold yellow]Warning:[/bold yellow] This will reload all plugins from disk.")
        print("Any plugin state will be lost and all plugins will be reinitialized.")
    
    @staticmethod
    def reload_starting():
        """Print plugin reload starting message."""
        print("[blue]Reloading plugins...[/blue]")
    
    @staticmethod
    def reload_complete():
        """Print plugin reload complete message."""
        print("[green]✓[/green] Plugin reload complete!")
    
    @staticmethod
    def reload_directory_error():
        """Print plugin reload directory error."""
        print("[bold red]Error:[/bold red] Could not locate plugin directory")
    
    @staticmethod
    def reload_cancelled():
        """Print plugin reload cancelled message."""
        print("Plugin reload cancelled.")
