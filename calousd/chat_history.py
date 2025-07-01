"""Chat history management for Hi, Ollama!"""
import json
from datetime import datetime
from pathlib import Path
from .utils import get_chat_color
from .unified_logger import unified_logger
from .constants import HISTORY_DIR

class ChatHistory:    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            print(message)
    
    def __init__(self, app, instance_index):
        self.app = app
        self.instance_index = instance_index
        self.history = []
        self.history_file = None
        self._ensure_history_dirs()
        self._load_existing_history()
        
    def _ensure_history_dirs(self):
        """Ensure the history directory exists."""
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        
    def _load_existing_history(self):
        """Load existing history from file if it exists."""
        try:
            history_file = self._get_history_filename()
            if history_file.exists():
                messages_loaded = 0
                with open(history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            message_data = json.loads(line.strip())
                            # Extract just the role and content for the in-memory history
                            role = message_data.get('role', '')
                            content = message_data.get('content', '')
                            if role and content:
                                self.history.append({"role": role, "content": content})
                                messages_loaded += 1
                        except json.JSONDecodeError:
                            # Skip malformed lines
                            continue
                if messages_loaded > 0:
                    # Only show loading message in debug mode
                    if hasattr(self.app, 'session_manager') and hasattr(self.app.session_manager, 'debug') and self.app.session_manager.debug:
                        self._output(f"[dim green]Loaded {messages_loaded} messages from chat history[/dim green]")
                    
        except Exception as e:
            # Don't crash if loading fails, just start with empty history
            self._output(f"[dim red]Warning: Failed to load chat history: {e}[/dim red]")
            self.history = []
    
    def _get_history_filename(self):
        """Get history filename for current chat (simple, persistent naming)."""
        if self.history_file is None:
            self.history_file = HISTORY_DIR / f"chat_{self.instance_index + 1:03d}.jsonl"
        return self.history_file
        
    def _save_message_to_file(self, role, content):
        """Save a single message to the history file in JSONL format."""
        try:
            history_file = self._get_history_filename()
            message_data = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "model": getattr(self.app, 'selected_model', None),
                "chat_index": self.instance_index
            }
            
            # Append to JSONL file (one JSON object per line)
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message_data, ensure_ascii=False) + '\n')
                
        except Exception as e:
            # Don't crash the app if history saving fails, just log it
            self._output(f"[dim red]Warning: Failed to save message to history file: {e}[/dim red]")
    
    def _delete_history_file(self):
        """Delete the current chat's history file."""
        history_file = self._get_history_filename()
        if history_file.exists():
            try:
                history_file.unlink()
                self._output(f"[dim green]History file deleted: {history_file.name}[/dim green]")
            except Exception as e:
                self._output(f"[dim red]Warning: Failed to delete history file: {e}[/dim red]")
    
    def add_message(self, role, content):
        """Add a message to the chat history."""
        # Check if history is enabled for this chat
        if not getattr(self.app, 'history_enabled', True):
            # History is disabled, skip adding to history and file
            # Still log to unified logger if logging is enabled
            model = getattr(self.app, 'selected_model', None) or ""
            unified_logger.log_conversation(self.instance_index, role, content, model)
            return
            
        self.history.append({"role": role, "content": content})
        
        # Save message to history file immediately
        self._save_message_to_file(role, content)
        
        # Log to unified logger
        model = getattr(self.app, 'selected_model', None) or ""
        unified_logger.log_conversation(self.instance_index, role, content, model)

    def print_history(self):
        """Display the current chat history with styled formatting."""
        chat_color = get_chat_color(self.app.active_chat_index)
        
        # Start header with CHAT # in the chat color
        self._output(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]START CHAT {self.app.active_chat_index + 1} HISTORY[/bold {chat_color}]\n")
        
        if not self.history:
            self._output(f"[bold {chat_color}]|[/bold {chat_color}] [grey70]No messages in history.[/grey70]")
        else:
            for i, msg in enumerate(self.history, 1):
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                
                # Color code the role
                if role == "USER":
                    role_color = "bold"
                elif role == "ASSISTANT":
                    role_color = "cyan"
                else:
                    role_color = "grey70"
                
                # Display message with consistent formatting
                self._output(f"[bold {chat_color}]|[/bold {chat_color}] [{role_color}]{role}[/{role_color}]: [grey70]{content}[/grey70]")
          # End header with CHAT # in the chat color
        self._output(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]END CHAT {self.app.active_chat_index + 1} HISTORY[/bold {chat_color}]\n")

    def clear(self):
        """Clear the chat history."""
        self.history = []
        
        # Delete the history file when clearing
        self._delete_history_file()
        
        # Reset history file for new conversation
        self.history_file = None
        
        # Log the clear action
        unified_logger.log_chat_history_clear(self.instance_index)