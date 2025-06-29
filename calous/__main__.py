import argparse
import sys
from .session_manager import ChatSessionManager
from .constants import DEFAULT_NUM_CHATS, MAX_CHATS
from .config import ConfigManager

def main():
    parser = argparse.ArgumentParser(description="Hi, Ollama! - Multi-chat AI interface")
    parser.add_argument('num_chats', nargs='?', type=int, default=None, 
                       help=f'Number of chat channels (default: saved preference or {DEFAULT_NUM_CHATS})')
    parser.add_argument('--max-chats', type=int, default=MAX_CHATS,
                       help=f'Maximum allowed chat channels (default: {MAX_CHATS})')
    parser.add_argument('--socket', action='store_true',
                       help='Run CALOUS as a socket server daemon')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Print debug output while running in socket mode')

    args = parser.parse_args()

    # In socket mode, always use 14 chats (ignore num_chats argument and config)
    if args.socket:
        num_chats = 14
        # Warn user if they specified a chat count that will be ignored
        if args.num_chats is not None:
            print(f"[Warning] Chat channel argument '{args.num_chats}' ignored in socket mode. Using 14 chat channels.")
    else:
        if args.num_chats is None:
            num_chats = ConfigManager.get_num_chats()
        else:
            num_chats = args.num_chats

        if num_chats < 1:
            print("Error: Number of chats must be at least 1")
            sys.exit(1)
        if num_chats > args.max_chats:
            print(f"Error: Number of chats cannot exceed {args.max_chats}")
            sys.exit(1)

    session_manager = ChatSessionManager(num_chats=num_chats)

    if args.socket:
        # Set all chats to non-interactive mode for socket/server
        for chat in session_manager.get_all_chats():
            chat.non_interactive = True
        session_manager.listen_for_socket(interactive=args.interactive)
    else:
        session_manager.run()

if __name__ == "__main__":
    main()
