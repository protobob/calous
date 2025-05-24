"""Model interaction for Hi, Ollama!"""
import ollama
import requests
from rich import print
from .utils import get_chat_color

class ModelInteraction:
    def __init__(self, app):
        self.app = app

    def talk_to_model(self, user_prompt):
        """Send a prompt to the selected model and return the response."""
        try:
            # Prepare the messages for the API call
            messages = [self.app.system_prompt] + self.app.chat_history.history.copy()
            messages.append({'role': 'user', 'content': user_prompt})

            # Call the Ollama API
            response = ollama.chat(model=self.app.selected_model, messages=messages)

            # Debug: Log the raw response
            # print(f"[bold yellow]Debug: Raw API Response:[/bold yellow] {response}")

            # Validate the response structure
            if not hasattr(response, 'message') or not hasattr(response.message, 'content'):
                raise ValueError("API response is missing 'message' or 'content' attributes.")

            return response

        except requests.exceptions.HTTPError as http_err:
            print(f"[bold red]HTTP Error:[/bold red] {http_err}")
            return {"message": {"content": "[Error: HTTP error occurred.]"}}

        except requests.exceptions.ConnectionError as conn_err:
            print(f"[bold red]Connection Error:[/bold red] {conn_err}")
            return {"message": {"content": "[Error: Failed to connect to the API server.]"}}

        except requests.exceptions.Timeout as timeout_err:
            print(f"[bold red]Timeout Error:[/bold red] {timeout_err}")
            return {"message": {"content": "[Error: API request timed out.]"}}

        except Exception as err:
            print(f"[bold red]Unexpected Error:[/bold red] {err}")
            return {"message": {"content": "[Error: An unexpected error occurred.]"}}

    def list_ollama_models(self):
        """Get a list of available Ollama models."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            return [model["name"] for model in response.json().get("models", [])]
        except requests.exceptions.RequestException as e:
            print(f"[bold red]Error fetching models:[/bold red] {e}")
            return []

    def select_model(self):
        """Display available models and let the user select one."""
        models = self.list_ollama_models()
        if not models:
            print("[bold red]No models installed.[/bold red]")
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
            print("[bold red]Invalid selection, try again.[/bold red]")

    def process_response(self, user_input, response):
        """Process the response from the model, handles logging, and updates chat history."""
        raw_response = response.get('message', {}).get('content', '')
        if not raw_response:
            return

        # Store the last response in the HiOllamaChat instance
        self.app.last_response = response  # Store the entire response dictionary

        clean_response = self.app.chat_history.strip_thoughts(raw_response) if self.app.think_filtering else raw_response
        if not clean_response:
            clean_response = "[No valid response received from the model.]"

        # Determine color based on chat index
        chat_index = getattr(self.app, 'active_chat_index', 0)
        chat_color = get_chat_color(chat_index)

        # Print with colored bar, colored chat number and underlined model name, response on a new line
        print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]{chat_index + 1})[/bold {chat_color}][underline]{self.app.selected_model}[/underline]:\n")
        print(f"{clean_response}")

        if self.app.verbosity:
            if 'eval_count' in response and 'eval_duration' in response:
                print(self.pull_eval_data(response))
            else:
                print("[italic][grey50]Evaluation data missing in response.[/grey50][/italic]")

        if isinstance(clean_response, str):
            self.app.chat_history.log_file(user_input, clean_response)
        else:
            print("[bold red]Error:[/bold red] Response is not a valid string and will not be logged.")

        self.app.chat_history.add_message("assistant", clean_response)

    def pull_eval_data(self, response):
        """Extract and format evaluation data from the response."""
        eval_count = response.get('eval_count')
        eval_duration_ns = response.get('eval_duration')
        if not eval_count or not eval_duration_ns:
            return "[italic][grey50]Invalid data: eval_count or eval_duration missing or zero.[/grey50][/italic]"
        eval_duration_s = eval_duration_ns / 1_000_000_000
        avg_per_token_ms = (eval_duration_ns / eval_count) / 1_000_000
        return (
            f"[italic][grey50](Eval Count: {eval_count}, "
            f"Eval Duration: {eval_duration_s:.2f}s, "
            f"Average per-token time: {avg_per_token_ms:.2f}ms)[/grey50][/italic]"
        )