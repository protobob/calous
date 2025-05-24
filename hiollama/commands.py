"""Command handlers for Hi, Ollama!"""
from pathlib import Path
from rich.prompt import Prompt
from rich import print
from .utils import get_chat_color, format_message_preview, reset_twist_content
from .constants import MAX_PROMPTS

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
            "/showvar": self.cmd_showvar,
            "/twist": self.cmd_twist
        }
    
    def parse_and_execute(self, user_input):
        """Parse and execute commands."""
        if not user_input.startswith('/'):
            return False
        
        # Helper function to handle commands that need arguments
        def handle_command_with_args(command_prefix, min_args, usage_msg, handler_func):
            if user_input.lower().startswith(command_prefix + " "):
                parts = user_input.split(" ", min_args)  # Split based on required args
                
                # Check if we have enough arguments
                if len(parts) <= min_args:
                    print(usage_msg)
                    return True
                    
                # Extract arguments and call handler
                args = [part.strip() for part in parts[1:]]
                handler_func(*args)
                return True
            # Check for exact command match without arguments
            elif user_input.lower() == command_prefix:
                print(usage_msg)  # Show usage when command is used without arguments
                return True
            return False
    
        # Handle special commands that need arguments
        if handle_command_with_args("/load", 2, "Usage: /load filename prompt", self.cmd_load):
            return True
    
        if handle_command_with_args("/system", 1, "Usage: /system new system prompt", self.cmd_system):
            return True
    
        if handle_command_with_args("/setmax", 1, "Usage: /setmax NUMBER (even number between 2-100)", self.cmd_setmax):
            return True
    
        if handle_command_with_args("/setprompt", 2, "Usage: /setprompt NUMBER PROMPT_TEXT (NUMBER must be 1-10)", self.cmd_setprompt):
            return True
    
        if handle_command_with_args("/prompt", 1, "Usage: /prompt NUMBER (number between 1-10)", self.cmd_prompt):
            return True
    
        if handle_command_with_args("/showprompt", 1, "Usage: /showprompt NUMBER or /showprompt all", self.cmd_showprompt):
            return True
    
        # Handle standard commands from the dictionary
        command = user_input.split()[0].lower()
        
        if command in self.commands:
            self.commands[command]()
            return True
        else:
            print(f"Unknown command: {command}. Type /help for a list of commands.")
            return True
        
        return False
        
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
        """Select a different model."""
        selected = self.app.model.select_model()
        if selected:
            self.app.selected_model = selected
            self.app.config["selected_model"] = self.app.selected_model
            print(f"You selected: {self.app.selected_model}")
    
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
    
    def cmd_system(self, new_prompt):
        """Change the system prompt."""
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
            
    def cmd_showvar(self):
        """Display system variables."""
        self.app.ui.show_variables()
        
    def cmd_twist(self):
        """Copy the last AI response, switch chats, and send it as a prompt."""
        # Get last AI response
        last_assistant_msg = self._find_last_assistant_message()
        if not last_assistant_msg:
            print("[bold red]No assistant response to twist![/bold red]")
            return
        
        # Get the content and validate
        twist_content = last_assistant_msg.get("content", "")
        if not twist_content:
            print("[bold red]Empty response to twist![/bold red]")
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