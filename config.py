"""Configuration management for Hi, Ollama!"""
import json
from pathlib import Path
from rich import print

class ConfigManager:
    CONFIG_PATH = Path.home() / ".hiollama_config.json"
    DEFAULT_CONFIG = {
        "selected_model": "qwen3:0.6B",
        "verbosity": True,
        "think_filtering": True,
        "MAX_HISTORY": 20,
        "system_prompt": "You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code.",
        "prompts": {f"prompt{i}": "" for i in range(1, 11)},
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