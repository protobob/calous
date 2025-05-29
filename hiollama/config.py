"""Configuration management for Hi, Ollama!"""
import json
from rich import print
from .constants import CONFIG_PATH, DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS, DEFAULT_NUM_CHATS

class ConfigManager:
    # Unified config file path
    UNIFIED_CONFIG_PATH = CONFIG_PATH.with_name(f"{CONFIG_PATH.stem}_unified{CONFIG_PATH.suffix}")
    
    DEFAULT_UNIFIED_CONFIG = {
        "global": {
            "selected_model": DEFAULT_MODEL,
            "num_chats": DEFAULT_NUM_CHATS
        },
        "chats": {
            "0": {
                "verbosity": True,
                "think_filtering": True,
                "MAX_HISTORY": DEFAULT_MAX_HISTORY,
                "system_prompt": DEFAULT_SYSTEM_PROMPT,
                "prompts": {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)},
                "logging_enabled": True
            },
            "1": {
                "verbosity": True,
                "think_filtering": True,
                "MAX_HISTORY": DEFAULT_MAX_HISTORY,
                "system_prompt": "You are a creative writing assistant who helps with storytelling and narrative development.",
                "prompts": {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)},
                "logging_enabled": True
            }
        }
    }
    
    @staticmethod
    def load_unified_config():
        """Load the unified configuration file."""
        if ConfigManager.UNIFIED_CONFIG_PATH.exists():
            try:
                with open(ConfigManager.UNIFIED_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"\n[red]Error loading unified config: {e}[/red]")
                return ConfigManager.DEFAULT_UNIFIED_CONFIG.copy()
        return ConfigManager.DEFAULT_UNIFIED_CONFIG.copy()
    
    @staticmethod
    def save_unified_config(config):
        """Save the unified configuration file."""
        try:
            with open(ConfigManager.UNIFIED_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"\n[red]Error saving unified config: {e}[/red]")
    
    @staticmethod
    def get_chat_config(instance_index):
        """Get configuration for a specific chat instance."""
        unified_config = ConfigManager.load_unified_config()
        
        chat_key = str(instance_index)
        if chat_key in unified_config.get("chats", {}):
            return unified_config["chats"][chat_key]
        
        # Return default config for new chat instances
        return {
            "verbosity": True,
            "think_filtering": True,
            "MAX_HISTORY": DEFAULT_MAX_HISTORY,
            "system_prompt": DEFAULT_SYSTEM_PROMPT,
            "prompts": {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)},
            "logging_enabled": True
        }
    
    @staticmethod
    def update_chat_config(instance_index, chat_config):
        """Update configuration for a specific chat instance."""
        unified_config = ConfigManager.load_unified_config()
        
        # Ensure chats section exists
        if "chats" not in unified_config:
            unified_config["chats"] = {}
        
        # Update the specific chat config
        unified_config["chats"][str(instance_index)] = chat_config
        
        ConfigManager.save_unified_config(unified_config)
    
    @staticmethod
    def update_global_config(global_updates):
        """Update global configuration settings."""
        unified_config = ConfigManager.load_unified_config()
        
        # Ensure global section exists
        if "global" not in unified_config:
            unified_config["global"] = {}
        
        # Update global settings
        unified_config["global"].update(global_updates)
        
        ConfigManager.save_unified_config(unified_config)
    
    @staticmethod
    def get_global_config():
        """Get global configuration settings."""
        unified_config = ConfigManager.load_unified_config()
        return unified_config.get("global", ConfigManager.DEFAULT_UNIFIED_CONFIG["global"])
    
    @staticmethod
    def get_num_chats():
        """Get the configured number of chats."""
        global_config = ConfigManager.get_global_config()
        return global_config.get("num_chats", DEFAULT_NUM_CHATS)