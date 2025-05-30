"""Entry point for the hiollama package."""
import argparse
import sys
from .session_manager import ChatSessionManager
from .constants import DEFAULT_NUM_CHATS, MAX_CHATS

def main():
    parser = argparse.ArgumentParser(description="Hi, Ollama! - Multi-chat AI interface")
    parser.add_argument('num_chats', nargs='?', type=int, default=DEFAULT_NUM_CHATS, 
                       help=f'Number of chat channels (default: {DEFAULT_NUM_CHATS})')
    parser.add_argument('--max-chats', type=int, default=MAX_CHATS,
                       help=f'Maximum allowed chat channels (default: {MAX_CHATS})')
    
    args = parser.parse_args()
    
    # Validate input
    if args.num_chats < 1:
        print("Error: Number of chats must be at least 1")
        sys.exit(1)
    if args.num_chats > args.max_chats:
        print(f"Error: Number of chats cannot exceed {args.max_chats}")
        sys.exit(1)
    
    # Start the session manager with the specified number of chats
    session_manager = ChatSessionManager(num_chats=args.num_chats)
    session_manager.run()  # Changed from .start() to .run()

if __name__ == "__main__":
    main()