"""Provider formatters for ANSI output."""
from typing import List, Dict, Any
from ..formatters import CommandFormatter
from ...constants import Colors


class ProviderFormatter(CommandFormatter):
    """Formatter for provider command output."""
    
    @staticmethod
    def format_provider_list(providers: List[Dict[str, Any]], current_provider: str):
        """Format the list of available providers."""
        ProviderFormatter._output(f"\n{Colors.INFO}Available LLM Providers:{Colors.RESET}")
        
        if not providers:
            ProviderFormatter._output(f"{Colors.HINT}No providers available.{Colors.RESET}")
            return
        
        for provider in providers:
            name = provider["name"]
            description = provider["description"]
            loaded = provider["loaded"]
            is_plugin = provider["plugin"]
            is_current = name == current_provider
            
            # Status indicators
            status_indicators = []
            if is_current:
                status_indicators.append(f"\033[1;32m(current){Colors.RESET}")
            if loaded:
                status_indicators.append(f"{Colors.SUCCESS}✓{Colors.RESET}")
            else:
                status_indicators.append(f"{Colors.ERROR}✗{Colors.RESET}")
            if is_plugin:
                status_indicators.append(f"{Colors.COMMAND}(plugin){Colors.RESET}")
            
            status = " ".join(status_indicators)
            
            ProviderFormatter._output(f"  {name:<12} {status}")
            ProviderFormatter._output(f"    {Colors.HINT}{description}{Colors.RESET}")
            
            # Show capabilities
            capabilities = []
            if loaded:
                if provider.get("streaming"):
                    capabilities.append("streaming")
                if provider.get("function_calling"):
                    capabilities.append("functions")
            
            if capabilities:
                ProviderFormatter._output(f"    {Colors.HINT}Supports: {', '.join(capabilities)}{Colors.RESET}")
            
            # Show error if not loaded
            if not loaded and provider.get("error"):
                ProviderFormatter._output(f"    {Colors.ERROR}Error: {provider['error']}{Colors.RESET}")
            
            ProviderFormatter._output("")  # Blank line between providers
    
    @staticmethod
    def format_provider_switched(provider_name: str):
        """Format provider switch success message."""
        ProviderFormatter._output(f"\n{Colors.SUCCESS}✓{Colors.RESET} Provider switched to: {Colors.INFO}{provider_name}{Colors.RESET}")
    
    @staticmethod
    def format_provider_error(error_message: str):
        """Format provider error message."""
        ProviderFormatter._output(f"\n{Colors.ERROR}Provider Error:{Colors.RESET} {error_message}")
    
    @staticmethod
    def format_provider_vars(service):
        """Format provider variables and settings."""
        current_provider = service.get_current_provider()
        ProviderFormatter._output(f"\n{Colors.INFO}Provider Variables:{Colors.RESET}")
        ProviderFormatter._output(f"  Current Provider: {Colors.WARNING}{current_provider}{Colors.RESET}")
        
        # Get provider info
        provider_info = service.get_provider_info(current_provider)
        if provider_info:
            ProviderFormatter._output(f"  Description: {Colors.HINT}{provider_info.get('description', 'N/A')}{Colors.RESET}")
            
            # Show capabilities
            capabilities = []
            if provider_info.get("streaming"):
                capabilities.append("streaming")
            if provider_info.get("function_calling"):
                capabilities.append("functions")
            
            if capabilities:
                ProviderFormatter._output(f"  Capabilities: {Colors.HINT}{', '.join(capabilities)}{Colors.RESET}")
            
            # Show available models
            models = provider_info.get("models", [])
            if models:
                model_count = len(models)
                ProviderFormatter._output(f"  Available Models: {Colors.HINT}{model_count} models{Colors.RESET}")
                if model_count <= 5:
                    for model in models:
                        ProviderFormatter._output(f"    {Colors.HINT}- {model}{Colors.RESET}")
                else:
                    for model in models[:3]:
                        ProviderFormatter._output(f"    {Colors.HINT}- {model}{Colors.RESET}")
                    ProviderFormatter._output(f"    {Colors.HINT}... and {model_count - 3} more{Colors.RESET}")
        
        ProviderFormatter._output("")  # Blank line at end