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

# === Config Handling ===
CONFIG_PATH = Path.home() / ".hiollama_config.json"
DEFAULT_CONFIG = {
    "selected_model": "qwen3:0.6B",
    "verbosity": True,
    "think_filtering": True,
    "MAX_HISTORY": 20,
    "system_prompt": "You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code."
}

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

# === Global State ===
console = Console()
config = load_config()
selected_model = config["selected_model"]
verbosity = config["verbosity"]
think_filtering = config["think_filtering"]
MAX_HISTORY = config["MAX_HISTORY"]
chat_history = []
system_prompt = {
    "role": "system",
    "content": config["system_prompt"]
}

# === Utilities ===

def spinner(stop_flag):
    spinner_widget = Spinner("dots", text="Inference")
    with Live(spinner_widget, refresh_per_second=10, console=console) as live:
        while not stop_flag.is_set():
            time.sleep(0.1)

def add_message(role, content):
    chat_history.append({"role": role, "content": content})
    if len(chat_history) > MAX_HISTORY:
        chat_history.pop(0)

def strip_thoughts(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def print_chat_history():
    print("\n--- Chat History ---")
    for msg in chat_history:
        role = msg.get("role", "unknown").capitalize()
        print(f"[{role}] {msg['content']}")
    print("--------------------\n")

def help_menu():
    print(
        f"\n[bold]Welcome to 'Hi, Ollama!' v0.2[/bold]\n\n"
        f"'/quit' to exit.\n"
        f"'/model' to select model.\n"
        f"'/load filename' to send 'filename' to the model (will ask for a prompt).\n"
        f"'/system' to change system prompt.\n"
        f"'/togglethink' to toggle llm thought filtering (for reasoning models).\n"
        f"'/history' prints out current chat history.\n"
        f"'/clear' clears the chat history.\n"
        f"'/setmax' sets max chat history (must be even number).\n"
        f"'/verbosity' to toggle eval data shown after response.\n"
        f"'/help' for this help screen.\n\n"
        f"[bold]System Variables[/bold]\n\n"
        f"Model: {selected_model}\n"
        f"Think Toggle: {think_filtering}\n"
        f"Verbosity: {verbosity}\n"
        f"Max Chat History: {MAX_HISTORY}\n"
        f"System Prompt: [italic]{system_prompt['content']}[/italic]\n"
    )

def load_file_as_prompt(filepath, filenotes):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return f"{filenotes}:\n\n{content}"

def talkllm(userprompt, history, model_name):
    messages = [system_prompt] + history.copy()
    messages.append({'role': 'user', 'content': userprompt})
    return ollama.chat(model=model_name, messages=messages)

def list_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch models: {e}")

def select_model():
    models = list_ollama_models()
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

def log_file(prompt, model, response):
    try:
        timestamp = datetime.now()
        log_filename = f"{timestamp.strftime('%Y-%m-%d')}.txt"
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp.strftime('%H:%M:%S')}] You: {prompt}\n")
            f.write(f"[{timestamp.strftime('%H:%M:%S')}] {model}: {response}\n\n")
    except Exception as e:
        print(f"Failed to write chat log: {e}")

def pull_eval_data(response):
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

def cmd_help():
    help_menu()

def cmd_quit():
    save_config(config)
    print("Exiting.")
    exit()

def cmd_model():
    global selected_model
    selected_model = select_model()
    config["selected_model"] = selected_model
    print(f"You selected: {selected_model}")

def cmd_togglethink():
    global think_filtering
    think_filtering = not think_filtering
    config["think_filtering"] = think_filtering
    print(f"\nThink filtering is now: {think_filtering}")

def cmd_clear():
    chat_history.clear()
    print("\nChat history cleared.")

def cmd_history():
    print_chat_history()

def cmd_system():
    global system_prompt
    print(f"\nCurrent System Prompt: {system_prompt['content']}\n")
    user_system = input("New System Prompt: ")
    system_prompt = {"role": "system", "content": user_system}
    config["system_prompt"] = user_system

def cmd_setmax():
    global MAX_HISTORY
    while True:
        new_limit = input("\nSet new maximum chat history (even number between 2–100): ").strip()
        if new_limit.isdigit():
            new_limit = int(new_limit)
            if 2 <= new_limit <= 100 and new_limit % 2 == 0:
                MAX_HISTORY = new_limit
                config["MAX_HISTORY"] = MAX_HISTORY
                while len(chat_history) > MAX_HISTORY:
                    chat_history.pop(0)
                print(f"\nMaximum chat history set to {MAX_HISTORY}")
                break
            print("Please enter an even number between 2 and 100.")
        else:
            print("Invalid input. Please enter a number.")

def cmd_verbosity():
    global verbosity
    verbosity = not verbosity
    config["verbosity"] = verbosity
    print(f"\nVerbosity is now: {verbosity}")

# === Command Map ===

COMMANDS = {
    "/help": cmd_help,
    "/quit": cmd_quit,
    "/model": cmd_model,
    "/togglethink": cmd_togglethink,
    "/clear": cmd_clear,
    "/history": cmd_history,
    "/system": cmd_system,
    "/setmax": cmd_setmax,
    "/verbosity": cmd_verbosity
}

# === Entry Point ===

os.system('cls' if os.name == 'nt' else 'clear')
print(f"\nLoaded config from: {CONFIG_PATH}\n")
selected_model = config["selected_model"]
print(f"Model: {selected_model}")

try:
    while True:
        prompt_text = (
            f"\n"
            f"[italic][grey50]Max:[/grey50]"
            f"[grey70]{MAX_HISTORY}[/grey70][/italic]"
            f"[grey50] (Type /help for help.)[/grey50]\n"
            f"[bold]You[/bold]"
        )

        user_input = Prompt.ask(prompt_text).strip().lower()

        if user_input.startswith("/load "):
            filepath = user_input[len("/load "):].strip()
            try:
                file_message = Prompt.ask("[bold]Instructions[/bold]")
                file_prompt = load_file_as_prompt(filepath, file_message)
                print(f"\n[grey50]Sent [italic]{filepath}[/italic] -- hold on, this might take awhile...[/grey50]")

                stop_flag = threading.Event()
                spinner_thread = threading.Thread(target=spinner, args=(stop_flag,))
                spinner_thread.start()

                add_message("user", file_prompt)
                response = talkllm(file_prompt, chat_history, selected_model)

                stop_flag.set()
                spinner_thread.join()
            except Exception as e:
                print(f"Failed to load file: {e}")
                continue

        elif user_input in COMMANDS:
            COMMANDS[user_input]()
            continue

        else:
            add_message("user", user_input)
            try:
                stop_flag = threading.Event()
                spinner_thread = threading.Thread(target=spinner, args=(stop_flag,))
                spinner_thread.start()

                response = talkllm(user_input, chat_history, selected_model)

                stop_flag.set()
                spinner_thread.join()
            except ollama.APIError as e:
                print(f"Ollama API Error: {e}")
                continue
            except Exception as e:
                print(f"Model Error: {e}")
                continue

        raw_response = response['message']['content']
        clean_response = strip_thoughts(raw_response) if think_filtering else raw_response
        print(f"\n{selected_model}: {clean_response}")
        if verbosity:
            print(pull_eval_data(response))
        add_message("assistant", clean_response)
        log_file(user_input, selected_model, clean_response)

except KeyboardInterrupt:
    print("\nInterrupted. Saving config and exiting.")
finally:
    save_config(config)
