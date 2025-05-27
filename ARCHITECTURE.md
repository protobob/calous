# Hi, Ollama! - Technical Architecture

This document provides a technical overview of the `hiollama` project - a dual-chat command-line interface for interacting with Ollama language models. It explains the package structure, component relationships, and how data flows through the system.

## Project Structure

```
hiollama/
├── README.md               # User documentation
├── CHANGELOG.md            # Version history and changes
├── ARCHITECTURE.md         # This technical documentation
├── setup.py                # Package installation configuration
├── hiollama/               # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point and dual-chat orchestration
│   ├── app.py              # Main HiOllamaChat class with global model management
│   ├── chat_history.py     # Instance-specific chat history management
│   ├── commands.py         # Command handlers with chat-aware functionality
│   ├── config.py           # Configuration management (global + per-instance)
│   ├── constants.py        # Shared constants and defaults
│   ├── model_interaction.py # Ollama API communication
│   ├── ui.py               # Rich-based user interface with chat colors
│   └── utils.py            # Utility functions for formatting and chat management
└── hiollama.egg-info/      # Package metadata (generated)
```

## Component Relationships

The application uses a modular design pattern with these key components:

### Core Classes

1. **`HiOllamaChat` (app.py)**: The central application class that coordinates all other components and manages chat state. Features:
   - Class-level global model management
   - Instance registration system for synchronized updates
   - Dual-chat switching and twist functionality
   - Configuration management per instance

2. **`ConfigManager` (config.py)**: Handles both global and instance-specific configuration:
   - **Global Config**: `~/.hiollama_config_global.json` (shared model selection)
   - **Instance Configs**: `~/.hiollama_config_0.json`, `~/.hiollama_config_1.json`
   - Automatic separation of global vs instance-specific settings

3. **`UIManager` (ui.py)**: Rich-based interface management:
   - Color-coded chat instances (green/blue)
   - Interactive prompts and spinners
   - Formatted help menus and variable displays
   - Chat-aware prompt generation

4. **`ChatHistory` (chat_history.py)**: Instance-specific conversation management:
   - Per-chat message storage with configurable limits
   - Automatic logging to separate directories
   - Thought filtering for reasoning models
   - History display and clearing functionality

5. **`ModelInteraction` (model_interaction.py)**: Ollama API communication:
   - Native `ollama.chat()` and `ollama.list()` integration
   - Response processing with evaluation data
   - Model selection interface
   - Error handling for API failures

6. **`CommandHandler` (commands.py)**: Comprehensive command system:
   - Global model changes affecting both chats
   - Chat switching and twist functionality
   - Prompt management (save/load/use)
   - Configuration toggles and file loading

### Utility Components

7. **`Utils` (utils.py)**: Shared utility functions:
   - Chat color management
   - Message formatting and previews
   - Rainbow header display
   - Switch/twist state management

8. **`Constants` (constants.py)**: Centralized configuration:
   - UI colors and formatting
   - Default settings and limits
   - File paths and API endpoints
   - Version management

## Data Flow and Architecture Patterns

### Initialization Process

1. **Dual-Chat Setup**: `__main__.py` creates two `HiOllamaChat` instances
2. **Global Registration**: Each instance registers for global model updates
3. **Configuration Loading**: 
   - Global config loaded once at class level
   - Instance configs loaded separately for each chat
4. **Component Initialization**: UI, history, model interaction, and commands initialized per instance

### Global Model Management

```
┌─────────────────┐    ┌─────────────────┐
│   Chat 1        │    │   Chat 2        │
│                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ /model cmd  │ │───▶│ │ Auto-update │ │
│ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘
         │                       ▲
         ▼                       │
┌─────────────────────────────────────────┐
│        Global Config                    │
│  ~/.hiollama_config_global.json        │
│  { "selected_model": "qwen3:0.6B" }    │
└─────────────────────────────────────────┘
```

### Chat Switching and Twist Flow

```
Chat 1 ──/switch──▶ Chat 2
   │                   ▲
   │                   │
   ▼                   │
/twist ────────────────┘
   │
   ▼
Last Response → Twist Content → Chat 2 Prompt
```

