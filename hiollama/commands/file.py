"""File operation commands."""
from typing import List
from rich import print
from pathlib import Path
from ..types import CommandResult, ActionType
from .registry import registry
from .types import CommandCategory


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


# New hierarchical file commands
@registry.register("file.load", "Load a file and send it with a prompt", category=CommandCategory.FILE)
def cmd_file_load(handler, filepath: str, prompt: str) -> CommandResult:
    """Load a file and send it with a prompt."""
    return cmd_load(handler, filepath, prompt)