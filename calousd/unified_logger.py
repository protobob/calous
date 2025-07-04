"""Enhanced unified logging system for CALOUS with multi-stream support and debug routing."""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager
from .constants import LOG_DIR


class UnifiedLogger:
    """Enhanced unified logging system with multi-stream support and debug routing separation."""
    
    # Log stream definitions
    STREAMS = {
        'app': 'app.log',           # General application events
        'debug': 'debug.log',       # Debug information (daemon internals, socket handling)  
        'model': 'model.log',       # Model interactions, API calls, responses
        'audit': 'audit.log',       # Command execution, user actions
        'error': 'error.log',       # Errors and exceptions
        'legacy': None              # Legacy daily log (YYYY-MM-DD.txt)
    }
    
    def __init__(self, debug_enabled: bool = False):
        self.enabled = True
        self.debug_enabled = debug_enabled
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_level = logging.INFO
        self.structured_format = False  # JSON vs plain text
        
        # Context for structured logging
        self._context_data: Dict[str, Any] = {}
        
        # Initialize log directory
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Set up stream-specific loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Initialize stream-specific loggers with rotation and formatting."""
        # Configure root logger to avoid interference
        logging.getLogger().setLevel(logging.WARNING)
        
        for stream_name, filename in self.STREAMS.items():
            if filename is None:  # Skip legacy stream for now
                continue
                
            logger = logging.getLogger(f"calous.{stream_name}")
            
            # Set appropriate level based on stream and debug setting
            if stream_name == 'debug':
                logger.setLevel(logging.DEBUG if self.debug_enabled else logging.INFO)
            else:
                logger.setLevel(self.log_level)
                
            logger.propagate = False  # Prevent propagation to root logger
            
            # Clear any existing handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Create file handler with daily rotation
            log_file = LOG_DIR / filename
            handler = logging.FileHandler(log_file, encoding='utf-8')
            
            # Set formatter based on structured_format preference
            if self.structured_format:
                formatter = logging.Formatter(
                    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "stream": "' + stream_name + '", "message": %(message)s}'
                )
            else:
                formatter = logging.Formatter(
                    '[%(asctime)s] [%(levelname)s] [' + stream_name.upper() + '] %(message)s',
                    datefmt='%H:%M:%S'
                )
            
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            self.loggers[stream_name] = logger
    
    def _log_to_stream(self, stream: str, level: int, message: str, **kwargs):
        """Internal method to log to a specific stream with context."""
        if not self.enabled:
            return
            
        # Skip debug messages if debug is disabled
        if stream == 'debug' and not self.debug_enabled:
            return
            
        logger = self.loggers.get(stream)
        if not logger:
            return
            
        # Add context data
        context = {**self._context_data, **kwargs}
        
        if self.structured_format:
            # JSON structured logging
            log_data = {
                "message": message,
                **context
            }
            logger.log(level, json.dumps(log_data))
        else:
            # Plain text with context
            context_str = ""
            if context:
                context_parts = [f"{k}={v}" for k, v in context.items()]
                context_str = f" [{', '.join(context_parts)}]"
            
            logger.log(level, f"{message}{context_str}")
    
    # Legacy compatibility methods (reimplemented using new system)
    def _get_log_file_path(self) -> Path:
        """Get the current log file path based on today's date (legacy method)."""
        timestamp = datetime.now()
        return LOG_DIR / f"{timestamp.strftime('%Y-%m-%d')}.txt"
    
    def _write_log_entry(self, entry_type: str, content: str, chat_index: Optional[int] = None):
        """Write a formatted log entry to the legacy daily log file."""
        if not self.enabled:
            return
            
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_file = self._get_log_file_path()
            
            # Format the log entry
            chat_info = f"[Chat {chat_index + 1}]" if chat_index is not None else "[System]"
            log_entry = f"[{timestamp}] {chat_info} {entry_type}: {content}\n"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            # Use new error logging instead of _output
            self.error(f"Failed to write legacy log: {e}", component='legacy_logging')
    
    def log_conversation(self, chat_index: int, role: str, content: str, model: Optional[str] = None):
        """Log a conversation message."""
        # Log to both legacy format and new structured logging
        if role.lower() == "user":
            self._write_log_entry("USER", content, chat_index)
            self.info(f"User message", stream='app', chat_channel=chat_index, 
                     role=role, content_length=len(content))
        elif role.lower() == "assistant":
            model_info = f" ({model})" if model else ""
            self._write_log_entry(f"ASSISTANT{model_info}", content, chat_index)
            self.model_interaction(request="", response=content, model=model, chat_channel=chat_index)
        else:
            self._write_log_entry(f"{role.upper()}", content, chat_index)
            self.info(f"Message from {role}", stream='app', chat_channel=chat_index, 
                     role=role, content_length=len(content))
    
    def log_channel_switch(self, from_chat: int, to_chat: int, reason: str = "manual"):
        """Log channel switching events."""
        message = f"From Chat {from_chat + 1} to Chat {to_chat + 1} ({reason})"
        self._write_log_entry("CHANNEL_SWITCH", message)
        self.audit("chat.switch", result=f"from_{from_chat}_to_{to_chat}", reason=reason)
    
    def log_twist_action(self, from_chat: int, to_chat: int, content_preview: str):
        """Log twist actions between channels."""
        preview = content_preview.replace('\n', ' ').strip()
        if len(preview) > 100:
            preview = preview[:100] + "..."
        message = f"From Chat {from_chat + 1} to Chat {to_chat + 1}: \"{preview}\""
        self._write_log_entry("TWIST", message)
        self.audit("chat.twist", result=f"from_{from_chat}_to_{to_chat}", 
                  content_preview=preview)
    
    def log_system_prompt_change(self, chat_index: int, new_prompt: str):
        """Log system prompt changes."""
        preview = new_prompt.replace('\n', ' ').strip()
        if len(preview) > 100:
            preview = preview[:100] + "..."
        self._write_log_entry("SYSTEM_PROMPT", f"\"{preview}\"", chat_index)
        self.audit("system_prompt.change", chat_channel=chat_index, 
                  prompt_preview=preview, prompt_length=len(new_prompt))
    
    def log_command_execution(self, chat_index: int, command: str, result: Optional[str] = None):
        """Log command execution."""
        if result:
            self._write_log_entry("COMMAND", f"{command} -> {result}", chat_index)
        else:
            self._write_log_entry("COMMAND", command, chat_index)
        
        self.audit(command, chat_channel=chat_index, result=result)
    
    def log_model_change(self, new_model: str, chat_count: int):
        """Log global model changes."""
        message = f"Changed to {new_model} (affecting {chat_count} chats)"
        self._write_log_entry("MODEL_CHANGE", message)
        self.audit("model.change", result=new_model, affected_chats=chat_count)
    
    def log_session_start(self, num_chats: int, model: str):
        """Log session startup."""
        message = f"Started with {num_chats} chats using model {model}"
        self._write_log_entry("SESSION_START", message)
        self.info(f"Session started", stream='app', num_chats=num_chats, model=model)
    
    def log_session_end(self):
        """Log session shutdown."""
        self._write_log_entry("SESSION_END", "Application shutdown")
        self.info("Session ended", stream='app')
    
    def log_chat_history_clear(self, chat_index: int):
        """Log when chat history is cleared."""
        self._write_log_entry("HISTORY_CLEAR", "Chat history cleared", chat_index)
        self.audit("history.clear", chat_channel=chat_index)
    
    def log_export_action(self, chat_index: int, filename: str):
        """Log chat export actions."""
        self._write_log_entry("EXPORT", f"Chat exported to {filename}", chat_index)
        self.audit("chat.export", chat_channel=chat_index, filename=filename)
    
    def toggle_logging(self) -> bool:
        """Toggle unified logging on/off."""
        self.enabled = not self.enabled
        self._write_log_entry("LOGGING_TOGGLE", f"Logging {'enabled' if self.enabled else 'disabled'}")
        self.info(f"Logging {'enabled' if self.enabled else 'disabled'}", stream='app')
        return self.enabled
    
    def add_separator(self, label: Optional[str] = None):
        """Add a visual separator to the legacy log file."""
        if not self.enabled:
            return
            
        try:
            log_file = self._get_log_file_path()
            separator = "=" * 50
            if label:
                separator = f"=== {label} " + "=" * (44 - len(label))
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{separator}\n\n")
            
            if label:
                self.info(f"Log separator added: {label}", stream='app')
        except Exception as e:
            self.error(f"Failed to write log separator: {e}", component='legacy_logging')
            
    def log_plugin_event(self, event_type: str, message: str):
        """Log plugin-related events."""
        self._write_log_entry(f"PLUGIN_{event_type.upper()}", message)
        self.info(f"Plugin {event_type}: {message}", stream='app', component='plugin')
    
    # Enhanced logging methods with proper debug routing
    def debug(self, message: str, stream: str = 'debug', **kwargs):
        """Debug-level logging - routes to log files, NOT client output."""
        self._log_to_stream(stream, logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, stream: str = 'app', **kwargs):
        """Info-level logging."""
        self._log_to_stream(stream, logging.INFO, message, **kwargs)
    
    def warning(self, message: str, stream: str = 'app', **kwargs):
        """Warning-level logging."""
        self._log_to_stream(stream, logging.WARNING, message, **kwargs)
    
    def error(self, message: str, stream: str = 'error', **kwargs):
        """Error-level logging."""
        self._log_to_stream(stream, logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, stream: str = 'error', **kwargs):
        """Critical-level logging."""
        self._log_to_stream(stream, logging.CRITICAL, message, **kwargs)
    
    def audit(self, command: str, user_info: Optional[str] = None, result: Optional[str] = None, **kwargs):
        """Audit logging for command execution and user actions."""
        audit_data = {
            'command': command,
            'user_info': user_info,
            'result': result,
            **kwargs
        }
        self._log_to_stream('audit', logging.INFO, f"Command executed: {command}", **audit_data)
    
    def model_interaction(self, request: str, response: Optional[str] = None, 
                         timing: Optional[float] = None, model: Optional[str] = None, **kwargs):
        """Model interaction logging."""
        model_data = {
            'model': model,
            'timing_ms': timing,
            'request_length': len(request) if request else 0,
            'response_length': len(response) if response else 0,
            **kwargs
        }
        
        log_msg = f"Model interaction"
        if model:
            log_msg += f" with {model}"
        if timing:
            log_msg += f" ({timing:.2f}ms)"
            
        self._log_to_stream('model', logging.INFO, log_msg, **model_data)
    
    # Debug routing methods - these NEVER send output to clients
    def debug_socket(self, message: str, connection_id: Optional[str] = None):
        """Route socket debug info to debug.log, not client."""
        self.debug(message, stream='debug', component='socket', connection_id=connection_id)
    
    def debug_command(self, command: str, args: Optional[str] = None, chat_channel: Optional[int] = None):
        """Route command processing debug info to debug.log."""
        self.debug(f"Processing command: {command}", stream='debug', 
                  component='command', args=args, chat_channel=chat_channel)
    
    def debug_model(self, prompt: str, response: Optional[str] = None, metadata: Optional[Dict] = None):
        """Route model interaction debug info to debug.log."""
        debug_data = {'component': 'model'}
        if metadata:
            debug_data.update(metadata)
        
        self.debug(f"Model debug info", stream='debug', 
                  prompt_length=len(prompt), response_length=len(response) if response else 0, 
                  **debug_data)
    
    # Context management
    @contextmanager
    def log_context(self, chat_channel: Optional[int] = None, user_id: Optional[str] = None, **kwargs):
        """Add context to all log messages in this block."""
        context = {}
        if chat_channel is not None:
            context['chat_channel'] = chat_channel
        if user_id is not None:
            context['user_id'] = user_id
        context.update(kwargs)
        
        # Save current context
        old_context = self._context_data.copy()
        
        # Add new context
        self._context_data.update(context)
        
        try:
            yield
        finally:
            # Restore old context
            self._context_data = old_context
    
    # Configuration methods
    def set_debug_enabled(self, enabled: bool):
        """Enable or disable debug logging."""
        self.debug_enabled = enabled
        # Reinitialize loggers with new debug setting
        self._setup_loggers()
        self.info(f"Debug logging {'enabled' if enabled else 'disabled'}", stream='app')
    
    def set_structured_format(self, structured: bool):
        """Switch between JSON and plain text logging."""
        self.structured_format = structured
        # Reinitialize loggers with new format
        self._setup_loggers()
        self.info(f"Logging format changed to {'JSON' if structured else 'plain text'}", stream='app')
    
    def set_log_level(self, level: Union[int, str]):
        """Set the global log level."""
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        self.log_level = level
        
        # Update all existing loggers
        for logger in self.loggers.values():
            logger.setLevel(level)
            
        self.info(f"Log level changed to {logging.getLevelName(level)}", stream='app')


# Global unified logger instance with debug disabled by default (enabled via --debug flag)
unified_logger = UnifiedLogger(debug_enabled=False)
