"""Chat management services."""
from typing import Optional, NamedTuple


class ChatOperationResult(NamedTuple):
    success: bool
    error_message: Optional[str] = None
    chat_number: Optional[int] = None
    target_index: Optional[int] = None
    content: Optional[str] = None


class ChatInfo(NamedTuple):
    number: int
    color: str
    chat_index: int


class ChatService:
    """Service for managing chat operations."""
    
    def __init__(self, app):
        self.app = app
    
    
    def validate_switch(self, chat_number: Optional[int]) -> ChatOperationResult:
        """Validate chat switch operation."""
        if chat_number is not None:
            if chat_number < 1:
                return ChatOperationResult(
                    success=False,
                    error_message="Chat number must be 1 or greater."
                )
            target_index = chat_number - 1  # Convert to 0-based index
            if target_index >= self.app.session_manager.num_chats:
                return ChatOperationResult(
                    success=False,
                    error_message=f"Chat number {chat_number} does not exist. Available chats: 1-{self.app.session_manager.num_chats}."
                )
        else:
            target_index = None

        return ChatOperationResult(
            success=True,
            target_index=target_index
        )
    
    
    def validate_twist(self, target_chat: Optional[int]) -> ChatOperationResult:
        """Validate twist operation."""
        # Validate last response exists
        last_response = self.app.last_response
        if not last_response:
            return ChatOperationResult(
                success=False,
                error_message="No previous response to twist. Generate an AI response first."
            )
        
        # Extract content
        twist_content = last_response.get("message", {}).get("content", "")
        if not twist_content:
            return ChatOperationResult(
                success=False,
                error_message="Previous response is empty or invalid format."
            )
        
        # With native Ollama API, last_response already contains clean content (no thinking)
        clean_twist_content = twist_content
        if not clean_twist_content:
            return ChatOperationResult(
                success=False,
                error_message="No valid content to twist."
            )
        
        # Process target chat
        target_index = None
        if target_chat is not None:
            if target_chat < 1:
                return ChatOperationResult(
                    success=False,
                    error_message="Target chat number must be 1 or greater."
                )
            target_index = target_chat - 1  # Convert to 0-based index
        
        return ChatOperationResult(
            success=True,
            content=clean_twist_content,
            target_index=target_index
        )
    
    def get_chat_info(self) -> ChatInfo:
        """Get basic information about the current chat."""
        from ...utils import get_chat_color
        
        chat_number = self.app.instance_index + 1
        chat_color = get_chat_color(self.app.instance_index)
        
        return ChatInfo(
            number=chat_number,
            color=chat_color,
            chat_index=self.app.instance_index
        )
    
    def reset_to_defaults(self) -> bool:
        """Reset the chat instance to factory defaults."""
        try:
            from ...config import ConfigManager
            
            # Get the default chat configuration
            default_config = ConfigManager._generate_default_chat_config()
            
            # Update the chat instance with default values
            self.app.verbosity = default_config["verbosity"]
            self.app.system_prompt = {
                "role": "system",
                "content": default_config["system_prompt"]
            }
            self.app.logging_enabled = default_config["logging_enabled"]
            self.app.thinking_enabled = False  # Default to False for clean output
            self.app.prompts = default_config["prompts"]
            
            # Clear chat history
            self.app.chat_history.clear()
            
            # Reset persona to default empty state
            self.app.persona.reset()
            
            # Save the updated configuration
            self.app.save_config()
            
            return True
            
        except Exception:
            return False
    
    def show_chat_variables(self):
        """Display chat-specific variables."""
        self.app.ui.show_chat_variables()
