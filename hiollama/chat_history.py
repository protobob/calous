"""Chat history management for Hi, Ollama!"""
import re
from datetime import datetime
from pathlib import Path
from rich import print
from .constants import LOG_DIR

class ChatHistory:
    def __init__(self, app):
        self.app = app
        self.history = []
        
    def add_message(self, role, content):
        """Add a message to the chat history, respecting the maximum history limit."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.app.MAX_HISTORY:
            self.history.pop(0)

    def strip_thoughts(self, text):
        """Remove <think>...</think> sections from text."""
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def print_history(self):
        """Display the current chat history."""
        print("\n--- Chat History ---")
        for msg in self.history:
            role = msg.get("role", "unknown").capitalize()
            print(f"[{role}] {msg['content']}")
        print("--------------------\n")
    
    def log_file(self, prompt, response):
        """Log the conversation to a file if logging is enabled."""
        if not self.app.logging_enabled:
            return
        try:
            timestamp = datetime.now()
            log_dir = LOG_DIR
            log_dir.mkdir(exist_ok=True)
            log_filename = log_dir / f"{timestamp.strftime('%Y-%m-%d')}.txt"
            with open(log_filename, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp.strftime('%H:%M:%S')}] You: {prompt}\n")
                f.write(f"[{timestamp.strftime('%H:%M:%S')}] {self.app.selected_model}: {response}\n\n")
        except Exception as e:
            print(f"Failed to write chat log: {e}")

    def clear(self):
        """Clear the chat history."""
        self.history = []