### Command Processing Architecture

Commands follow a structured pattern:
- **Input Parsing**: Commands identified by `/` prefix
- **Argument Handling**: Complex commands parse arguments
- **Global Updates**: Model changes propagate to all instances
- **State Management**: Switch/twist requests handled via flags

### Configuration Hierarchy

```
Global Settings (Shared)
├── selected_model
└── [Future global settings]

Instance Settings (Per-Chat)
├── system_prompt
├── verbosity
├── think_filtering
├── MAX_HISTORY
├── saved_prompts (1-10)
└── logging_enabled
```

## Key Features Implementation

### Dual-Chat System

- **Independent State**: Each chat maintains separate history, logs, and settings
- **Synchronized Updates**: Model changes apply globally via class-level management
- **Seamless Switching**: `/switch` command with state preservation
- **Twist Functionality**: Response copying between chats with preview

### Advanced State Management

- **Instance Registration**: New instances automatically register for global updates
- **Flag-based Switching**: `switch_requested` and `twist_content` attributes coordinate chat changes
- **Configuration Separation**: Global vs instance-specific settings properly isolated

### Rich Terminal Interface

- **Color Coding**: Green (Chat 1) and Blue (Chat 2) with consistent theming
- **Dynamic Prompts**: Chat-aware prompt generation with history counters
- **Interactive Elements**: Spinners, confirmations, and formatted displays
- **Rainbow Header**: Version display with colorful branding

### File and Prompt Management

- **Saved Prompts**: 10 slots per chat instance with persistence
- **File Loading**: Code and text file processing with instructions
- **System Prompts**: Per-chat customization with defaults
- **History Management**: Configurable limits with automatic trimming

## Technical Decisions and Patterns

### Class-Level Global State

```python
class HiOllamaChat:
    _global_config = None  # Shared across all instances
    _all_instances = []    # Instance registry for updates
```

Benefits:
- Ensures model consistency across chats
- Enables synchronized updates
- Maintains separation of concerns

### Command Pattern Implementation

Commands use method mapping with argument parsing:
```python
self.commands = {
    "/help": self.cmd_help,
    "/model": self.cmd_model,
    # ... more commands
}
```

### Configuration Strategy

- **JSON Storage**: Human-readable and editable
- **Automatic Separation**: Global vs instance settings
- **Default Fallbacks**: Graceful handling of missing configs
- **Error Recovery**: Continues with defaults on load failures

### Modern Ollama Integration

- **Native API**: Uses `ollama.chat()` and `ollama.list()`
- **Response Objects**: Proper handling of structured responses
- **Error Handling**: Comprehensive exception management
- **Evaluation Data**: Optional performance metrics display

## Extending the Architecture

### Adding New Commands

1. Add method to `CommandHandler` class
2. Register in `commands` dictionary
3. Update help menu in `UIManager`
4. Add any required configuration options

### Adding Global Settings

1. Extend `DEFAULT_GLOBAL_CONFIG` in `ConfigManager`
2. Update `update_global_model` pattern for new setting
3. Implement synchronization across instances

### Adding Instance Features

1. Add to `DEFAULT_CONFIG` in `ConfigManager`
2. Initialize in `HiOllamaChat.__init__()`
3. Implement save/load in configuration methods
4. Add UI elements as needed

## Performance and Scalability

### Memory Management
- History limits prevent unbounded growth
- Configuration caching reduces I/O
- Instance registration allows controlled updates

### File I/O Optimization
- Lazy configuration loading
- Separate global/instance file access
- Error-tolerant save operations

### Threading Considerations
- Spinner animations run in separate threads
- UI updates synchronized through Rich library
- Graceful shutdown with proper cleanup

## Security and Error Handling

### Input Validation
- Command argument parsing with type checking
- File path validation for load operations
- Configuration value bounds checking

### Error Recovery
- Default configuration fallbacks
- Graceful API failure handling
- User feedback for all error conditions

### Data Persistence
- Automatic configuration saving
- Separate log directories per instance
- Timestamp-based log file organization

This architecture provides a robust, extensible foundation for the dual-chat Ollama interface while maintaining clean separation of concerns and enabling future enhancements.