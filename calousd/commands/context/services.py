"""Context management services."""
import json
import os
from pathlib import Path
from typing import Optional, NamedTuple, Dict, Any
from ...constants import CONTEXT_DIR


class ContextOperationResult(NamedTuple):
    success: bool
    error_message: Optional[str] = None
    data: Optional[Any] = None


class ContextService:
    """Service for managing context operations."""
    
    def __init__(self, app):
        self.app = app
        self.context_dir = CONTEXT_DIR
        self.context_dir.mkdir(parents=True, exist_ok=True)
    
    def save_context(self, name: str) -> ContextOperationResult:
        """Save current context (persona, prompts, history) to a file."""
        try:
            # Collect all context data
            context_data = {
                "persona": {
                    "name": self.app.persona.name,
                    "slots": dict(self.app.persona.slots)
                },
                "prompts": dict(self.app.prompts),
                "chat_history": self.app.chat_history.history.copy()
            }
            
            # Save to file
            filepath = self.context_dir / f"{name}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
            
            return ContextOperationResult(
                success=True,
                data={"filepath": filepath, "name": name}
            )
            
        except Exception as e:
            return ContextOperationResult(
                success=False,
                error_message=f"Failed to save context: {str(e)}"
            )
    
    def load_context(self, name: str) -> ContextOperationResult:
        """Load context from a file (overwrites current data)."""
        try:
            filepath = self.context_dir / f"{name}.json"
            if not filepath.exists():
                return ContextOperationResult(
                    success=False,
                    error_message=f"Context file '{name}' not found"
                )
            
            # Load context data
            with open(filepath, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            # Apply persona data
            persona_data = context_data.get("persona", {})
            self.app.persona.name = persona_data.get("name", "")
            self.app.persona.slots = persona_data.get("slots", {})
            
            # Apply prompts
            prompts_data = context_data.get("prompts", {})
            self.app.prompts = prompts_data
            
            # Apply chat history
            history_data = context_data.get("chat_history", [])
            self.app.chat_history.history = history_data
            
            # Save the updated configuration
            self.app.save_config()
            
            return ContextOperationResult(
                success=True,
                data={"name": name, "filepath": filepath}
            )
            
        except Exception as e:
            return ContextOperationResult(
                success=False,
                error_message=f"Failed to load context: {str(e)}"
            )
    
    def list_contexts(self) -> ContextOperationResult:
        """List all saved context files."""
        try:
            if not self.context_dir.exists():
                return ContextOperationResult(
                    success=True,
                    data={"contexts": []}
                )
            
            # Get all .json files in the contexts directory
            context_files = []
            for filepath in sorted(self.context_dir.glob("*.json")):
                context_files.append({
                    "name": filepath.stem,
                    "size": filepath.stat().st_size,
                    "filepath": filepath
                })
            
            return ContextOperationResult(
                success=True,
                data={"contexts": context_files}
            )
            
        except Exception as e:
            return ContextOperationResult(
                success=False,
                error_message=f"Failed to list contexts: {str(e)}"
            )
    
    def delete_context(self, name: str) -> ContextOperationResult:
        """Delete a saved context file."""
        try:
            filepath = self.context_dir / f"{name}.json"
            if not filepath.exists():
                return ContextOperationResult(
                    success=False,
                    error_message=f"Context file '{name}' not found"
                )
            
            filepath.unlink()
            
            return ContextOperationResult(
                success=True,
                data={"name": name, "filepath": filepath}
            )
            
        except Exception as e:
            return ContextOperationResult(
                success=False,
                error_message=f"Failed to delete context: {str(e)}"
            )