"""Service layer for chat management operations."""
from typing import Dict, Any
from ..config import ConfigManager


class ChatService:
    """Service class for chat management operations."""
    
    @staticmethod
    def reset_chat_to_defaults(app) -> bool:
        """Reset the chat instance to factory defaults.
        
        Args:
            app: The application instance containing chat state
            
        Returns:
            bool: True if reset was successful, False otherwise
        """
        try:
            # Get the default chat configuration
            default_config = ConfigManager._generate_default_chat_config()
            
            # Update the chat instance with default values
            app.verbosity = default_config["verbosity"]
            app.system_prompt = {
                "role": "system",
                "content": default_config["system_prompt"]
            }
            app.logging_enabled = default_config["logging_enabled"]
            app.thinking_enabled = False  # Default to False for clean output
            app.prompts = default_config["prompts"]
            
            # Clear chat history
            app.chat_history.clear()
            
            # Save the updated configuration
            app.save_config()
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_chat_info(app) -> Dict[str, Any]:
        """Get basic information about the current chat.
        
        Args:
            app: The application instance
            
        Returns:
            Dict containing chat number and color information
        """
        from ..utils import get_chat_color
        
        chat_number = app.instance_index + 1
        chat_color = get_chat_color(app.instance_index)
        
        return {
            "number": chat_number,
            "color": chat_color,
            "index": app.instance_index
        }
