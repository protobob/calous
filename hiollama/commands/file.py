"""File operation commands."""
from typing import List
from rich import print
from pathlib import Path
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


@registry.register("load", "Load and send file with prompt", category=CommandCategory.FILE)
def cmd_load(handler, filepath: str, prompt: str) -> CommandResult:
    """Load a file and send it with a prompt."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            print(f"[bold red]Error:[/bold red] File not found: {filepath}")
            return CommandResult(ActionType.CONTINUE)
        
        if not file_path.is_file():
            print(f"[bold red]Error:[/bold red] Path is not a file: {filepath}")
            return CommandResult(ActionType.CONTINUE)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    file_content = f.read()
            except Exception as e:
                print(f"[bold red]Error:[/bold red] Cannot read file: {e}")
                return CommandResult(ActionType.CONTINUE)
        
        # Combine file content with prompt
        full_prompt = f"{prompt}\n\nFile content from {file_path.name}:\n```\n{file_content}\n```"
        
        print(f"Loading file: {file_path.name} ({len(file_content)} chars)")
        print(f"Prompt: {prompt}")
        
        # Send the combined prompt
        handler.app.handle_regular_input(full_prompt)
        
    except Exception as e:
        print(f"[bold red]Error loading file:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)


@registry.register("save", "Save conversation to file", category=CommandCategory.FILE)
def cmd_save(handler, filename: str) -> CommandResult:
    """Save the current conversation to a text file."""
    try:
        save_path = Path(filename)
        
        # Ensure .txt extension
        if not save_path.suffix:
            save_path = save_path.with_suffix('.txt')
        
        # Get conversation history
        history = handler.app.get_full_history()
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(f"Chat Session Export\n")
            f.write(f"Model: {handler.app.current_model}\n")
            f.write(f"System Prompt: {handler.app.system_prompt.get('content', 'None')}\n")
            f.write("=" * 50 + "\n\n")
            
            for msg in history:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                f.write(f"{role}:\n{content}\n\n" + "-" * 30 + "\n\n")
        
        print(f"Conversation saved to: {save_path.absolute()}")
        
    except Exception as e:
        print(f"[bold red]Error saving conversation:[/bold red] {e}")
    
    return CommandResult(ActionType.CONTINUE)