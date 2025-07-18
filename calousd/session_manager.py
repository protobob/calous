"""Chat session management for Hi, Ollama!"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import os
import json
import socket
import signal
import sys
import time
import uuid
import threading
from datetime import datetime
from pathlib import Path

from .types import ActionType, CommandResult
from .utils import get_chat_color, print_rainbow_header, format_message_preview
from .config import ConfigManager
from .constants import SERVER_DEFAULT_NUM_CHATS, TWIST_PREVIEW_LENGTH, SWITCH_PREVIEW_LENGTH, SOCKET_PATH, MessageTypes
from .unified_logger import unified_logger

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from .app import Chat

class ChatSessionManager:
    def __init__(self, num_chats: Optional[int] = None, debug: bool = False):
        self.chats: List['Chat'] = []
        # Load saved active chat index from config
        self.active_chat_index: int = ConfigManager.get_active_chat_index()
        # Use constant for default
        self.num_chats = num_chats if num_chats is not None else SERVER_DEFAULT_NUM_CHATS
        
        # Connection tracking for daemon mode
        self.current_connection = None
        self.socket_mode = False
        self.debug = debug
        
        # Confirmation support for socket mode
        self.supports_confirmations = False
        self.pending_confirmation = None
        self.confirmation_event = None  # Threading event for confirmation coordination
        self.command_thread = None      # Thread for executing commands that need confirmations
        
        # Note: Client format preference removed - always send ANSI codes
        
        # Initialize plugin manager at session level
        self._initialize_plugin_manager()
        
        # Initialize chats with plugin manager
        self._initialize_chats()
        
        # Log session start
        model = ConfigManager.get_global_config().get("selected_model", "unknown")        
        unified_logger.log_session_start(self.num_chats, model)
    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client (daemon mode only)."""
        if self.socket_mode and self.current_connection:
            self.send_to_client(message, message_type)
        # In daemon mode, no fallback to print - output should only go through socket
          
    def _initialize_plugin_manager(self):
        """Initialize the plugin manager for all chat instances."""
        import os
        from pathlib import Path
        from .plugins.manager import PluginManager
        
        # Get the plugin directory path
        plugin_dir = Path(os.path.dirname(__file__)) / 'plugins'
        self.plugin_manager = PluginManager(debug=self.debug)
        
        # Set output callback so plugin manager can send messages to socket clients
        self.plugin_manager.set_output_callback(self.send_to_client)
        
        self.plugin_manager.discover_and_load_plugins(plugin_dir)
    
    def _initialize_chats(self):
        """Initialize all chat instances."""
        # Import here to avoid circular import
        from .app import Chat
        self.chats = [Chat(i) for i in range(self.num_chats)]  # Use parameter
        
        # Configure chat instances - REMOVED CIRCULAR REFERENCE
        for i, chat in enumerate(self.chats):
            chat.active_chat_index = i
            chat.session_manager = self  # Give chats reference to session manager only
            chat.plugin_manager = self.plugin_manager  # type: ignore # Inject shared plugin manager
    
    def get_active_chat(self) -> 'Chat':
        """Get the currently active chat instance."""
        return self.chats[self.active_chat_index]
    
    def get_all_chats(self) -> List['Chat']:
        """Get all chat instances - for use by other components."""
        return self.chats
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get current status information for REPL display."""
        active_chat = self.get_active_chat()
        return {
            "provider": getattr(active_chat, 'selected_provider', 'ollama'),
            "model": getattr(active_chat, 'selected_model', 'none'),
            "chat": self.active_chat_index + 1,  # 1-based for display
            "history": getattr(active_chat, 'history_enabled', True)
        }
    
    def _validate_chat_index(self, chat_index: int) -> bool:
        """Validate chat index is within bounds."""
        return 0 <= chat_index < self.num_chats
    
    def _create_error_response(self, message: str) -> Dict[str, str]:
        """Create standardized error response."""
        return {"error": message}
    
    def _create_success_response(self, message: str) -> Dict[str, str]:
        """Create standardized success response."""
        return {"response": message}
    
    def switch_to_chat(self, target_index: Optional[int] = None) -> bool:
        """Switch to specified chat or next chat if no index provided."""
        previous_chat_index = self.active_chat_index
        
        if target_index is None:
            # Default behavior: switch to next chat (cycling)
            target_index = (self.active_chat_index + 1) % self.num_chats
        
        if self._validate_chat_index(target_index):
            if target_index != previous_chat_index:
                # Log the channel switch
                unified_logger.log_channel_switch(previous_chat_index, target_index, "manual")
            self.active_chat_index = target_index
            # Save the new active chat index to config
            ConfigManager.set_active_chat_index(target_index)
            return True
        
        self.send_to_client(f"\n[1;31mError:[0m Invalid chat number. Available chats: 1-{self.num_chats}", "error")
        return False
    def twist_to_chat(self, content: str, target_index: Optional[int] = None) -> bool:
        """Twist content to specified chat or next chat if no index provided."""
        source_chat_index = self.active_chat_index
        
        if target_index is None:
            # Default behavior: twist to next chat
            target_index = (self.active_chat_index + 1) % self.num_chats

        if not self._validate_chat_index(target_index):
            self.send_to_client(f"\n[1;31mError:[0m Invalid chat number. Available chats: 1-{self.num_chats}", "error")
            return False

        # Log the twist action
        unified_logger.log_twist_action(source_chat_index, target_index, content)

        # Display twist preview from source chat
        source_color = get_chat_color(self.active_chat_index)
        target_color = get_chat_color(target_index)

        preview = format_message_preview(content, 50)
        
        # Temporarily disable buffering for twist output
        old_buffer = getattr(self, '_command_output_buffer', None)
        if hasattr(self, '_command_output_buffer'):
            delattr(self, '_command_output_buffer')
        
        self.send_to_client(f"\033[1m{source_color}↪ Twisting to Chat {target_index + 1}: "
              f"\033[0m\033[3m{target_color}\"{preview}\"\033[0m")

        # Switch to target chat FIRST
        self.active_chat_index = target_index
        # Save the new active chat index to config
        ConfigManager.set_active_chat_index(target_index)

        # Show FULL context for the target chat (including chat summary)
        target_chat = self.chats[target_index]
        
        # Use module-level imported get_chat_color
        target_chat_color = get_chat_color(target_index)
        target_chat.ui.display_chat_context(target_chat_color)

        # Display the twist content indicator with SOURCE CHAT COLOR
        # Truncate content and make it single line
        twist_preview = content.replace('\n', ' ').strip()
        if len(twist_preview) > TWIST_PREVIEW_LENGTH:
            twist_preview = twist_preview[:TWIST_PREVIEW_LENGTH] + "..."

        # Use SOURCE_COLOR instead of target_color for the TWIST CONTENT display
        self.send_to_client(f"\n\033[1m{source_color}|\033[0m \033[1m{source_color}TWIST CONTENT:\033[0m")
        self.send_to_client(f"\033[1m{source_color}|\033[0m [37m{twist_preview}[0m\n")


        # Restore buffering if it was enabled
        if old_buffer is not None:
            self._command_output_buffer = old_buffer

        # Ensure target chat has proper session manager reference for output routing
        target_chat.session_manager = self

        # Enable model streaming for the response
        self._model_streaming_active = True
        
        # Send the content as a prompt (which will trigger AI response)
        target_chat.handle_regular_input(content)

        return True    
        
    def update_global_model(self, new_model):
        """Update the selected model globally across all instances."""
        # Update global config
        ConfigManager.update_global_config({"selected_model": new_model})
        
        # Update all chat instances
        updated_count = 0
        for chat in self.chats:
            chat.selected_model = new_model
            updated_count += 1
        
        # Log the model change
        unified_logger.log_model_change(new_model, updated_count)
        
        return updated_count
    
    def update_global_num_ctx(self, new_num_ctx):
        """Update the context window globally across all instances."""
        # Update global config
        ConfigManager.set_global_num_ctx(new_num_ctx)
        # Update all chat instances
        updated_count = 0
        for chat in self.chats:
            chat.num_ctx = new_num_ctx
            updated_count += 1
        
        # Log the context window change
        unified_logger._write_log_entry("CONTEXT_CHANGE", f"Global context window changed to {new_num_ctx} tokens (affecting {updated_count} chats)")
        
        return updated_count
    
        

    def process_command_result(self, result: CommandResult) -> bool:
        """Process a command result and take appropriate action.
        
        Returns:
            True if the main loop should continue, False if it should exit
        """
        if result.action == ActionType.SWITCH:
            data = result.data or {}
            target_index = data.get('target_chat')
            if self.switch_to_chat(target_index):
                self._display_chat_context()
        
        elif result.action == ActionType.TWIST:
            data = result.data or {}
            content = data.get('content', '')
            target_index = data.get('target_chat')
            
            if content:
                self.twist_to_chat(content, target_index)
                # Remove the duplicate _display_chat_context() call here
                # twist_to_chat() already handles the display
        
    
        # CONTINUE action requires no special handling
        return True
    
    def _display_chat_context(self, clear_screen=True):
        """Display context for the active chat."""
        active_chat = self.get_active_chat()
        if clear_screen:
            active_chat.ui.clear_screen()
        
        # Use module-level imported get_chat_color
        chat_color = get_chat_color(self.active_chat_index)
        active_chat.ui.display_chat_context(chat_color)    
    
    def save_all_configs(self):
        """Save configurations for all chat instances."""
        # Only try to output if we have a client connection
        if self.socket_mode and self.current_connection:
            try:
                self._output("\n[1mExiting and saving configurations.[0m")
            except (BrokenPipeError, ConnectionError):
                pass  # Don't let output issues prevent saving
        
        # Log session end
        unified_logger.log_session_end()
        
        for chat in self.chats:
            try:
                chat.save_config()
            except Exception as e:
                self._output(f"\nError saving config: {e}")
    
    def run(self):
        """Run the main application loop."""
        # Display startup header
        self._display_startup_header()
        
        # Show initial context WITHOUT clearing the screen
        self._display_chat_context(clear_screen=False)
        
        try:
            while True:
                active_chat = self.get_active_chat()
                
                # Get user input
                user_input = active_chat.ui.get_user_input()
                
                # Process input and get result
                result = active_chat.process_input(user_input)
                
                # Handle the result
                if not self.process_command_result(result):
                    break  # Exit the application
                    
        except KeyboardInterrupt:
            self.save_all_configs()
            import os
            os._exit(0)
    
    def _display_startup_header(self):
        """Display the application startup header."""
        # Skip clear screen in daemon mode as it would affect stdout
        if not self.socket_mode:
            os.system('cls' if os.name == 'nt' else 'clear')
        print_rainbow_header(self._output)

    def send_to_client(self, message: str, message_type: str = "response", conn=None):
        """
        Send a message directly to the connected client.
        For command mode, buffer the output instead of sending immediately.
        """
        
        # Use provided connection or current connection
        target_conn = conn or self.current_connection
        if not target_conn:
            return  # No client connected
            
        # Always send ANSI codes directly - client handles color stripping if needed
        clean_message = message
        
        # If we're in command processing mode, buffer output EXCEPT confirmations and when model is streaming
        # Always allow confirmations and model streaming to pass through immediately
        if (hasattr(self, '_command_output_buffer') and 
            message_type not in ["confirmation_request", "end_response"] and
            not getattr(self, '_model_streaming_active', False)):
            self._command_output_buffer.append(clean_message)
            return
        
        # Otherwise send immediately (for prompts and confirmation requests)
        # Send raw content with delimiter protocol
        try:
            # Escape any \x00 bytes in the message to prevent delimiter collision
            escaped_message = clean_message.replace('\x00', '\x00\x00')
            
            if message_type == "error":
                # Send error with special delimiter
                target_conn.sendall(b'\x00ERROR\x00')
                target_conn.sendall(escaped_message.encode())
                target_conn.sendall(b'\x00END\x00')
            elif message_type == "end_response":
                # Send end-of-response delimiter for streaming
                # Test status generation with debug logging
                try:
                    import json
                    status_info = self.get_status_info()
                    unified_logger.debug_socket(f"Status info collected: {status_info}")
                    status_json = json.dumps(status_info)
                    unified_logger.debug_socket(f"Status JSON: {status_json}")
                    escaped_status = status_json.replace('\x00', '\x00\x00')
                    unified_logger.debug_socket(f"Escaped status: {escaped_status}")
                    target_conn.sendall(f'\x00STATUS\x00{escaped_status}\x00END\x00'.encode())
                    unified_logger.debug_socket("Status sent successfully")
                except Exception as e:
                    unified_logger.debug_socket(f"Error in status generation: {e}")
                    target_conn.sendall(b'\x00END\x00')
            else:
                # Send normal response content (no delimiter for streaming chunks)
                unified_logger.debug_socket(f"Sending chunk: {repr(escaped_message[:50])}")
                target_conn.sendall(escaped_message.encode())
        except BrokenPipeError:
            # Client disconnected
            self.current_connection = None
        except Exception as e:
            # Log error but don't crash
            pass
    
    def request_confirmation(self, message: str, default: str = "n") -> bool:
        """Request confirmation from socket client using threading to avoid deadlock."""
        
        if not self.current_connection or not self.supports_confirmations:
            # Fall back to auto-confirm with default
            return default == "y"
        
        # Generate unique ID for this confirmation
        confirmation_id = str(uuid.uuid4())
        
        # Create threading event for coordination
        self.confirmation_event = threading.Event()
        self.pending_confirmation = {
            "id": confirmation_id,
            "timestamp": time.time(),
            "response": None,
            "event": self.confirmation_event
        }
        
        # Send confirmation request DIRECTLY to client using delimiter protocol
        try:
            # Escape any \x00 bytes in the message
            escaped_message = message.replace('\x00', '\x00\x00')
            escaped_default = default.replace('\x00', '\x00\x00')
            
            # Send confirmation with special delimiter format: \x00CONFIRM\x00{message}\x00{default}\x00{id}\x00END\x00
            confirmation_message = f'\x00CONFIRM\x00{escaped_message}\x00{escaped_default}\x00{confirmation_id}\x00END\x00'
            self.current_connection.sendall(confirmation_message.encode())
            
            # Wait for the threading event to be set (when response is received)
            if self.confirmation_event.wait(timeout=30.0):
                # Response received
                response_value = self.pending_confirmation.get('response', default)
                self.pending_confirmation = None
                self.confirmation_event = None
                return response_value.lower() == "y"
            else:
                # Timeout
                self.pending_confirmation = None
                self.confirmation_event = None
                return default == "y"
            
        except Exception:
            # If anything goes wrong, fall back to default
            self.pending_confirmation = None
            self.confirmation_event = None
            return default == "y"
    
    def listen_for_socket(self, debug=False):
        """Listen for socket connections and handle multi-chat commands."""
        
        # Set daemon mode
        self.socket_mode = True
        
        # Remove existing socket file if it exists
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        
        # Create Unix socket
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(1)

        def handle_exit(signum, frame):
            try:
                # Save configs without client output to avoid issues
                unified_logger.log_session_end()
                for chat in self.chats:
                    try:
                        chat.save_config()
                    except Exception as e:
                        # Log error but continue saving other configs
                        unified_logger._write_log_entry("ERROR", f"Failed to save config for chat {chat.instance_index}: {e}")
            except Exception as e:
                # Log critical error but still try to clean up
                unified_logger._write_log_entry("CRITICAL", f"Failed to save configs during shutdown: {e}")
            finally:
                # Always clean up socket
                try:
                    server.close()
                except (OSError, AttributeError):
                    pass
                # Remove socket file
                try:
                    if os.path.exists(SOCKET_PATH):
                        os.remove(SOCKET_PATH)
                except (OSError, FileNotFoundError):
                    pass
                exit(0)

        signal.signal(signal.SIGINT, handle_exit)
            
        while True:
            conn, addr = server.accept()
            # Track current connection
            self.current_connection = conn
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Handle multiple messages on the same connection
            try:
                while True:
                    # Read all data from the connection until we find the end delimiter
                    data = b""
                    while True:
                        chunk = conn.recv(8192)
                        if not chunk:
                            break
                        data += chunk
                        
                        # Check if we have a complete message ending with \x00END\x00
                        if b'\x00END\x00' in data:
                            break
                            
                        # If the connection is closed and we have partial data, break
                        if len(chunk) == 0:
                            break
                    
                    if not data:
                        break  # Connection closed
                        
                    decoded_data = data.decode('utf-8')
                    if debug:
                        unified_logger.debug_socket(f"Raw data received: {decoded_data[:200]}{'...' if len(decoded_data) > 200 else ''} at {timestamp}")
                        unified_logger.debug_socket(f"Total data size: {len(data)} bytes")
                    
                    # Parse delimiter-based message format
                    # Expected formats:
                    # PROMPT\x00{content}\x00END\x00
                    # CMD\x00{content}\x00END\x00  
                    # CONFIRM_RESPONSE\x00{id}\x00{response}\x00END\x00
                    
                    # Remove the trailing \x00END\x00  
                    if decoded_data.endswith('\x00END\x00'):
                        message_content = decoded_data[:-5]  # Remove \0END\0 (5 bytes)
                    else:
                        message_content = decoded_data
                    
                    # Split by \x00 and unescape
                    parts = message_content.split('\x00')
                    if len(parts) < 2:
                        raise ValueError("Invalid message format")
                    
                    # Check for confirmation response first (starts with empty + CONFIRM_RESPONSE)
                    if len(parts) >= 4 and parts[0] == "" and parts[1] == "CONFIRM_RESPONSE":
                        # Handle confirmation response - signal the waiting thread
                        # Format: \0CONFIRM_RESPONSE\0{id}\0{response}\0END\0
                        confirmation_id = parts[2]  # parts[1] is "CONFIRM_RESPONSE", parts[2] is id
                        confirmation_response = parts[3]  # parts[3] is the actual response
                        
                        if debug:
                            unified_logger.debug_socket(f"Received confirmation response: id={confirmation_id}, response={confirmation_response}")
                        
                        # Signal the waiting thread with the response
                        if (hasattr(self, 'pending_confirmation') and 
                            self.pending_confirmation and 
                            self.pending_confirmation.get('id') == confirmation_id):
                            
                            self.pending_confirmation['response'] = confirmation_response
                            if self.confirmation_event:
                                self.confirmation_event.set()
                            if debug:
                                unified_logger.debug_socket(f"Signaled confirmation thread with response")
                        
                        # Continue reading more data from the same connection
                        # The command thread will send the final response
                        continue
                    
                    # Regular message parsing
                    msg_type = parts[0]
                    content = parts[1].replace('\x00\x00', '\x00')  # Unescape null bytes
                    target_chat = None  # For now, no chat targeting in delimiter protocol
                    
                    
                    
                    if msg_type == "PROMPT":
                        msg_type = "prompt"  # Convert to old format for compatibility
                    elif msg_type == "CMD":
                        msg_type = "cmd"     # Convert to old format for compatibility
                    else:
                        # Default to prompt for backwards compatibility
                        msg_type = "prompt"
                        content = message_content.replace('\x00\x00', '\x00')
                    
                    # Always assume client supports confirmations in new protocol
                    self.supports_confirmations = True
                    
                    if debug:
                        unified_logger.debug_socket(f"Parsed request: type={msg_type}, data length={len(content)} chars, target_chat={target_chat} at {timestamp}")
                    
                    # Handle chat targeting
                    original_active_chat = self.active_chat_index
                    if target_chat is not None:
                        # Convert to 0-based index and validate
                        target_index = target_chat - 1
                        if self._validate_chat_index(target_index):
                            self.active_chat_index = target_index
                            if debug:
                                unified_logger.debug_socket(f"Switched to chat {target_chat} for this command", connection_id=str(id(conn)))
                        else:
                            response = {"error": f"Invalid chat number: {target_chat}. Available chats: 1-{self.num_chats}"}
                            conn.sendall(json.dumps(response).encode())
                            conn.close()
                            continue
                    
                    # Get the targeted chat for processing
                    active_chat = self.get_active_chat()
                    
                    # Initialize response
                    response: Optional[Dict[str, Any]] = {"error": "Unknown error"}
                    
                    if msg_type == "confirmation_response":
                        # Handle confirmation response - this will be processed by _wait_for_confirmation_response
                        # Just acknowledge receipt and let the waiting method handle it
                        response = {"response": "confirmation received"}
                        
                    elif msg_type == "prompt":
                        # Handle prompt message - model will send output via send_to_client
                        active_chat.chat_history.add_message("user", content)
                        if debug:
                            unified_logger.debug("About to call talk_to_model", stream='model', chat_channel=active_chat.instance_index)
                        
                        # Set flag to prevent buffering of model streaming responses
                        self._model_streaming_active = True
                        try:
                            model_response = active_chat.model.talk_to_model(content, stream=True)
                        finally:
                            # Always clear the flag when done
                            self._model_streaming_active = False
                            
                        if debug:
                            unified_logger.debug(f"Model response received: {model_response}", stream='model', chat_channel=active_chat.instance_index)
                        # Model response already streamed to client, no need to send again
                        response = None  # No additional response needed
                        
                    elif msg_type == "cmd":
                        try:
                            # In delimiter protocol, content is the raw command
                            action = content.strip()
                            if action:
                                # Check if this command might need confirmation
                                # Commands that typically need confirmation: history.clear, context.load, etc.
                                needs_confirmation = any(cmd in action.lower() for cmd in [
                                    'history.clear', 'history.delete', 'history.save', 'history.load', 'history.purge',
                                    'context.save', 'context.load', 'context.delete',
                                    'chat.reset', 'config.reset', 'plugin.reload', 'file.delete'
                                ])
                                
                                if needs_confirmation:
                                    # Execute command in a separate thread to avoid blocking socket handler
                                    if debug:
                                        unified_logger.debug_socket(f"Starting threaded execution for command: {action}")
                                    
                                    self.command_thread = threading.Thread(
                                        target=self._execute_command_in_thread,
                                        args=(action, active_chat, conn, debug),
                                        daemon=True
                                    )
                                    self.command_thread.start()
                                    response = None  # Thread will send the response
                                    
                                    # Don't close connection yet - continue to handle confirmation responses
                                    continue
                                else:
                                    # Execute command normally (no confirmation needed)
                                    try:
                                        # Set up output buffering for command
                                        self._command_output_buffer = []
                                        
                                        # Inject session manager into formatter before command execution
                                        from .commands.formatters import CommandFormatter
                                        CommandFormatter._session_manager = self
                                        
                                        # Process command using active chat
                                        if debug:
                                            unified_logger.debug_command(f"Processing command: {action}", chat_channel=active_chat.instance_index)
                                        
                                        try:
                                            cmd_result = active_chat.process_input(f"{action}")
                                            if debug:
                                                unified_logger.debug_command(f"Command result: {cmd_result}", chat_channel=active_chat.instance_index)
                                        except Exception as e:
                                            if debug:
                                                unified_logger.error(f"Error in process_input: {e}", component='command_processing', chat_channel=active_chat.instance_index)
                                            raise
                                        
                                        # Process the command result through session manager
                                        try:
                                            self.process_command_result(cmd_result)
                                            if debug:
                                                unified_logger.debug_command("Command result processed successfully", chat_channel=active_chat.instance_index)
                                        except Exception as e:
                                            if debug:
                                                unified_logger.error(f"Error in process_command_result: {e}", component='session_management')
                                            raise
                                        
                                        # Send buffered output using delimiter protocol
                                        if self._command_output_buffer:
                                            combined_output = "\n".join(self._command_output_buffer)
                                            # Ensure output ends with newline for proper terminal formatting
                                            if combined_output and not combined_output.endswith('\n'):
                                                combined_output += '\n'
                                            if debug:
                                                unified_logger.debug_socket(f"Sending buffered output: {len(self._command_output_buffer)} lines")
                                            
                                            # Escape any \x00 bytes and send with delimiter
                                            escaped_output = combined_output.replace('\x00', '\x00\x00')
                                            conn.sendall(escaped_output.encode())
                                            conn.sendall(b'\x00END\x00')
                                        else:
                                            # No output to send, just send the end delimiter
                                            if debug:
                                                unified_logger.debug_socket("No buffered output, sending end delimiter only")
                                            conn.sendall(b'\x00END\x00')
                                        response = None  # Prevent the main handler from sending another response
                                        
                                        # Clean up buffer
                                        delattr(self, '_command_output_buffer')
                                        
                                    except Exception as e:
                                        if debug:
                                            unified_logger.error(f"Exception in command processing: {e}", component='command_execution')
                                        # Make sure to clean up buffer even on error
                                        if hasattr(self, '_command_output_buffer'):
                                            delattr(self, '_command_output_buffer')
                                        # Send error with delimiter protocol  
                                        error_msg = f"Command processing failed: {str(e)}"
                                        escaped_error = error_msg.replace('\x00', '\x00\x00')
                                        conn.sendall(b'\x00ERROR\x00')
                                        conn.sendall(escaped_error.encode())
                                        conn.sendall(b'\x00END\x00')
                                        response = None
                            else:
                                # Send error with delimiter protocol
                                error_msg = "Missing action in command."
                                escaped_error = error_msg.replace('\x00', '\x00\x00')
                                conn.sendall(b'\x00ERROR\x00')
                                conn.sendall(escaped_error.encode()) 
                                conn.sendall(b'\x00END\x00')
                                response = None
                        except ValueError as e:
                            # Send error with delimiter protocol
                            error_msg = f"Invalid command format: {str(e)}"
                            escaped_error = error_msg.replace('\x00', '\x00\x00')
                            conn.sendall(b'\x00ERROR\x00')
                            conn.sendall(escaped_error.encode())
                            conn.sendall(b'\x00END\x00')
                            response = None
                    else:
                        # Send error with delimiter protocol
                        error_msg = "Unknown message type."
                        escaped_error = error_msg.replace('\x00', '\x00\x00')
                        conn.sendall(b'\x00ERROR\x00')
                        conn.sendall(escaped_error.encode())
                        conn.sendall(b'\x00END\x00')
                        response = None
                            
                    # Restore original active chat if we switched for targeting
                    if target_chat is not None and original_active_chat != self.active_chat_index:
                        self.active_chat_index = original_active_chat
                        if debug:
                            unified_logger.debug_socket(f"Restored active chat to {original_active_chat + 1}")
                        
            except UnicodeDecodeError as e:
                if debug:
                    unified_logger.error(f"Unicode decode error: {e}", component='socket_parsing')
                    unified_logger.debug_socket(f"Raw bytes: {data[:100]}...")
                # Send error with delimiter protocol
                try:
                    error_msg = f"Invalid UTF-8 in request: {str(e)}"
                    escaped_error = error_msg.replace('\x00', '\x00\x00')
                    conn.sendall(b'\x00ERROR\x00')
                    conn.sendall(escaped_error.encode())
                    conn.sendall(b'\x00END\x00')
                except:
                    pass
            except Exception as e:
                if debug:
                    unified_logger.error(f"Unexpected error: {e}", component='socket_handler')
                # Send error with delimiter protocol
                try:
                    error_msg = f"Server error: {str(e)}"
                    escaped_error = error_msg.replace('\x00', '\x00\x00')
                    conn.sendall(b'\x00ERROR\x00')
                    conn.sendall(escaped_error.encode())
                    conn.sendall(b'\x00END\x00')
                except:
                    pass
            
            # Wait for any running command thread to complete before closing connection
            if self.command_thread and self.command_thread.is_alive():
                if debug:
                    unified_logger.debug_socket("Waiting for command thread to complete")
                self.command_thread.join(timeout=5.0)  # Wait up to 5 seconds
                if self.command_thread.is_alive():
                    if debug:
                        unified_logger.debug_socket("Command thread still running after timeout")
            
            # Clean up connection
            conn.close()
            self.current_connection = None
    
    def _execute_command_in_thread(self, action: str, active_chat, conn, debug: bool = False):
        """Execute a command in a separate thread to allow confirmation handling."""
        try:
            # Set up output buffering for command
            self._command_output_buffer = []
            
            # Inject session manager into formatter before command execution
            from .commands.formatters import CommandFormatter
            CommandFormatter._session_manager = self
            
            # Process command using active chat
            if debug:
                unified_logger.debug_command(f"Processing command in thread: {action}", chat_channel=active_chat.instance_index)
            
            try:
                cmd_result = active_chat.process_input(f"{action}")
                if debug:
                    unified_logger.debug_command(f"Command result: {cmd_result}", chat_channel=active_chat.instance_index)
            except Exception as e:
                if debug:
                    unified_logger.error(f"Error in process_input: {e}", component='command_processing', chat_channel=active_chat.instance_index)
                raise
            
            # Process the command result through session manager
            try:
                self.process_command_result(cmd_result)
                if debug:
                    unified_logger.debug_command("Command result processed successfully", chat_channel=active_chat.instance_index)
            except Exception as e:
                if debug:
                    unified_logger.error(f"Error in process_command_result: {e}", component='session_management')
                raise
            
            # Send buffered output using delimiter protocol
            if self._command_output_buffer:
                combined_output = "\n".join(self._command_output_buffer)
                # Ensure output ends with newline for proper terminal formatting
                if combined_output and not combined_output.endswith('\n'):
                    combined_output += '\n'
                if debug:
                    unified_logger.debug_socket(f"Sending buffered output from thread: {len(self._command_output_buffer)} lines")
                
                # Escape any \x00 bytes and send with delimiter
                escaped_output = combined_output.replace('\x00', '\x00\x00')
                conn.sendall(escaped_output.encode())
                conn.sendall(b'\x00END\x00')
            else:
                # No output to send, just send the end delimiter
                if debug:
                    unified_logger.debug_socket("No buffered output from thread, sending end delimiter only")
                conn.sendall(b'\x00END\x00')
            
            # Clean up buffer
            if hasattr(self, '_command_output_buffer'):
                delattr(self, '_command_output_buffer')
                
        except Exception as e:
            if debug:
                unified_logger.error(f"Exception in threaded command processing: {e}", component='command_execution')
            # Make sure to clean up buffer even on error
            if hasattr(self, '_command_output_buffer'):
                delattr(self, '_command_output_buffer')
            # Send error with delimiter protocol  
            try:
                error_msg = f"Command processing failed: {str(e)}"
                escaped_error = error_msg.replace('\x00', '\x00\x00')
                conn.sendall(b'\x00ERROR\x00')
                conn.sendall(escaped_error.encode())
                conn.sendall(b'\x00END\x00')
            except:
                pass
        finally:
            # Reset command thread reference
            self.command_thread = None