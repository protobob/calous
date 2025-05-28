# Hi, Ollama! - Technical Architecture

This document provides a technical overview of the `hiollama` project - a command-line interface for interacting with Ollama language models. It explains the package structure, component relationships, and how data flows through the system.

## Project Structure

```
hiollama/
├── README.md               # User documentation
├── CHANGELOG.md            # Version history and changes
├── ARCHITECTURE.md         # This technical documentation
├── setup.py                # Package installation configuration
├── hiollama/               # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point (creates ChatSessionManager)
│   ├── session_manager.py  # Central session coordination and chat orchestration
│   ├── app.py              # HiOllamaChat class with global model management
│   ├── chat_history.py     # Instance-specific chat history management
│   ├── commands.py         # Command handlers with event-driven results
│   ├── config.py           # Configuration management (global + per-instance)
│   ├── constants.py        # Shared constants and defaults
│   ├── model_interaction.py # Ollama API communication
│   ├── ui.py               # Rich-based user interface with rainbow chat colors
│   └── utils.py            # Utility functions for formatting and chat management
└── hiollama.egg-info/      # Package metadata (generated)
```

## Component Relationships

The application uses an event-driven architecture with centralized session management:

### Core Classes

1. **`ChatSessionManager` (session_manager.py)**: Central coordinator for all chat operations:
   - Manages multiple chat instances (configurable, defaults to 2)
   - Handles chat switching and twist functionality
   - Processes command results through event system
   - Orchestrates the main application loop
   - Manages startup and shutdown procedures

2. **`HiOllamaChat` (app.py)**: Individual chat instance:
   - Class-level global model management
   - Instance-specific configuration and state
   - Processes user input and returns structured command results
   - Coordinates with other components (UI, history, model, commands)

3. **`CommandHandler` (commands.py)**: Event-driven command processing:
   - Returns `CommandResult` objects with action intentions
   - Supports optional chat number arguments for `/switch` and `/twist`
   - Handles argument parsing and validation
   - Provides structured command responses

4. **`ConfigManager` (config.py)**: Dual-layer configuration system:
   - **Global Config**: `~/.hiollama_config_global.json` (shared model selection)
   - **Instance Configs**: `~/.hiollama_config_0.json`, `~/.hiollama_config_1.json`, etc.
   - Automatic separation of global vs instance-specific settings

5. **`UIManager` (ui.py)**: Rich-based interface with rainbow theming:
   - Rainbow color progression for chat instances (red, orange1, yellow1, green, blue, purple, magenta)
   - Multi-chat overview displays
   - Chat context visualization
   - Interactive prompts and spinners

6. **`ChatHistory` (chat_history.py)**: Instance-specific conversation management:
   - Per-chat message storage with configurable limits
   - Automatic logging to separate directories
   - Thought filtering for reasoning models
   - History display and clearing functionality

7. **`ModelInteraction` (model_interaction.py)**: Ollama API communication:
   - Native `ollama.chat()` and `ollama.list()` integration
   - Response processing with evaluation data
   - Model selection interface
   - Error handling for API failures

### Event System Components

8. **`ActionType` (session_manager.py)**: Enumeration of possible command intentions:
   - `CONTINUE`: Normal operation, no special action
   - `SWITCH`: Request to switch to a different chat
   - `TWIST`: Request to copy content to another chat
   - `QUIT`: Request to exit the application

9. **`CommandResult` (session_manager.py)**: Structured command response:
   - Contains action type and optional data payload
   - Enables clean separation between command logic and session coordination
   - Provides extensible framework for new command types

## Data Flow and Architecture Patterns

### Initialization Process

```
ChatSessionManager
├── Creates N chat instances (default 2)
├── Configures cross-references between chats
├── Displays startup header
└── Enters main event loop
```

### Event-Driven Command Flow

```
User Input → HiOllamaChat.process_input() → CommandHandler.parse_and_execute()
                                                      ↓
CommandResult ← ChatSessionManager.process_command_result() ← Returns CommandResult
     ↓
Action Taken (switch, twist, continue, or quit)
```

### Multi-Chat Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Chat 1      │    │     Chat 2      │    │     Chat N      │
│    (red)        │    │   (orange1)     │    │   (rainbow)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   ChatSessionManager   │
                    │  - Active chat index   │
                    │  - Command processing  │
                    │  - Switch coordination │
                    │  - Twist management    │
                    └─────────────────────────┘
```

### Enhanced Switch and Twist Flow

**Switch Command:**
```
/switch [N] → CommandResult(SWITCH, {target_chat: N-1}) → switch_to_chat() → Display context
```

**Twist Command:**
```
/twist [N] → Extract last response → CommandResult(TWIST, {content, target_chat}) 
          → twist_to_chat() → Switch + Display + Send as prompt
