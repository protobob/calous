"""Unified logging system for Hi, Ollama!"""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from .constants import LOG_DIR


class UnifiedLogger:
    """Handles unified logging across all chat channels and system events."""
    
    def __init__(self):
        self.enabled = True
    
    def _get_log_file_path(self) -> Path:
        """Get the current log file path based on today's date."""
        timestamp = datetime.now()
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        return LOG_DIR / f"{timestamp.strftime('%Y-%m-%d')}.txt"
    
    def _write_log_entry(self, entry_type: str, content: str, chat_index: Optional[int] = None):
        """Write a formatted log entry to the unified log file."""
        if not self.enabled:
            return
            
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_file = self._get_log_file_path()
            
            # Format the log entry
            chat_info = f"[Chat {chat_index + 1}]" if chat_index is not None else "[System]"
            log_entry = f"[{timestamp}] {chat_info} {entry_type}: {content}\n"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Failed to write unified log: {e}")
    
    def log_conversation(self, chat_index: int, role: str, content: str, model: Optional[str] = None):
        """Log a conversation message."""
        if role.lower() == "user":
            self._write_log_entry("USER", content, chat_index)
        elif role.lower() == "assistant":
            model_info = f" ({model})" if model else ""
            self._write_log_entry(f"ASSISTANT{model_info}", content, chat_index)
        else:
            self._write_log_entry(f"{role.upper()}", content, chat_index)
    
    def log_channel_switch(self, from_chat: int, to_chat: int, reason: str = "manual"):
        """Log channel switching events."""
        self._write_log_entry("CHANNEL_SWITCH", f"From Chat {from_chat + 1} to Chat {to_chat + 1} ({reason})")
    
    def log_twist_action(self, from_chat: int, to_chat: int, content_preview: str):
        """Log twist actions between channels."""
        preview = content_preview.replace('\n', ' ').strip()
        if len(preview) > 100:
            preview = preview[:100] + "..."
        self._write_log_entry("TWIST", f"From Chat {from_chat + 1} to Chat {to_chat + 1}: \"{preview}\"")
    
    def log_system_prompt_change(self, chat_index: int, new_prompt: str):
        """Log system prompt changes."""
        preview = new_prompt.replace('\n', ' ').strip()
        if len(preview) > 100:
            preview = preview[:100] + "..."
        self._write_log_entry("SYSTEM_PROMPT", f"\"{preview}\"", chat_index)
    
    def log_command_execution(self, chat_index: int, command: str, result: Optional[str] = None):
        """Log command execution."""
        if result:
            self._write_log_entry("COMMAND", f"{command} -> {result}", chat_index)
        else:
            self._write_log_entry("COMMAND", command, chat_index)
    
    def log_model_change(self, new_model: str, chat_count: int):
        """Log global model changes."""
        self._write_log_entry("MODEL_CHANGE", f"Changed to {new_model} (affecting {chat_count} chats)")
    
    def log_session_start(self, num_chats: int, model: str):
        """Log session startup."""
        self._write_log_entry("SESSION_START", f"Started with {num_chats} chats using model {model}")
    
    def log_session_end(self):
        """Log session shutdown."""
        self._write_log_entry("SESSION_END", "Application shutdown")
    
    def log_chat_history_clear(self, chat_index: int):
        """Log when chat history is cleared."""
        self._write_log_entry("HISTORY_CLEAR", "Chat history cleared", chat_index)
    
    def log_export_action(self, chat_index: int, filename: str):
        """Log chat export actions."""
        self._write_log_entry("EXPORT", f"Chat exported to {filename}", chat_index)
    
    def toggle_logging(self) -> bool:
        """Toggle unified logging on/off."""
        self.enabled = not self.enabled
        self._write_log_entry("LOGGING_TOGGLE", f"Logging {'enabled' if self.enabled else 'disabled'}")
        return self.enabled
    
    def add_separator(self, label: Optional[str] = None):
        """Add a visual separator to the log file."""
        if not self.enabled:
            return
            
        try:
            log_file = self._get_log_file_path()
            separator = "=" * 50
            if label:
                separator = f"=== {label} " + "=" * (44 - len(label))
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{separator}\n\n")
        except Exception as e:
            print(f"Failed to write log separator: {e}")
            
    def log_plugin_event(self, event_type: str, message: str):
        """Log plugin-related events."""
        self._write_log_entry(f"PLUGIN_{event_type.upper()}", message)


# Global unified logger instance
unified_logger = UnifiedLogger()
