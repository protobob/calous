import ollama
import re
from datetime import datetime
from rich import print
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt
import requests
import os
import threading
import time
import sys
import json
from pathlib import Path

class HiOllamaChat:
    CONFIG_PATH = Path.home() / ".hiollama_config.json"
    DEFAULT_CONFIG = {
        "selected_model": "qwen3:0.6B",
        "verbosity": True,
        "think_filtering": True,
        "MAX_HISTORY": 20,
        "system_prompt": "You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code.",
        "prompts": {f"prompt{i}": "" for i in range(1, 11)}  # Add this line
    }

    def __init__(self):
        self.console = Console()
        self.config = self.load_config()
        self.selected_model = self.config.get("selected_model", "qwen3:0.6B")
        self.verbosity = self.config.get("verbosity", True)
        self.think_filtering = self.config.get("think_filtering", True)
        self.MAX_HISTORY = self.config.get("MAX_HISTORY", 20)
        self.chat_history = []
        self.system_prompt = {
            "role": "system",
            "content": self.config.get("system_prompt", "You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code.")
        }
        self.logging_enabled = self.config.get("logging_enabled", True)  # Load logging state
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, 11)})  # Load prompts
        self.COMMANDS = {
            "/help": self.cmd_help,
            "/quit": self.cmd_quit,
            "/model": self.cmd_model,
            "/togglethink": self.cmd_togglethink,
            "/clear": self.cmd_clear,
            "/history": self.cmd_history,
            "/system": self.cmd_system,
            "/setmax": self.cmd_setmax,
            "/verbosity": self.cmd_verbosity,
            "/togglelog": self.cmd_togglelog,
            "/setprompt": self.cmd_setprompt,
            "/prompt": self.cmd_prompt,
            "/showprompt": self.cmd_showprompt  # Add this line
        }

    def load_config(self):
        if self.CONFIG_PATH.exists():
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config
            except Exception as e:
                print(f"Failed to load config: {e}")
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            self.config["selected_model"] = self.selected_model
            self.config["verbosity"] = self.verbosity
            self.config["think_filtering"] = self.think_filtering
            self.config["MAX_HISTORY"] = self.MAX_HISTORY
            self.config["system_prompt"] = self.system_prompt["content"]
            self.config["logging_enabled"] = self.logging_enabled  # Save logging state
            self.config["prompts"] = self.prompts  # Save prompts
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def spinner(self, stop_flag):
        spinner_widget = Spinner("dots", text="Inference")
        with Live(spinner_widget, refresh_per_second=10, console=self.console) as live:
            while not stop_flag.is_set():
                time.sleep(0.1)

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})
        if len(self.chat_history) > self.MAX_HISTORY:
            self.chat_history.pop(0)

    def strip_thoughts(self, text):
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def print_chat_history(self):
        print("\n--- Chat History ---")
        for msg in self.chat_history:
            role = msg.get("role", "unknown").capitalize()
            print(f"[{role}] {msg['content']}")
        print("--------------------\n")

    def help_menu(self):
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
            f"\n  Model:          {self.selected_model}"
            f"\n  Logging:        {self.logging_enabled}"
            f"\n  Think Filtering:{self.think_filtering}"
            f"\n  Verbosity:      {self.verbosity}"
            f"\n  Max History:    {self.MAX_HISTORY}"
            f"\n  System Prompt:  [italic]{self.system_prompt['content']}[/italic]"
            "\n"
        )

    def load_file_as_prompt(self, filepath, filenotes):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"{filenotes}:\n\n{content}"

    def talkllm(self, userprompt):
        messages = [self.system_prompt] + self.chat_history.copy()
        messages.append({'role': 'user', 'content': userprompt})
        return ollama.chat(model=self.selected_model, messages=messages)

    def list_ollama_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            return [model["name"] for model in response.json().get("models", [])]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch models: {e}")

    def select_model(self):
        models = self.list_ollama_models()
        if not models:
            print("No models installed.")
            return None

        print("\nAvailable Ollama models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        while True:
            choice = input("\nSelect a model by number: ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(models):
                    return models[index]
            print("Invalid selection, try again.")

    def log_file(self, prompt, response):
        if not self.logging_enabled:
            return
        try:
            timestamp = datetime.now()
            log_dir = Path.home() / "hiollama_logs"  # Save logs in a subdirectory in the home folder
            log_dir.mkdir(exist_ok=True)  # Ensure the directory exists
            log_filename = log_dir / f"{timestamp.strftime('%Y-%m-%d')}.txt"
            with open(log_filename, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp.strftime('%H:%M:%S')}] You: {prompt}\n")
                f.write(f"[{timestamp.strftime('%H:%M:%S')}] {self.selected_model}: {response}\n\n")
        except Exception as e:
            print(f"Failed to write chat log: {e}")

    def pull_eval_data(self, response):
        eval_count = response.get('eval_count')
        eval_duration_ns = response.get('eval_duration')
        if not eval_count or not eval_duration_ns:
            return "Invalid data: eval_count or eval_duration missing or zero."
        eval_duration_s = eval_duration_ns / 1_000_000_000
        avg_per_token_ms = (eval_duration_ns / eval_count) / 1_000_000
        return (
            f"[italic][grey50](Eval Count: {eval_count}, "
            f"Eval Duration: {eval_duration_s:.2f}s, "
            f"Average per-token time: {avg_per_token_ms:.2f}ms)[/grey50][/italic]"
        )

    # === Command Handlers ===

    def cmd_help(self):
        self.help_menu()

    def cmd_quit(self):
        self.save_config()
        print("Exiting.")
        exit()

    def cmd_model(self):
        selected = self.select_model()
        if selected:
            self.selected_model = selected
            self.config["selected_model"] = self.selected_model
            print(f"You selected: {self.selected_model}")

    def cmd_togglethink(self):
        self.think_filtering = not self.think_filtering
        self.config["think_filtering"] = self.think_filtering
        print(f"\nThink filtering is now: {self.think_filtering}")

    def cmd_clear(self):
        confirm = input("Are you sure you want to clear the chat history? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.chat_history.clear()
            print("\nChat history cleared.")
        else:
            print("\nClear operation canceled.")

    def cmd_history(self):
        self.print_chat_history()

    def cmd_system(self):
        print(f"\nCurrent System Prompt: {self.system_prompt['content']}\n")
        user_system = input("New System Prompt: ")
        self.system_prompt = {"role": "system", "content": user_system}
        self.config["system_prompt"] = user_system

    def cmd_setmax(self):
        while True:
            new_limit = input("\nSet new maximum chat history (even number between 2–100): ").strip()
            if new_limit.isdigit():
                new_limit = int(new_limit)
                if 2 <= new_limit <= 100 and new_limit % 2 == 0:
                    self.MAX_HISTORY = new_limit
                    self.config["MAX_HISTORY"] = self.MAX_HISTORY
                    while len(self.chat_history) > self.MAX_HISTORY:
                        self.chat_history.pop(0)
                    print(f"\nMaximum chat history set to {self.MAX_HISTORY}")
                    break
                print("Please enter an even number between 2 and 100.")
            else:
                print("Invalid input. Please enter a number.")

    def cmd_verbosity(self):
        self.verbosity = not self.verbosity
        self.config["verbosity"] = self.verbosity
        print(f"\nVerbosity is now: {self.verbosity}")

    def cmd_togglelog(self):
        self.logging_enabled = not self.logging_enabled
        print(f"\nLogging is now: {self.logging_enabled}")

    def cmd_setprompt(self):
        """
        Allows the user to set a specific prompt (e.g., /setprompt 1).
        """
        try:
            prompt_number = int(input("Enter prompt number (1-10): ").strip())
            if 1 <= prompt_number <= 10:
                new_prompt = input(f"Enter the text for prompt{prompt_number}: ").strip()
                self.prompts[f"prompt{prompt_number}"] = new_prompt
                print(f"Prompt{prompt_number} set successfully!")
                # Save the updated prompts to the config
                self.save_config()
            else:
                print("Invalid prompt number. Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    def cmd_prompt(self):
        """
        Allows the user to use a specific prompt (e.g., /prompt 1).
        """
        try:
            prompt_number = int(input("Enter prompt number (1-10): ").strip())
            if 1 <= prompt_number <= 10:
                selected_prompt = self.prompts[f"prompt{prompt_number}"]
                if selected_prompt:
                    print(f"Using Prompt{prompt_number}: {selected_prompt}")
                    self.add_message("user", selected_prompt)
                    response = self.talkllm(selected_prompt)
                    self.process_response(selected_prompt, response)
                else:
                    print(f"Prompt{prompt_number} is empty. Set it first using /setprompt.")
            else:
                print("Invalid prompt number. Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    def cmd_showprompt(self):
        """
        Displays a specific prompt or all prompts if no number is provided.
        """
        try:
            prompt_number = input("Enter prompt number (1-10) or leave blank to show all: ").strip()
            if prompt_number == "":
                # Show all prompts
                print("\n--- Saved Prompts ---")
                for i in range(1, 11):
                    prompt = self.prompts[f"prompt{i}"]
                    print(f"Prompt{i}: {prompt if prompt else '[Empty]'}")
                print("---------------------\n")
            elif prompt_number.isdigit() and 1 <= int(prompt_number) <= 10:
                # Show a specific prompt
                prompt_number = int(prompt_number)
                prompt = self.prompts[f"prompt{prompt_number}"]
                print(f"\nPrompt{prompt_number}: {prompt if prompt else '[Empty]'}\n")
            else:
                print("Invalid input. Please enter a number between 1 and 10, or leave blank to show all prompts.")
        except Exception as e:
            print(f"Error displaying prompts: {e}")

    def process_response(self, user_input, response):
        """
        Processes the response from the model, handles logging, and updates chat history.
        """
        raw_response = response.get('message', {}).get('content', '')
        if not raw_response:
            print("Error: Response does not contain the expected 'message' or 'content' keys.")
            return

        clean_response = self.strip_thoughts(raw_response) if self.think_filtering else raw_response
        if not clean_response:
            clean_response = "[No valid response received from the model.]"
        print(f"\n{self.selected_model}: {clean_response}")

        if self.verbosity:
            if 'eval_count' in response and 'eval_duration' in response:
                print(self.pull_eval_data(response))
            else:
                print("[italic][grey50]Evaluation data missing in response.[/grey50][/italic]")

        if isinstance(clean_response, str):
            self.log_file(user_input, clean_response)
        else:
            print("Error: Response is not a valid string and will not be logged.")

        self.add_message("assistant", clean_response)

    def run_with_spinner(self, target, *args):
        stop_flag = threading.Event()
        spinner_thread = threading.Thread(target=self.spinner, args=(stop_flag,))
        spinner_thread.start()
        result = target(*args)
        stop_flag.set()
        spinner_thread.join()
        return result

    # === Command Handlers ===

    def cmd_load(self, filepath):
        """
        Load a file and send it to the model with user instructions.
        """
        if not Path(filepath).exists():
            print(f"Error: File '{filepath}' does not exist.")
            return
            
        try:
            file_message = Prompt.ask("[bold]Instructions[/bold]")
            file_prompt = self.load_file_as_prompt(filepath, file_message)
            print(f"\n[grey50]Sent [italic]{filepath}[/italic] -- hold on, this might take awhile...[/grey50]")

            self.add_message("user", file_prompt)
            # Use the spinner while waiting for the model response
            response = self.run_with_spinner(self.talkllm, file_prompt)

            self.process_response(file_prompt, response)
        except Exception as e:
            print(f"Failed to load file: {e}")

    # === Main Loop ===

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\nLoaded config from: {self.CONFIG_PATH}\n")
        print(f"Model: {self.selected_model}")

        try:
            while True:
                prompt_text = (
                    f"\n"
                    f"[italic][grey50]Max:[/grey50]"
                    f"[grey70]{self.MAX_HISTORY}[/grey70][/italic]"
                    f"[grey50] (Type /help for help.)[/grey50]\n"
                    f"[bold]You[/bold]"
                )

                user_input = Prompt.ask(prompt_text).strip()

                if user_input.lower().startswith("/load "):
                    filepath = user_input[len("/load "):].strip()
                    self.cmd_load(filepath)
                    continue

                elif user_input.lower() in self.COMMANDS:
                    self.COMMANDS[user_input.lower()]()
                    continue

                else:
                    self.add_message("user", user_input)
                    try:
                        # Use the spinner while waiting for the model response
                        response = self.run_with_spinner(self.talkllm, user_input)
                    except ollama.APIError as e:
                        print(f"Ollama API Error: {e}")
                        continue
                    except Exception as e:
                        print(f"Model Error: {e}")
                        continue

                    # Call the method to process the response
                    self.process_response(user_input, response)

        except KeyboardInterrupt:
            print("\nInterrupted. Saving config and exiting.")
        finally:
            self.save_config()

if __name__ == "__main__":
    HiOllamaChat().run()