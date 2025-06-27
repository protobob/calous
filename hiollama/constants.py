"""Constants for the hiollama package."""
from pathlib import Path

# Rainbow text colors for logo
RAINBOW_COLORS = ["red", "orange1", "yellow1", "green", "blue", "purple", "magenta"]

# Extended rainbow colors for more chats (original + darker variants)
EXTENDED_RAINBOW_COLORS = [
    # Original bright colors (chats 1-7)
    "red", "orange1", "yellow1", "green", "blue", "purple", "magenta",
    # Darker variants (chats 8-14)
    "dark_red", "orange3", "yellow3", "dark_green", "blue3", "purple3", "magenta3"
]

# Rainbow text constant for logo display
RAINBOW_TEXT = "HIOLLAMA!"

# Default configuration
DEFAULT_MODEL = ""
DEFAULT_SYSTEM_PROMPT = ""
DEFAULT_NUM_CTX = 2048
DEFAULT_TEMPERATURE = 0.8

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
HIOLLAMA_DIR = Path.home() / "hiollama"
LOG_DIR = HIOLLAMA_DIR / "logs"
HISTORY_DIR = HIOLLAMA_DIR / ".history"
PERSONA_DIR = HIOLLAMA_DIR / "persona"
CONFIG_PATH = HIOLLAMA_DIR / "config.json"  # Changed from Path.home() / ".hiollama_config_unified.json"
CLI_HISTORY_PATH = HIOLLAMA_DIR / ".cli_history"

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
APP_VERSION = "0.12.18.dev"

# Multi-chat configuration
DEFAULT_NUM_CHATS = 4  # default if no config

# Chat session defaults
MAX_CHATS = 14
TWIST_PREVIEW_LENGTH = 100
SWITCH_PREVIEW_LENGTH = 50

# Added SOCKET_PATH for centralized configuration
SOCKET_PATH = "/tmp/hiollama.sock"

# UI Formatting Constants
class Colors:
    """Rich color constants for consistent UI formatting."""
    ERROR = "[bold red]"
    SUCCESS = "[green]"
    WARNING = "[yellow]"
    INFO = "[bold cyan]"
    HINT = "[grey50]"
    COMMAND = "[cyan]"
    RESET = ""

class Messages:
    """Standard message templates."""
    OPERATION_CANCELLED = "Operation cancelled."
    ALIAS_CREATION_FAILED = "Failed to create alias"
    ALIAS_REMOVAL_FAILED = "Failed to remove alias"
    
class Confirmations:
    """Standard confirmation choices."""
    YES_NO = ["y", "n"]
    DEFAULT_NO = "n"