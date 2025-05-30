"""Configuration management for Hi, Ollama!"""
import json
from rich import print
from .constants import CONFIG_PATH, DEFAULT_MODEL, DEFAULT_MAX_HISTORY, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS, DEFAULT_NUM_CHATS

class ConfigManager:
    
    @staticmethod
    def _generate_default_chat_config():
        """Generate default configuration for a chat instance."""
        return {
            "verbosity": True,
            "think_filtering": True,
            "MAX_HISTORY": DEFAULT_MAX_HISTORY,
            "system_prompt": DEFAULT_SYSTEM_PROMPT,
            "prompts": {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)}
        }
    
    @staticmethod
    def _generate_default_unified_config(num_chats=None):
        """Generate default unified configuration for any number of chats."""
        if num_chats is None:
            num_chats = DEFAULT_NUM_CHATS
            
        config = {
            "global": {
                "selected_model": DEFAULT_MODEL,
                "num_chats": num_chats
            },
            "chats": {}
        }
        
        # Generate chat configs dynamically
        for i in range(num_chats):
            if i == 0:
                # Chat 0 gets the default technical prompt
                config["chats"][str(i)] = ConfigManager._generate_default_chat_config()
            elif i == 1:
                # Chat 1 gets the creative writing prompt (preserve existing behavior)
                chat_config = ConfigManager._generate_default_chat_config()
                chat_config["system_prompt"] = "You are a creative writing assistant who helps with storytelling and narrative development."
                config["chats"][str(i)] = chat_config
            else:
                # Additional chats get generic prompts
                chat_config = ConfigManager._generate_default_chat_config()
                chat_config["system_prompt"] = f"You are a helpful assistant for Chat {i + 1}. Provide clear, concise responses."
                config["chats"][str(i)] = chat_config
        
        return config
    
    @staticmethod
    def load_unified_config():
        """Load the unified configuration file."""
        if not CONFIG_PATH.exists():
            return ConfigManager._generate_default_unified_config()
        
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"\nError loading config: {e}")
            print("Creating new default configuration...")
            return ConfigManager._generate_default_unified_config()
    
    @staticmethod
    def save_unified_config(config):
        """Save the unified configuration file."""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"\nError saving config: {e}")
    
    @staticmethod
    def get_chat_config(instance_index):
        """Get configuration for a specific chat instance."""
        unified_config = ConfigManager.load_unified_config()
        
        chat_key = str(instance_index)
        if chat_key in unified_config.get("chats", {}):
            return unified_config["chats"][chat_key]
        
        # Generate default config for new chat instances
        if instance_index == 0:
            return ConfigManager._generate_default_chat_config()
        elif instance_index == 1:
            chat_config = ConfigManager._generate_default_chat_config()
            chat_config["system_prompt"] = "You are a creative writing assistant who helps with storytelling and narrative development."
            return chat_config
        else:
            chat_config = ConfigManager._generate_default_chat_config()
            chat_config["system_prompt"] = f"You are a helpful assistant for Chat {instance_index + 1}. Provide clear, concise responses."
            return chat_config
    
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
        
        # If num_chats changed, ensure we have configs for all chats
        if "num_chats" in global_updates:
            new_num_chats = global_updates["num_chats"]
            for i in range(new_num_chats):
                chat_key = str(i)
                if chat_key not in unified_config.get("chats", {}):
                    # Generate missing chat config
                    if i == 0:
                        unified_config["chats"][chat_key] = ConfigManager._generate_default_chat_config()
                    elif i == 1:
                        chat_config = ConfigManager._generate_default_chat_config()
                        chat_config["system_prompt"] = "You are a creative writing assistant who helps with storytelling and narrative development."
                        unified_config["chats"][chat_key] = chat_config
                    else:
                        chat_config = ConfigManager._generate_default_chat_config()
                        chat_config["system_prompt"] = f"You are a helpful assistant for Chat {i + 1}. Provide clear, concise responses."
                        unified_config["chats"][chat_key] = chat_config
        
        ConfigManager.save_unified_config(unified_config)
    
    @staticmethod
    def get_global_config():
        """Get global configuration settings."""
        unified_config = ConfigManager.load_unified_config()
        return unified_config.get("global", {"selected_model": DEFAULT_MODEL, "num_chats": DEFAULT_NUM_CHATS})
    
    @staticmethod
    def get_num_chats():
        """Get the configured number of chats."""
        global_config = ConfigManager.get_global_config()
        return global_config.get("num_chats", DEFAULT_NUM_CHATS)