"""Prompt commands module."""
from typing import Optional
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import PromptService
from .formatters import PromptFormatter


@registry.register("prompt.set", "Save a prompt", category=CommandCategory.PROMPT)
def cmd_prompt_set(handler, slot: int, prompt: str) -> CommandResult:
    """Set a saved prompt."""
    from ...constants import MAX_PROMPTS
    
    formatter = PromptFormatter()
    
    # Use the service to validate and set the prompt
    result = PromptService.set_prompt(handler.app, slot, prompt)
    
    if not result.success:
        if "Slot" in result.error_message:
            formatter.prompt_slot_error(MAX_PROMPTS)
        elif "empty" in result.error_message:
            formatter.prompt_empty_error()
        else:
            formatter.print_error(result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    formatter.prompt_set_success(slot)
    return CommandResult(ActionType.CONTINUE)


@registry.register("prompt.use", "Use a saved prompt", category=CommandCategory.PROMPT)
def cmd_prompt_use(handler, slot: int) -> CommandResult:
    """Use a saved prompt."""
    from ...utils import get_chat_color
    
    formatter = PromptFormatter()
    
    # Use the service to get the prompt
    result = PromptService.get_prompt(handler.app, slot)
    
    if not result.success:
        if result.is_empty:
            formatter.prompt_not_set_error(slot)
        else:
            formatter.print_error(result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    # Get chat color for consistent styling
    chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
    
    # Display and use the prompt
    formatter.using_prompt(chat_color, slot, result.prompt_content)
    handler.app.handle_regular_input(result.prompt_content)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("prompt.list", "List all saved prompts", category=CommandCategory.PROMPT)
def cmd_prompt_list(handler, slot: Optional[int] = None) -> CommandResult:
    """Display saved prompts."""
    from ...constants import MAX_PROMPTS
    from ...utils import get_chat_color
    
    formatter = PromptFormatter()
    
    # Get chat color for consistent styling
    chat_color = get_chat_color(getattr(handler.app, 'active_chat_index', 0))
    active_chat_index = getattr(handler.app, 'active_chat_index', 0)
    
    if slot is not None:
        # Show a specific prompt
        result = PromptService.get_prompt(handler.app, slot)
        
        if not result.success:
            if "Slot" in result.error_message:
                formatter.prompt_slot_error(MAX_PROMPTS)
            elif result.is_empty:
                formatter.prompt_not_set_error(slot)
            else:
                formatter.print_error(result.error_message)
            return CommandResult(ActionType.CONTINUE)
        
        formatter.show_single_prompt(chat_color, active_chat_index, slot, result.prompt_content)
    else:
        # Show all prompts
        formatter.show_prompt_list_header(chat_color, active_chat_index)
        
        all_prompts = PromptService.get_all_prompts(handler.app)
        for slot_num, content in all_prompts.items():
            formatter.show_prompt_list_item(chat_color, slot_num, content)
        
        self._output()  # Add spacing after output
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("prompt.help", "Show help for prompt commands", category=CommandCategory.PROMPT)
def cmd_prompt_help(handler) -> CommandResult:
    """Show help for prompt commands - alias for /sys.help prompt."""
    handler.app.ui.show_category_help("prompt")
    return CommandResult(ActionType.CONTINUE)
