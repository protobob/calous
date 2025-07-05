"""Provider service layer."""
from typing import List, Dict, Any, Optional, NamedTuple
from ...config import ConfigManager


class ProviderResult(NamedTuple):
    """Result from provider operations."""
    success: bool
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ProviderService:
    """Service layer for provider management."""
    
    def __init__(self, app):
        self.app = app
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers including ollama."""
        providers = []
        
        # Always include ollama as the default built-in provider
        providers.append({
            "name": "ollama",
            "description": "Local Ollama models",
            "loaded": True,
            "plugin": False,
            "streaming": True,
            "function_calling": True
        })
        
        # Get provider plugins
        if hasattr(self.app, 'plugin_manager') and self.app.plugin_manager:
            provider_plugins = self.app.plugin_manager.get_provider_plugins()
            for provider_name, plugin in provider_plugins.items():
                providers.append({
                    "name": provider_name,
                    "description": plugin.description,
                    "loaded": plugin.loaded,
                    "plugin": True,
                    "streaming": plugin.supports_streaming() if plugin.loaded else False,
                    "function_calling": plugin.supports_function_calling() if plugin.loaded else False,
                    "error": plugin.error if not plugin.loaded else None
                })
        
        return providers
    
    def get_current_provider(self) -> str:
        """Get the currently selected provider."""
        # Always read from config for consistency
        global_config = ConfigManager.get_global_config()
        return global_config.get('selected_provider', 'ollama')
    
    def set_provider(self, provider_name: str) -> ProviderResult:
        """Switch to a different provider."""
        # Validate provider exists
        available_providers = [p["name"] for p in self.get_available_providers()]
        if provider_name not in available_providers:
            return ProviderResult(
                success=False,
                error_message=f"Provider '{provider_name}' not found. Available: {', '.join(available_providers)}"
            )
        
        # Check if provider plugin is loaded (if it's a plugin)
        if provider_name != 'ollama':
            if hasattr(self.app, 'plugin_manager') and self.app.plugin_manager:
                plugin = self.app.plugin_manager.get_provider_plugin(provider_name)
                if not plugin or not plugin.loaded:
                    error_msg = plugin.error if plugin else "Plugin not found"
                    return ProviderResult(
                        success=False,
                        error_message=f"Provider '{provider_name}' plugin not loaded: {error_msg}"
                    )
        
        # Update app and config
        self.app.selected_provider = provider_name
        
        # Clear the selected model when switching providers since model names are provider-specific
        self.app.selected_model = ""
        
        # Save to config
        ConfigManager.update_global_config({
            "selected_provider": provider_name,
            "selected_model": ""  # Clear model when switching providers
        })
        
        # Update all chat instances if we have access to session manager
        if hasattr(self.app, 'session_manager') and self.app.session_manager:
            session_manager = self.app.session_manager
            if hasattr(session_manager, 'chats'):
                for chat in session_manager.chats:
                    if chat:
                        chat.selected_provider = provider_name
                        chat.selected_model = ""  # Clear model for all chats
                        # Clear cached provider in model interaction
                        if hasattr(chat, 'model') and hasattr(chat.model, '_current_provider'):
                            chat.model._current_provider = None
        
        # Clear any cached provider in model interaction for current app
        if hasattr(self.app, 'model') and hasattr(self.app.model, '_current_provider'):
            self.app.model._current_provider = None
        
        return ProviderResult(success=True)
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific provider."""
        if provider_name == 'ollama':
            return {
                "name": "ollama",
                "description": "Local Ollama models",
                "models": self._get_ollama_models(),
                "streaming": True,
                "function_calling": True,
                "plugin": False
            }
        
        # Get plugin info
        if hasattr(self.app, 'plugin_manager') and self.app.plugin_manager:
            plugin = self.app.plugin_manager.get_provider_plugin(provider_name)
            if plugin and plugin.loaded:
                return plugin.get_provider_info()
        
        return None
    
    def _get_ollama_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            if hasattr(self.app, 'model'):
                return self.app.model.list_ollama_models()
        except Exception:
            pass
        return []
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        """Get available models for a specific provider."""
        if provider_name == 'ollama':
            return self._get_ollama_models()
        
        # Get models from plugin
        if hasattr(self.app, 'plugin_manager') and self.app.plugin_manager:
            plugin = self.app.plugin_manager.get_provider_plugin(provider_name)
            if plugin and plugin.loaded:
                try:
                    return plugin.get_available_models()
                except Exception:
                    pass
        
        return []