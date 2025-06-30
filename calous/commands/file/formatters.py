"""File command formatters module."""
from rich import print as rich_print
from ..formatters import CommandFormatter
from ...constants import Colors, Messages


class FileFormatter(CommandFormatter):
    """Specialized formatter for file operation output."""
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
    @staticmethod
    def file_not_found_error(filepath: str, resolved_path):
        """Print file not found error with resolved path."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} File not found: {filepath}")
        CommandFormatter._output(f"{Colors.HINT}Resolved path:{Colors.RESET} {resolved_path}")
    
    @staticmethod
    def not_a_file_error(filepath: str):
        """Print error when path is not a file."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} Path is not a file: {filepath}")
    
    @staticmethod
    def file_size_error(file_size: int, max_size: int):
        """Print error for files that exceed size limit."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} File too large ({file_size:,} bytes). Maximum allowed: {max_size:,} bytes")
    
    @staticmethod
    def large_file_warning(file_size: int):
        """Print warning for large files."""
        CommandFormatter._output(f"\n{Colors.WARNING}Warning:{Colors.RESET} Large file ({file_size:,} bytes). This may take a moment to process.")
    
    @staticmethod
    def no_extension_notice():
        """Print notice for files without extensions."""
        CommandFormatter._output(f"\n{Colors.INFO}Notice:{Colors.RESET} File has no extension. Attempting to load as text.")
    
    @staticmethod
    def binary_file_warning(extension: str):
        """Print warning for potentially binary files."""
        CommandFormatter._output(f"\n{Colors.WARNING}Warning:{Colors.RESET} '{extension}' files are typically binary and may not display properly as text.")
    
    @staticmethod
    def unknown_extension_notice(extension: str):
        """Print notice for unknown file extensions."""
        CommandFormatter._output(f"\n{Colors.INFO}Notice:{Colors.RESET} Unknown file type '{extension}'. Attempting to load as text.")
    
    @staticmethod
    def content_preview(preview: str):
        """Print a preview of file content."""
        CommandFormatter._output(f"\n{Colors.HINT}Content preview:\n\n{Colors.RESET}{preview}")
    
    @staticmethod
    def file_load_cancelled():
        """Print file loading cancelled message."""
        CommandFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def generic_error(message: str):
        """Print generic error message."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error:{Colors.RESET} {message}")
        
        # Add helpful hint for vision model errors
        if "does not support vision" in message:
            CommandFormatter._output(f"{Colors.HINT}Try switching to a vision-capable model like llava, bakllava, or other multimodal models.{Colors.RESET}")
    
    @staticmethod
    def file_loaded_success(filename: str, char_count: int, prompt: str = ""):
        """Print successful file load message."""
        CommandFormatter._output(f"\n{Colors.SUCCESS}✓{Colors.RESET} Loaded file: {filename} ({char_count:,} characters)")
        if prompt.strip():
            CommandFormatter._output(f"{Colors.HINT}Prompt:{Colors.RESET} {prompt}")
        else:
            CommandFormatter._output(f"{Colors.HINT}No additional prompt provided{Colors.RESET}")
    
    @staticmethod
    def file_load_error(message: str):
        """Print file loading error."""
        CommandFormatter._output(f"\n{Colors.ERROR}Error loading file:{Colors.RESET} {message}")
    
    @staticmethod
    def image_loaded_success(image_info: dict):
        """Print successful image load message."""
        CommandFormatter._output(f"[green]✓[/green] Image loaded: {image_info['name']} ({image_info['size_mb']} MB)")
    
    @staticmethod
    def show_content_preview(content: str, preview_length: int = 100):
        """Show content preview if content is long."""
        if len(content) > preview_length:
            preview = content[:preview_length] + "..."
            FileFormatter.content_preview(preview)
