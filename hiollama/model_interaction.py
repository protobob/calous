"""Model interaction for Hi, Ollama!"""
import ollama
from rich import print
from .utils import get_chat_color

class ModelInteraction:
    def __init__(self, app):
        self.app = app

    def talk_to_model(self, user_prompt):
        """Send a prompt to the selected model and return the streaming response."""
        messages = [self.app.system_prompt] + self.app.chat_history.history.copy()
        return self._handle_streaming(messages, user_prompt)    
    
    def _handle_streaming(self, messages, user_prompt):
        """Handle streaming response from the model."""
        full_response = ""
        thinking_content = ""
        response_dict = None
        
        try:            # Print the header before streaming starts
            chat_index = getattr(self.app, 'active_chat_index', 0)
            chat_color = get_chat_color(chat_index)
            print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]{chat_index + 1})[/bold {chat_color}][underline]{self.app.selected_model}[/underline]:\n")
            
            # Try to use native thinking API, fall back to without think parameter
            try:
                chunks = ollama.chat(model=self.app.selected_model, messages=messages, stream=True, think=self.app.thinking_enabled)
            except TypeError:
                # Fallback for older ollama client that doesn't support think parameter
                chunks = ollama.chat(model=self.app.selected_model, messages=messages, stream=True)
            
            for chunk in chunks:
                # Handle both content and thinking from the new API
                if hasattr(chunk, 'message'):
                    # Regular content (always clean with native API)
                    content = getattr(chunk.message, 'content', '')
                    if content:
                        full_response += content
                        print(content, end='', flush=True)
                    
                    # Thinking content (only displayed when thinking is enabled)
                    if self.app.thinking_enabled and hasattr(chunk.message, 'thinking'):
                        thinking = getattr(chunk.message, 'thinking', '')
                        if thinking:
                            thinking_content += thinking
                            # Display thinking in a different style (dim cyan for reasoning)
                            print(f"[dim cyan]{thinking}[/dim cyan]", end='', flush=True)
                
                # Store the last chunk to get eval data if available
                response_dict = chunk            
            
            print()  # newline after stream
            
            # With native API, full_response is always clean (no manual stripping needed)
            clean_response = full_response
                
            if not clean_response:
                clean_response = "[No valid response received from the model.]"
            
            # Create response object with cleaned content for history and twist operations
            final_response = {"message": {"content": clean_response}}
            
            # Add eval data if available from the last chunk
            if response_dict and hasattr(response_dict, 'eval_count'):
                final_response['eval_count'] = response_dict.eval_count
            if response_dict and hasattr(response_dict, 'eval_duration'):
                final_response['eval_duration'] = response_dict.eval_duration
            
            # Process the complete response (this handles history, logging, etc.)
            self._process_response(user_prompt, final_response, full_response)
            return final_response

        except ollama.ResponseError as e:
            return self._handle_response_error(e)
        except ConnectionError as e:
            return self._handle_connection_error(e)
        except TimeoutError as e:
            return self._handle_timeout_error(e)
        except Exception as e:
            return self._handle_unexpected_error(e)

    def _handle_response_error(self, e):
        """Handle ResponseError with detailed messaging."""
        if "model not found" in str(e).lower() or "model" in str(e).lower() and "not found" in str(e).lower():
            print(f"\n[bold red]Model Error:[/bold red] Model '{self.app.selected_model}' not found.")
            print(f"[grey50]Try: /model to select an available model[/grey50]")
            available_models = self.list_ollama_models()
            if available_models:
                print(f"[grey50]Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}[/grey50]")
        else:
            print(f"\n[bold red]Ollama API Error:[/bold red] {e}")
        return {"message": {"content": "[Error: Model response failed.]"}}

    def _handle_connection_error(self, e):
        """Handle ConnectionError with helpful messaging."""
        print(f"\n[bold red]Connection Error:[/bold red] Cannot connect to Ollama server.")
        print(f"[grey50]Try: 'ollama serve' in another terminal or check if port 11434 is accessible[/grey50]")
        return {"message": {"content": "[Error: Cannot connect to Ollama server.]"}}

    def _handle_timeout_error(self, e):
        """Handle TimeoutError with helpful messaging."""
        print(f"\n[bold red]Timeout Error:[/bold red] Request timed out.")
        print(f"[grey50]The model may be processing a complex request. Try again or use a smaller model.[/grey50]")
        return {"message": {"content": "[Error: Request timed out.]"}}    
    
    def _handle_unexpected_error(self, e):
        """Handle unexpected errors with helpful messaging."""
        print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
        print(f"[grey50]If this persists, try restarting Ollama with 'ollama serve'[/grey50]")
        return {"message": {"content": "[Error: An unexpected error occurred.]"}}

    def _process_response(self, user_input, response, full_response_for_logging=None):
        """Process response for history and logging (no output printing since streaming already printed)."""
        raw_response = response.get('message', {}).get('content', '')
        if not raw_response:
            return

        # CRITICAL: For twist operations, last_response must ALWAYS contain clean content (no thinking)
        # This ensures twist never sends model reasoning to other chats
        self.app.last_response = response  # This already contains clean content from _handle_streaming

        # The response already contains cleaned content (thoughts stripped)
        clean_response = raw_response

        # Show eval data if verbosity is enabled
        if self.app.verbosity:
            if 'eval_count' in response and 'eval_duration' in response:
                print(self.pull_eval_data(response))
            else:
                print("[italic][grey50]Evaluation data missing in response.[/grey50][/italic]")

        # Add to chat history (clean response without thoughts)
        self.app.chat_history.add_message("assistant", clean_response)

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