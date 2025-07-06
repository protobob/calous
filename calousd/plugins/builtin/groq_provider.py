"""Groq provider plugin for CALOUS."""
import os
import json
from typing import Dict, Any, List, Optional, Iterator
from ..base import ProviderPlugin


class GroqProviderPlugin(ProviderPlugin):
    """Plugin that provides Groq AI integration for CALOUS."""
    
    def __init__(self):
        super().__init__(
            name="groq_provider",
            version="1.0.0",
            description="Groq AI provider plugin for fast language model inference"
        )
        self.groq_client = None
        self.api_key = None
        self._cached_models = None  # Cache the model list
        
    def initialize(self) -> bool:
        """Initialize the Groq provider plugin."""
        try:
            # Check for API key
            self.api_key = os.environ.get("GROQ_API_KEY")
            if not self.api_key:
                self.error = "GROQ_API_KEY environment variable not set"
                return False
            
            # Import and initialize Groq client
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.api_key)
            except ImportError:
                self.error = "groq package not installed. Install with: pip install groq"
                return False
            
            # Test connection by listing models
            try:
                models = self.groq_client.models.list()
                if not models or not models.data:
                    self.error = "No models available from Groq API"
                    return False
            except Exception as e:
                self.error = f"Failed to connect to Groq API: {e}"
                return False
            
            return True
            
        except Exception as e:
            self.error = f"Failed to initialize Groq provider: {e}"
            return False
    
    def get_provider_name(self) -> str:
        """Return the name of this provider."""
        return "groq"
    
    def get_available_models(self) -> List[str]:
        """Return list of available Groq models."""
        if not self.groq_client:
            return []
        
        # Return cached models if available
        if self._cached_models is not None:
            return self._cached_models
        
        try:
            models = self.groq_client.models.list()
            model_list = [model.id for model in models.data if model.id]
            self._cached_models = sorted(model_list)  # Cache the sorted list
            return self._cached_models
        except Exception:
            return []
    
    def supports_streaming(self) -> bool:
        """Return True if this provider supports streaming responses."""
        return True
    
    def supports_function_calling(self) -> bool:
        """Return True if this provider supports function calling."""
        return True  # Re-enabled with proper format conversion
    
    def generate_response(self, messages: List[Dict[str, Any]], model: str, 
                         stream: bool = True, **kwargs) -> Any:
        """Generate a response using Groq's API."""
        if not self.groq_client:
            raise Exception("Groq client not initialized")
        
        # Convert CALOUS message format to Groq format
        groq_messages = self._convert_messages_to_groq(messages)
        
        # Debug: log the messages being sent (only in debug mode)
        try:
            from ...unified_logger import unified_logger
            unified_logger.debug_command(f"Sending {len(groq_messages)} messages to Groq API")
            unified_logger.debug_command(f"Messages summary: {[msg.get('role', 'unknown') for msg in groq_messages]}")
        except:
            pass
        
        # Extract generation parameters
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 8192)
        
        # Build request parameters
        request_params = {
            "model": model,
            "messages": groq_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        # Add function calling if tools are provided
        tools = kwargs.get('tools')
        if tools:
            # Convert CALOUS tool format to Groq format
            groq_tools = self._convert_tools_to_groq(tools)
            if groq_tools:
                request_params["tools"] = groq_tools
                # Debug: log the tools being sent
                try:
                    from ...unified_logger import unified_logger
                    unified_logger.debug_command(f"Sending {len(groq_tools)} tools to Groq")
                    for i, tool in enumerate(groq_tools):
                        unified_logger.debug_command(f"Tool {i}: {tool.get('function', {}).get('name', 'unknown')}")
                except:
                    pass
        
        try:
            response = self.groq_client.chat.completions.create(**request_params)
        except Exception as e:
            raise Exception(f"Groq API call failed: {str(e)}")
        
        # Wrap the response to convert tool calls on-the-fly
        if request_params.get("stream", False):
            return self._wrap_streaming_response(response)
        else:
            return response
    
    def _convert_messages_to_groq(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert CALOUS message format to Groq format."""
        groq_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # Handle tool results - Groq expects specific format for tool messages
            if role == 'tool':
                # Simplify complex JSON tool results for Groq
                try:
                    import json
                    parsed_content = json.loads(content)
                    if isinstance(parsed_content, dict) and 'summary' in parsed_content:
                        # Use just the summary for simpler processing
                        simplified_content = parsed_content['summary']
                    else:
                        simplified_content = content
                except:
                    simplified_content = content
                
                # Debug: log the simplified content
                try:
                    from ...unified_logger import unified_logger
                    unified_logger.debug_command(f"Simplified tool result: {simplified_content}")
                    unified_logger.debug_command(f"Tool call ID: {message.get('tool_call_id', 'missing')}")
                except:
                    pass
                    
                groq_message = {
                    "role": "tool", 
                    "content": simplified_content,
                    "tool_call_id": message.get('tool_call_id', '')
                }
            # Handle assistant messages with tool calls
            elif role == 'assistant' and 'tool_calls' in message:
                # For Groq: assistant messages with tool_calls should NOT have content
                groq_message = {
                    "role": "assistant",
                    "tool_calls": message['tool_calls']
                }
            else:
                # Regular messages
                groq_message = {
                    "role": role,
                    "content": content
                }
                
                # Handle images (if supported by Groq in the future)
                if 'images' in message:
                    groq_message["content"] = f"{content}\n[Image content not supported by Groq]"
            
            groq_messages.append(groq_message)
        
        return groq_messages
    
    def _convert_tools_to_groq(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert CALOUS tool format to Groq format."""
        groq_tools = []
        
        for tool in tools:
            # CALOUS format is OpenAI-compatible, which Groq should accept
            # Ensure we have the expected structure
            if "type" in tool and tool["type"] == "function" and "function" in tool:
                groq_tools.append(tool)
            elif "name" in tool and "description" in tool:
                # Convert simplified format to full format
                groq_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool.get("parameters", {})
                    }
                }
                groq_tools.append(groq_tool)
        
        return groq_tools
    
    def _wrap_streaming_response(self, response_generator):
        """Wrap streaming response to convert tool calls to dictionaries."""
        for chunk in response_generator:
            if hasattr(chunk, 'choices') and chunk.choices:
                choice = chunk.choices[0]
                # Convert tool calls if present
                if (choice.delta and hasattr(choice.delta, 'tool_calls') and 
                    choice.delta.tool_calls):
                    # Create a wrapper class that behaves like the original but with converted tool calls
                    class DeltaWrapper:
                        def __init__(self, original_delta):
                            self.original = original_delta
                            self.content = getattr(original_delta, 'content', None)
                            self.role = getattr(original_delta, 'role', None)
                            # Convert tool calls to dictionaries
                            self.tool_calls = []
                            if hasattr(original_delta, 'tool_calls') and original_delta.tool_calls:
                                for tool_call in original_delta.tool_calls:
                                    tool_call_dict = {
                                        'id': getattr(tool_call, 'id', ''),
                                        'type': getattr(tool_call, 'type', 'function'),
                                        'function': {
                                            'name': getattr(tool_call.function, 'name', '') if hasattr(tool_call, 'function') else '',
                                            'arguments': getattr(tool_call.function, 'arguments', '') if hasattr(tool_call, 'function') else ''
                                        }
                                    }
                                    self.tool_calls.append(tool_call_dict)
                    
                    # Create a wrapper choice that uses the wrapped delta
                    class ChoiceWrapper:
                        def __init__(self, original_choice, wrapped_delta):
                            self.original = original_choice
                            self.delta = wrapped_delta
                            self.finish_reason = getattr(original_choice, 'finish_reason', None)
                            self.index = getattr(original_choice, 'index', None)
                    
                    # Create wrapped chunk
                    class ChunkWrapper:
                        def __init__(self, original_chunk, wrapped_choice):
                            self.original = original_chunk
                            self.choices = [wrapped_choice]
                            self.id = getattr(original_chunk, 'id', None)
                            self.created = getattr(original_chunk, 'created', None)
                            self.model = getattr(original_chunk, 'model', None)
                            self.object = getattr(original_chunk, 'object', None)
                    
                    wrapped_delta = DeltaWrapper(choice.delta)
                    wrapped_choice = ChoiceWrapper(choice, wrapped_delta)
                    wrapped_chunk = ChunkWrapper(chunk, wrapped_choice)
                    yield wrapped_chunk
                else:
                    yield chunk
            else:
                yield chunk
    
    def stream_response(self, response_generator) -> Iterator[Dict[str, Any]]:
        """Convert Groq streaming response to CALOUS format."""
        for chunk in response_generator:
            if chunk.choices and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if choice.delta and choice.delta.content:
                    yield {
                        "message": {
                            "content": choice.delta.content,
                            "role": "assistant"
                        }
                    }
                
                # Handle tool calls in streaming
                if choice.delta and hasattr(choice.delta, 'tool_calls') and choice.delta.tool_calls:
                    # Convert tool call objects to dictionaries to avoid serialization issues
                    tool_calls = []
                    for tool_call in choice.delta.tool_calls:
                        tool_call_dict = {
                            'id': getattr(tool_call, 'id', ''),
                            'type': getattr(tool_call, 'type', 'function'),
                            'function': {
                                'name': getattr(tool_call.function, 'name', '') if hasattr(tool_call, 'function') else '',
                                'arguments': getattr(tool_call.function, 'arguments', '') if hasattr(tool_call, 'function') else ''
                            }
                        }
                        tool_calls.append(tool_call_dict)
                    
                    yield {
                        "message": {
                            "tool_calls": tool_calls,
                            "role": "assistant"
                        }
                    }
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if not self.groq_client:
            return {}
        
        try:
            models = self.groq_client.models.list()
            for model_info in models.data:
                if model_info.id == model:
                    return {
                        "id": model_info.id,
                        "context_window": getattr(model_info, 'context_window', 8192),
                        "created": getattr(model_info, 'created', None),
                        "owned_by": getattr(model_info, 'owned_by', 'groq')
                    }
        except Exception:
            pass
        
        return {}
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.groq_client = None
        self.api_key = None