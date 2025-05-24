"""Configuration management for Hi, Ollama!"""
import json
from rich import print
from .constants import CONFIG_PATH, DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS

class ConfigManager:
    CONFIG_PATH = CONFIG_PATH
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
    def load_config():
        """Load configuration from file or return defaults."""
        if ConfigManager.CONFIG_PATH.exists():
            try:
                with open(ConfigManager.CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config: {e}")
        return ConfigManager.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save_config(config):
        """Save configuration to file."""
        try:
            with open(ConfigManager.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")