"""History management services."""
from typing import NamedTuple
import json


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
    
    def save_history_to_file(self, save_path):
        """Save current chat history to a .jsonl file. Returns number of messages saved."""
        history = getattr(self.app.chat_history, 'history', [])
        if not history:
            return 0
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                for msg in history:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
            return len(history)
        except Exception as e:
            print(f"\n[red]Error saving history: {e}[/red]")
            return 0

    def load_history_from_file(self, load_path):
        """Load chat history from a .jsonl file, overwriting current in-memory history. Returns number of messages loaded."""
        try:
            messages = []
            with open(load_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        msg = json.loads(line.strip())
                        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                            messages.append({"role": msg["role"], "content": msg["content"]})
                    except Exception:
                        continue
            self.app.chat_history.history = messages
            return len(messages)
        except Exception as e:
            print(f"\n[red]Error loading history: {e}[/red]")
            return 0
