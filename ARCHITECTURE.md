# Hi, Ollama! - Technical Architecture

This document provides a technical overview of the `hiollama` project - a command-line interface for interacting with Ollama language models. It explains the package structure, component relationships, and how data flows through the system.

## Project Structure

hiollama/
├── README.md               # User documentation
├── setup.py                # Package installation configuration
├── hiollama/               # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point
│   ├── app.py              # Main application class
│   ├── chat_history.py     # Chat history management
│   ├── commands.py         # Command handlers
│   ├── config.py           # Configuration management
│   ├── constants.py        # Shared constants
│   ├── model_interaction.py # Model communication logic
│   ├── ui.py               # User interface elements
│   └── utils.py            # Utility functions
└── hiollama.egg-info/      # Package metadata (generated)
```

## Component Relationships

The application uses a modular design pattern with these key components:

1. **`HiOllamaChat` (app.py)**: The central class that coordinates all other components and manages the application state. It supports multi-instance chat functionality and handles user input, commands, and model interactions.

2. **`ConfigManager` (config.py)**: Handles loading and saving configuration settings for each chat instance. Configurations are stored in JSON files, allowing instance-specific settings.

3. **`UIManager` (ui.py)**: Manages user interface elements, including formatted prompts, spinners, and help menus, using the Rich library.

4. **`ChatHistory` (chat_history.py)**: Manages conversation history, including adding/removing messages, logging, and displaying chat history.

5. **`ModelInteraction` (model_interaction.py)**: Handles communication with Ollama models, including sending prompts, processing responses, and listing available models.

6. **`CommandHandler` (commands.py)**: Parses and executes commands prefixed with a slash (e.g., `/help`, `/model`). Supports commands for managing chat history, models, prompts, and system settings.

7. **`Utils` (utils.py)**: Contains utility functions for formatting messages, printing headers, and loading files as prompts.

8. **`Constants` (constants.py)**: Defines shared constants, such as default configurations, API settings, and UI colors.

## Data Flow and Process

### Initialization Process

1. The `__main__.py` file creates two instances of `HiOllamaChat` for multi-instance support.
2. Each `HiOllamaChat` instance loads its configuration and initializes its components.
3. The main application loop alternates between the two chat instances.

### Main Application Loop

1. The application displays a prompt using `UIManager.generate_prompt_text()`.
2. The user enters text input.
3. The input is processed:
   - If it begins with `/`, it's sent to `CommandHandler.parse_and_execute()`.
   - Otherwise, it's sent to `HiOllamaChat.handle_regular_input()`.

### Regular Input Processing

1. The input is added to chat history with `ChatHistory.add_message()`.
2. A spinner animation is displayed with `UIManager.run_with_spinner()`.
3. The model is queried via `ModelInteraction.talk_to_model()`.
4. The response is processed through `ModelInteraction.process_response()`.
5. The response is added to chat history and displayed to the user.

### Command Processing

Commands are methods in the `CommandHandler` class prefixed with `cmd_`:

- `/help` → `cmd_help()`: Displays the help menu.
- `/model` → `cmd_model()`: Selects a different model.
- `/clear` → `cmd_clear()`: Clears the chat history.
- `/twist` → `cmd_twist()`: Copies the last AI response to the other chat instance.
...and more.

### Configuration Management

- Configurations are stored in instance-specific JSON files (e.g., `~/.hiollama_config_0.json`).
- Loaded at startup via `ConfigManager.load_config()`.
- Updated when settings change and saved on exit via `ConfigManager.save_config()`.

### Logs

- Chat logs are stored in `~/hiollama_logs/` with instance-specific subdirectories.
- File names are based on the current date.
- Logging can be toggled with the `/toggle_log` command.

## Key Features

### Multi-Instance Chat

- Supports two simultaneous chat instances.
- Users can switch between chats with `/switch`.
- Responses from one chat can be sent as prompts to the other using `/twist`.

### Chat History Management

- Messages are stored in memory as a list of message objects.
- Maximum history size is configurable (default: 20 messages).
- History can be viewed with the `/history` command.

### Model Interaction

- Communicates with locally installed Ollama models.
- Passes system prompts and chat history for context.
- Formats responses and displays evaluation statistics (optional).
- Supports filtering of "thought" sections in responses.

### Prompt Management

- Saves up to 10 custom prompts.
- Prompts can be set, viewed, and used with commands.
- System prompts can be customized.

### File Processing

- Can load file contents as prompts.
- Supports adding instructions for how to process the file.

## Package Installation

The project uses standard Python packaging:

- `setup.py` defines metadata and dependencies.
- `entry_points` defines the console script `hiollama`.
- Installation via `pip install -e .` makes it available system-wide.

## Technical Decisions

### Rich Library

The project uses the Rich library for:

- Formatted console output.
- Spinners for async operations.
- Interactive prompts.
- ANSI color and style support.

### Modular Design

- Each component has a single responsibility.
- Components communicate through the central `HiOllamaChat` class.
- This makes the code more maintainable and testable.

### Command Pattern

- Commands are implemented using a simple command pattern.
- The `CommandHandler` maps command strings to methods.
- This makes it easy to add new commands.

### Config as JSON

- Configuration is stored as a simple JSON file.
- This makes it easy to save/load settings.
- It's also human-readable and editable outside the app.

## Adding New Features

To add a new feature:

1. Determine which component it belongs in.
2. Add the necessary methods to that component.
3. If it's a new command, add it to the `commands` dictionary in `CommandHandler.__init__()`.
4. Update the help menu in `UIManager.help_menu()` if needed.
5. Add any new configuration options to `ConfigManager.DEFAULT_CONFIG`.
