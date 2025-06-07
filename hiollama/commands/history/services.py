"""History management services."""
from typing import NamedTuple


class ChatInfo(NamedTuple):
    number: int
    color: str
    index: int


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
            index=self.app.instance_index
        )
    
    def clear_history(self):
        """Clear the chat history."""
        self.app.chat_history.clear()
    
    def display_history(self):
        """Display the chat history."""
        self.app.chat_history.print_history()
