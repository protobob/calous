import argparse
import sys
from .session_manager import ChatSessionManager
from .constants import DEFAULT_NUM_CHATS, MAX_CHATS, SERVER_DEFAULT_NUM_CHATS
from .config import ConfigManager
from .unified_logger import unified_logger

def main():
    parser = argparse.ArgumentParser(description="Hi, Ollama! - Multi-chat AI interface")
    parser.add_argument('num_chats', nargs='?', type=int, default=None, 
                       help=f'Number of chat channels (default: saved preference or {DEFAULT_NUM_CHATS})')
    parser.add_argument('--max-chats', type=int, default=MAX_CHATS,
                       help=f'Maximum allowed chat channels (default: {MAX_CHATS})')
    parser.add_argument('--debug', action='store_true',
                       help='Print debug output while running in socket mode')

    args = parser.parse_args()

    # Always run in socket/server mode
    num_chats = SERVER_DEFAULT_NUM_CHATS
    # Warn user if they specified a chat count that will be ignored
    if args.num_chats is not None:
        unified_logger._write_log_entry("WARNING", f"Chat channel argument '{args.num_chats}' ignored in socket mode. Using {SERVER_DEFAULT_NUM_CHATS} chat channels.")

    session_manager = ChatSessionManager(num_chats=num_chats, debug=args.debug)
    # Set all chats to non-interactive mode for socket/server
    for chat in session_manager.get_all_chats():
        chat.non_interactive = True
    session_manager.listen_for_socket(debug=args.debug)

if __name__ == "__main__":
    main()
