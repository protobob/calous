"""File operation commands."""
from rich import print
from rich.prompt import Prompt
from pathlib import Path
import textwrap
from ..types import CommandResult, ActionType
from ..constants import MAX_FILE_SIZE, LARGE_FILE_WARNING_SIZE
from .registry import registry
from .types import CommandCategory

# Supported text file extensions
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
    '.ini', '.cfg', '.conf', '.log', '.sql', '.sh', '.bat', '.ps1', '.csv', '.tsv',
    '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.php', '.rb', '.go', '.rs', '.kt',
    '.swift', '.scala', '.clj', '.hs', '.elm', '.lua', '.r', '.m', '.pl', '.vim'
}

# Binary/executable extensions to warn about
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.img', '.iso', '.zip', '.rar', '.tar',
    '.gz', '.7z', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
}


def _read_file_content(file_path: Path) -> str:
    """Read file content with multiple encoding attempts and safety checks."""
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        print(f"\n[bold red]Error:[/bold red] File too large ({file_size:,} bytes). Maximum allowed: {MAX_FILE_SIZE:,} bytes")
        raise ValueError("File size exceeds limit")
    
    if file_size > LARGE_FILE_WARNING_SIZE:
        print(f"\n[bold yellow]Warning:[/bold yellow] Large file ({file_size:,} bytes). This may take a moment to process.")
        confirm = Prompt.ask("Continue loading this large file?", choices=["y", "n"], default="n")
        if confirm.lower() != "y":
            raise ValueError("User cancelled large file load")
    
    # Try multiple encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise ValueError(f"Cannot read file: {e}")
    
    raise ValueError("Unable to decode file with any supported encoding")


def _validate_file_type(file_path: Path) -> bool:
    """Validate file type and warn about potentially problematic files."""
    extension = file_path.suffix.lower()
    
    # Handle files without extensions
    if not extension:
        print(f"\n[bold yellow]Notice:[/bold yellow] File has no extension. Attempting to load as text.")
        return True
    
    # Warn about binary files
    if extension in BINARY_EXTENSIONS:
        print(f"\n[bold yellow]Warning:[/bold yellow] '{extension}' files are typically binary and may not display properly as text.")
        confirm = Prompt.ask("Continue loading this file?", choices=["y", "n"], default="n")
        return confirm.lower() == "y"
    
    # Warn about unknown extensions
    if extension not in TEXT_EXTENSIONS:
        print(f"\n[bold yellow]Notice:[/bold yellow] Unknown file type '{extension}'. Attempting to load as text.")
    
    return True


def _format_file_content(file_path: Path, content: str, prompt: str) -> str:
    """Format the combined prompt with file content."""
    # Show content preview
    preview_length = 100
    if len(content) > preview_length:
        preview = content[:preview_length] + "..."
        print(f"\n[grey50]Content preview:\n\n[/grey50]{preview}")
    
    # Escape potential markdown injection by using indentation instead of code blocks
    indented_content = textwrap.indent(content, '    ')
    
    # Format the full prompt with safe indentation
    if prompt.strip():
        return f"{prompt}\n\nFile content from {file_path.name}:\n{indented_content}"
    else:
        return f"File content from {file_path.name}:\n{indented_content}"


def cmd_load(handler, filepath: str, prompt: str = "") -> CommandResult:
    """Load a file and send it with a prompt."""
    try:
        # Resolve path (handles relative paths from current working directory)
        file_path = Path(filepath).resolve()
        if not file_path.exists():
            print(f"\n[bold red]Error:[/bold red] File not found: {filepath}")
            print(f"[grey50]Resolved path:[/grey50] {file_path}")
            return CommandResult(ActionType.CONTINUE)
        
        if not file_path.is_file():
            print(f"\n[bold red]Error:[/bold red] Path is not a file: {filepath}")
            return CommandResult(ActionType.CONTINUE)
        
        # Validate file type
        if not _validate_file_type(file_path):
            print("\nFile loading cancelled.")
            return CommandResult(ActionType.CONTINUE)
        
        # Read file content with safety checks
        try:
            file_content = _read_file_content(file_path)
        except ValueError as e:
            print(f"\n[bold red]Error:[/bold red] {e}")
            return CommandResult(ActionType.CONTINUE)
        
        # Format the combined prompt
        full_prompt = _format_file_content(file_path, file_content, prompt)
        print(f"\n[green]✓[/green] Loaded file: {file_path.name} ({len(file_content):,} characters)")
        if prompt.strip():
            print(f"[grey50]Prompt:[/grey50] {prompt}")
        else:
            print(f"[grey50]No additional prompt provided[/grey50]")
        
        # Send the combined prompt
        handler.app.handle_regular_input(full_prompt)
        
        return CommandResult(ActionType.CONTINUE)
    except KeyboardInterrupt:
        print("\nFile loading cancelled.")
        return CommandResult(ActionType.CONTINUE)
    except Exception as e:
        print(f"\n[bold red]Error loading file:[/bold red] {e}")
        return CommandResult(ActionType.CONTINUE)


# New hierarchical file commands
@registry.register("file.load", "Load a file and send it with a prompt", category=CommandCategory.FILE)
def cmd_file_load(handler, filepath: str, prompt: str = "") -> CommandResult:
    """Load a file and send it with a prompt."""
    return cmd_load(handler, filepath, prompt)