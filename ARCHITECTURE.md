# CALOUS Architecture

CALOUS (Context Abstraction Layer Over Unix Sockets) is a daemon-based multi-channel chat system for local LLM interaction.

## System Overview

CALOUS operates as a background daemon service that provides a socket-based API for interacting with locally hosted LLMs through Ollama. The system supports 14 independent chat channels, each maintaining isolated conversation contexts and personas.

### Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CALOUS DAEMON                           │
│  Unix Socket Server (/tmp/calous.sock)                         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │ Session Manager│ │  Core Services  │ │ Command System │
        │                │ │                 │ │                │
        │ • Multi-Chat   │ │ • ModelInter-   │ │ • Registry     │
        │ • Socket Comm  │ │   action        │ │ • Handler      │
        │ • ANSI Output  │ │ • ChatHistory   │ │ • Services     │
        │ • Confirmation │ │ • ConfigManager │ │ • Formatters   │
        │ • Client State │ │ • Persona       │ │ • 54 Commands  │
        │                │ │ • UnifiedLogger │ │ • 9 Categories │
        └────────────────┘ └─────────────────┘ └────────────────┘
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │   UI Manager   │ │   Data Layer    │ │  Plugin System │
        │                │ │                 │ │                │
        │ • ANSI Output  │ │ • Config Files  │ │ • Plugin Mgr   │
        │ • Help System  │ │ • Chat History  │ │ • Base Classes │
        │ • Formatting   │ │ • Log Files     │ │ • Built-ins    │
        │ • Display      │ │ • Personas      │ │ • Function Call│
        └────────────────┘ └─────────────────┘ └────────────────┘
```

## Entry Points

### Main Entry (`__main__.py`)
- **Purpose**: Daemon startup and configuration
- **Responsibilities**:
  - Command-line argument parsing
  - Debug flag configuration
  - Fixed 14-chat initialization
  - Session manager creation and socket listening
- **Operation**: Always runs in daemon mode with Unix socket interface

## Core Components

### Session Manager (`session_manager.py`)
**Central coordination hub for multi-chat management and client communication.**

**Key Responsibilities**:
- **Multi-Chat Coordination**: Manages 14 independent chat instances
- **Socket Communication**: Unix socket server with delimiter-based streaming protocol
- **Real-time Streaming**: Efficient model response streaming to clients
- **Threading Coordination**: Separate threads for confirmation-requiring commands
- **Client State Management**: Tracks connection capabilities and confirmation support
- **Interactive Confirmations**: Thread-safe y/n confirmations with event coordination
- **Active Chat Persistence**: Saves/restores active chat across restarts

**Socket Protocol**:
- **Endpoint**: `/tmp/calous.sock`
- **Format**: Delimiter-based protocol using `\0END\0` markers
- **Message Types**: `PROMPT\0{content}\0END\0`, `CMD\0{content}\0END\0`
- **Confirmations**: `\0CONFIRM\0{message}\0{default}\0{id}\0END\0`
- **Streaming**: Content streams immediately without delimiters, terminated by `\0END\0`
- **Output**: Always sends raw content for streaming, client handles color control

### Chat Application (`app.py`)
**Individual chat instance representing one conversation channel.**

**Core Features**:
- **Isolated Context**: Each chat maintains independent conversation state
- **Configuration Management**: Per-chat settings (persona, temperature, etc.)
- **Component Integration**: Coordinates UI, Model, Commands, and History
- **Output Routing**: Delegates output to session manager for socket delivery

**Key Attributes**:
- `instance_index`: Chat channel number (0-13)
- `selected_model`: Current Ollama model
- `persona`: Multi-slot persona system
- `chat_history`: Conversation memory
- `model`: Model interaction handler
- `commands`: Command processing system

### Model Interaction (`model_interaction.py`)
**Handles all communication with Ollama models.**

**Core Functions**:
- **Model Communication**: Direct integration with Ollama API
- **Context Analysis**: Dynamic context window detection and management
- **Function Calling**: Tool/function calling support for compatible models
- **Thinking Mode**: Support for models with thinking capabilities
- **Error Handling**: Comprehensive error management with user feedback
- **Streaming**: Real-time response streaming with ANSI formatting

**Key Features**:
- **Streaming Support**: Real-time model response streaming with delimiter protocol
- **Ollama Integration**: Direct API communication with local Ollama instances
- **Context Management**: Dynamic context window detection and adaptive handling
- **Cumulative Content Handling**: Intelligent duplicate detection for streaming chunks
- **Function Calling**: Tool/function calling support for compatible models
- **Thinking Mode**: Support for models with thinking capabilities
- **Error Handling**: Comprehensive error management with user feedback
- **Debug Logging**: Structured debug information (never sent to clients)

## Command System

### Command Architecture
**Registry-based command system with decorators for registration.**

**Pattern**: `Registry → Handler → Service → Formatter`

#### Command Registry (`commands/registry.py`)
- **Decorator-based Registration**: `@registry.register()` for command definition
- **Argument Parsing**: Integrated argparse for type-safe command arguments
- **Alias Management**: System and user-defined command aliases
- **Category Organization**: Commands grouped by functional area

#### Command Handler (`commands/handler.py`)
- **Request Processing**: Parses user input and routes to appropriate commands
- **Argument Validation**: Type checking and argument parsing
- **Execution Coordination**: Delegates to service layer for business logic

#### Command Categories (9 total, 54 commands)
```
├── chat/         # Chat management (7 commands)
├── model/        # Model operations (7 commands)  
├── persona/      # Persona management (11 commands)
├── history/      # History operations (9 commands)
├── log/          # Logging operations (5 commands)
├── prompt/       # Prompt management (4 commands)
├── file/         # File operations (1 command)
├── sys/          # System commands (2 commands)
├── alias/        # Alias management (4 commands)
└── plugin/       # Plugin system (4 commands)
```

#### Service Layer Pattern
Each command category follows a consistent pattern:
- **`commands.py`**: Command registration and argument handling
- **`services.py`**: Business logic and data manipulation
- **`formatters.py`**: ANSI-formatted output generation

### Command Flow Example
```python
@registry.register("chat.switch", "Switch between chat sessions")
def cmd_chat_switch(handler, chat_number: Optional[int] = None) -> CommandResult:
    service = ChatService(handler.app)
    result = service.validate_switch(chat_number)
    
    if not result.success:
        ChatFormatter.format_switch_error(result.error_message)
        return CommandResult(ActionType.CONTINUE)
    
    return CommandResult(ActionType.SWITCH, {"target_chat": result.target_index})
