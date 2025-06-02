"""Plugin management commands."""
from typing import Optional
from rich import print
from rich.table import Table
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


@registry.register("plugins", "List available plugins and their status", category=CommandCategory.GENERAL)
def cmd_plugins(handler) -> CommandResult:
    """List all available plugins and their status."""
    if not hasattr(handler.app, 'plugin_manager') or not handler.app.plugin_manager:
        print("[bold red]Plugin system not available[/bold red]")
        return CommandResult(ActionType.CONTINUE)
    
    plugin_manager = handler.app.plugin_manager
    plugins = plugin_manager.get_all_plugins()
    
    if not plugins:
        print("[yellow]No plugins loaded[/yellow]")
        return CommandResult(ActionType.CONTINUE)
    
    # Create a table for plugin display
    table = Table(title="HiOllama Plugins")
    table.add_column("Plugin", style="cyan", no_wrap=True)
    table.add_column("Version", style="dim")
    table.add_column("Status", style="green")
    table.add_column("Capabilities", style="blue")
    table.add_column("Description", style="white")
    
    for plugin in plugins:
        # Determine status
        status = "✓ Active" if plugin.is_active else "✗ Inactive"
        status_style = "green" if plugin.is_active else "red"
        
        # Format capabilities
        capabilities = []
        for cap in plugin.capabilities:            
            if cap.name == "FUNCTION_CALLING":
                capabilities.append("🔧 LLM Tools")
            elif cap.name == "COMMANDS":
                capabilities.append("💬 Commands")
            elif cap.name == "HOOKS":
                capabilities.append("🔗 Hooks")
            elif cap.name == "UI":
                capabilities.append("🎨 UI")
        
        capabilities_str = " ".join(capabilities) if capabilities else "None"
        table.add_row(
            plugin.name,
            getattr(plugin, 'version', '1.0.0'),
            f"[{status_style}]{status}[/{status_style}]",
            capabilities_str,
            plugin.description
        )
    
    print(table)    # Show function calling plugins specifically    
    function_plugins = plugin_manager.get_function_calling_plugins()
    if function_plugins:
        print(f"\n[bold cyan]Available LLM Tools:[/bold cyan]")
        for plugin in function_plugins:
            schemas = plugin.get_function_schemas()
            for schema in schemas:
                function_info = schema.get('function', {})
                func_name = function_info.get('name', 'Unknown')
                func_desc = function_info.get('description', 'No description')
                print(f"  • [bold]{func_name}[/bold]: {func_desc}")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("plugin", "Get details about a specific plugin", category=CommandCategory.GENERAL)
def cmd_plugin(handler, plugin_name: Optional[str] = None) -> CommandResult:
    """Get detailed information about a specific plugin."""
    if not plugin_name:
        print("[bold red]Error:[/bold red] Please specify a plugin name")
        print("[grey50]Usage: /plugin <plugin_name>[/grey50]")
        return CommandResult(ActionType.CONTINUE)
    
    if not hasattr(handler.app, 'plugin_manager') or not handler.app.plugin_manager:
        print("[bold red]Plugin system not available[/bold red]")
        return CommandResult(ActionType.CONTINUE)
    
    plugin_manager = handler.app.plugin_manager
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        print(f"[bold red]Plugin '{plugin_name}' not found[/bold red]")
        print("[grey50]Use /plugins to see available plugins[/grey50]")
        return CommandResult(ActionType.CONTINUE)
      # Display detailed plugin information
    print(f"\n[bold cyan]Plugin Details: {plugin.name}[/bold cyan]")
    print(f"[bold]Version:[/bold] {getattr(plugin, 'version', '1.0.0')}")
    print(f"[bold]Description:[/bold] {plugin.description}")
    print(f"[bold]Status:[/bold] {'✓ Active' if plugin.is_active else '✗ Inactive'}")
    
    # Show capabilities
    print(f"[bold]Capabilities:[/bold]")
    for cap in plugin.capabilities:        
        if cap.name == "FUNCTION_CALLING":
            print("  • 🔧 LLM Tools - Provides capabilities for LLM use")
        elif cap.name == "COMMANDS":
            print("  • 💬 Commands - Adds user commands")
        elif cap.name == "HOOKS":
            print("  • 🔗 Hooks - Integrates with message processing")
        elif cap.name == "UI":
            print("  • 🎨 UI - Modifies user interface")    # Show functions if it's a function calling plugin    if hasattr(plugin, 'get_function_schemas'):
        schemas = plugin.get_function_schemas()
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
    
    return CommandResult(ActionType.CONTINUE)
