"""Image handling service for vision models."""
import base64
from pathlib import Path
from typing import Union, Optional, Dict, Any


class ImageService:
    """Service for handling image files for vision models."""
    
    @staticmethod
    def is_image_file(file_path: Path) -> bool:
        """Check if a file is an image based on its extension."""
        from ..constants import IMAGE_EXTENSIONS
        return file_path.suffix.lower() in IMAGE_EXTENSIONS
    
    @staticmethod
    def encode_image_to_base64(file_path: Path) -> str:
        """Encode an image file to base64 string."""
        try:
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode image {file_path.name}: {str(e)}")
    
    @staticmethod
    def prepare_image_for_ollama(file_path: Path) -> Union[str, bytes]:
        """Prepare an image for Ollama API (returns file path or base64)."""
        if not ImageService.is_image_file(file_path):
            raise ValueError(f"File {file_path.name} is not a supported image format")
        
        # Ollama supports file paths directly, which is more efficient than base64
        return str(file_path.resolve())
    
    @staticmethod
    def get_image_info(file_path: Path) -> Dict[str, Any]:
        """Get basic information about an image file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        file_size = file_path.stat().st_size
        extension = file_path.suffix.lower()
        
        return {
            'name': file_path.name,
            'extension': extension,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'path': str(file_path.resolve())
        }