```

## User Interface System

### UI Manager (`ui.py`)
**Centralized display logic and console management.**

**Core Responsibilities**:
- **Help System**: Hierarchical help menus (overview → category → command)
- **Display Formatting**: ANSI-formatted output with consistent styling
- **Status Display**: Chat headers, model information, configuration views
- **Error Presentation**: User-friendly error messages and warnings

**Output Philosophy**:
- All UI components generate ANSI-formatted content
- Socket clients receive ANSI codes directly
- Color control handled client-side via `--no-color` flags

## Data Management

### Configuration System (`config.py`)
**Hierarchical configuration with global and per-chat settings.**

**Configuration Layers**:
```
Global Config (affects all chats)
├── selected_model: Current Ollama model
├── num_ctx: Context window size  
├── temperature: Model creativity setting
├── active_chat_index: Persisted active chat
└── keep_alive: Model memory management

Per-Chat Config (chat-specific)
├── persona: Multi-slot persona system
├── prompts: Saved prompt slots (1-9)
├── verbosity: Output level
├── logging_enabled: Chat-specific logging
└── thinking_enabled: Thinking mode preference
```

**Persistence**:
- **Global**: `~/.calous/config.json`
- **Per-Chat**: Individual configuration files
- **Active Chat**: Persists across daemon restarts

### Chat History (`chat_history.py`)
**Conversation memory management with persistence.**

**Features**:
- Per-chat conversation storage
- Message truncation and management
- History export and import
- Search and filtering capabilities

### Persona System (`persona.py`)
**Multi-slot persona management for AI personality customization.**

**Structure**:
- **10 Persona Slots** (0-9): Composable personality components
- **Combined Prompts**: Automatic merging of active persona slots
- **Naming System**: Custom AI assistant names
- **Persistence**: Saved as part of chat configuration

## Logging Architecture

### Unified Logger (`unified_logger.py`)
**Multi-stream logging system with debug routing separation.**

**Log Streams**:
```
~/.calous/logs/
├── app.log          # Application events
├── debug.log        # Debug info (NEVER sent to clients!)
├── model.log        # Model interactions  
├── audit.log        # Command execution tracking
├── error.log        # Errors and exceptions
└── 2025-MM-DD.txt   # Legacy daily log (compatibility)
```

**Critical Feature**: Debug methods (`debug_socket()`, `debug_command()`, `debug_model()`) route ONLY to log files, preventing debug information leakage to socket clients.

**Capabilities**:
- Structured logging with JSON support
- Context management for grouped operations
- Level-based filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Performance optimization (debug generation skipped when disabled)

## Plugin System

### Plugin Manager (`plugins/manager.py`)
**Extensible plugin system for custom functionality.**

**Plugin Types**:
- **Function Calling**: Custom tools/functions for model use
- **Command Plugins**: New command registration
- **Hook Plugins**: Event-based system extensions

**Architecture**:
- **Base Classes**: `PluginBase`, `FunctionCallingPlugin`, `CommandPlugin`, `HookPlugin`
- **Discovery**: Automatic plugin loading from plugin directories
- **Integration**: Seamless integration with command system and model interaction

## External Client Integration

### Rust Client (`cx_rust/`)
**Reference implementation for external CALOUS interaction with streaming support.**

**Features**:
- **Real-time Streaming**: Immediate display of model responses as they arrive
- **Duplicate Prevention**: Client-side logic prevents double-printing of streamed content
- **Command Mode** (`-c`): Direct command execution with streaming support
- **Interactive Mode** (`-i`): REPL-style interface with readline support
- **Confirmation Support**: Interactive y/n prompts for destructive operations
- **Stdin Support**: Pipe data from shell commands with truncation controls
- **Tab Completion**: Auto-completion for all commands and aliases
- **Color Control**: `--no-color` flag for ANSI stripping
- **History**: Persistent command history and configuration

**Socket Communication**:
- **Delimiter Protocol**: Efficient streaming using `\0END\0` markers
- **Streaming Logic**: Immediate content display with end-marker detection  
- **Confirmation Handling**: Interactive prompts with response coordination
- **Error Handling**: Proper connection management and error display
- **Content Processing**: Escape sequence handling and output optimization

## Data Flow Patterns

### Client Request Flow
```
External Client → Unix Socket → Delimiter Parser → Session Manager
    ↓
