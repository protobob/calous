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
            # Error will be handled by caller
            return 0

    def load_history_from_file(self, load_path):
        """Load chat history from a .jsonl file, overwriting current in-memory history and .history file. Returns number of messages loaded."""
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
            
            # Update in-memory history
            self.app.chat_history.history = messages
            
            # Overwrite the .history file with loaded messages
            history_file = self.app.chat_history._get_history_filename()
            try:
                with open(history_file, 'w', encoding='utf-8') as f:
                    for msg in messages:
                        # Create full message data for file storage
                        from datetime import datetime
                        message_data = {
                            "timestamp": datetime.now().isoformat(),
                            "role": msg["role"],
                            "content": msg["content"],
                            "model": getattr(self.app, 'selected_model', None),
                            "chat_index": self.app.instance_index
                        }
                        f.write(json.dumps(message_data, ensure_ascii=False) + '\n')
            except Exception:
                # If file write fails, still return success for in-memory load
                pass
                
            return len(messages)
        except Exception as e:
            # Error will be handled by caller
            return 0
    
    def purge_history(self, num_entries: int) -> int:
        """Purge the most recent N entries from the current chat's history. Returns number purged."""
        history = self.app.chat_history.history
        total = len(history)
        n = max(0, min(num_entries, total))
        if n == 0:
            return 0
        del history[-n:]
        self.app.chat_history.history = history
        # Overwrite the history file with the new history
        history_file = self.app.chat_history._get_history_filename()
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                for msg in history:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        except Exception as e:
            # Error will be handled by caller
            pass
        return n
