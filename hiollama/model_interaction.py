"""Model interaction for Hi, Ollama!"""
import ollama
import re
import json
from typing import Optional, NamedTuple, Dict, Any, List
from rich import print
from .utils import get_chat_color

class ContextWindowInfo(NamedTuple):
    """Information about a model's context window."""
    max_context: int               # Training context window (from model metadata)
    runtime_context: Optional[int] # Runtime context window (from num_ctx parameter)
    actual_context: int            # Actual context being used for inference
    tokenizer_type: str           # Tokenizer family (gpt2, llama, etc.)
    architecture: str             # Model architecture (qwen3, llama, etc.)
    parameter_count: Optional[str] # Model parameter count (e.g., "8.2B")
    quantization: Optional[str]    # Quantization level (e.g., "Q4_K_M")

class ModelInteraction:
    def __init__(self, app):
        self.app = app    
        self._context_cache = {}  # Cache context window info to avoid repeated API calls
    
    def get_context_window_info(self, model_name: str) -> Optional[ContextWindowInfo]:
        """Get context window information for a model."""
        if not model_name:
            return None
            
        # Check cache first
        if model_name in self._context_cache:
            return self._context_cache[model_name]
        
        try:
            # Get model metadata from Ollama
            response = ollama.show(model_name)
            model_dict = response.model_dump()
            
            # Extract model info and parameters
            model_info = model_dict.get('modelinfo', {})
            parameters = model_dict.get('parameters', '')
            
            # Determine architecture
            architecture = model_info.get('general.architecture', 'unknown')
            
            # Get context window based on architecture
            context_key = f"{architecture}.context_length"
            max_context = model_info.get(context_key)
            
            # Fallback to common context length keys if architecture-specific key not found
            if max_context is None:
                for fallback_key in ['llama.context_length', 'context_length', 'max_position_embeddings']:
                    max_context = model_info.get(fallback_key)
                    if max_context is not None:
                        break
            
            # If still no context found, use a reasonable default based on model info
            if max_context is None:
                # Try to infer from model family in details
                details = model_dict.get('details', {})
                family = details.get('family', '').lower() if isinstance(details, dict) else ''
                
                # Default context windows for known families
                family_defaults = {
                    'llama': 4096,
                    'qwen': 8192, 
                    'mistral': 8192,
                    'gemma': 8192,
                    'phi': 4096,
                }
                max_context = family_defaults.get(family, 4096)
            
            # Parse runtime context from parameters string
            runtime_context = self._parse_num_ctx_parameter(parameters)
            
            # Determine actual context (runtime takes precedence if set)
            actual_context = runtime_context if runtime_context is not None else max_context
              # Get tokenizer type
            tokenizer_type = model_info.get('tokenizer.ggml.model', 'unknown')
            
            # Get model parameter count and quantization info
            parameter_count = model_info.get('general.parameter_count')
            if parameter_count:
                # Convert to human readable format (e.g., 8190735360 -> "8.2B")
                if parameter_count >= 1e9:
                    parameter_count = f"{parameter_count/1e9:.1f}B"
                elif parameter_count >= 1e6:
                    parameter_count = f"{parameter_count/1e6:.1f}M"
                else:
                    parameter_count = str(parameter_count)
            else:
                # Try to get from details if not in model_info
                details = model_dict.get('details', {})
                parameter_count = details.get('parameter_size', 'unknown') if isinstance(details, dict) else 'unknown'
            
            quantization = model_info.get('general.quantization_version')
            if not quantization:
                details = model_dict.get('details', {})
                quantization = details.get('quantization_level', 'unknown') if isinstance(details, dict) else 'unknown'
            
            # Create context window info
            context_info = ContextWindowInfo(
                max_context=max_context,
                runtime_context=runtime_context,
                actual_context=actual_context,
                tokenizer_type=tokenizer_type,
                architecture=architecture,
                parameter_count=parameter_count,
                quantization=quantization
            )
            
            # Cache the result
            self._context_cache[model_name] = context_info
            return context_info
            
        except Exception as e:
            print(f"[yellow]Warning: Could not get context window info for {model_name}: {e}[/yellow]")
            return None
    
    def _parse_num_ctx_parameter(self, parameters: str) -> Optional[int]:
        """Parse the num_ctx parameter from the parameters string."""
        if not parameters:
            return None
            
        # Look for num_ctx parameter in the parameters string
        # Format is typically: "num_ctx                        2048"
        match = re.search(r'num_ctx\s+(\d+)', parameters)
        if match:
            return int(match.group(1))
        return None
    
    def estimate_token_count(self, text: str, tokenizer_type: str = 'gpt2') -> int:
        """Estimate token count for given text based on tokenizer type."""
        if not text:
            return 0
            
        # For now, use a simple character-based estimation
        # This can be enhanced later with actual tokenizer libraries
        
        # Different tokenizer families have different character-to-token ratios
        char_to_token_ratios = {
            'gpt2': 4.0,      # GPT-2 style tokenizers        'llama': 4.2,     # LLaMA tokenizers tend to be slightly less efficient
            'mistral': 4.0,   # Similar to GPT-2
            'unknown': 4.0,   # Safe default
        }
        
        ratio = char_to_token_ratios.get(tokenizer_type, 4.0)
        return max(1, int(len(text) / ratio))
    
    def get_context_usage_percentage(self, model_name: str) -> Optional[float]:
        """Calculate current context window usage percentage."""
        context_info = self.get_context_window_info(model_name)
        if not context_info:
            return None
        
        # Count tokens in current conversation
        total_tokens = 0
        
        # Add system prompt tokens
        if self.app.system_prompt and self.app.system_prompt.get('content'):
            total_tokens += self.estimate_token_count(
                self.app.system_prompt['content'], 
                context_info.tokenizer_type
            )
        
        # Add chat history tokens
        for message in self.app.chat_history.history:
            content = message.get('content', '')
            total_tokens += self.estimate_token_count(content, context_info.tokenizer_type)
        
        # Calculate percentage based on user-set context window
        if self.app.num_ctx > 0:
            percentage = (total_tokens / self.app.num_ctx) * 100
            return min(100.0, percentage)  # Cap at 100%
        
        return 0.0    
    
    def estimate_context_vram_usage(self, context_info: ContextWindowInfo) -> str:
        """Estimate VRAM usage for context window based on model parameters."""
        if not context_info or not context_info.parameter_count or context_info.parameter_count == 'unknown':
            return "unknown"
        
        try:
            # Extract parameter count as float
            param_str = context_info.parameter_count.lower().replace('b', '').replace('m', '')
            if 'b' in context_info.parameter_count.lower():
                param_count = float(param_str) * 1e9
            elif 'm' in context_info.parameter_count.lower():
                param_count = float(param_str) * 1e6
            else:
                param_count = float(param_str)
            
            # Rough estimates for KV cache VRAM usage
            # Based on: tokens * hidden_dim * num_layers * 2 (key + value) * bytes_per_param
            
            # Model size to hidden dimension mapping (approximate)
            if param_count >= 70e9:  # 70B+
                hidden_dim = 8192
                num_layers = 80
            elif param_count >= 30e9:  # 30B+
                hidden_dim = 6144
                num_layers = 60
            elif param_count >= 13e9:  # 13B+
                hidden_dim = 5120
                num_layers = 40
            elif param_count >= 7e9:   # 7B+
                hidden_dim = 4096
                num_layers = 32
            elif param_count >= 3e9:   # 3B+
                hidden_dim = 3200
                num_layers = 26
            else:  # < 3B
                hidden_dim = 2048
                num_layers = 24            # Bytes per parameter based on quantization
            quant = str(context_info.quantization).upper() if context_info.quantization else ''
            if 'Q4' in quant:
                bytes_per_param = 0.5  # 4-bit quantization
            elif 'Q8' in quant:
                bytes_per_param = 1.0  # 8-bit quantization
            elif 'F16' in quant:
                bytes_per_param = 2.0  # 16-bit float
            elif 'F32' in quant:
                bytes_per_param = 4.0  # 32-bit float
            else:
                bytes_per_param = 0.5  # Default to Q4 estimate            # Calculate KV cache VRAM for full context
            tokens = context_info.actual_context
            kv_cache_bytes = tokens * hidden_dim * num_layers * 2 * bytes_per_param
            kv_cache_gb = kv_cache_bytes / (1024**3)
            
            # Add realistic estimate for attention computation overhead
            # Use a small percentage of KV cache size instead of quadratic formula
            attention_overhead_gb = kv_cache_gb * 0.2  # 20% overhead for attention computation
            total_context_vram = kv_cache_gb + attention_overhead_gb
            
            if total_context_vram < 1:
                return f"~{total_context_vram*1024:.0f}MB"
            else:
                return f"~{total_context_vram:.1f}GB"
                
        except (ValueError, AttributeError) as e:
            return "unknown"      
            
    def talk_to_model(self, user_prompt, images=None):
        """Send a prompt to the selected model and return the streaming response."""
        # Check if model is selected before making API call
        if not self.app.selected_model or self.app.selected_model.strip() == "":
            print(f"\n[bold red]No Model Selected:[/bold red] Please select a model first.")
            print(f"[grey50]Use /model to choose an available model[/grey50]")
            return {"message": {"content": "[Error: No model selected. Use /model to choose a model.]"}}
        
        messages = [self.app.system_prompt] + self.app.chat_history.history.copy()
        
        # If images are provided, add them to the last user message
        if images and messages:
            # Find the most recent user message (should be the last one in history)
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get('role') == 'user':
                    # Add images to this message
                    messages[i] = {**messages[i], 'images': images}
                    break
        
        # Get available function tools from plugin system
        tools = self._get_function_tools()
        
        return self._handle_streaming(messages, user_prompt, tools)
    
    def _get_function_tools(self) -> List[Dict[str, Any]]:
        """Get function tools from the plugin system."""
        # Access plugin manager through the app if available
        if hasattr(self.app, 'plugin_manager') and self.app.plugin_manager:
            tools = []            
            for plugin in self.app.plugin_manager.get_function_calling_plugins():
                schemas = plugin.get_function_schemas()
                if schemas:
                    # Add all function schemas from this plugin
                    tools.extend(schemas)
            return tools
        return []
    def _handle_function_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle function calls from the model."""
        from .unified_logger import unified_logger
        
        results = []
        
        if not hasattr(self.app, 'plugin_manager') or not self.app.plugin_manager:
            return results
        
        for tool_call in tool_calls:
            function_name = tool_call.get('function', {}).get('name')
            function_args = tool_call.get('function', {}).get('arguments', {})
            
            # Parse arguments if they're a string
            if isinstance(function_args, str):
                try:
                    function_args = json.loads(function_args)
                except json.JSONDecodeError:
                    function_args = {}
            
            print(f"[dim yellow]🔧 Using LLM tool: {function_name}[/dim yellow]")
            
            # Log function call attempt
            unified_logger._write_log_entry(
                entry_type="PLUGIN_FUNCTION_CALL",
                content=f"Function: {function_name}, Args: {function_args}"
            )
            
            # Find plugin that can handle this function
            result = None
            plugin_name = None
            try:
                for plugin in self.app.plugin_manager.get_function_calling_plugins():
                    schemas = plugin.get_function_schemas()
                    for schema in schemas:
                        if schema.get('function', {}).get('name') == function_name:
                            plugin_name = plugin.name
                            result = plugin.call_function(function_name, function_args)
                            break
                    if result is not None:
                        break
                
                if result is None:
                    result = {
                        "error": f"Function {function_name} not found",
                        "success": False
                    }
                    # Log function not found
                    unified_logger._write_log_entry(
                        entry_type="PLUGIN_FUNCTION_ERROR",
                        content=f"Function: {function_name}, Error: Function not found"
                    )
                else:
                    # Log successful function result
                    unified_logger._write_log_entry(
                        entry_type="PLUGIN_FUNCTION_RESULT",
                        content=f"Plugin: {plugin_name}, Function: {function_name}, Result: {result}"
                    )
                    
            except Exception as e:
                result = {
                    "error": f"Error executing {function_name}: {str(e)}",
                    "success": False
                }
                # Log function execution error
                unified_logger._write_log_entry(
                    entry_type="PLUGIN_FUNCTION_ERROR",
                    content=f"Plugin: {plugin_name}, Function: {function_name}, Error: {str(e)}"
                )
            
            # Format result for model
            tool_result = {
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False),
                "tool_call_id": tool_call.get('id', '')
            }
            results.append(tool_result)
        
        return results    
    def _handle_streaming(self, messages, user_prompt, tools=None):
        """Handle streaming response from the model with optional function calling."""
        full_response = ""
        thinking_content = ""
        response_dict = None
        tool_calls = []
        
        try:
            # Print the header before streaming starts
            chat_index = getattr(self.app, 'active_chat_index', 0)
            chat_color = get_chat_color(chat_index)
            print(f"\n[bold {chat_color}]|[/bold {chat_color}] [bold {chat_color}]{chat_index + 1})[/bold {chat_color}][underline]{self.app.selected_model}[/underline]:\n")
            
            # Prepare chat options
            chat_options = {
                'model': self.app.selected_model,
                'messages': messages,
                'stream': True,
                'options': {'num_ctx': self.app.num_ctx, 'temperature': self.app.temperature}
            }
            
            # Add tools if available
            if tools:
                chat_options['tools'] = tools
            
            # Try to use native thinking API, fall back to without think parameter
            try:
                chat_options['think'] = self.app.thinking_enabled
                chunks = ollama.chat(**chat_options)
            except TypeError:
                # Fallback for older ollama client that doesn't support think parameter
                chat_options.pop('think', None)
                chunks = ollama.chat(**chat_options)
            
            for chunk in chunks:
                # Handle both content and thinking from the new API
                if hasattr(chunk, 'message'):
                    # Regular content (always clean with native API)
                    content = getattr(chunk.message, 'content', '')
                    if content:
                        full_response += content
                        print(content, end='', flush=True)
                    
                    # Handle tool calls
                    if hasattr(chunk.message, 'tool_calls') and chunk.message.tool_calls:
                        tool_calls.extend(chunk.message.tool_calls)
                    
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
            
            # Handle function calls if present
            if tool_calls:
                tool_results = self._handle_function_calls(tool_calls)
                if tool_results:
                    # Add tool calls to messages and call model again
                    messages.append({"role": "assistant", "content": full_response, "tool_calls": tool_calls})
                    messages.extend(tool_results)
                    print(f"[dim green]🔄 Processing function results...[/dim green]")
                    # Make follow-up call without tools to get final response
                    return self._handle_streaming(messages, user_prompt, tools=None)
            
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
            # Get context window info for display
            context_info = self.get_context_window_info(model)
            if context_info:
                context_display = f"[cyan]{context_info.actual_context//1000}k[/cyan] ctx"
                print(f"{i}. {model} [{context_display}]")
            else:
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