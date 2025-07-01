"""Prompt command services module."""
from typing import Optional, Dict, List


class PromptResult:
    """Result object for prompt operations."""
    
    def __init__(self, success: bool, prompt_content: str = "", 
                 error_message: str = "", is_empty: bool = False):
        self.success = success
        self.prompt_content = prompt_content
        self.error_message = error_message
        self.is_empty = is_empty


class PromptService:
    """Service for prompt operations."""
    
    @staticmethod
    def validate_slot(slot: int, max_prompts: int) -> PromptResult:
        """Validate if a prompt slot is within valid range."""
        if not (1 <= slot <= max_prompts):
            return PromptResult(success=False, error_message=f"Slot must be between 1 and {max_prompts}")
        
        return PromptResult(success=True)
    
    @staticmethod
    def validate_prompt_text(prompt_text: str) -> PromptResult:
        """Validate if prompt text is not empty."""
        if not prompt_text.strip():
            return PromptResult(success=False, error_message="Prompt text cannot be empty")
        
        return PromptResult(success=True)
    
    @staticmethod
    def get_prompt_key(slot: int) -> str:
        """Get the key used to store the prompt in app.prompts dictionary."""
        return f"prompt{slot}"
    
    @staticmethod
    def set_prompt(app, slot: int, prompt_text: str) -> PromptResult:
        """Set a prompt in the given slot."""
        from ...constants import MAX_PROMPTS
        
        # Validate slot
        slot_result = PromptService.validate_slot(slot, MAX_PROMPTS)
        if not slot_result.success:
            return slot_result
        
        # Validate prompt text
        text_result = PromptService.validate_prompt_text(prompt_text)
        if not text_result.success:
            return text_result
        
        # Set the prompt and save config
        prompt_key = PromptService.get_prompt_key(slot)
        app.prompts[prompt_key] = prompt_text
        app.save_config()
        
        return PromptResult(success=True, prompt_content=prompt_text)
    
    @staticmethod
    def get_prompt(app, slot: int) -> PromptResult:
        """Get a prompt from the given slot."""
        from ...constants import MAX_PROMPTS
        
        # Validate slot
        slot_result = PromptService.validate_slot(slot, MAX_PROMPTS)
        if not slot_result.success:
            return slot_result
        
        # Get the prompt content
        prompt_key = PromptService.get_prompt_key(slot)
        prompt_content = app.prompts.get(prompt_key, "")
        
        if not prompt_content:
            return PromptResult(
                success=False, 
                error_message=f"Prompt{slot} is not set", 
                is_empty=True
            )
        
        return PromptResult(success=True, prompt_content=prompt_content)
    
    @staticmethod
    def get_all_prompts(app) -> Dict[int, str]:
        """Get all prompts as a dictionary mapping slot number to content."""
        from ...constants import MAX_PROMPTS
        
        result = {}
        for slot in range(1, MAX_PROMPTS + 1):
            prompt_key = PromptService.get_prompt_key(slot)
            prompt_content = app.prompts.get(prompt_key, "")
            result[slot] = prompt_content
        
        return result