```

### Global Model Management

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat 1        │    │   Chat 2        │    │   Chat N        │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ /model cmd  │ │───▶│ │ Auto-update │ │───▶│ │ Auto-update │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
┌─────────────────────────────────────────┐
│        Global Config                    │
│  ~/.hiollama_config_global.json        │
│  { "selected_model": "qwen3:0.6B" }    │
└─────────────────────────────────────────┘
```

## Key Features Implementation

### Event-Driven Architecture

**Command Processing:**
- Commands return `CommandResult` objects with action intentions
- Session manager processes results and coordinates responses
- Clean separation between command logic and session coordination

**State Management:**
- Centralized in `ChatSessionManager`
- No inter-chat dependencies or state flags
- Each chat instance focuses solely on its conversation
- Event system handles all coordination

### Multi-Chat System

**Scalable Chat Support:**
- Configurable number of chats (defaults to 2)
- Rainbow color progression for visual distinction
- `/switch` and `/twist` commands accept optional chat numbers
- Automatic cycling behavior when no target specified

**Advanced Command Syntax:**
```bash
/switch          # Cycle to next chat
/switch 3        # Switch to chat 3
/twist           # Twist to next chat
/twist 2         # Twist to chat 2
```

### Rich Terminal Interface

**Rainbow Color System:**
- Progressive color assignment: red → orange1 → yellow1 → green → blue → purple → magenta
- Consistent theming across all UI elements
- Visual chat distinction with colored bars and indicators
- Active chat highlighting with arrow indicators (►)

## Technical Decisions and Patterns

### Event-Driven Design

```python
@dataclass
class CommandResult:
    action: ActionType
    data: Optional[Dict[str, Any]] = None

# Commands return intentions, not side effects
return CommandResult(ActionType.SWITCH, {"target_chat": 2})
```

Benefits:
- Clear command intentions
- Testable command logic
- Centralized coordination
- Easy extension for new actions

### Centralized Session Management

```python
class ChatSessionManager:
    def process_command_result(self, result: CommandResult) -> bool:
        if result.action == ActionType.SWITCH:
            # Handle switching logic
        elif result.action == ActionType.TWIST:
            # Handle twist logic
        # etc.
```

Benefits:
- Single source of truth for multi-chat coordination
- Clear control flow
- Easy debugging and maintenance
- Scalable to N chats

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

### Modern Ollama Integration

- **Native API**: Uses `ollama.chat()` and `ollama.list()`
- **Response Objects**: Proper handling of structured responses
- **Error Handling**: Comprehensive exception management
- **Evaluation Data**: Optional performance metrics display

## Extending the Architecture

### Adding New Command Actions

1. Add new `ActionType` enum value
2. Update `process_command_result()` in `ChatSessionManager`
3. Create command handler that returns appropriate `CommandResult`
4. Add help documentation

### Adding More Chat Instances

1. Update `DEFAULT_NUM_CHATS` in constants
2. Ensure rainbow color cycling handles additional chats
3. Update help text for multi-chat commands
4. Test switch/twist functionality with N chats

### Adding Inter-Chat Features

The event system makes it easy to add features like:
- Chat comparison views
- Message forwarding between chats
- Collaborative workflows
- Chat forking and merging

### Adding Global Settings

1. Extend `DEFAULT_GLOBAL_CONFIG` in `ConfigManager`
2. Update `update_global_model` pattern for new setting
3. Implement synchronization across instances
4. Add UI controls for the setting

## Performance and Scalability

### Memory Management
- History limits prevent unbounded growth
- Configuration caching reduces I/O
- Event system reduces state complexity
- Clean chat instance separation

### Event Processing
- O(1) command result processing
- Direct action dispatch
- Minimal coordination overhead

### Multi-Chat Scalability
- Rainbow color cycling supports unlimited chats
- Session manager handles N instances efficiently
- Configuration system scales with instance count
- UI adapts to any number of active chats

## Security and Error Handling

### Input Validation
- Command argument parsing with type checking
- Chat number bounds validation
- File path validation for load operations
- Configuration value bounds checking

### Error Recovery
- Default configuration fallbacks
- Graceful API failure handling
- User feedback for all error conditions
- Automatic configuration saving on exit

### Data Persistence
- Automatic configuration saving
- Separate log directories per instance
- Timestamp-based log file organization
- Error-tolerant save operations

This architecture provides a robust, scalable foundation for multi-chat Ollama interaction while maintaining clean separation of concerns and enabling future enhancements. The event-driven design provides excellent extensibility and maintainability for ongoing development.