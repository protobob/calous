"""Model interaction for Hi, Ollama!"""
import ollama
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
            
            # Call the Ollama API
            response = ollama.chat(model=self.app.selected_model, messages=messages)

            # Validate the response structure
            if not hasattr(response, 'message') or not hasattr(response.message, 'content'):
                raise ValueError("API response is missing 'message' or 'content' attributes.")

            return response

        except ollama.ResponseError as e:
            if "model not found" in str(e).lower() or "model" in str(e).lower() and "not found" in str(e).lower():
                print(f"\n[bold red]Model Error:[/bold red] Model '{self.app.selected_model}' not found.")
                print(f"[grey50]Try: /model to select an available model[/grey50]")
                available_models = self.list_ollama_models()
                if available_models:
                    print(f"[grey50]Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}[/grey50]")
            else:
                print(f"\n[bold red]Ollama API Error:[/bold red] {e}")
            return {"message": {"content": "[Error: Model response failed.]"}}

        except ConnectionError as e:
            print(f"\n[bold red]Connection Error:[/bold red] Cannot connect to Ollama server.")
            print(f"[grey50]Try: 'ollama serve' in another terminal or check if port 11434 is accessible[/grey50]")
            return {"message": {"content": "[Error: Cannot connect to Ollama server.]"}}

        except TimeoutError as e:
            print(f"\n[bold red]Timeout Error:[/bold red] Request timed out.")
            print(f"[grey50]The model may be processing a complex request. Try again or use a smaller model.[/grey50]")
            return {"message": {"content": "[Error: Request timed out.]"}}

        except Exception as e:
            print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
            print(f"[grey50]If this persists, try restarting Ollama with 'ollama serve'[/grey50]")
            return {"message": {"content": "[Error: An unexpected error occurred.]"}}

    def list_ollama_models(self):
        """Get a list of available Ollama models with better error handling."""
        try:
            response = ollama.list()
            if not response or not hasattr(response, 'models'):
                print(f"\n[yellow]Warning:[/yellow] Unexpected response format from Ollama")
                return []
            return [model.model for model in response.models]
        except ollama.ResponseError as e:
            print(f"\n[bold red]Ollama API Error:[/bold red] {e}")
            print(f"[grey50]Check if Ollama is running properly[/grey50]")
            return []
        except ConnectionError:
            print(f"\n[bold red]Connection Error:[/bold red] Cannot connect to Ollama server.")
            print(f"[grey50]Make sure Ollama is running: 'ollama serve'[/grey50]")
            return []
        except Exception as e:
            print(f"\n[bold red]Error fetching models:[/bold red] {e}")
            print(f"[grey50]Check if Ollama is installed and running properly[/grey50]")
            return []

    def select_model(self):
        """Display available models and let the user select one."""
        models = self.list_ollama_models()
        if not models:
            print("\n[bold red]No models installed.[/bold red]")
            print("[grey50]Install a model with: 'ollama pull model-name'[/grey50]")
            return None

        print("\nAvailable Ollama models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        while True:
            try:
                choice = input("\nSelect a model by number (or 'q' to cancel): ").strip()
                if choice.lower() == 'q':
                    return None
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(models):
                        return models[index]
                    else:
                        print(f"\n[bold red]Invalid selection.[/bold red] Please choose 1-{len(models)}")
                else:
                    print("\n[bold red]Invalid input.[/bold red] Please enter a number or 'q' to cancel")
            except KeyboardInterrupt:
                print("\n[grey50]Model selection cancelled.[/grey50]")
                return None

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
            print("\n[bold red]Error:[/bold red] Response is not a valid string and will not be logged.")

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