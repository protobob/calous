"""Persona command services module."""
from typing import Optional, Dict, Any, List
from ...persona import PersonaManager


class PersonaResult:
    """Result object for persona operations."""
    
    def __init__(self, success: bool, error_message: str = "", 
                 cancelled: bool = False, data: Any = None):
        self.success = success
        self.error_message = error_message
        self.cancelled = cancelled
        self.data = data


class PersonaService:
    """Service for persona operations."""
    
    @staticmethod
    def validate_slot(slot: int) -> PersonaResult:
        """Validate that slot is in valid range."""
        if not (0 <= slot <= 9):
            return PersonaResult(success=False, error_message="Slot must be between 0 and 9.")
        return PersonaResult(success=True)
    
    @staticmethod
    def validate_content(content) -> PersonaResult:
        """Validate and process content input."""
        # Handle both single strings and lists (from nargs='+')
        if isinstance(content, list):
            content = ' '.join(content)
        
        if not content.strip():
            return PersonaResult(success=False, error_message="Content cannot be empty.")
        
        return PersonaResult(success=True, data=content.strip())
    
    @staticmethod
    def validate_name(name) -> PersonaResult:
        """Validate and process name input."""
        # Handle both single strings and lists (from nargs='+')
        if isinstance(name, list):
            name = ' '.join(name)
        
        if not name.strip():
            return PersonaResult(success=False, error_message="Name cannot be empty.")
        
        return PersonaResult(success=True, data=name.strip())
    
    @staticmethod
    def set_persona_slot(app, slot: int, content: str) -> PersonaResult:
        """Set content for a persona slot."""
        try:
            app.persona.set_slot(slot, content)
            app.save_config()
            return PersonaResult(success=True)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def get_persona_slot(app, slot: int) -> PersonaResult:
        """Get content for a persona slot."""
        try:
            content = app.persona.get_slot(slot)
            return PersonaResult(success=True, data=content)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def clear_persona_slot(app, slot: int) -> PersonaResult:
        """Clear content for a persona slot."""
        try:
            if not app.persona.get_slot(slot):
                return PersonaResult(success=False, error_message=f"Slot {slot} is already empty.")
            
            app.persona.clear_slot(slot)
            app.save_config()
            return PersonaResult(success=True)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def set_persona_name(app, name: str) -> PersonaResult:
        """Set persona name."""
        try:
            app.persona.set_name(name)
            app.save_config()
            return PersonaResult(success=True)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def get_persona_info(app) -> PersonaResult:
        """Get complete persona information."""
        try:
            data = {
                'name': app.persona.name,
                'slots': app.persona.slots,
                'has_content': app.persona.has_content(),
                'combined_prompt': app.persona.get_combined_prompt() if app.persona.has_content() else None
            }
            return PersonaResult(success=True, data=data)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def reset_persona(app) -> PersonaResult:
        """Reset persona completely."""
        try:
            if app.persona.is_empty():
                return PersonaResult(success=False, error_message="Persona is already empty.")
            
            app.persona.reset()
            app.save_config()
            return PersonaResult(success=True)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def save_persona(app) -> PersonaResult:
        """Save current persona to file."""
        try:
            if not app.persona.name:
                return PersonaResult(
                    success=False, 
                    error_message="You must set a persona name before saving."
                )
            
            if not app.persona.has_content():
                return PersonaResult(
                    success=False, 
                    error_message="Persona has no slot content to save."
                )
            
            manager = PersonaManager()
            success = manager.save_persona(app.persona.name, app.persona.slots)
            return PersonaResult(success=success)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def load_persona(app, name: str) -> PersonaResult:
        """Load persona from file."""
        try:
            manager = PersonaManager()
            data = manager.load_persona(name)
            
            if data:
                app.persona.load_from_data(data)
                app.save_config()
                return PersonaResult(success=True, data=name)
            else:
                return PersonaResult(success=False, error_message=f"Failed to load persona '{name}'")
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def list_personas() -> PersonaResult:
        """List all saved personas."""
        try:
            manager = PersonaManager()
            personas = manager.list_personas()
            return PersonaResult(success=True, data=personas)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
    
    @staticmethod
    def delete_persona(name: str) -> PersonaResult:
        """Delete a saved persona file."""
        try:
            manager = PersonaManager()
            success = manager.delete_persona(name)
            return PersonaResult(success=success)
        except Exception as e:
            return PersonaResult(success=False, error_message=str(e))
