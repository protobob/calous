"""File command services module."""
from pathlib import Path
from typing import Union, Dict, Any
import textwrap

from ...types import CommandResult
from ...constants import MAX_FILE_SIZE, LARGE_FILE_WARNING_SIZE, TEXT_EXTENSIONS, BINARY_EXTENSIONS, IMAGE_EXTENSIONS
from .image_service import ImageService


class FileResult:
    """Result object for file operations."""
    
    def __init__(self, success: bool, content: str = "", file_path: Path = None, 
                 error_message: str = "", is_cancelled: bool = False):
        self.success = success
        self.content = content
        self.file_path = file_path
        self.error_message = error_message
        self.is_cancelled = is_cancelled


class FileService:
    """Service for file operations."""
    
    @staticmethod
    def validate_file_path(filepath: str) -> FileResult:
        """Validate file path and existence."""
        try:
            file_path = Path(filepath).resolve()
            if not file_path.exists():
                return FileResult(success=False, error_message=f"File not found: {filepath}", file_path=file_path)
            
            if not file_path.is_file():
                return FileResult(success=False, error_message=f"Path is not a file: {filepath}")
            
            return FileResult(success=True, file_path=file_path)
        except Exception as e:
            return FileResult(success=False, error_message=f"Invalid file path: {str(e)}")
    
    @staticmethod
    def validate_file_type(file_path: Path, app=None) -> FileResult:
        """Validate file type and get user confirmation for problematic files."""
        from .formatters import FileFormatter
        
        formatter = FileFormatter()
        extension = file_path.suffix.lower()
        
        # Handle files without extensions
        if not extension:
            formatter.no_extension_notice()
            return FileResult(success=True, file_path=file_path)
        
        # Handle image files - no validation needed for supported vision models
        if extension in IMAGE_EXTENSIONS:
            return FileResult(success=True, file_path=file_path)
        
        # Warn about binary files
        if extension in BINARY_EXTENSIONS:
            formatter.binary_file_warning(extension)
            if app and hasattr(app, 'confirm'):
                if not app.confirm("Continue loading this file?", default=True):
                    return FileResult(success=False, is_cancelled=True)
            else:
                confirm = input("Continue loading this file? (y/n) [n]: ")
                if confirm.lower() != "y":
                    return FileResult(success=False, is_cancelled=True)
        
        # Warn about unknown extensions
        if extension not in TEXT_EXTENSIONS:
            formatter.unknown_extension_notice(extension)
        
        return FileResult(success=True, file_path=file_path)
    
    @staticmethod
    def read_file_content(file_path: Path, app=None) -> FileResult:
        """Read file content with multiple encoding attempts and safety checks."""
        from .formatters import FileFormatter
        
        formatter = FileFormatter()
        
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                formatter.file_size_error(file_size, MAX_FILE_SIZE)
                return FileResult(success=False, error_message="File size exceeds limit")
            
            if file_size > LARGE_FILE_WARNING_SIZE:
                formatter.large_file_warning(file_size)
                if app and hasattr(app, 'confirm'):
                    if not app.confirm("Continue loading this large file?", default=True):
                        return FileResult(success=False, is_cancelled=True)
                else:
                    confirm = input("Continue loading this large file? (y/n) [n]: ")
                    if confirm.lower() != "y":
                        return FileResult(success=False, is_cancelled=True)
            
            # Try multiple encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return FileResult(success=True, content=content, file_path=file_path)
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    return FileResult(success=False, error_message=f"Cannot read file: {str(e)}")
            
            return FileResult(success=False, error_message="Unable to decode file with any supported encoding")
            
        except Exception as e:
            return FileResult(success=False, error_message=f"Error reading file: {str(e)}")
    
    @staticmethod
    def format_file_content(file_path: Path, content: str, prompt: str) -> str:
        """Format the combined prompt with file content."""
        # Escape potential markdown injection by using indentation instead of code blocks
        indented_content = textwrap.indent(content, '    ')
        
        # Format the full prompt with safe indentation
        if prompt.strip():
            return f"{prompt}\n\nFile content from {file_path.name}:\n{indented_content}"
        else:
            return f"File content from {file_path.name}:\n{indented_content}"
    
    @staticmethod
    def handle_image_load(file_path: Path, prompt: str, handler) -> FileResult:
        """Handle loading of image files for vision models."""
        try:
            # Get image information
            image_info = ImageService.get_image_info(file_path)
            
            # Check if current model supports vision
            from .model_utils import check_model_vision_support
            model_name = handler.app.selected_model
            
            if not check_model_vision_support(model_name):
                return FileResult(
                    success=False, 
                    error_message=f"Model '{model_name}' does not support vision capabilities. "
                                  f"Please switch to a vision-capable model first with /model.switch"
                )
            
            # Prepare image for Ollama (returns file path)
            image_path = ImageService.prepare_image_for_ollama(file_path)
            
            # Send to model with image
            if prompt.strip():
                handler.app.handle_regular_input(prompt, images=[image_path])
            else:
                # Default prompt for image analysis
                handler.app.handle_regular_input("Please analyze this image.", images=[image_path])
            
            return FileResult(success=True, content=f"Image loaded: {image_info['name']} ({image_info['size_mb']} MB)")
            
        except Exception as e:
            return FileResult(success=False, error_message=f"Failed to load image: {str(e)}")
