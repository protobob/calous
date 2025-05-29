"""Configuration management for Hi, Ollama!"""
import json
from rich import print
from .constants import CONFIG_PATH, DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS

class ConfigManager:
    DEFAULT_CONFIG = {
        "selected_model": DEFAULT_MODEL,
        "verbosity": True,
        "think_filtering": True,
        "MAX_HISTORY": DEFAULT_MAX_HISTORY,
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "prompts": {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)},
        "logging_enabled": True
    }
    
    # Add global config for shared settings
    GLOBAL_CONFIG_PATH = CONFIG_PATH.with_name(f"{CONFIG_PATH.stem}_global{CONFIG_PATH.suffix}")
    DEFAULT_GLOBAL_CONFIG = {
        "selected_model": DEFAULT_MODEL
    }
    
    @staticmethod
    def get_config_path(instance_index):
        """Generate a config path for a specific chat instance."""
        return CONFIG_PATH.with_name(f"{CONFIG_PATH.stem}_{instance_index}{CONFIG_PATH.suffix}")
    
    @staticmethod
    def load_config(instance_index):
        """Load configuration for a specific chat instance."""
        config_path = ConfigManager.get_config_path(instance_index)
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Remove selected_model from instance config if it exists
                    config.pop("selected_model", None)
                    return config
            except Exception as e:
                print(f"\n[red]Error loading config: {e}[/red]")
                return ConfigManager.DEFAULT_CONFIG.copy()
        
        # Remove selected_model from default config for instances
        instance_config = ConfigManager.DEFAULT_CONFIG.copy()
        instance_config.pop("selected_model", None)
        return instance_config
    
    @staticmethod
    def save_config(config, instance_index):
        """Save configuration for a specific chat instance."""
        config_path = ConfigManager.get_config_path(instance_index)
        try:
            # Don't save selected_model in instance config
            instance_config = config.copy()
            instance_config.pop("selected_model", None)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(instance_config, f, indent=2)
        except Exception as e:
            print(f"\n[red]Error saving config: {e}[/red]")
    
    @staticmethod
    def load_global_config():
        """Load global configuration shared across all instances."""
        if ConfigManager.GLOBAL_CONFIG_PATH.exists():
            try:
                with open(ConfigManager.GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"\n[red]Error loading global config: {e}[/red]")
                return ConfigManager.DEFAULT_GLOBAL_CONFIG.copy()
        return ConfigManager.DEFAULT_GLOBAL_CONFIG.copy()
    
    @staticmethod
    def save_global_config(global_config):
        """Save global configuration shared across all instances."""
        try:
            with open(ConfigManager.GLOBAL_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(global_config, f, indent=2)
        except Exception as e:
            print(f"\n[red]Error saving global config: {e}[/red]")