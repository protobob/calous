"""User interface elements for Hi, Ollama!"""
from rich.console import Console
from rich.prompt import Prompt
from rich import print
from rich.table import Table
from .utils import get_chat_color, print_message_with_bar, find_last_messages
from .constants import APP_VERSION, MAX_PREVIEW_LENGTH
from .config import ConfigManager
from typing import Dict, Any
import os


class UIManager:
    def __init__(self, app):
        self.app = app
        self.console = Console()
    
    def help_menu(self):
        """Display the help menu with available commands."""
        # Define the command color as a variable
        command_color = "grey70"

        # Create a table for the help menu
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Command", style=f"bold {command_color}", no_wrap=True)
        table.add_column("Description", style="grey70")        # Add a header for General Commands
        table.add_row("[bold white]General Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/help[/bold {command_color}]", "Show this help menu.")
        table.add_row(f"[bold {command_color}]/quit[/bold {command_color}]", "Exit the program and save the configuration.")
        table.add_row(f"[bold {command_color}]/showvars[/bold {command_color}]", "Display current system variables.")
        table.add_row(f"[bold {command_color}]/resetchat[/bold {command_color}]", "Reset chat to factory defaults.")
        
        # Get num_chats dynamically from session manager
        num_chats = self.app.session_manager.num_chats if hasattr(self.app, 'session_manager') and self.app.session_manager else ConfigManager.get_num_chats()
        
        # Add a header for Chat Navigation Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]Chat Navigation Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/switch [NUMBER][/bold {command_color}]", f"Switch between chats (1-{num_chats}). Default switches to next chat.")
        table.add_row(f"[bold {command_color}]/twist [NUMBER][/bold {command_color}]", f"Copy AI's last response to target chat (1-{num_chats}). Default uses next chat.")
        table.add_row(f"[bold {command_color}]/addchat[/bold {command_color}]", "Add a new chat session.")
        table.add_row(f"[bold {command_color}]/removechat[/bold {command_color}]", "Remove a chat session.")# Add a header for Model Commands        table.add_row("", "")  # Empty row for spacing
        table.add_row("\n[bold white]Model Commands:[/bold white]", "")          
        table.add_row(f"[bold {command_color}]/model[/bold {command_color}]", "Select a different model.")
        table.add_row(f"[bold {command_color}]/setctx[/bold {command_color}]", f"Set context window size. Usage: [bold {command_color}]/setctx NUMBER[/bold {command_color}] (2048-32768 tokens).")
        table.add_row(f"[bold {command_color}]/settemp[/bold {command_color}]", f"Set model temperature. Usage: [bold {command_color}]/settemp NUMBER[/bold {command_color}] (0.0-2.0).")
        table.add_row(f"[bold {command_color}]/toggle_eval[/bold {command_color}]", "Toggle evaluation data display after responses.")
        table.add_row(f"[bold {command_color}]/toggle_think[/bold {command_color}]", "Toggle thinking mode (show/hide model reasoning).")

        # Add a header for Prompt Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]Prompt Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/setprompt[/bold {command_color}]", f"Set a saved prompt. Usage: [bold {command_color}]/setprompt NUMBER PROMPT_TEXT[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/prompt[/bold {command_color}]", f"Use a saved prompt. Usage: [bold {command_color}]/prompt NUMBER[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/showprompt[/bold {command_color}]", f"Display saved prompts. Usage: [bold {command_color}]/showprompt NUMBER[/bold {command_color}] or [bold {command_color}]/showprompt all[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/system[/bold {command_color}]", "Change the system prompt.")        # Add a header for Chat History Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]Chat History Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/history[/bold {command_color}]", "Display the current chat history.")
        table.add_row(f"[bold {command_color}]/clear[/bold {command_color}]", "Clear the current chat history.")
        table.add_row(f"[bold {command_color}]/export[/bold {command_color}]", "Export chat history.")
        table.add_row(f"[bold {command_color}]/toggle_log[/bold {command_color}]", "Toggle logging of chat history.")
        table.add_row(f"[bold {command_color}]/unified_log[/bold {command_color}]", "View unified log for today.")

        # Add a header for File Commands
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold white]File Commands:[/bold white]", "")
        table.add_row(f"[bold {command_color}]/load[/bold {command_color}]", f"Load a file as a prompt. Usage: [bold {command_color}]/load FILENAME PROMPT[/bold {command_color}].")
        table.add_row(f"[bold {command_color}]/save[/bold {command_color}]", "Save conversation to file.")

        # Print the table
        print(f"\n[bold grey70]| GLOBAL HELP MENU[/bold grey70]\n")
        print(table)
    
    def display_active_chats_overview(self):
        """Display overview of all configured chats."""
        # Get num_chats and chat instances via session manager
        if hasattr(self.app, 'session_manager') and self.app.session_manager:
            num_chats = self.app.session_manager.num_chats
            chat_instances = self.app.session_manager.get_all_chats()
        else:
            # Fallback for standalone operation
            num_chats = ConfigManager.get_num_chats()
            chat_instances = [self.app]  # Just show current app
        
        # Always use the dynamic version
        switch_hint = f"/switch [1-{num_chats}] to change" if num_chats > 1 else ""
        
        print(f"[bold white]ACTIVE CHATS:[/bold white] [grey50]({switch_hint})[/grey50]")
        
        for i, chat in enumerate(chat_instances):
            chat_color_for_chat = get_chat_color(i)
            
            # Get system prompt and truncate if needed
            sys_prompt = chat.system_prompt.get('content', '[No system prompt set]')
            if len(sys_prompt) > MAX_PREVIEW_LENGTH:
                sys_prompt = sys_prompt[:MAX_PREVIEW_LENGTH] + "..."
              # Mark active chat with arrow (using ASCII character for Windows compatibility)
            prefix = ">" if i == self.app.active_chat_index else " "
            
            print(f"{prefix} [bold {chat_color_for_chat}]{i + 1}:[/bold {chat_color_for_chat}] [grey70]{sys_prompt}[/grey70]")
        
        print()  # Add spacing after overview
    
    def get_user_input(self):
        """Get user input with formatted prompt."""
        prompt_text = self.generate_prompt_text()
        return Prompt.ask(prompt_text).strip()    
    def generate_prompt_text(self):
        """Generate the formatted prompt text shown before user input."""
        # Determine color based on chat index
        chat_index = getattr(self.app, 'active_chat_index', 0)
        chat_color = get_chat_color(chat_index)
        # Get context window usage percentage
        context_display = "Context: ??"
        if self.app.selected_model:
            usage_percentage = self.app.model.get_context_usage_percentage(self.app.selected_model)
            if usage_percentage is not None:
                # Determine color based on percentage ranges
                if usage_percentage <= 24:
                    percentage_color = "green"
                elif usage_percentage <= 49:
                    percentage_color = "yellow"
                elif usage_percentage <= 74:
                    percentage_color = "orange1"
                else:  # 75-100
                    percentage_color = "red"
                
                context_display = f"Context: [{percentage_color}]{usage_percentage:.0f}%[/{percentage_color}]"
        
        # Prepare the 'YOU:' part
        you_text = f"[bold {chat_color}]|[/bold {chat_color}] [bold]YOU[/bold]"        
        return (
            f"\n"
            f"[bold {chat_color}]|[/bold {chat_color}] [italic][white]{context_display}[/white][/italic]"
            f"[grey50] (/help for help)[/grey50]\n"
            f"{you_text}"
        )
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_variables(self):
        """Display current system variables."""
        chat_color = get_chat_color(getattr(self.app, 'active_chat_index', 0))
        active_chat_index = getattr(self.app, 'active_chat_index', 0)
        
        # Title with CHAT # in the chat color
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]CHAT {active_chat_index + 1} VARIABLES[/bold {chat_color}]\n")

        # Get the actual paths from constants and objects
        from .constants import CONFIG_PATH, LOG_DIR
        
        # Add error handling for path operations
        try:
            config_path = str(CONFIG_PATH.relative_to(CONFIG_PATH.home()))
        except ValueError:
            config_path = str(CONFIG_PATH)
            
        try:
            log_dir = str(LOG_DIR.relative_to(LOG_DIR.home()))
        except ValueError:
            log_dir = str(LOG_DIR)

        # Variables with updated formatting        
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Selected Model:':<20} {self.app.selected_model}")        # Context window information
        if self.app.selected_model:
            context_info = self.app.model.get_context_window_info(self.app.selected_model)
            usage_percentage = self.app.model.get_context_usage_percentage(self.app.selected_model)
            if context_info:
                # Display user-set context window with model's max context for reference
                if self.app.num_ctx != context_info.max_context:
                    context_display = f"{self.app.num_ctx:,} tokens (Model Max: {context_info.max_context:,})"
                else:
                    context_display = f"{self.app.num_ctx:,} tokens"
                
                print(f"[bold {chat_color}]|[/bold {chat_color}] {'Context Window:':<20} [bold cyan]{context_display}[/bold cyan]")
                
                # Show usage percentage with visual indicator
                if usage_percentage is not None:
                    # Create visual progress bar
                    bar_length = 10
                    filled_length = int(bar_length * usage_percentage / 100)
                    bar = "█" * filled_length + "░" * (bar_length - filled_length)
                      # Color the percentage based on usage level
                    if usage_percentage <= 24:
                        percentage_color = "green"
                    elif usage_percentage <= 49:
                        percentage_color = "yellow"
                    elif usage_percentage <= 74:
                        percentage_color = "orange1"
                    else:  # 75-100
                        percentage_color = "red"
                    
                    print(f"[bold {chat_color}]|[/bold {chat_color}] {'Usage:':<20} [{percentage_color}]{bar} {usage_percentage:.1f}%[/{percentage_color}]")
                # Show model info (without tokenizer details)
                model_info = f"{context_info.architecture}"
                if context_info.parameter_count != 'unknown':
                    model_info += f" ({context_info.parameter_count}"
                    if context_info.quantization != 'unknown':
                        model_info += f", {context_info.quantization}"
                        model_info += ")"                
                    elif context_info.quantization != 'unknown':
                        model_info += f" ({context_info.quantization})"
                print(f"[bold {chat_color}]|[/bold {chat_color}] {'Model Info:':<20} [grey70]{model_info}[/grey70]")                # Show estimated VRAM usage for user-set context window
                # Create a modified context info that uses the user's num_ctx setting
                user_context_info = context_info._replace(actual_context=self.app.num_ctx)
                vram_estimate = self.app.model.estimate_context_vram_usage(user_context_info)
                if vram_estimate != "unknown":
                    print(f"[bold {chat_color}]|[/bold {chat_color}] {'Context VRAM:':<20} [yellow]{vram_estimate}[/yellow] [grey50](est.)[/grey50]")
        
        # Display temperature with color coding based on value
        temp_color = "blue" if self.app.temperature == 0.0 else "green" if self.app.temperature < 0.7 else "yellow" if self.app.temperature <= 1.0 else "orange1" if self.app.temperature <= 1.5 else "red"
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Temperature:':<20} [bold {temp_color}]{self.app.temperature}[/bold {temp_color}]")
        
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Verbosity:':<20} [bold][{'green' if self.app.verbosity else 'red'}]{self.app.verbosity}[/{'green' if self.app.verbosity else 'red'}][/bold]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Thinking Mode:':<20} [bold][{'green' if self.app.thinking_enabled else 'red'}]{self.app.thinking_enabled}[/{'green' if self.app.thinking_enabled else 'red'}][/bold]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Logging Enabled:':<20} [bold][{'green' if self.app.logging_enabled else 'red'}]{self.app.logging_enabled}[/{'green' if self.app.logging_enabled else 'red'}][/bold]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Config Path:':<20} [grey70]~/{config_path}[/grey70]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'Log Directory:':<20} [grey70]~/{log_dir}[/grey70]")
        print(f"[bold {chat_color}]|[/bold {chat_color}] {'System Prompt:':<20} [grey70]{self.app.system_prompt['content']}[/grey70]\n")

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
            
            # Use the passed chat_color parameter instead of recalculating
            # Display the last user message
            if last_messages.get('user'):
                print_message_with_bar(chat_color, "YOU", last_messages['user'].get('content', ''))
            
            # Display the last assistant message
            if last_messages.get('assistant'):
                print_message_with_bar(chat_color, "LLM", last_messages['assistant'].get('content', ''))