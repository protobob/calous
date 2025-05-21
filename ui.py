"""User interface elements for Hi, Ollama!"""
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt
from rich import print
import threading
import time
import os

class UIManager:
    def __init__(self, app):
        self.app = app
        self.console = Console()
    
    def spinner(self, stop_flag):
        """Display a spinner while waiting for a task to complete."""
        spinner_widget = Spinner("dots", text="Inference")
        with Live(spinner_widget, refresh_per_second=10, console=self.console) as live:
            while not stop_flag.is_set():
                time.sleep(0.1)
        
    def run_with_spinner(self, target, *args):
        """Run a function with a spinner animation."""
        stop_flag = threading.Event()
        spinner_thread = threading.Thread(target=self.spinner, args=(stop_flag,))
        spinner_thread.start()
        result = target(*args)
        stop_flag.set()
        spinner_thread.join()
        return result
        
    def generate_prompt_text(self):
        """Generate the formatted prompt text shown before user input."""
        current_history_len = len(self.app.chat_history.history)
        return (
            f"\n"
            f"[italic][grey50]CH:[/grey50]"
            f"[grey70]{current_history_len}/{self.app.MAX_HISTORY}[/grey70][/italic]"
            f"[grey50] (Type /help for help.)[/grey50]\n"
            f"[bold]You[/bold]"
        )
        
    def help_menu(self):
        """Display the help menu with available commands."""
        current_history_len = len(self.app.chat_history.history)
        print(
            "\n[bold]Welcome to 'Hi, Ollama!' v0.2[/bold]\n"
            "\n[bold]General Commands:[/bold]"
            "\n  /help          - Show this help menu."
            "\n  /quit          - Exit the program and save the configuration."
            "\n"
            "\n[bold]Model Commands:[/bold]"
            "\n  /model         - Select a different model."
            "\n  /verbosity     - Toggle evaluation data display after responses."
            "\n  /togglethink   - Toggle filtering of LLM 'thoughts' (for reasoning models)."
            "\n"
            "\n[bold]Prompt Commands:[/bold]"
            "\n  /setprompt     - Set a saved prompt. Usage: /setprompt, then enter a number (1-10)."
            "\n                  Example: Type /setprompt, then enter '1' to set Prompt 1."
            "\n  /prompt        - Use a saved prompt. Usage: /prompt, then enter a number (1-10)."
            "\n                  Example: Type /prompt, then enter '1' to use Prompt 1."
            "\n  /showprompt    - Display saved prompts. Usage: /showprompt to view all, or enter a number (1-10)."
            "\n                  Example: Type /showprompt, then enter '1' to view Prompt 1."
            "\n  /system        - Change the system prompt."
            "\n"
            "\n[bold]Chat History Commands:[/bold]"
            "\n  /history       - Display the current chat history."
            "\n  /clear         - Clear the current chat history."
            "\n  /setmax        - Set the maximum chat history (even number between 2-100)."
            "\n  /togglelog     - Toggle logging of chat history."
            "\n"
            "\n[bold]File Commands:[/bold]"
            "\n  /load          - Load a file as a prompt. Usage: /load <filename>."
            "\n                  Example: /load example.txt -- you will be prompted for instructions."
            "\n"
            "\n[bold]System Variables:[/bold]"
            f"\n  Model:          {self.app.selected_model}"
            f"\n  Logging:        {self.app.logging_enabled}"
            f"\n  Think Filtering:{self.app.think_filtering}"
            f"\n  Verbosity:      {self.app.verbosity}"
            f"\n  Max History:    {self.app.MAX_HISTORY}"
            f"\n  System Prompt:  [italic]{self.app.system_prompt['content']}[/italic]"
            "\n" 
        )
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')