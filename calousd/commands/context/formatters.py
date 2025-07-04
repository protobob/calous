"""Context command formatters."""
from ..formatters import CommandFormatter


class ContextFormatter(CommandFormatter):
    """Formatter for context command outputs."""
    
    @staticmethod
    def format_save_success(name: str, filepath):
        """Print context save success message."""
        ContextFormatter._output(f"\n[32mContext saved to {filepath} as '{name}'[0m")
    
    @staticmethod
    def format_save_error(error_message: str):
        """Print context save error."""
        ContextFormatter._output(f"\n[31mError saving context: {error_message}[0m")
    
    @staticmethod
    def format_load_success(name: str):
        """Print context load success message."""
        ContextFormatter._output(f"\n[32mContext '{name}' loaded successfully[0m")
        ContextFormatter._output("[37mCurrent persona, prompts, and chat history have been overwritten[0m")
    
    @staticmethod
    def format_load_error(error_message: str):
        """Print context load error."""
        ContextFormatter._output(f"\n[31mError loading context: {error_message}[0m")
    
    @staticmethod
    def format_load_warning():
        """Print context load warning."""
        ContextFormatter._output("\n[33mWarning: Loading will overwrite current persona, prompts, and chat history[0m")
    
    @staticmethod
    def format_no_contexts():
        """Print message when no contexts are found."""
        ContextFormatter._output("\n[33mNo saved contexts found[0m")
        ContextFormatter._output("[37mUse /context.save <name> to save your first context[0m")
    
    @staticmethod
    def format_contexts_header():
        """Print header for contexts list."""
        ContextFormatter._output("\n[1mSaved Contexts:[0m")
    
    @staticmethod
    def format_context_item(name: str, size: int):
        """Print context list item."""
        ContextFormatter._output(f"  [36m{name}[0m  ({size} bytes)")
    
    @staticmethod
    def format_delete_success(name: str):
        """Print context delete success message."""
        ContextFormatter._output(f"\n[32mContext '{name}' deleted successfully[0m")
    
    @staticmethod
    def format_delete_error(error_message: str):
        """Print context delete error."""
        ContextFormatter._output(f"\n[31mError deleting context: {error_message}[0m")
    
    @staticmethod
    def format_delete_warning(name: str):
        """Print delete warning."""
        ContextFormatter._output(f"\n[33mAre you sure you want to delete context '{name}'? This cannot be undone.[0m")