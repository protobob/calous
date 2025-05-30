"""Prompt management commands."""
from typing import Optional
from rich import print
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory
from ..unified_logger import unified_logger


@registry.register("system", "Change system prompt", category=CommandCategory.PROMPT)
def cmd_system(handler, prompt: str) -> CommandResult:
    """Change the system prompt."""
    if not prompt.strip():
        print("\n[bold red]Error:[/bold red] System prompt cannot be empty.")
        return CommandResult(ActionType.CONTINUE)

    print(f"\nPrevious System Prompt: [grey50]{handler.app.system_prompt['content']}[/grey50]")
    handler.app.system_prompt = {"role": "system", "content": prompt}
    print(f"System prompt updated to: [grey50]{prompt}[/grey50]")
    
    # Log the system prompt change
    unified_logger.log_system_prompt_change(handler.app.instance_index, prompt)
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("setprompt", "Save a prompt to a slot", category=CommandCategory.PROMPT)
def cmd_setprompt(handler, slot: int, prompt: str) -> CommandResult:
    """Set a saved prompt."""
    from ..constants import MAX_PROMPTS
    
    if not (1 <= slot <= MAX_PROMPTS):
        print(f"[bold red]Error:[/bold red] Slot must be between 1 and {MAX_PROMPTS}.")
        return CommandResult(ActionType.CONTINUE)
    
    if not prompt.strip():
        print("[bold red]Error:[/bold red] Prompt text cannot be empty.")
        return CommandResult(ActionType.CONTINUE)
    
    handler.app.prompts[f"prompt{slot}"] = prompt
    print(f"Prompt{slot} set successfully!")
    handler.app.save_config()
    return CommandResult(ActionType.CONTINUE)


@registry.register("prompt", "Use a saved prompt", category=CommandCategory.PROMPT)
def cmd_prompt(handler, slot: int) -> CommandResult:
    """Use a saved prompt."""
    from ..constants import MAX_PROMPTS
    
    if not (1 <= slot <= MAX_PROMPTS):
        print(f"[bold red]Error:[/bold red] Slot must be between 1 and {MAX_PROMPTS}.")
        return CommandResult(ActionType.CONTINUE)
    
    selected_prompt = handler.app.prompts[f"prompt{slot}"]
    if not selected_prompt:
        print(f"[bold red]Error:[/bold red] Prompt{slot} is not set.")
        return CommandResult(ActionType.CONTINUE)
    
    print(f"Using Prompt{slot}: {selected_prompt}")
    handler.app.handle_regular_input(selected_prompt)
    return CommandResult(ActionType.CONTINUE)


@registry.register("showprompt", "Display saved prompts", aliases=["prompts"], category=CommandCategory.PROMPT)
def cmd_showprompt(handler, slot: Optional[int] = None) -> CommandResult:
    """Display saved prompts."""
    from ..constants import MAX_PROMPTS
    
    if slot is not None:
        if not (1 <= slot <= MAX_PROMPTS):
            print(f"[bold red]Error:[/bold red] Slot must be between 1 and {MAX_PROMPTS}.")
            return CommandResult(ActionType.CONTINUE)
        
        prompt_content = handler.app.prompts.get(f"prompt{slot}", "")
        if prompt_content:
            print(f"Prompt{slot}: {prompt_content}")
        else:
            print(f"Prompt{slot} is not set.")
    else:
        # Show all prompts
        print("\n[bold]Saved Prompts:[/bold]")
        found_any = False
        for i in range(1, MAX_PROMPTS + 1):
            prompt_content = handler.app.prompts.get(f"prompt{i}", "")
            if prompt_content:
                print(f"  Prompt{i}: {prompt_content}")
                found_any = True
        
        if not found_any:
            print("  No prompts saved.")
    
    return CommandResult(ActionType.CONTINUE)