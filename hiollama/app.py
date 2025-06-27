"""Main application class for Hi, Ollama!"""
from rich.prompt import Prompt
from rich import print

import socket
import sys
import os
import json
import signal
from datetime import datetime

from .config import ConfigManager
from .commands.handler import AdvancedCommandHandler  # Fixed import path
from .ui import UIManager
from .chat_history import ChatHistory
from .model_interaction import ModelInteraction
from .persona import Persona
from .constants import DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, MAX_PROMPTS, DEFAULT_NUM_CTX, DEFAULT_TEMPERATURE
from .types import CommandResult, ActionType
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_manager import ChatSessionManager

SOCKET_PATH = "/tmp/hiollama.sock"

class Chat:

    def __init__(self, instance_index):
        self.instance_index = instance_index
        # Load configs from unified system
        self.config = ConfigManager.get_chat_config(instance_index)
        global_config = ConfigManager.get_global_config()
        self.selected_model = global_config.get("selected_model", DEFAULT_MODEL)
        self.verbosity = self.config.get("verbosity", True)

        # Initialize persona system
        self.persona = Persona()
        persona_data = self.config.get("persona", {})
        if persona_data:
            self.persona.load_from_data(persona_data)
        else:
            old_system_prompt = self.config.get("system_prompt", "")
            if old_system_prompt and old_system_prompt != DEFAULT_SYSTEM_PROMPT:
                self.persona.set_slot(0, old_system_prompt)

        self.system_prompt = {
            "role": "system",
            "content": self.persona.get_combined_prompt()
        }
        self.logging_enabled = self.config.get("logging_enabled", True)
        self.thinking_enabled = self.config.get("thinking_enabled", False)
        self.history_enabled = self.config.get("history_enabled", True)
        self.num_ctx = ConfigManager.get_global_num_ctx()
        self.temperature = self.config.get("temperature", DEFAULT_TEMPERATURE)
        self.prompts = self.config.get("prompts", {f"prompt{i}": "" for i in range(1, MAX_PROMPTS + 1)})
        self.active_chat_index = instance_index
        self.session_manager = None
        self.plugin_manager = None
        self.non_interactive = False  # Add this line for auto-confirm mode

        self.ui = UIManager(self)
        self.chat_history = ChatHistory(self, instance_index)
        self.model = ModelInteraction(self)
        self.commands = AdvancedCommandHandler(self)
        self.last_response = None

    def update_global_model(self, new_model):
        if self.session_manager:
            return self.session_manager.update_global_model(new_model)
        else:
            ConfigManager.update_global_config({"selected_model": new_model})
            self.selected_model = new_model
            return 1

    def update_global_num_ctx(self, new_num_ctx):
        if self.session_manager:
            return self.session_manager.update_global_num_ctx(new_num_ctx)
        else:
            ConfigManager.set_global_num_ctx(new_num_ctx)
            self.num_ctx = new_num_ctx
            return 1

    def save_config(self):
        self.system_prompt["content"] = self.persona.get_combined_prompt()
        chat_config = {
            "verbosity": self.verbosity,
            "persona": self.persona.to_dict(),
            "logging_enabled": self.logging_enabled,
            "thinking_enabled": self.thinking_enabled,
            "history_enabled": self.history_enabled,
            "temperature": self.temperature,
            "prompts": self.prompts
        }
        ConfigManager.update_chat_config(self.instance_index, chat_config)
        ConfigManager.update_global_config({"selected_model": self.selected_model})

    def process_input(self, user_input: str):
        if user_input.startswith('/'):
            return self.commands.parse_and_execute(user_input)
        if self.plugin_manager:
            processed_input = self.plugin_manager.apply_pre_message_hooks(user_input, context={})
        else:
            processed_input = user_input
        if processed_input != user_input and processed_input.startswith("[shell:"):
            self.ui.display_shell_output(processed_input)
            return CommandResult(ActionType.CONTINUE)
        # Avoid calling handle_regular_input for commands
        return CommandResult(ActionType.CONTINUE)

    def handle_regular_input(self, user_input, images=None):
        self.chat_history.add_message("user", user_input)
        try:
            response = self.model.talk_to_model(user_input, images=images)
        except Exception as e:
            print(f"[bold red]Error processing input:[/bold red] {e}")

    def listen_for_socket(self, interactive=False):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(1)

        def handle_exit(signum, frame):
            print("[hiollama] Shutting down socket server...")
            self.save_config()
            server.close()
            exit(0)

        signal.signal(signal.SIGINT, handle_exit)

        if interactive:
            print(f"[hiollama] Listening on {SOCKET_PATH}")
        while True:
            conn, addr = server.accept()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[Debug] Connection accepted from {addr} at {timestamp}")
            data = conn.recv(8192)
            print(f"[Debug] Raw data received: {data.decode().strip()} at {timestamp}")
            try:
                req = json.loads(data)
                msg_type = req.get("type")
                content = req.get("data", "")
                print(f"[Debug] Parsed request: type={msg_type}, data={content} at {timestamp}")
                if msg_type == "prompt":
                    self.chat_history.add_message("user", content)
                    model_response = self.model.talk_to_model(content, stream=False)
                    response_text = model_response.get("message", {}).get("content", "")
                    response = {"response": response_text}
                elif msg_type == "cmd":
                    try:
                        action = json.loads(content).get("action")
                        print(f"[Debug] Extracted action: {action} at {timestamp}")
                        if action:
                            # Capture ALL output from command processing
                            import io
                            import re
                            
                            original_stdout = sys.stdout
                            buffer = io.StringIO()
                            
                            try:
                                # Set non-interactive mode for socket commands
                                self.non_interactive = True
                                sys.stdout = buffer
                                cmd_result = self.process_input(f"{action}")
                                
                                # If there's a session manager, also process the command result
                                # (this is where the additional output like ACTIVE CHATS comes from)
                                if hasattr(self, 'session_manager') and self.session_manager:
                                    self.session_manager.process_command_result(cmd_result)
                                    
                            finally:
                                # Reset non-interactive mode
                                self.non_interactive = False
                                sys.stdout = original_stdout
                            
                            # Get captured output and strip Rich tags
                            captured_output = buffer.getvalue()
                            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                            clean_output = ansi_escape.sub('', captured_output)
                            
                            # Print Rich output to terminal (so user sees it)
                            if captured_output:
                                print(captured_output, end='')
                            
                            # Send clean output to client
                            response = {"response": clean_output.strip() if clean_output.strip() else (cmd_result.message if hasattr(cmd_result, "message") else str(cmd_result))}
                        else:
                            response = {"error": "Missing action in command."}
                    except json.JSONDecodeError:
                        response = {"error": "Invalid JSON in 'data' field for command."}
                else:
                    response = {"error": "Unknown message type."}
            except json.JSONDecodeError:
                response = {"error": "Invalid JSON in request."}
            except Exception as e:
                response = {"error": f"model error: {str(e)}"}
            try:
                conn.sendall(json.dumps(response).encode())
            except BrokenPipeError:
                print("[hiollama] Client closed connection before response was sent.")
            conn.close()
            if interactive:
                print(f"[hiollama] Received: {data.decode().strip()} -> Sent: {json.dumps(response)}")

    def confirm(self, question, default=True):
        """Auto-confirm if non_interactive, else prompt the user."""
        if getattr(self, 'non_interactive', False):
            return default
        return Prompt.ask(question, choices=["y", "n"], default="y" if default else "n") == "y"
