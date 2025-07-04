"""History command formatters."""

from ...constants import Colors, Messages, Confirmations
from ..formatters import CommandFormatter


class HistoryFormatter(CommandFormatter):
    """Handles formatting for history command outputs."""
    
    @staticmethod
    def format_clear_warning(chat_info):
        """Print history clear warning with colored chat identification."""
        HistoryFormatter._output(f"\n[1;33mWarning:[0m This will [1;31mCLEAR[0m \033[1m{chat_color}CHAT {chat_info.number}\033[0m history.")
        HistoryFormatter._output("All conversation history will be permanently deleted.")
    
    @staticmethod
    def format_clear_success(chat_info):
        """Print history clear success message."""
        HistoryFormatter._output(f"\033[1m{chat_color}CHAT {chat_info.number}\033[0m history cleared successfully!")
    
    @staticmethod
    def confirm_clear() -> bool:
        """Confirm history clear operation."""
        prompt = "\nAre you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"
    
    @staticmethod
    def format_operation_cancelled():
        """Print operation cancelled message."""
        HistoryFormatter._output(f"\n{Messages.OPERATION_CANCELLED}")
    
    @staticmethod
    def format_history_enabled(chat_info):
        """Print history enabled message."""
        HistoryFormatter._output(f"\033[1m{chat_color}CHAT {chat_info.number}\033[0m history recording [1;32mENABLED[0m")
    
    @staticmethod
    def format_history_disabled(chat_info):
        """Print history disabled message."""
        HistoryFormatter._output(f"\033[1m{chat_color}CHAT {chat_info.number}\033[0m history recording [1;31mDISABLED[0m")
    
    @staticmethod
    def format_history_already_enabled(chat_info):
        """Print history already enabled message."""
        HistoryFormatter._output(f"\033[1m{chat_color}CHAT {chat_info.number}\033[0m history recording is already [1;32mENABLED[0m")
    
    @staticmethod
    def format_history_already_disabled(chat_info):
        """Print history already disabled message."""
        HistoryFormatter._output(f"\033[1m{chat_color}CHAT {chat_info.number}\033[0m history recording is already [1;31mDISABLED[0m")
    
    @staticmethod
    def format_purge_warning(chat_info, n):
        HistoryFormatter._output(f"\n[1;33mWarning:[0m This will [1;31mDELETE[0m the [1m{n}[0m most recent message(s) from \033[1m{chat_color}CHAT {chat_info.number}\033[0m history.")
        HistoryFormatter._output("This cannot be undone.")

    @staticmethod
    def confirm_purge() -> bool:
        from ...constants import Confirmations
        prompt = "Are you sure you want to continue? (y/n) [n]: "
        response = input(prompt).strip().lower()
        if not response:
            response = "n"
        return response == "y"

    @staticmethod
    def format_purge_success(n):
        HistoryFormatter._output(f"[32mPurged {n} message(s) from chat history.[0m")

    @staticmethod
    def format_no_messages_to_purge():
        HistoryFormatter._output(f"[33m\nNo messages to purge.[0m")
    
    @staticmethod
    def format_file_exists_warning(filename: str):
        """Print warning when save file already exists."""
        HistoryFormatter._output(f"\n[33mFile {filename} already exists.[0m")
    
    @staticmethod
    def format_save_success(filepath, count: int):
        """Print save success message."""
        HistoryFormatter._output(f"\n[32mChat history saved to {filepath} ({count} messages).[0m")
    
    @staticmethod
    def format_save_no_messages():
        """Print message when no messages to save."""
        HistoryFormatter._output(f"\n[33mNo messages to save. File not created.[0m")
    
    @staticmethod
    def format_load_file_not_found(filepath):
        """Print file not found error for load."""
        HistoryFormatter._output(f"\n[31mFile not found: {filepath}[0m")
    
    @staticmethod
    def format_load_warning():
        """Print load overwrite warning."""
        HistoryFormatter._output("\n[33mWarning: Loading will overwrite current chat history in memory.[0m")
    
    @staticmethod
    def format_load_success(filepath, count: int):
        """Print load success message."""
        HistoryFormatter._output(f"\n[32mLoaded {count} messages from {filepath} into current chat history.[0m")
    
    @staticmethod
    def format_no_saved_files():
        """Print message when no saved files found."""
        HistoryFormatter._output("\n[33mNo saved chat history files found.[0m")
    
    @staticmethod
    def format_saved_files_header():
        """Print header for saved files list."""
        HistoryFormatter._output("\n[1mSaved chat history files:[0m")
    
    @staticmethod
    def format_saved_file_item(filename: str, size: int):
        """Print saved file item."""
        HistoryFormatter._output(f"  [36m{filename}[0m  ({size} bytes)")
    
    @staticmethod
    def format_delete_file_not_found(filepath):
        """Print file not found error for delete."""
        HistoryFormatter._output(f"\n[31mFile not found: {filepath}[0m")
    
    @staticmethod
    def format_delete_warning(filename: str):
        """Print delete confirmation warning."""
        HistoryFormatter._output(f"\n[33mAre you sure you want to delete {filename}? This cannot be undone.[0m")
    
    @staticmethod
    def format_delete_success(filename: str):
        """Print delete success message."""
        HistoryFormatter._output(f"\n[32mDeleted {filename}.[0m")
    
    @staticmethod
    def format_delete_error(error: str):
        """Print delete error message."""
        HistoryFormatter._output(f"\n[31mError deleting file: {error}[0m")
    
    @staticmethod
    def format_purge_file_error(error: str):
        """Print purge file update error."""
        HistoryFormatter._output(f"[31mError updating history file: {error}[0m")
    
    @staticmethod
    def format_history_vars(chat_info, history_enabled: bool, message_count: int):
        """Print history variables information."""
        status_text = "[1;32mENABLED[0m" if history_enabled else "[1;31mDISABLED[0m"
        
        HistoryFormatter._output(f"\n\033[1m{chat_color}|\033[0m \033[1m{chat_color}CHAT {chat_info.number} HISTORY VARIABLES\033[0m\n")
        HistoryFormatter._output(f"\033[1m{chat_color}|\033[0m {'Recording Status:':<20} {status_text}")
        HistoryFormatter._output(f"\033[1m{chat_color}|\033[0m {'Message Count:':<20} [37m{message_count}[0m")
        HistoryFormatter._output("")
