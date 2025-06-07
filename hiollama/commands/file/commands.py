"""File commands module."""
from ...types import CommandResult, ActionType
from ..registry import registry
from ..types import CommandCategory
from .services import FileService
from .formatters import FileFormatter
from .image_service import ImageService


@registry.register("file.load", "Load a file and send it with a prompt", category=CommandCategory.FILE)
def cmd_file_load(handler, filepath: str, prompt: str = "") -> CommandResult:
    """Load a file and send it with a prompt."""
    formatter = FileFormatter()
    
    try:
        # Validate file path
        path_result = FileService.validate_file_path(filepath)
        if not path_result.success:
            if path_result.file_path:
                formatter.file_not_found_error(filepath, path_result.file_path)
            else:
                formatter.not_a_file_error(filepath)
            return CommandResult(ActionType.CONTINUE)
        
        file_path = path_result.file_path
        
        # Validate file type
        type_result = FileService.validate_file_type(file_path)
        if not type_result.success:
            if type_result.is_cancelled:
                formatter.file_load_cancelled()
            return CommandResult(ActionType.CONTINUE)
        
        # Handle image files differently
        if ImageService.is_image_file(file_path):
            image_result = FileService.handle_image_load(file_path, prompt, handler)
            if image_result.success:
                # Success message already printed in handle_image_load
                pass
            else:
                formatter.generic_error(image_result.error_message)
            return CommandResult(ActionType.CONTINUE)
        
        # Handle text files
        content_result = FileService.read_file_content(file_path)
        if not content_result.success:
            if content_result.is_cancelled:
                formatter.file_load_cancelled()
            else:
                formatter.generic_error(content_result.error_message)
            return CommandResult(ActionType.CONTINUE)
        
        file_content = content_result.content
        
        # Show content preview if long
        formatter.show_content_preview(file_content)
        
        # Format the combined prompt
        full_prompt = FileService.format_file_content(file_path, file_content, prompt)
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
