"""User interface elements for Hi, Ollama!"""
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt
from rich import print
from rich.table import Table
from .utils import get_chat_color, print_message_with_bar, find_last_messages
from .constants import APP_VERSION, MAX_PREVIEW_LENGTH
from typing import Dict, Any
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
    
    def get_user_input(self):
        """Get user input with formatted prompt."""
        prompt_text = self.generate_prompt_text()
        return Prompt.ask(prompt_text).strip()
        
    def generate_prompt_text(self):
        """Generate the formatted prompt text shown before user input."""
        current_history_len = len(self.app.chat_history.history)
        
        # Determine color based on chat index
        chat_index = getattr(self.app, 'active_chat_index', 0)
        chat_color = get_chat_color(chat_index)
        
        # Prepare the 'YOU:' part
        you_text = f"[bold {chat_color}]|[/bold {chat_color}] [bold]YOU[/bold]"

        return (
            f"\n"
            f"[bold {chat_color}]|[/bold {chat_color}] [italic][bold {chat_color}]CH:[/bold {chat_color}]"
            f"[grey70]{current_history_len}/{self.app.MAX_HISTORY}[/grey70][/italic]"
            f"[grey50] (/help for help)[/grey50]\n"
            f"{you_text}"
        )
        
    def help_menu(self):
        """Display the help menu with available commands."""
        # Define the command color as a variable
        command_color = "grey70"

        # Create a table for the help menu
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Command", style=f"bold {command_color}", no_wrap=True)
        table.add_column("Description", style="grey70")

        # Add a header for General Commands
        table.add_row("[bold white]General Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/help[/bold {command_color}]", "Show this help menu.")
        table.add_row(f"[bold {command_color}]/quit[/bold {command_color}]", "Exit the program and save the configuration.")
        table.add_row(f"[bold {command_color}]/showvars[/bold {command_color}]", "Display current system variables.")
        
        # Enhanced switch/twist help text for multi-chat support
        num_chats = len(self.app.chat_instances) if self.app.chat_instances else 2
        if num_chats == 2:
            table.add_row(f"[bold {command_color}]/switch[/bold {command_color}]", f"Switch between chats (or /switch NUMBER).")
            table.add_row(f"[bold {command_color}]/twist[/bold {command_color}]", "Copy AI's last response, switch chats, and use it as a prompt (or /twist NUMBER).")
        else:
            table.add_row(f"[bold {command_color}]/switch NUMBER[/bold {command_color}]", f"Switch to chat NUMBER (1-{num_chats}).")
            table.add_row(f"[bold {command_color}]/twist NUMBER[/bold {command_color}]", f"Copy AI's last response to chat NUMBER (1-{num_chats}).")

        # Add a header for Model Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]Model Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/model[/bold {command_color}]", "Select a different model.")
        table.add_row(f"[bold {command_color}]/toggle_eval[/bold {command_color}]", "Toggle evaluation data display after responses.")
        table.add_row(f"[bold {command_color}]/toggle_think[/bold {command_color}]", "Toggle filtering of LLM 'thoughts'.")

        # Add a header for Prompt Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]Prompt Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/setprompt[/bold {command_color}]", f"Set a saved prompt. Usage: [bold {command_color}]/setprompt NUMBER PROMPT_TEXT[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/prompt[/bold {command_color}]", f"Use a saved prompt. Usage: [bold {command_color}]/prompt NUMBER[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/showprompt[/bold {command_color}]", f"Display saved prompts. Usage: [bold {command_color}]/showprompt NUMBER[/bold {command_color}] or [bold {command_color}]/showprompt all[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/system[/bold {command_color}]", "Change the system prompt.")

        # Add a header for Chat History Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]Chat History Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/history[/bold {command_color}]", "Display the current chat history.")
        table.add_row(f"[bold {command_color}]/clear[/bold {command_color}]", "Clear the current chat history.")
        table.add_row(f"[bold {command_color}]/setmax[/bold {command_color}]", f"Set maximum chat history. Usage: [bold {command_color}]/setmax NUMBER[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/toggle_log[/bold {command_color}]", "Toggle logging of chat history.")

        # Add a header for File Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]File Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/load[/bold {command_color}]", f"Load a file as a prompt. Usage: [bold {command_color}]/load FILENAME PROMPT[/bold {command_color}].")

        # Print the table
        print(f"\n[bold grey70]| GLOBAL HELP MENU[/bold grey70]\n")
        print(table)
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_variables(self):
        """Display current system variables."""
        print(
            "\n[bold]System Variables:[/bold]"
            f"\n  Model:          {self.app.selected_model}"
            f"\n  Logging:        {self.app.logging_enabled}"
            f"\n  Think Filtering:{self.app.think_filtering}"
            f"\n  Verbosity:      {self.app.verbosity}"
            f"\n  Max History:    {self.app.MAX_HISTORY}"
            f"\n  System Prompt:  [italic]{self.app.system_prompt['content']}[/italic]"
            "\n"
        )
        
    def display_variables(
        self,
        active_chat_index,
        selected_model,
        verbosity,
        think_filtering,
        max_history,
        system_prompt,
        logging_enabled,
        log_dir,
        config_path
    ):
        """Display application variables in a clean, aligned format."""
        chat_color = get_chat_color(active_chat_index)

        # Title with CHAT # in the chat color
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {active_chat_index + 1} VARIABLES[/bold {chat_color}]\n")

        # Variables with updated formatting
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Selected Model:':<20} {selected_model}")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Max History:':<20} [bold cyan]{max_history}[/bold cyan]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Verbosity:':<20} [bold][{'green' if verbosity else 'red'}]{verbosity}[/{'green' if verbosity else 'red'}][/bold]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Think Filtering:':<20} [bold][{'green' if think_filtering else 'red'}]{think_filtering}[/{'green' if think_filtering else 'red'}][/bold]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Logging Enabled:':<20} [bold][{'green' if logging_enabled else 'red'}]{logging_enabled}[/{'green' if logging_enabled else 'red'}][/bold]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Config Path:':<20} [grey70]{config_path}[/grey70]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Log Directory:':<20} [grey70]{log_dir}[/grey70]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'System Prompt:':<20} [grey70]{system_prompt}[/grey70]\n")
    
    def display_active_chats_overview(self):
        """Display overview of all configured chats."""
        num_chats = len(self.app.chat_instances) if self.app.chat_instances else 2
        
        if num_chats == 2:
            switch_hint = "/switch to change"
        else:
            switch_hint = f"/switch NUMBER (1-{num_chats}) to change"
            
        print(f"[bold white]ACTIVE CHATS:[/bold white] [grey50]({switch_hint})[/grey50]")
        
        for i, chat in enumerate(self.app.chat_instances):
            chat_color_for_chat = get_chat_color(i)
            
            # Get system prompt and truncate if needed
            sys_prompt = chat.system_prompt.get('content', '[No system prompt set]')
            if len(sys_prompt) > MAX_PREVIEW_LENGTH:
                sys_prompt = sys_prompt[:MAX_PREVIEW_LENGTH] + "..."
            
            # Mark active chat with arrow
            prefix = "►" if i == self.app.active_chat_index else " "
            
            print(f"{prefix} [bold {chat_color_for_chat}]{i + 1}:[/bold {chat_color_for_chat}] [grey70]{sys_prompt}[/grey70]")
        
        print()  # Add spacing after overview

    def display_chat_context(self, chat_color: str) -> None:
        """Display the current chat context with active chats overview first."""
        # Show active chats overview at the top
        self.display_active_chats_overview()
        
        # Find last messages using utility function
        last_messages = find_last_messages(self.app.chat_history)
        
        # Only show chat header and context if there are messages
        if last_messages:
            # Show the current chat's detailed context
            from .utils import print_chat_header
            print_chat_header(self.app.active_chat_index)
            
            # Get the current chat's color for the bars
            current_chat_color = get_chat_color(self.app.active_chat_index)
            
            # Display the last user message
            if last_messages.get('user'):
                print_message_with_bar(current_chat_color, "YOU", last_messages['user'].get('content', ''))
            
            # Display the last assistant message
            if last_messages.get('assistant'):
                print_message_with_bar(current_chat_color, "LLM", last_messages['assistant'].get('content', ''))