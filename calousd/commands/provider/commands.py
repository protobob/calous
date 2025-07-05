"""Provider management commands."""
from typing import Optional
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import ProviderService
from .formatters import ProviderFormatter


@registry.register("provider.list", "List available LLM providers", category=CommandCategory.PROVIDER)
def cmd_provider_list(handler) -> CommandResult:
    """List all available provider plugins."""
    service = ProviderService(handler.app)
    providers = service.get_available_providers()
    ProviderFormatter.format_provider_list(providers, service.get_current_provider())
    return CommandResult(ActionType.CONTINUE)


@registry.register("provider.set", "Switch to a different LLM provider", category=CommandCategory.PROVIDER)
def cmd_provider_set(handler, provider_name: str) -> CommandResult:
    """Switch to a different LLM provider."""
    service = ProviderService(handler.app)
    result = service.set_provider(provider_name)
    
    if result.success:
        ProviderFormatter.format_provider_switched(provider_name)
        return CommandResult(ActionType.CONTINUE, message=f"Provider switched to: {provider_name}")
    else:
        ProviderFormatter.format_provider_error(result.error_message)
        return CommandResult(ActionType.CONTINUE, message=f"Error: {result.error_message}")


@registry.register("provider.vars", "Show provider-related variables", category=CommandCategory.PROVIDER)
def cmd_provider_vars(handler) -> CommandResult:
    """Display provider-related variables and settings."""
    service = ProviderService(handler.app)
    ProviderFormatter.format_provider_vars(service)
    return CommandResult(ActionType.CONTINUE)


@registry.register("provider.help", "Show help for provider commands", category=CommandCategory.PROVIDER)
def cmd_provider_help(handler) -> CommandResult:
    """Show help for provider commands - alias for /sys.help provider."""
    handler.app.ui.show_category_help("provider")
    return CommandResult(ActionType.CONTINUE)