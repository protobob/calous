"""File operation commands."""
from rich.prompt import Prompt
from rich import print
from pathlib import Path
import textwrap
from ..types import CommandResult, ActionType
from ..constants import MAX_FILE_SIZE, LARGE_FILE_WARNING_SIZE, TEXT_EXTENSIONS, BINARY_EXTENSIONS, IMAGE_EXTENSIONS
from .registry import registry
from .types import CommandCategory
from .formatters import FileFormatter
from .image_service import ImageService


def _read_file_content(file_path: Path) -> str:
    """Read file content with multiple encoding attempts and safety checks."""
    formatter = FileFormatter()
    
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        formatter.file_size_error(file_size, MAX_FILE_SIZE)
        raise ValueError("File size exceeds limit")
    
    if file_size > LARGE_FILE_WARNING_SIZE:
        formatter.large_file_warning(file_size)
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
    formatter = FileFormatter()
    extension = file_path.suffix.lower()
    
    # Handle files without extensions
    if not extension:
        formatter.no_extension_notice()
        return True
    
    # Handle image files - no validation needed for supported vision models
    if extension in IMAGE_EXTENSIONS:
        return True
    
    # Warn about binary files
    if extension in BINARY_EXTENSIONS:
        formatter.binary_file_warning(extension)
        confirm = Prompt.ask("Continue loading this file?", choices=["y", "n"], default="n")
        return confirm.lower() == "y"
    
    # Warn about unknown extensions
    if extension not in TEXT_EXTENSIONS:
        formatter.unknown_extension_notice(extension)
    
    return True


def _format_file_content(file_path: Path, content: str, prompt: str) -> str:
    """Format the combined prompt with file content."""
    formatter = FileFormatter()
    
    # Show content preview
    preview_length = 100
    if len(content) > preview_length:
        preview = content[:preview_length] + "..."
        formatter.content_preview(preview)
    
    # Escape potential markdown injection by using indentation instead of code blocks
    indented_content = textwrap.indent(content, '    ')
    
    # Format the full prompt with safe indentation
    if prompt.strip():
        return f"{prompt}\n\nFile content from {file_path.name}:\n{indented_content}"
    else:
        return f"File content from {file_path.name}:\n{indented_content}"


def _handle_image_load(handler, file_path: Path, prompt: str) -> CommandResult:
    """Handle loading of image files for vision models."""
    formatter = FileFormatter()
    
    try:
        # Get image information
        image_info = ImageService.get_image_info(file_path)
        
        # Prepare image for Ollama (returns file path)
        image_path = ImageService.prepare_image_for_ollama(file_path)
        
        # Display image loading success
        print(f"[green]✓[/green] Image loaded: {image_info['name']} ({image_info['size_mb']} MB)")
        
        # Send to model with image
        if prompt.strip():
            handler.app.handle_regular_input(prompt, images=[image_path])
        else:
            # Default prompt for image analysis
            handler.app.handle_regular_input("Please analyze this image.", images=[image_path])
        
        return CommandResult(ActionType.CONTINUE)
        
    except Exception as e:
        formatter.generic_error(f"Failed to load image: {str(e)}")
        return CommandResult(ActionType.CONTINUE)


def cmd_load(handler, filepath: str, prompt: str = "") -> CommandResult:
    """Load a file and send it with a prompt."""
    formatter = FileFormatter()
    
    try:
        # Resolve path (handles relative paths from current working directory)
        file_path = Path(filepath).resolve()
        if not file_path.exists():
            formatter.file_not_found_error(filepath, file_path)
            return CommandResult(ActionType.CONTINUE)
        
        if not file_path.is_file():
            formatter.not_a_file_error(filepath)
            return CommandResult(ActionType.CONTINUE)
        
        # Validate file type
        if not _validate_file_type(file_path):
            formatter.file_load_cancelled()
            return CommandResult(ActionType.CONTINUE)
        
        # Handle image files differently
        if ImageService.is_image_file(file_path):
            return _handle_image_load(handler, file_path, prompt)
        
        # Handle text files (existing logic)
        try:
            file_content = _read_file_content(file_path)
        except ValueError as e:
            formatter.generic_error(str(e))
            return CommandResult(ActionType.CONTINUE)
        
        # Format the combined prompt
        full_prompt = _format_file_content(file_path, file_content, prompt)
        formatter.file_loaded_success(file_path.name, len(file_content), prompt)
        
        # Send the combined prompt
        handler.app.handle_regular_input(full_prompt)
        
        return CommandResult(ActionType.CONTINUE)
    except KeyboardInterrupt:
        formatter.file_load_cancelled()
        return CommandResult(ActionType.CONTINUE)
    except Exception as e:
        formatter.file_load_error(str(e))
        return CommandResult(ActionType.CONTINUE)


# New hierarchical file commands
@registry.register("file.load", "Load a file and send it with a prompt", category=CommandCategory.FILE)
def cmd_file_load(handler, filepath: str, prompt: str = "") -> CommandResult:
    """Load a file and send it with a prompt."""
    return cmd_load(handler, filepath, prompt)