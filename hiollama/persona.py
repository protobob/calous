"""Persona system for Hi, Ollama!"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from rich import print
from .constants import PERSONA_DIR


class PersonaManager:
    """Manages persona storage and operations."""
    
    def __init__(self):
        self.persona_dir = PERSONA_DIR
        self.persona_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize persona name for safe filename use."""
        # Replace invalid filename characters with underscores
        invalid_chars = '<>:"|?*\\/'
        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        return sanitized.strip()
    
    def save_persona(self, name: str, slots: Dict[int, str]) -> bool:
        """Save persona to file."""
        if not name.strip():
            print("[bold red]Error:[/bold red] Persona name cannot be empty.")
            return False
        
        sanitized_name = self.sanitize_filename(name)
        filepath = self.persona_dir / f"{sanitized_name}.json"
        
        # Check for overwrite protection
        if filepath.exists():
            from rich.prompt import Prompt
            confirm = Prompt.ask(
                f"\n[bold yellow]Warning:[/bold yellow] Persona '{name}' already exists. Overwrite?",
                choices=["y", "n"],
                default="n"
            )
            if confirm != 'y':
                print("Save operation cancelled.")
                return False
        
        persona_data = {
            "name": name,
            "slots": {str(k): v for k, v in slots.items() if v.strip()}
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(persona_data, f, indent=2, ensure_ascii=False)
            print(f"[bold green]Success:[/bold green] Persona '{name}' saved!")
            return True
        except Exception as e:
            print(f"[bold red]Error:[/bold red] Failed to save persona: {e}")
            return False
    
    def load_persona(self, name: str) -> Optional[Dict]:
        """Load persona from file."""
        sanitized_name = self.sanitize_filename(name)
        filepath = self.persona_dir / f"{sanitized_name}.json"
        
        if not filepath.exists():
            print(f"[bold red]Error:[/bold red] Persona '{name}' not found.")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[bold red]Error:[/bold red] Failed to load persona: {e}")
            return None
    
    def list_personas(self) -> List[str]:
        """List all saved personas."""
        if not self.persona_dir.exists():
            return []
        
        personas = []
        for file in self.persona_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    personas.append(data.get('name', file.stem))
            except Exception:
                # If we can't read the file, use the filename
                personas.append(file.stem)
        
        return sorted(personas)
    
    def delete_persona(self, name: str) -> bool:
        """Delete a saved persona."""
        sanitized_name = self.sanitize_filename(name)
        filepath = self.persona_dir / f"{sanitized_name}.json"
        
        if not filepath.exists():
            print(f"[bold red]Error:[/bold red] Persona '{name}' not found.")
            return False
        
        try:
            filepath.unlink()
            print(f"[bold green]Success:[/bold green] Persona '{name}' deleted!")
            return True
        except Exception as e:
            print(f"[bold red]Error:[/bold red] Failed to delete persona: {e}")
            return False


class Persona:
    """Represents a chat persona with named slots."""
    
    def __init__(self):
        self.name: str = ""
        self.slots: Dict[int, str] = {}
    
    def set_name(self, name: str):
        """Set the persona name."""
        self.name = name.strip()
    
    def set_slot(self, slot: int, content: str):
        """Set content for a specific slot."""
        if not (0 <= slot <= 9):
            raise ValueError("Slot must be between 0 and 9")
        
        content = content.strip()
        if content:
            self.slots[slot] = content
        elif slot in self.slots:
            # Remove empty slots
            del self.slots[slot]
    
    def get_slot(self, slot: int) -> str:
        """Get content for a specific slot."""
        if not (0 <= slot <= 9):
            raise ValueError("Slot must be between 0 and 9")
        return self.slots.get(slot, "")
    
    def clear_slot(self, slot: int):
        """Clear content for a specific slot."""
        if not (0 <= slot <= 9):
            raise ValueError("Slot must be between 0 and 9")
        
        if slot in self.slots:
            del self.slots[slot]
    
    def get_combined_prompt(self) -> str:
        """Get the combined system prompt from all non-empty slots."""
        if not self.slots:
            return ""
        
        # Sort slots by key and join with double newlines
        sorted_prompts = [self.slots[k] for k in sorted(self.slots.keys())]
        return "\n\n".join(p for p in sorted_prompts if p.strip())
    
    def reset(self):
        """Clear name and all slot contents."""
        self.name = ""
        self.slots.clear()
    
    def load_from_data(self, data: Dict):
        """Load persona from saved data."""
        self.name = data.get('name', '')
        self.slots.clear()
        
        slots_data = data.get('slots', {})
        for slot_str, content in slots_data.items():
            try:
                slot_num = int(slot_str)
                if 0 <= slot_num <= 9 and content.strip():
                    self.slots[slot_num] = content
            except ValueError:
                continue
    
    def to_dict(self) -> Dict:
        """Convert persona to dictionary for saving."""
        return {
            'name': self.name,
            'slots': {str(k): v for k, v in self.slots.items()}
        }
    
    def is_empty(self) -> bool:
        """Check if persona has no content."""
        return not self.name and not self.slots
    
    def has_content(self) -> bool:
        """Check if persona has any slot content."""
        return bool(self.slots)
