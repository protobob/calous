import socket
import os
import json
from .session_manager import ChatSessionManager

SOCKET_PATH = "/tmp/hiollama.sock"

def run_socket_server(interactive=False):
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)

    if interactive:
        print(f"[hiollama] Listening on {SOCKET_PATH}")

    session_manager = ChatSessionManager(num_chats=1)
    chat = session_manager.chats[0]

    while True:
        conn, _ = server.accept()
        data = conn.recv(8192)
        try:
            req = json.loads(data)
            msg_type = req.get("type")
            content = req.get("data", "")

            if msg_type == "prompt":
                model_response = chat.model.talk_to_model(content, stream=False)
                response_text = model_response.get("message", {}).get("content", "")
                response = {"response": response_text}
            elif msg_type == "cmd":
                response = {"result": f"ran command: {content}"}
            else:
                response = {"error": "unknown message type"}

        except Exception as e:
            response = {"error": f"model error: {str(e)}"}

        try:
            conn.sendall(json.dumps(response).encode())
        except BrokenPipeError:
            if interactive:
                print("[hiollama] Client closed connection before response was sent.")

        conn.close()

        if interactive:
            print(f"[hiollama] Received: {data.decode().strip()} -> Sent: {json.dumps(response)}")
