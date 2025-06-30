"""Configuration management for Hi, Ollama!"""
import json
from rich import print as rich_print
from .constants import CONFIG_PATH, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS, DEFAULT_NUM_CHATS, DEFAULT_NUM_CTX, DEFAULT_KEEP_ALIVE

class ConfigManager:
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
    @staticmethod    
    def _generate_default_chat_config():
        """Generate default configuration for a chat instance."""
        return {
            "verbosity": True,
            "system_prompt": DEFAULT_SYSTEM_PROMPT,
            "logging_enabled": True,
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
                "num_chats": num_chats,
                "num_ctx": DEFAULT_NUM_CTX,
                "keep_alive": DEFAULT_KEEP_ALIVE
            },
            "chats": {}
        }
          # Generate chat configs dynamically (all with blank system prompts)
        for i in range(num_chats):
            config["chats"][str(i)] = ConfigManager._generate_default_chat_config()
        
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
            CommandFormatter._output(f"\nError loading config: {e}")
            CommandFormatter._output("Creating new default configuration...")
            return ConfigManager._generate_default_unified_config()
    
    @staticmethod
    def save_unified_config(config):
        """Save the unified configuration file."""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            CommandFormatter._output(f"\nError saving config: {e}")
    @staticmethod
    def get_chat_config(instance_index):
        """Get configuration for a specific chat instance."""
        unified_config = ConfigManager.load_unified_config()
        
        chat_key = str(instance_index)
        if chat_key in unified_config.get("chats", {}):
            return unified_config["chats"][chat_key]
        
        # Generate default config for new chat instances (all get blank system prompts)
        return ConfigManager._generate_default_chat_config()
    
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
        unified_config["global"].update(global_updates)                # If num_chats changed, ensure we have configs for all chats
        if "num_chats" in global_updates:
            new_num_chats = global_updates["num_chats"]
            for i in range(new_num_chats):
                chat_key = str(i)
                if chat_key not in unified_config.get("chats", {}):
                    # Generate missing chat config (all with blank system prompts)
                    unified_config["chats"][chat_key] = ConfigManager._generate_default_chat_config()
        
        ConfigManager.save_unified_config(unified_config)
      
    @staticmethod
    def get_global_config():
        """Get global configuration settings."""
        unified_config = ConfigManager.load_unified_config()
        return unified_config.get("global", {"selected_model": DEFAULT_MODEL, "num_chats": DEFAULT_NUM_CHATS, "num_ctx": DEFAULT_NUM_CTX, "keep_alive": DEFAULT_KEEP_ALIVE})
    
    @staticmethod
    def get_global_num_ctx():
        """Get the global context window setting."""
        global_config = ConfigManager.get_global_config()
        return global_config.get("num_ctx", DEFAULT_NUM_CTX)
    
    @staticmethod
    def set_global_num_ctx(num_ctx):
        """Set the global context window setting."""
        ConfigManager.update_global_config({"num_ctx": num_ctx})
    
    @staticmethod
    def get_num_chats():
        """Get the configured number of chats."""
        global_config = ConfigManager.get_global_config()
        return global_config.get("num_chats", DEFAULT_NUM_CHATS)
    
    @staticmethod
    def get_keep_alive():
        """Get the global keep_alive setting."""
        global_config = ConfigManager.get_global_config()
        return global_config.get("keep_alive", DEFAULT_KEEP_ALIVE)
    
    @staticmethod
    def get_aliases():
        """Get user-defined command aliases from config."""
        global_config = ConfigManager.get_global_config()
        return global_config.get("aliases", {})
    
    @staticmethod
    def add_alias(alias, command):
        """Add a user-defined command alias."""
        unified_config = ConfigManager.load_unified_config()
        
        # Ensure global section exists
        if "global" not in unified_config:
            unified_config["global"] = {}
        
        # Ensure aliases section exists
        if "aliases" not in unified_config["global"]:
            unified_config["global"]["aliases"] = {}
        
        # Add the alias
        unified_config["global"]["aliases"][alias] = command
        
        ConfigManager.save_unified_config(unified_config)
    
    @staticmethod
    def remove_alias(alias):
        """Remove a user-defined command alias."""
        unified_config = ConfigManager.load_unified_config()
        
        # Check if aliases exist
        if ("global" in unified_config and 
            "aliases" in unified_config["global"] and 
            alias in unified_config["global"]["aliases"]):
            
            del unified_config["global"]["aliases"][alias]
            ConfigManager.save_unified_config(unified_config)
            return True
        return False
    
    @staticmethod
    def list_aliases():
        """List all user-defined command aliases."""
        return ConfigManager.get_aliases()