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
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config for instance {instance_index}: {e}")
        return ConfigManager.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save_config(config, instance_index):
        """Save configuration for a specific chat instance."""
        config_path = ConfigManager.get_config_path(instance_index)
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config for instance {instance_index}: {e}")