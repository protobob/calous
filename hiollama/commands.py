"""Command handlers for Hi, Ollama!"""
from pathlib import Path
from rich.prompt import Prompt
from rich import print
from .utils import get_chat_color, format_message_preview, reset_twist_content
from .constants import MAX_PROMPTS
from .config import ConfigManager

class CommandHandler:
    def __init__(self, app):
        self.app = app
        # Commands without arguments
        self.commands = {
            "/help": self.cmd_help,
            "/quit": self.cmd_quit,
            "/model": self.cmd_model,
            "/toggle_think": self.cmd_toggle_think,
            "/clear": self.cmd_clear,
            "/history": self.cmd_history,
            "/toggle_eval": self.cmd_toggle_eval,
            "/toggle_log": self.cmd_toggle_log,
            "/showvars": self.cmd_showvars,  # Updated command name
            "/twist": self.cmd_twist
        }
    
    def parse_and_execute(self, user_input):
        """Parse and execute commands."""
        if not user_input.startswith('/'):
            return False

        # Handle commands with arguments
        if user_input.lower().startswith("/system "):
            parts = user_input.split(" ", 1)  # Split into command and arguments
            if len(parts) > 1:
                self.cmd_system(parts[1])
            else:
                print("[bold red]Error:[/bold red] No system prompt provided.")
            return True

        # Handle commands with arguments that need special parsing
        user_input_lower = user_input.lower()
        
        # Handle /setmax command
        if user_input_lower.startswith("/setmax "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                self.cmd_setmax(parts[1])
            else:
                print("[bold red]Error:[/bold red] No maximum value provided.")
            return True
        
        # Handle /setprompt command
        if user_input_lower.startswith("/setprompt "):
            parts = user_input.split(" ", 2)
            if len(parts) >= 3:
                self.cmd_setprompt(parts[1], *parts[2:])
            else:
                print("[bold red]Error:[/bold red] Usage: /setprompt NUMBER PROMPT_TEXT")
            return True
        
        # Handle /prompt command
        if user_input_lower.startswith("/prompt "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                self.cmd_prompt(parts[1])
            else:
                print("[bold red]Error:[/bold red] Usage: /prompt NUMBER")
            return True
        
        # Handle /showprompt command
        if user_input_lower.startswith("/showprompt"):
            if user_input_lower == "/showprompt":
                # No arguments provided, default to all
                self.cmd_showprompt("all")
            else:
                # Arguments provided
                parts = user_input.split(" ", 1)
                if len(parts) > 1:
                    self.cmd_showprompt(parts[1])
                else:
                    self.cmd_showprompt("all")
            return True
        
        # Handle /load command
        if user_input_lower.startswith("/load "):
            parts = user_input.split(" ", 2)
            if len(parts) >= 2:
                filepath = parts[1]
                instructions = parts[2] if len(parts) > 2 else ""
                self.cmd_load(filepath, instructions)
            else:
                print("[bold red]Error:[/bold red] Usage: /load FILENAME [INSTRUCTIONS]")
            return True

        # Execute the command if it matches (no arguments)
        for command, handler in self.commands.items():
            if user_input.lower() == command:
                handler()
                return True

        # If we get here, it's an invalid command starting with /
        print(f"\n[bold red]Invalid command:[/bold red] {user_input}")
        print("[grey50]Type /help to see available commands.[/grey50]")
        return True

    def cmd_help(self):
        """Display the help menu."""
        self.app.ui.help_menu()
    
    def cmd_quit(self):
        """Save configuration and exit the program."""
        print("Saving configuration and exiting...")
        
        # Save configuration for all chat instances
        if hasattr(self.app, 'chat_instances') and self.app.chat_instances:
            for chat in self.app.chat_instances:
                try:
                    chat.save_config()
                except Exception as e:
                    print(f"Error saving config: {e}")
        else:
            # Just save this instance's config
            self.app.save_config()
        
        # Use os._exit(0) to force exit all threads
        import os
        os._exit(0)
    
    def cmd_model(self):
        """Select a different model globally for all chat instances."""
        selected = self.app.model.select_model()
        if selected:
            # Update the model globally
            updated_count = self.app.update_global_model(selected)
            print(f"Model changed globally to: {selected}")
            print(f"Updated model for {updated_count} chat instance(s).")
    
    def cmd_toggle_think(self):
        """Toggle filtering of LLM 'thought' sections."""
        self.app.think_filtering = not self.app.think_filtering
        self.app.config["think_filtering"] = self.app.think_filtering
        print(f"\nThink filtering is now: {self.app.think_filtering}")
    
    def cmd_clear(self):
        """Clear the chat history after confirmation."""
        confirm = input("Are you sure you want to clear the chat history? (y/n): ").strip().lower()
        if confirm in ["y", "yes"]:
            self.app.chat_history.clear()
            print("\nChat history cleared.")
        else:
            print("\nClear operation canceled.")
    
    def cmd_history(self):
        """Display the chat history."""
        self.app.chat_history.print_history()
    
    def cmd_system(self, *args):
        """Change the system prompt."""
        new_prompt = " ".join(args).strip()
        if not new_prompt:
            print("[bold red]Error:[/bold red] System prompt cannot be empty.")
            return

        print(f"\nPrevious System Prompt: [grey50]{self.app.system_prompt['content']}[/grey50]")
        self.app.system_prompt = {"role": "system", "content": new_prompt}
        self.app.config["system_prompt"] = new_prompt
        print(f"System prompt updated to: [grey50]{new_prompt}[/grey50]")

    def cmd_setmax(self, new_limit_str=""):
        """Set the maximum chat history size."""
        try:
            # Try to convert input to integer
            new_limit = int(new_limit_str)
            
            # Check if the value is valid
            if 2 <= new_limit <= 100 and new_limit % 2 == 0:
                self.app.MAX_HISTORY = new_limit
                self.app.config["MAX_HISTORY"] = self.app.MAX_HISTORY
                print(f"\nMaximum chat history set to {self.app.MAX_HISTORY}")
            else:
                print("Invalid value. Please use an even number between 2 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    def cmd_toggle_eval(self):
        """Toggle display of evaluation data after responses."""
        self.app.verbosity = not self.app.verbosity
        self.app.config["verbosity"] = self.app.verbosity
        print(f"\nVerbosity is now: {self.app.verbosity}")
    
    def cmd_toggle_log(self):
        """Toggle logging of chat history."""
        self.app.logging_enabled = not self.app.logging_enabled
        self.app.config["logging_enabled"] = self.app.logging_enabled
        print(f"\nLogging is now: {self.app.logging_enabled}")
    
    def cmd_setprompt(self, prompt_number_str="", *prompt_parts):
        """Set a saved prompt."""
        try:
            # Try to convert input to integer
            prompt_number = int(prompt_number_str)
            
            # Check if the value is valid
            if 1 <= prompt_number <= MAX_PROMPTS:
                # Join all prompt parts to create the full prompt text
                new_prompt = " ".join(prompt_parts).strip()
                if not new_prompt:
                    print("Error: Prompt text cannot be empty.")
                    return
                
                self.app.prompts[f"prompt{prompt_number}"] = new_prompt
                print(f"Prompt{prompt_number} set successfully!")
                self.app.save_config()
            else:
                print(f"Invalid prompt number. Please enter a number between 1 and {MAX_PROMPTS}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    def cmd_prompt(self, prompt_number_str=""):
        """Use a saved prompt."""
        try:
            prompt_number = int(prompt_number_str)
            if 1 <= prompt_number <= MAX_PROMPTS:
                selected_prompt = self.app.prompts[f"prompt{prompt_number}"]
                if selected_prompt:
                    print(f"Using Prompt{prompt_number}: {selected_prompt}")
                    self.app.handle_regular_input(selected_prompt)
                else:
                    print(f"Prompt{prompt_number} is empty. Set it first using /setprompt.")
            else:
                print(f"Invalid prompt number. Please enter a number between 1 and {MAX_PROMPTS}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    def cmd_showprompt(self, prompt_selector="all"):
        """Display saved prompts."""
        try:
            if prompt_selector.lower() == "all":
                # Show all prompts
                print("\n--- Saved Prompts ---")
                for i in range(1, MAX_PROMPTS + 1):
                    prompt = self.app.prompts[f"prompt{i}"]
                    print(f"Prompt{i}: {prompt if prompt else '[Empty]'}")
                print("---------------------\n")
            elif prompt_selector.isdigit():
                # Show a specific prompt
                prompt_number = int(prompt_selector)
                if 1 <= prompt_number <= MAX_PROMPTS:
                    prompt = self.app.prompts[f"prompt{prompt_number}"]
                    print(f"\nPrompt{prompt_number}: {prompt if prompt else '[Empty]'}\n")
                else:
                    print(f"Invalid prompt number. Please enter a number between 1 and {MAX_PROMPTS}.")
            else:
                print(f"Invalid input. Use '/showprompt all' or '/showprompt NUMBER' (1-{MAX_PROMPTS}).")
        except Exception as e:
            print(f"Error displaying prompts: {e}")
    
    def cmd_load(self, filepath, file_message=""):
        """Load a file and send it to the model with user instructions."""
        if not Path(filepath).exists():
            print(f"Error: File '{filepath}' does not exist.")
            return
            
        try:
            # If no message was provided in the command, ask for it
            if not file_message:
                file_message = Prompt.ask("[bold]Instructions[/bold]")
                
            from .utils import Utils
            file_prompt = Utils.load_file_as_prompt(filepath, file_message)
            print(f"\n[grey50]Sent [italic]{filepath}[/italic] -- hold on, this might take awhile...[/grey50]")
            self.app.handle_regular_input(file_prompt)
        except Exception as e:
            print(f"Failed to load file: {e}")
            
    def cmd_showvars(self):
        """Display application variables, including log and config paths."""
        self.app.ui.display_variables(
            active_chat_index=self.app.active_chat_index,
            selected_model=self.app.selected_model,
            verbosity=self.app.verbosity,
            think_filtering=self.app.think_filtering,
            max_history=self.app.MAX_HISTORY,
            system_prompt=self.app.system_prompt['content'],
            logging_enabled=self.app.logging_enabled,
            log_dir=self.app.chat_history.log_dir,
            config_path=ConfigManager.get_config_path(self.app.instance_index)
        )

    def cmd_twist(self):
        """Copy the last AI response, switch chats, and send it as a prompt."""
        # Get the last response dictionary
        last_response = self.app.last_response
        if not last_response:
            return

        # Extract the content from the last response
        twist_content = last_response.get("message", {}).get("content", "")
        if not twist_content:
            return

        # Show twist preview and store content
        self._display_twist_preview(twist_content)
        self._store_twist_content(twist_content)

        # Request chat switch
        self.app.switch_requested = True

    def _find_last_assistant_message(self):
        """Find the last assistant message in the chat history."""
        for msg in reversed(self.app.chat_history.history):
            if msg.get("role") == "assistant":
                return msg
        return None

    def _display_twist_preview(self, content):
        """Display a preview of the content being twisted."""
        current_chat_color = get_chat_color(self.app.active_chat_index)
        preview = format_message_preview(content, 50)
        print(f"[bold {current_chat_color}]↪ Twisting this message: "
              f"[/bold {current_chat_color}][italic {current_chat_color}]\"{preview}\"[/italic {current_chat_color}]")

    def _store_twist_content(self, content):
        """Store the twist content for the other chat instance."""
        current_index = self.app.active_chat_index
        other_index = 1 - current_index
        
        # Clear any existing twist content
        reset_twist_content(self.app)
        
        # Store on target chat instance
        target_chat = self.app.chat_instances[other_index]
        target_chat.twist_content = content
        
        # Show confirmation
        target_chat_color = get_chat_color(other_index)
        print(f"[bold {target_chat_color}]Twisting response to Chat {other_index + 1}..."
              f"[/bold {target_chat_color}]")