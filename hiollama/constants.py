"""Constants for the hiollama package."""
from pathlib import Path

# Rainbow text colors for logo
RAINBOW_COLORS = ["red", "orange1", "yellow1", "green", "blue", "purple", "magenta"]
RAINBOW_TEXT = "HIOLLAMA!"

# Default configuration
DEFAULT_MODEL = "qwen3:0.6B"
DEFAULT_MAX_HISTORY = 20
DEFAULT_SYSTEM_PROMPT = "You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code."

# API configuration
OLLAMA_API_URL = "http://localhost:11434/api/tags"
API_TIMEOUT = 5

# File paths
LOG_DIR = Path.home() / "hiollama_logs"
CONFIG_PATH = Path.home() / ".hiollama_config_unified.json"

# Prompt configuration
MAX_PROMPTS = 10

# UI configuration
MAX_PREVIEW_LENGTH = 100
HEADER_SEPARATOR = ": SUMMARY"

# Application metadata
APP_VERSION = "0.5.2.dev"

# Multi-chat configuration
DEFAULT_NUM_CHATS = 4  # Changed from 2 to 4 for testing N-chat support