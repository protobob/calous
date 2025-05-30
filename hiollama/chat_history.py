"""Chat history management for Hi, Ollama!"""
import re
from datetime import datetime
from pathlib import Path
from rich import print
from .utils import get_chat_color
from .unified_logger import unified_logger

class ChatHistory:
    def __init__(self, app, instance_index):
        self.app = app
        self.instance_index = instance_index
        self.history = []
        
    def add_message(self, role, content):
        """Add a message to the chat history, respecting the maximum history limit."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.app.MAX_HISTORY:
            self.history.pop(0)
        
        # Log to unified logger
        model = getattr(self.app, 'selected_model', None)
        unified_logger.log_conversation(self.instance_index, role, content, model)

    def strip_thoughts(self, text):
        """Remove <think>...</think> sections from text."""
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def print_history(self):
        """Display the current chat history with styled formatting."""
        chat_color = get_chat_color(self.app.active_chat_index)
        
        # Start header with CHAT # in the chat color
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]START CHAT {self.app.active_chat_index + 1} HISTORY[/bold {chat_color}]\n")
        
        if not self.history:
            print(f"[bold {chat_color}]|[/bold {chat_color}] [grey70]No messages in history.[/grey70]")
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
                print(f"[bold {chat_color}]|[/bold {chat_color}] [{role_color}]{role}[/{role_color}]: [grey70]{content}[/grey70]")
          # End header with CHAT # in the chat color
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]END CHAT {self.app.active_chat_index + 1} HISTORY[/bold {chat_color}]\n")

    def clear(self):
        """Clear the chat history."""
        self.history = []
        
        # Log the clear action
        unified_logger.log_chat_history_clear(self.instance_index)