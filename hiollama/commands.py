"""Command handlers for Hi, Ollama!"""
from pathlib import Path
from rich.prompt import Prompt
from rich import print
from .utils import Utils

class CommandHandler:
    def __init__(self, app):
        self.app = app
        # Commands without arguments
        self.commands = {
            "/help": self.cmd_help,
            "/quit": self.cmd_quit,
            "/model": self.cmd_model,
            "/togglethink": self.cmd_togglethink,
            "/clear": self.cmd_clear,
            "/history": self.cmd_history,
            "/verbosity": self.cmd_verbosity,
            "/togglelog": self.cmd_togglelog,
            "/showprompt": self.cmd_showprompt
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
        self.app.save_config()
        print("Exiting.")
        exit()
    
    def cmd_model(self):
        """Select a different model."""
        selected = self.app.model.select_model()
        if selected:
            self.app.selected_model = selected
            self.app.config["selected_model"] = self.app.selected_model
            print(f"You selected: {self.app.selected_model}")
    
    def cmd_togglethink(self):
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
    
    def cmd_verbosity(self):
        """Toggle display of evaluation data after responses."""
        self.app.verbosity = not self.app.verbosity
        self.app.config["verbosity"] = self.app.verbosity
        print(f"\nVerbosity is now: {self.app.verbosity}")
    
    def cmd_togglelog(self):
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
            if 1 <= prompt_number <= 10:
                # Join all prompt parts to create the full prompt text
                new_prompt = " ".join(prompt_parts).strip()
                if not new_prompt:
                    print("Error: Prompt text cannot be empty.")
                    return
                
                self.app.prompts[f"prompt{prompt_number}"] = new_prompt
                print(f"Prompt{prompt_number} set successfully!")
                self.app.save_config()
            else:
                print("Invalid prompt number. Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    def cmd_prompt(self, prompt_number_str=""):
        """Use a saved prompt."""
        try:
            prompt_number = int(prompt_number_str)
            if 1 <= prompt_number <= 10:
                selected_prompt = self.app.prompts[f"prompt{prompt_number}"]
                if selected_prompt:
                    print(f"Using Prompt{prompt_number}: {selected_prompt}")
                    self.app.handle_regular_input(selected_prompt)
                else:
                    print(f"Prompt{prompt_number} is empty. Set it first using /setprompt.")
            else:
                print("Invalid prompt number. Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    def cmd_showprompt(self):
        """Display saved prompts."""
        try:
            prompt_number = input("Enter prompt number (1-10) or leave blank to show all: ").strip()
            if prompt_number == "":
                # Show all prompts
                print("\n--- Saved Prompts ---")
                for i in range(1, 11):
                    prompt = self.app.prompts[f"prompt{i}"]
                    print(f"Prompt{i}: {prompt if prompt else '[Empty]'}")
                print("---------------------\n")
            elif prompt_number.isdigit() and 1 <= int(prompt_number) <= 10:
                # Show a specific prompt
                prompt_number = int(prompt_number)
                prompt = self.app.prompts[f"prompt{prompt_number}"]
                print(f"\nPrompt{prompt_number}: {prompt if prompt else '[Empty]'}\n")
            else:
                print("Invalid input. Please enter a number between 1 and 10, or leave blank to show all prompts.")
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
                
            file_prompt = Utils.load_file_as_prompt(filepath, file_message)
            print(f"\n[grey50]Sent [italic]{filepath}[/italic] -- hold on, this might take awhile...[/grey50]")
            self.app.handle_regular_input(file_prompt)
        except Exception as e:
            print(f"Failed to load file: {e}")