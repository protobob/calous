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
DEFAULT_MAX_HISTORY = 20
DEFAULT_SYSTEM_PROMPT = ""

# API configuration
OLLAMA_API_URL = "http://localhost:11434/api/tags"
API_TIMEOUT = 5

# File paths
HIOLLAMA_DIR = Path.home() / "hiollama"
LOG_DIR = HIOLLAMA_DIR / "logs"
HISTORY_DIR = HIOLLAMA_DIR / ".history"
CONFIG_PATH = Path.home() / ".hiollama_config_unified.json"

# Prompt configuration
MAX_PROMPTS = 10

# UI configuration
MAX_PREVIEW_LENGTH = 100
HEADER_SEPARATOR = ": SUMMARY"

# Application metadata
APP_VERSION = "0.6.7.dev"

# Multi-chat configuration
DEFAULT_NUM_CHATS = 4  # default if no config

# Chat session defaults
MAX_CHATS = 14
TWIST_PREVIEW_LENGTH = 100
SWITCH_PREVIEW_LENGTH = 50