Command Handler → Registry Lookup → Service Execution (threaded if confirmations needed)
    ↓
Model Streaming → Real-time Content → Delimiter Protocol → Socket → Client
```

### Streaming Response Flow
```
ModelInteraction → Ollama API → Stream Chunks → Content Processing
    ↓
Duplicate Detection → Session Manager → Socket Protocol → Real-time Client Display
    ↓
End Marker → Client Processing Complete → Ready for Next Request
```

### Multi-Channel Communication
```
Source Chat → /twist command → ModelInteraction.generate()
    ↓
Response Capture → Target Chat Input → Independent Processing
    ↓
Both chats maintain separate histories and contexts
```

### Debug Information Flow
```
Application Components → unified_logger.debug_*() → Log Files ONLY
    ↓
Socket clients receive CLEAN output (no debug contamination)
```

## Security Model

### Access Control
- **Unix Socket Permissions**: OS-level user permissions control access
- **Local Only**: No network exposure, local machine access only
- **Process Isolation**: Socket connections run in application context
- **Input Validation**: Command parsing and argument validation

### Data Privacy
- **Local Storage**: All data remains on user's machine
- **No Telemetry**: No external data transmission
- **Optional Logging**: User-controlled conversation logging
- **Direct Model Communication**: Direct to local Ollama instance only

## Key Design Decisions

## Key Design Decisions

### Why Delimiter-Based Protocol?
- **Streaming Efficiency**: Immediate content delivery without JSON parsing overhead
- **Real-time Response**: Content appears as model generates it, not after completion
- **Simple Implementation**: Clear message boundaries with `\0END\0` markers
- **Client Flexibility**: Each client can optimize display and processing independently

### Why Threading for Confirmations?
- **Deadlock Prevention**: Socket handler remains free to receive confirmation responses
- **Interactive Experience**: Immediate confirmation prompts without blocking
- **Event Coordination**: Thread-safe synchronization between command execution and user input
- **Scalable Pattern**: Extensible to any command requiring user interaction

### Why Unix Sockets?
- **Performance**: Lower overhead than HTTP for local communication
- **Security**: File system permissions provide access control
- **Simplicity**: No authentication, CORS, or web server complexity
- **Local-First**: Designed for same-machine integration
- **Streaming Support**: Efficient real-time data transmission

### Why Single ANSI Output?
- **Consistency**: Daemon generates raw content, client controls formatting
- **Streaming Compatibility**: No server-side processing delays during streaming
- **Client Control**: Each client controls color preferences independently
- **Performance**: Zero server-side format negotiation or processing overhead

### Why 14 Fixed Channels?
- **Predictability**: Consistent interface across all deployments
- **Resource Management**: Bounded memory and state complexity
- **UI Design**: Manageable number for user interfaces
- **Simplicity**: No dynamic management complexity

## Development Guidelines

### Adding New Commands
1. **Choose Category**: Place in appropriate `commands/category/` directory
2. **Define Service**: Implement business logic in `services.py`
3. **Create Formatter**: Handle ANSI output in `formatters.py`
4. **Register Command**: Use `@registry.register()` decorator
5. **Update Help**: Ensure help system integration

### Common Patterns
- **Service Methods**: Return result objects with success/error states
- **Formatters**: Generate ANSI-formatted output, handle all display logic
- **Error Handling**: User-friendly error messages via formatters
- **Debug Info**: Use `unified_logger.debug_*()` methods (never client output)
- **Constants**: Use values from `constants.py` for all configuration

### Integration Points
- **Socket Communication**: All client interaction via session manager
- **Multi-Chat**: Respect channel isolation, use `/twist` for cross-channel data
- **Plugin Integration**: Leverage plugin system for extensibility
- **Configuration**: Use ConfigManager for all persistent settings
- **Logging**: Route appropriate information to correct log streams
