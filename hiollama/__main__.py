"""Entry point for the hiollama package."""
from .session_manager import ChatSessionManager

def main():
    """Main application entry point."""
    session_manager = ChatSessionManager()
    session_manager.run()

if __name__ == "__main__":
    main()