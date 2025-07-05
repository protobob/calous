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
        return False  # Temporarily disabled due to format issues
    
    def generate_response(self, messages: List[Dict[str, Any]], model: str, 
                         stream: bool = True, **kwargs) -> Any:
        """Generate a response using Groq's API."""
        if not self.groq_client:
            raise Exception("Groq client not initialized")
        
        # Convert CALOUS message format to Groq format
        groq_messages = self._convert_messages_to_groq(messages)
        
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
            # TODO: Fix tool format conversion for Groq
            # For now, disable function calling to prevent errors
            pass  # request_params["tools"] = tools
        
        return self.groq_client.chat.completions.create(**request_params)
    
    def _convert_messages_to_groq(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert CALOUS message format to Groq format."""
        groq_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            groq_message = {
                "role": role,
                "content": content
            }
            
            # Handle images (if supported by Groq in the future)
            if 'images' in message:
                # For now, just include text description
                groq_message["content"] = f"{content}\n[Image content not supported by Groq]"
            
            # Handle tool calls
            if 'tool_calls' in message:
                groq_message["tool_calls"] = message['tool_calls']
            
            # Handle tool results
            if role == 'tool':
                groq_message["tool_call_id"] = message.get('tool_call_id', '')
            
            groq_messages.append(groq_message)
        
        return groq_messages
    
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
                if choice.delta and choice.delta.tool_calls:
                    yield {
                        "message": {
                            "tool_calls": choice.delta.tool_calls,
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