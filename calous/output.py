"""
Output handling for CALOUS daemon mode.
All client-facing output should be sent through this module.
"""

def send_to_client(message, client_socket=None):
    """
    Send a message to the connected client.
    If client_socket is provided, send via socket.
    Otherwise, this is a placeholder for integration with session/socket manager.
    """
    if client_socket:
        # Ensure message is a string and encode to bytes
        if not isinstance(message, str):
            message = str(message)
        client_socket.sendall(message.encode('utf-8'))
    else:
        # Placeholder: integrate with session/socket manager as needed
        pass
