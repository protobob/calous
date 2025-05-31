"""Entry point for the hiollama package."""
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
    
    args = parser.parse_args()
    
    # Determine number of chats: command line arg > saved config > default constant
    if args.num_chats is None:
        # No argument provided, use saved preference or default
        num_chats = ConfigManager.get_num_chats()
    else:
        # Command line argument provided, use it
        num_chats = args.num_chats
    
    # Validate input
    if num_chats < 1:
        print("Error: Number of chats must be at least 1")
        sys.exit(1)
    if num_chats > args.max_chats:
        print(f"Error: Number of chats cannot exceed {args.max_chats}")
        sys.exit(1)
    
    # Start the session manager with the determined number of chats
    session_manager = ChatSessionManager(num_chats=num_chats)
    session_manager.run()  # Changed from .start() to .run()

if __name__ == "__main__":
    main()