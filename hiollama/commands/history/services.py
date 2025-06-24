"""History management services."""
from typing import NamedTuple


class ChatInfo(NamedTuple):
    number: int
    color: str
    chat_index: int


class HistoryService:
    """Service for managing history operations."""
    
    def __init__(self, app):
        self.app = app
    
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
    
    def clear_history(self):
        """Clear the chat history."""
        self.app.chat_history.clear()
    
    def display_history(self):
        """Display the chat history."""
        self.app.chat_history.print_history()
    
    def enable_history(self):
        """Enable chat history recording."""
        self.app.history_enabled = True
        
    def disable_history(self):
        """Disable chat history recording."""
        self.app.history_enabled = False
        
    def get_history_status(self) -> bool:
        """Get the current history status."""
        return getattr(self.app, 'history_enabled', True)
