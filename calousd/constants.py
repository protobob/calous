# Default number of chats for server/socket mode
SERVER_DEFAULT_NUM_CHATS = 14
"""Constants for the calous package."""
from pathlib import Path

# Rainbow text colors for logo (ANSI codes)
RAINBOW_COLORS = ["\033[31m", "\033[38;5;208m", "\033[93m", "\033[32m", "\033[34m", "\033[35m", "\033[35m"]

# Extended rainbow colors for more chats (ANSI codes)
EXTENDED_RAINBOW_COLORS = [
    # Original bright colors (chats 1-7)
    "\033[31m",      # red
    "\033[38;5;208m", # orange1
    "\033[93m",      # yellow1
    "\033[32m",      # green
    "\033[34m",      # blue
    "\033[35m",      # purple
    "\033[35m",      # magenta
    # Darker variants (chats 8-14)
    "\033[31m",      # dark_red (same as red)
    "\033[38;5;172m", # orange3
    "\033[33m",      # yellow3
    "\033[32m",      # dark_green (same as green)
    "\033[34m",      # blue3 (same as blue)
    "\033[35m",      # purple3 (same as purple)
    "\033[35m",      # magenta3 (same as magenta)
]

# Rainbow text constant for logo display
RAINBOW_TEXT = "CALOUSD"

# Default configuration
DEFAULT_MODEL = ""
DEFAULT_SYSTEM_PROMPT = ""
DEFAULT_NUM_CTX = 2048
DEFAULT_TEMPERATURE = 0.8

# VRAM Management
DEFAULT_KEEP_ALIVE = "30m"  # Keep models loaded for 30 minutes (change to "5m" if switching models frequently)

# Context window limits
MIN_NUM_CTX = 2048
MAX_NUM_CTX = 32768

# Temperature limits
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0

# API configuration
OLLAMA_API_URL = "http://localhost:11434/api/tags"
API_TIMEOUT = 5

# File paths
CALOUS_DIR = Path.home() / ".calous"
LOG_DIR = CALOUS_DIR / "logs"
HISTORY_DIR = CALOUS_DIR / ".history"
PERSONA_DIR = CALOUS_DIR / "persona"
CONTEXT_DIR = CALOUS_DIR / "contexts"
CHAT_HISTORY_DIR = CALOUS_DIR / "chat_history"
CONFIG_PATH = CALOUS_DIR / "config.json"
COMMANDS_FILE = CALOUS_DIR / "commands.txt"  # For cx_rust tab completion

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
LARGE_FILE_WARNING_SIZE = 1 * 1024 * 1024  # 1MB

# Supported file extensions for file operations
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
    '.ini', '.cfg', '.conf', '.log', '.sql', '.sh', '.bat', '.ps1', '.csv', '.tsv',
    '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.php', '.rb', '.go', '.rs', '.kt',
    '.swift', '.scala', '.clj', '.hs', '.elm', '.lua', '.r', '.m', '.pl', '.vim'
}

# Image extensions for vision models
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', '.svg'
}

# Binary/executable extensions that require user confirmation
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.img', '.iso', '.zip', '.rar', '.tar',
    '.gz', '.7z', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
}

# Prompt configuration
MAX_PROMPTS = 10

# UI configuration
MAX_PREVIEW_LENGTH = 100
HEADER_SEPARATOR = ": SUMMARY"

# Application metadata
APP_VERSION = "1.7.3.dev"

# Chat session defaults
TWIST_PREVIEW_LENGTH = 100
SWITCH_PREVIEW_LENGTH = 50

# Added SOCKET_PATH for centralized configuration
SOCKET_PATH = "/tmp/calous.sock"

# Socket message types
class MessageTypes:
    """Socket message type constants."""
    PROMPT = "prompt"
    CMD = "cmd"
    CONFIRMATION_REQUEST = "confirmation_request"
    CONFIRMATION_RESPONSE = "confirmation_response"

# UI Formatting Constants
class Colors:
    """ANSI color constants for consistent UI formatting."""
    ERROR = "\033[1;31m"      # bold red
    SUCCESS = "\033[32m"      # green
    WARNING = "\033[33m"      # yellow
    INFO = "\033[1;36m"       # bold cyan
    HINT = "\033[90m"         # grey50 (dark grey)
    COMMAND = "\033[36m"      # cyan
    RESET = "\033[0m"         # reset

class Messages:
    """Standard message templates."""
    OPERATION_CANCELLED = "Operation cancelled."
    ALIAS_CREATION_FAILED = "Failed to create alias"
    ALIAS_REMOVAL_FAILED = "Failed to remove alias"
    
class Confirmations:
    """Standard confirmation choices."""
    YES_NO = ["y", "n"]
    DEFAULT_NO = "n"
    DEFAULT_YES = "y"

# Enhanced logging configuration
class LogConfig:
    """Logging configuration constants."""
    DEFAULT_DEBUG_ENABLED = True
    DEFAULT_STRUCTURED_FORMAT = False
    LOG_ROTATION_DAYS = 30
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Log stream names
    STREAM_APP = 'app'
    STREAM_DEBUG = 'debug'
    STREAM_MODEL = 'model'
    STREAM_AUDIT = 'audit'
    STREAM_ERROR = 'error'