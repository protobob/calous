import socket
import json
from typing import Dict, Any, List, Optional
from ..base import FunctionCallingPlugin, PluginCapability

class MCPClientPlugin(FunctionCallingPlugin):
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
    def __init__(self):
        super().__init__(
            name="mcp_client",
            version="1.0.0",
            description="Model Control Protocol (MCP) client plugin for CALOUS."
        )
        self.server_host = "127.0.0.1"
        self.server_port = 8080
        self.capabilities.append(PluginCapability.FUNCTION_CALLING)

        self.request_id = 0
        self.initialized = False

    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id

    def initialize(self) -> bool:
        try:
            result = self._call_mcp_method("initialize", {
                "protocol_version": "2025-06-18",
                "client_info": {
                    "name": "calous",
                    "version": "0.1"
                },
                "capabilities": {
                    "roots": False,
                    "sampling": False,
                    "elicitation": False,
                    "experimental": False
                }
            })
            # You could log or store server_info and capabilities here
            self._call_mcp_method("initialized", {}, is_notification=True)
            self.initialized = True
            return True
        except Exception as e:
            self._output(f"Failed to initialize MCP session: {e}")
            return False

    def get_function_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "function": {
                    "name": "mcp_send_command",
                    "description": "Send a tool call to the MCP server and return the response.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool": {"type": "string", "description": "Tool name to invoke."},
                            "args": {"type": "object", "description": "Arguments for the tool."}
                        },
                        "required": ["tool"]
                    }
                }
            }
        ]

    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.initialized:
            self.initialize()
        result = self._call_mcp_method("tools/call", {
            "tool": arguments.get("tool"),
            "args": arguments.get("args", {})
        })
        if result is None:
            return {"error": "No response from MCP server"}
        return result

    def _call_mcp_method(self, method: str, params: Dict[str, Any], is_notification: bool = False) -> Optional[Dict[str, Any]]:
        try:
            with socket.create_connection((self.server_host, self.server_port), timeout=5) as sock:
                request = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params
                }
                if not is_notification:
                    request["id"] = self._next_id()
                payload = json.dumps(request) + "\n"
                sock.sendall(payload.encode("utf-8"))

                if is_notification:
                    return None

                response = b""
                while not response.endswith(b"\n"):
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk

                decoded = json.loads(response.decode("utf-8").strip())

                if "error" in decoded:
                    return {"error": decoded["error"]}
                return decoded.get("result")
        except Exception as e:
            return {"error": str(e)}
