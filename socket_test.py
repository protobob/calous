import socket
import json

SOCKET_PATH = "/tmp/hiollama.sock"

# Prepare the request as expected by your socket server
request = {
    "type": "prompt",
    "data": "What is the capital of France?"
}

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    client.connect(SOCKET_PATH)
    client.sendall(json.dumps(request).encode())
    response = client.recv(8192)
    print("Response from server:", response.decode())