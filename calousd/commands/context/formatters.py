"""Context command formatters."""
from ..formatters import CommandFormatter


class ContextFormatter(CommandFormatter):
    """Formatter for context command outputs."""
    
    @staticmethod
    def format_save_success(name: str, filepath):
        """Print context save success message."""
        ContextFormatter._output(f"\n[green]Context saved to {filepath} as '{name}'[/green]")
    
    @staticmethod
    def format_save_error(error_message: str):
        """Print context save error."""
        ContextFormatter._output(f"\n[red]Error saving context: {error_message}[/red]")
    
    @staticmethod
    def format_load_success(name: str):
        """Print context load success message."""
        ContextFormatter._output(f"\n[green]Context '{name}' loaded successfully[/green]")
        ContextFormatter._output("[grey70]Current persona, prompts, and chat history have been overwritten[/grey70]")
    
    @staticmethod
    def format_load_error(error_message: str):
        """Print context load error."""
        ContextFormatter._output(f"\n[red]Error loading context: {error_message}[/red]")
    
    @staticmethod
    def format_load_warning():
        """Print context load warning."""
        ContextFormatter._output("\n[yellow]Warning: Loading will overwrite current persona, prompts, and chat history[/yellow]")
    
    @staticmethod
    def format_no_contexts():
        """Print message when no contexts are found."""
        ContextFormatter._output("\n[yellow]No saved contexts found[/yellow]")
        ContextFormatter._output("[grey70]Use /context.save <name> to save your first context[/grey70]")
    
    @staticmethod
    def format_contexts_header():
        """Print header for contexts list."""
        ContextFormatter._output("\n[bold]Saved Contexts:[/bold]")
    
    @staticmethod
    def format_context_item(name: str, size: int):
        """Print context list item."""
        ContextFormatter._output(f"  [cyan]{name}[/cyan]  ({size} bytes)")
    
    @staticmethod
    def format_delete_success(name: str):
        """Print context delete success message."""
        ContextFormatter._output(f"\n[green]Context '{name}' deleted successfully[/green]")
    
    @staticmethod
    def format_delete_error(error_message: str):
        """Print context delete error."""
        ContextFormatter._output(f"\n[red]Error deleting context: {error_message}[/red]")
    
    @staticmethod
    def format_delete_warning(name: str):
        """Print delete warning."""
        ContextFormatter._output(f"\n[yellow]Are you sure you want to delete context '{name}'? This cannot be undone.[/yellow]")