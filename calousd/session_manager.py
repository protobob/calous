"""Chat session management for Hi, Ollama!"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import os
from .types import ActionType, CommandResult  # Import from types instead
from .utils import get_chat_color, print_rainbow_header, format_message_preview
from .config import ConfigManager
from .constants import DEFAULT_NUM_CHATS, TWIST_PREVIEW_LENGTH, SWITCH_PREVIEW_LENGTH, SOCKET_PATH
from .unified_logger import unified_logger

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from .app import Chat

class ChatSessionManager:    
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            print(message)
    
    def __init__(self, num_chats: Optional[int] = None, debug: bool = False):  # Remove hardcoded default
        self.chats: List['Chat'] = []
        self.active_chat_index: int = 0
        # Use constant for default
        self.num_chats = num_chats if num_chats is not None else DEFAULT_NUM_CHATS
        
        # Connection tracking for daemon mode
        self.current_connection = None
        self.socket_mode = False
        self.debug = debug
        
        # Initialize plugin manager at session level
        self._initialize_plugin_manager()
        
        # Initialize chats with plugin manager
        self._initialize_chats()
        
        # Log session start
        model = ConfigManager.get_global_config().get("selected_model", "unknown")        
        unified_logger.log_session_start(self.num_chats, model)
          
    def _initialize_plugin_manager(self):
        """Initialize the plugin manager for all chat instances."""
        import os
        from pathlib import Path
        from .plugins.manager import PluginManager
        
        # Get the plugin directory path
        plugin_dir = Path(os.path.dirname(__file__)) / 'plugins'
        self.plugin_manager = PluginManager(debug=self.debug)
        self.plugin_manager.discover_and_load_plugins(plugin_dir)
    
    def _initialize_chats(self):
        """Initialize all chat instances."""        # Import here to avoid circular import
        from .app import Chat
        self.chats = [Chat(i) for i in range(self.num_chats)]  # Use parameter
        
        # Configure chat instances - REMOVED CIRCULAR REFERENCE
        for i, chat in enumerate(self.chats):
            chat.active_chat_index = i
            chat.session_manager = self  # Give chats reference to session manager only
            chat.plugin_manager = self.plugin_manager  # Inject shared plugin manager
    
    def get_active_chat(self) -> 'Chat':
        """Get the currently active chat instance."""
        return self.chats[self.active_chat_index]
    
    def get_all_chats(self) -> List['Chat']:
        """Get all chat instances - for use by other components."""
        return self.chats
    def switch_to_chat(self, target_index: Optional[int] = None) -> bool:
        """Switch to specified chat or next chat if no index provided."""
        previous_chat_index = self.active_chat_index
        
        if target_index is None:
            # Default behavior: switch to next chat (cycling)
            target_index = (self.active_chat_index + 1) % self.num_chats
        
        if 0 <= target_index < self.num_chats:
            if target_index != previous_chat_index:
                # Log the channel switch
                unified_logger.log_channel_switch(previous_chat_index, target_index, "manual")
            self.active_chat_index = target_index
            return True
        
        self.send_to_client(f"\n[bold red]Error:[/bold red] Invalid chat number. Available chats: 1-{self.num_chats}", "error")
        return False
    def twist_to_chat(self, content: str, target_index: Optional[int] = None) -> bool:
        """Twist content to specified chat or next chat if no index provided."""
        source_chat_index = self.active_chat_index
        
        if target_index is None:
            # Default behavior: twist to next chat
            target_index = (self.active_chat_index + 1) % self.num_chats

        if not (0 <= target_index < self.num_chats):
            self.send_to_client(f"\n[bold red]Error:[/bold red] Invalid chat number. Available chats: 1-{self.num_chats}", "error")
            return False

        # Log the twist action
        unified_logger.log_twist_action(source_chat_index, target_index, content)

        # Display twist preview from source chat
        source_color = get_chat_color(self.active_chat_index)
        target_color = get_chat_color(target_index)

        preview = format_message_preview(content, 50)
        self.send_to_client(f"[bold {source_color}]↪ Twisting to Chat {target_index + 1}: "
              f"[/bold {source_color}][italic {target_color}]\"{preview}\"[/italic {target_color}]")

        # Switch to target chat FIRST
        self.active_chat_index = target_index

        # Clear screen and show FULL context for the target chat (including chat summary)
        target_chat = self.chats[target_index]
        target_chat.ui.clear_screen()
        
        # Use module-level imported get_chat_color
        target_chat_color = get_chat_color(target_index)
        target_chat.ui.display_chat_context(target_chat_color)

        # Display the twist content indicator with SOURCE CHAT COLOR
        # Truncate content and make it single line
        twist_preview = content.replace('\n', ' ').strip()
        if len(twist_preview) > TWIST_PREVIEW_LENGTH:
            twist_preview = twist_preview[:TWIST_PREVIEW_LENGTH] + "..."

        # Use SOURCE_COLOR instead of target_color for the TWIST CONTENT display
        self.send_to_client(f"\n[bold {source_color}]|[/bold {source_color}] [bold {source_color}]TWIST CONTENT:[/bold {source_color}]")
        self.send_to_client(f"[bold {source_color}]|[/bold {source_color}] [grey70]{twist_preview}[/grey70]\n")

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
    
    def add_chat(self) -> bool:
        """Add a new chat session dynamically."""        
        from .app import Chat
          # Create new chat instance
        new_chat_index = self.num_chats
        new_chat = Chat(new_chat_index)
        new_chat.session_manager = self
        
        # Inject shared plugin manager
        new_chat.plugin_manager = self.plugin_manager
        
        # Ensure new chat has global context window setting
        new_chat.num_ctx = ConfigManager.get_global_num_ctx()
        
        # Add to chats list
        self.chats.append(new_chat)
        
        # Update num_chats
        self.num_chats += 1
        
        # Update global config
        ConfigManager.update_global_config({"num_chats": self.num_chats})
        
        # Log the addition
        unified_logger.log_channel_switch(-1, new_chat_index, "addchat")
        
        self.send_to_client(f"[bold green]✓[/bold green] Chat {new_chat_index + 1} added successfully!")
        return True
        
    def remove_chat(self, target_index: int) -> bool:
        """Remove a chat session dynamically."""
        if target_index < 0 or target_index >= self.num_chats:
            return False
        
        # Save the chat's configuration before removing it
        chat_to_remove = self.chats[target_index]
        try:
            chat_to_remove.save_config()
            self._output(f"[grey70]Saved configuration for Chat {target_index + 1}[/grey70]")
        except Exception as e:
            self._output(f"[bold yellow]Warning:[/bold yellow] Could not save config for Chat {target_index + 1}: {e}")
        
        # Remove the chat from the list
        removed_chat = self.chats.pop(target_index)
        
        # Update num_chats
        self.num_chats -= 1
        
        # Update global config (preserves chat configs in unified file)
        ConfigManager.update_global_config({"num_chats": self.num_chats})
        
        # Adjust active_chat_index if necessary
        if self.active_chat_index >= self.num_chats:
            # If we removed the last chat and it was active, switch to the new last chat
            self.active_chat_index = self.num_chats - 1
        elif self.active_chat_index > target_index:
            # If we removed a chat before the active one, adjust the index
            self.active_chat_index -= 1
        
        # Update instance indices for remaining chats
        for i, chat in enumerate(self.chats):
            chat.instance_index = i
            chat.active_chat_index = i
        
        # Log the removal
        unified_logger.log_channel_switch(target_index, -1, "removechat")
        
        self.send_to_client(f"[bold green]✓[/bold green] Chat {target_index + 1} removed successfully!")
        self.send_to_client(f"[grey70]Configuration preserved in unified config file.[/grey70]")
        return True

    def process_command_result(self, result: CommandResult) -> bool:
        """Process a command result and take appropriate action.
        
        Returns:
            True if the main loop should continue, False if it should exit
        """
        if result.action == ActionType.QUIT:
            self.save_all_configs()
            return False
        
        elif result.action == ActionType.SWITCH:
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
        
        elif result.action == ActionType.ADDCHAT:
            if self.add_chat():
                # Switch to the new chat and display its context
                self.active_chat_index = self.num_chats - 1
                self._display_chat_context()
        
        elif result.action == ActionType.REMOVECHAT:
            data = result.data or {}
            target_index = data.get('target_index', self.num_chats - 1)
            if self.remove_chat(target_index):
                # Display context for the current active chat
                self._display_chat_context()
    
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
        self._output("\n[bold]Exiting and saving configurations.[/bold]")
        
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
        os.system('cls' if os.name == 'nt' else 'clear')
        from .utils import print_rainbow_header
        print_rainbow_header()

    def send_to_client(self, message: str, message_type: str = "response", conn=None):
        """
        Send a message directly to the connected client.
        For command mode, buffer the output instead of sending immediately.
        """
        import json
        import re
        
        # Use provided connection or current connection
        target_conn = conn or self.current_connection
        if not target_conn:
            return  # No client connected
            
        # Strip Rich markup for plain text output
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        rich_markup = re.compile(r'\[/?[^\]]*\]')
        
        # Remove ANSI codes and Rich markup
        clean_message = ansi_escape.sub('', message)
        clean_message = rich_markup.sub('', clean_message)
        
        # If we're in command processing mode, buffer the output
        if hasattr(self, '_command_output_buffer'):
            self._command_output_buffer.append(clean_message)
            return
        
        # Otherwise send immediately (for prompts)
        # Create response structure
        if message_type == "error":
            response = {"error": clean_message.strip()}
        else:
            response = {"response": clean_message.strip()}
        
        try:
            target_conn.sendall(json.dumps(response).encode())
        except BrokenPipeError:
            # Client disconnected
            self.current_connection = None
        except Exception as e:
            # Log error but don't crash
            pass
                
    def listen_for_socket(self, debug=False):
        """Listen for socket connections and handle multi-chat commands."""
        import socket
        import json
        import signal
        import sys
        import os
        from datetime import datetime
        
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
            self.save_all_configs()
            server.close()
            exit(0)

        signal.signal(signal.SIGINT, handle_exit)
            
        while True:
            conn, addr = server.accept()
            # Track current connection
            self.current_connection = conn
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Read all data from the connection
            data = b""
            while True:
                chunk = conn.recv(8192)
                if not chunk:
                    break
                data += chunk
                
                # Try to decode and parse JSON to see if we have a complete message
                try:
                    decoded_data = data.decode('utf-8')
                    json.loads(decoded_data)
                    # If we get here, we have valid complete JSON
                    break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If the connection is closed and we have partial data, break
                    if len(chunk) == 0:
                        break
                    # Otherwise continue reading
                    continue
            
            if not data:
                conn.close()
                self.current_connection = None
                continue
                
            try:
                decoded_data = data.decode('utf-8')
                if debug:
                    self._output(f"[Debug] Raw data received: {decoded_data[:200]}{'...' if len(decoded_data) > 200 else ''} at {timestamp}")
                    self._output(f"[Debug] Total data size: {len(data)} bytes")
                
                req = json.loads(decoded_data)
                msg_type = req.get("type")
                content = req.get("data", "")
                target_chat = req.get("chat")  # Optional chat channel targeting
                output_format = req.get("format", "plain")  # Default to plain for backward compatibility
                
                if debug:
                    self._output(f"[Debug] Parsed request: type={msg_type}, data length={len(content)} chars, target_chat={target_chat}, format={output_format} at {timestamp}")
                
                # Handle chat targeting
                original_active_chat = self.active_chat_index
                if target_chat is not None:
                    # Convert to 0-based index and validate
                    target_index = target_chat - 1
                    if 0 <= target_index < self.num_chats:
                        self.active_chat_index = target_index
                        if debug:
                            self._output(f"[Debug] Switched to chat {target_chat} for this command")
                    else:
                        response = {"error": f"Invalid chat number: {target_chat}. Available chats: 1-{self.num_chats}"}
                        conn.sendall(json.dumps(response).encode())
                        conn.close()
                        continue
                
                # Get the targeted chat for processing
                active_chat = self.get_active_chat()
                
                # Initialize response
                response: Dict[str, Any] = {"error": "Unknown error"}
                
                if msg_type == "prompt":
                    # Handle prompt message - model will send output via send_to_client
                    active_chat.chat_history.add_message("user", content)
                    if debug:
                        self._output(f"[Debug] About to call talk_to_model")
                    model_response = active_chat.model.talk_to_model(content, stream=False)
                    if debug:
                        self._output(f"[Debug] Model response received: {model_response}")
                    # Send JSON response with the content for compatibility
                    response_text = model_response.get("message", {}).get("content", "") if model_response else ""
                    response = {"response": response_text}
                    if debug:
                        self._output(f"[Debug] Sending JSON response: {response}")
                    
                elif msg_type == "cmd":
                    try:
                        action = json.loads(content).get("action")
                        if action:
                            # Set non-interactive mode for socket commands
                            active_chat.non_interactive = True
                            
                            try:
                                # Set up output buffering for command
                                self._command_output_buffer = []
                                
                                # Inject session manager into formatter before command execution
                                from .commands.formatters import CommandFormatter
                                CommandFormatter._session_manager = self
                                
                                # Process command using active chat
                                if debug:
                                    self._output(f"[Debug] Processing command: {action}")
                                cmd_result = active_chat.process_input(f"{action}")
                                if debug:
                                    self._output(f"[Debug] Command result: {cmd_result}")
                                
                                # Process the command result through session manager
                                # This enables chat switching and other session-level operations
                                self.process_command_result(cmd_result)
                                
                                # Send buffered output as single JSON response
                                if self._command_output_buffer:
                                    combined_output = "\n".join(self._command_output_buffer)
                                    response = {"response": combined_output}
                                else:
                                    response = {"response": "Command completed"}
                                    
                                # Send the buffered response immediately instead of letting the main handler do it
                                import json
                                conn.sendall(json.dumps(response).encode())
                                response = None  # Prevent the main handler from sending another response
                                
                                # Clean up buffer
                                delattr(self, '_command_output_buffer')
                                    
                            finally:
                                # Reset non-interactive mode
                                active_chat.non_interactive = False
                        else:
                            response = {"error": "Missing action in command."}
                    except json.JSONDecodeError:
                        response = {"error": "Invalid JSON in 'data' field for command."}
                else:
                    response = {"error": "Unknown message type."}
                        
                # Restore original active chat if we switched for targeting
                if target_chat is not None and original_active_chat != self.active_chat_index:
                    self.active_chat_index = original_active_chat
                    if debug:
                        self._output(f"[Debug] Restored active chat to {original_active_chat + 1}")
                    
            except json.JSONDecodeError as e:
                if debug:
                    try:
                        decoded_data = data.decode('utf-8', errors='replace')
                        self._output(f"[Debug] JSON decode error: {e}")
                        self._output(f"[Debug] Problematic data: {decoded_data[:500]}...")
                    except:
                        self._output(f"[Debug] JSON decode error: {e}")
                        self._output(f"[Debug] Raw bytes: {data[:100]}...")
                response = {"error": f"Invalid JSON in request: {str(e)}"}
            except UnicodeDecodeError as e:
                if debug:
                    self._output(f"[Debug] Unicode decode error: {e}")
                    self._output(f"[Debug] Raw bytes: {data[:100]}...")
                response = {"error": f"Invalid UTF-8 in request: {str(e)}"}
            except Exception as e:
                if debug:
                    self._output(f"[Debug] Unexpected error: {e}")
                response = {"error": f"Server error: {str(e)}"}
                
            # Send response back to client (for errors and acknowledgments)
            if response is not None:
                try:
                    conn.sendall(json.dumps(response).encode())
                except BrokenPipeError:
                    # Client closed connection before response was sent
                    pass
                except Exception:
                    # Log error but don't crash
                    pass
            
            # Clean up connection
            conn.close()
            self.current_connection = None