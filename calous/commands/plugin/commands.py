"""Plugin commands module."""
from rich import print
from rich.prompt import Prompt

from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import PluginService
from .formatters import PluginFormatter


@registry.register("plugin.list", "List all available plugins", category=CommandCategory.PLUGIN)
def cmd_plugin_list(handler) -> CommandResult:
    """List all available plugins and their status."""
    formatter = PluginFormatter()
    
    # Check if plugin system is available
    plugin_manager = PluginService.get_plugin_manager(handler.app)
    if not plugin_manager:
        formatter.plugin_system_not_available()
        return CommandResult(ActionType.CONTINUE)
    
    # Get all plugins
    plugins = PluginService.get_all_plugins(handler.app)
    if not plugins:
        formatter.no_plugins_loaded()
        return CommandResult(ActionType.CONTINUE)
    
    # Create and populate the table
    table = formatter.create_plugin_table()
    for plugin in plugins:
        # Determine status
        status = "✓ Active" if plugin.is_active else "✗ Inactive"
        status_style = "green" if plugin.is_active else "red"
        
        # Format capabilities
        capabilities_str = formatter.format_plugin_capabilities(plugin.capabilities)
        
        table.add_row(
            plugin.name,
            getattr(plugin, 'version', '1.0.0'),
            f"[{status_style}]{status}[/{status_style}]",
            capabilities_str,
            plugin.description
        )
    # Display the table with the rich console
    from rich.console import Console
    console = Console()
    console.print(table)
    
    # Show function calling plugins
    function_plugins = PluginService.get_function_calling_plugins(handler.app)
    formatter.show_function_calling_plugins(function_plugins)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("plugin.info", "Get details for a specific plugin", category=CommandCategory.PLUGIN)
def cmd_plugin_info(handler, name: str) -> CommandResult:
    """Get detailed information about a specific plugin."""
    formatter = PluginFormatter()
    
    # Check if plugin name is provided
    if not name:
        formatter.missing_plugin_name()
        return CommandResult(ActionType.CONTINUE)
    
    # Check if plugin system is available
    plugin_manager = PluginService.get_plugin_manager(handler.app)
    if not plugin_manager:
        formatter.plugin_system_not_available()
        return CommandResult(ActionType.CONTINUE)
    
    # Get the plugin
    plugin = PluginService.get_plugin_by_name(handler.app, name)
    if not plugin:
        formatter.plugin_not_found(name)
        return CommandResult(ActionType.CONTINUE)
    
    # Display plugin details
    formatter.show_plugin_details(plugin)
    
    # Show capabilities
    formatter.show_plugin_capabilities(plugin.capabilities)
    
    # Show functions if it's a function calling plugin
    if hasattr(plugin, 'get_function_schemas'):
        schemas = plugin.get_function_schemas()
        formatter.show_plugin_functions(schemas)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("plugin.reload", "Reload all plugins (for development)", category=CommandCategory.PLUGIN)
def cmd_plugin_reload(handler) -> CommandResult:
    """Reload all plugins from disk."""
    formatter = PluginFormatter()
    # Check if plugin system is available
    plugin_manager = PluginService.get_plugin_manager(handler.app)
    if not plugin_manager:
        formatter.plugin_system_not_available()
        return CommandResult(ActionType.CONTINUE)
    
    # Show plugin directory for debugging
    plugin_dir = PluginService.get_plugin_dir(handler.app)
    if plugin_dir:
        print(f"[grey50]Plugin directory: {plugin_dir}[/grey50]")
    
    # Ask for confirmation
    formatter.reload_warning()
    
    if handler.app.confirm("Are you sure you want to continue?", default=True):
        formatter.reload_starting()
        result = PluginService.reload_plugins(handler.app)
        
        if result.success:
            formatter.reload_complete()
        else:
            formatter.reload_directory_error()
    else:
        formatter.reload_cancelled()
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("plugin.help", "Show help for plugin commands", category=CommandCategory.PLUGIN)
def cmd_plugin_help(handler) -> CommandResult:
    """Show help for plugin commands - alias for /sys.help plugin."""
    handler.app.ui.show_category_help("plugin")
    return CommandResult(ActionType.CONTINUE)
