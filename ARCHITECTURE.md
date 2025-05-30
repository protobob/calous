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
│   ├── app.py              # HiOllamaChat class with individual chat instance management
│   ├── chat_history.py     # Instance-specific chat history management
│   ├── commands.py         # Command handlers with event-driven results
│   ├── config.py           # Unified configuration management system
│   ├── constants.py        # Shared constants and defaults
│   ├── model_interaction.py # Ollama API communication
│   ├── ui.py               # Rich-based user interface with rainbow chat colors
│   └── utils.py            # Utility functions for formatting and chat management
└── hiollama.egg-info/      # Package metadata (generated)
```

## Component Relationships

The application uses an event-driven architecture with centralized session management and a unified configuration system:

### Core Classes

1. **`ChatSessionManager` (session_manager.py)**: Central coordinator for all chat operations:
   - Manages configurable number of chat instances (default: 4)
   - Handles chat switching and twist functionality with optional chat targeting
   - Processes command results through event system
   - Orchestrates the main application loop
   - Manages startup and shutdown procedures
   - Provides global model updates across all instances

2. **`HiOllamaChat` (app.py)**: Individual chat instance:
   - Instance-specific configuration and state management
   - Processes user input and returns structured command results
   - Coordinates with other components (UI, history, model, commands)
   - Maintains reference to session manager for global operations
   - No circular references to other chat instances

3. **`CommandHandler` (commands.py)**: Event-driven command processing:
   - Returns `CommandResult` objects with action intentions
   - Supports optional chat number arguments for `/switch` and `/twist`
   - Handles argument parsing and validation
   - Provides structured command responses for all available commands

4. **`ConfigManager` (config.py)**: Unified configuration system:
   - **Single Config File**: `~/.hiollama_config_unified.json`
   - **Global Section**: Shared settings like selected model and number of chats
   - **Per-Chat Sections**: Instance-specific settings for each chat
   - Dynamic chat configuration generation for any number of instances

5. **`UIManager` (ui.py)**: Rich-based interface with rainbow theming:
   - Rainbow color progression for chat instances (red, orange1, yellow1, green, blue, purple, magenta)
   - Dynamic multi-chat overview displays
   - Chat context visualization with active chat indicators
   - Interactive prompts and spinners

6. **`ChatHistory` (chat_history.py)**: Instance-specific conversation management:
   - Per-chat message storage with configurable limits
   - Automatic logging to separate directories per chat instance
   - Thought filtering for reasoning models
   - History display and clearing functionality

7. **`ModelInteraction` (model_interaction.py)**: Ollama API communication:
   - Native `ollama.chat()` and `ollama.list()` integration
   - Response processing with evaluation data
   - Model selection interface
   - Comprehensive error handling for API failures

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
├── Loads configuration to determine number of chats
├── Creates N chat instances (configurable, default 4)
├── Sets up session manager references (no circular dependencies)
├── Displays startup header with rainbow logo
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
│     Chat 0      │    │     Chat 1      │    │     Chat N      │
│    (red)        │    │   (orange1)     │    │   (rainbow)     │
│   Technical     │    │   Creative      │    │   Generic       │
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
                    │  - Global operations   │
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

### Unified Configuration System

```
┌─────────────────────────────────────────┐
│    ~/.hiollama_config_unified.json     │
│                                         │
│  {                                      │
│    "global": {                          │
│      "selected_model": "qwen3:0.6B",   │
│      "num_chats": 4                     │
│    },                                   │
│    "chats": {                           │
│      "0": { /* Chat 0 config */ },     │
│      "1": { /* Chat 1 config */ },     │
│      "2": { /* Chat 2 config */ },     │
│      "3": { /* Chat 3 config */ }      │
│    }                                    │
│  }                                      │
└─────────────────────────────────────────┘
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Chat 0    │ │   Chat 1    │ │   Chat N    │
│ Technical   │ │ Creative    │ │ Generic     │
│ Assistant   │ │ Writing     │ │ Helper      │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Key Features Implementation

### Event-Driven Architecture

**Command Processing:**
- Commands return `CommandResult` objects with action intentions
- Session manager processes results and coordinates responses
- Clean separation between command logic and session coordination

**State Management:**
- Centralized in `ChatSessionManager`
- No inter-chat dependencies or circular references
- Each chat instance focuses solely on its conversation
- Event system handles all coordination

### Scalable Multi-Chat System

**Dynamic Chat Support:**
- Configurable number of chats via unified configuration
- Rainbow color progression for visual distinction
- Default smart prompts for different chat types
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

**Dynamic UI Elements:**
- Active chats overview showing all configured instances
- Chat-specific context displays
- Smart prompt generation based on chat type

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
- Scalable to any number of chats

### Unified Configuration Architecture

```python
# Global settings shared across all chats
"global": {
    "selected_model": "qwen3:0.6B",
    "num_chats": 4
}

# Per-chat instance settings
"chats": {
    "0": {
        "system_prompt": "Technical assistant...",
        "verbosity": True,
        "think_filtering": True,
        # ... other instance settings
    }
}
```

Benefits:
- Single configuration file for all settings
- Clear separation of global vs instance-specific settings
- Dynamic chat configuration generation
- Atomic configuration saves

### Memory-Efficient Architecture

**No Circular References:**
- Chat instances only reference session manager
- Session manager maintains list of all chats
- No inter-chat instance references
- Clean memory management and garbage collection

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

1. Update `DEFAULT_NUM_CHATS` in constants or via configuration
2. Ensure rainbow color cycling handles additional chats
3. Add appropriate default prompts for new chat types
4. Test switch/twist functionality with N chats

### Adding Inter-Chat Features

The event system makes it easy to add features like:
- Chat comparison views
- Message forwarding between chats
- Collaborative workflows
- Chat forking and merging

### Adding Global Settings

1. Extend global section in unified configuration
2. Update `ConfigManager` methods for new setting
3. Implement synchronization across instances
4. Add UI controls for the setting

## Performance and Scalability

### Memory Management
- No circular references between components
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
- Unified configuration system scales with instance count
- UI adapts to any number of active chats

### Configuration Performance
- Single file for all settings reduces I/O operations
- Atomic saves prevent configuration corruption
- Dynamic generation of missing configurations
- Efficient JSON serialization/deserialization

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
- Unified configuration saving
- Separate log directories per instance
- Timestamp-based log file organization
- Error-tolerant save operations

### Configuration Robustness
- Fallback to defaults for missing configurations
- Dynamic chat configuration generation
- Validation of configuration structure
- Recovery from corrupted configuration files

## Default Chat Configurations

The system provides intelligent default prompts for different chat types:

### Chat 0 (Technical)
- **Color**: Red
- **Purpose**: Technical assistance and debugging
- **Prompt**: Direct, technical assistant focused on coding and problem-solving

### Chat 1 (Creative)
- **Color**: Orange1
- **Purpose**: Creative writing and storytelling
- **Prompt**: Creative writing assistant for narrative development

### Chat 2+ (Generic)
- **Color**: Rainbow progression
- **Purpose**: General assistance
- **Prompt**: Helpful assistant with clear, concise responses

This architecture provides a robust, scalable foundation for multi-chat Ollama interaction while maintaining clean separation of concerns and enabling future enhancements. The unified configuration system and event-driven design provide excellent extensibility and maintainability for ongoing development.