## Architecture Overview

### CLI Mode Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    CLI MODE FLOW                                │
│  __main__.py → ChatSessionManager → Interactive Terminal Loop   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │  Core Services │ │   UI Management │ │ Command System │
        │                │ │                 │ │                │
        │ • ModelInter-  │ │ • UIManager     │ │ • Handler      │
        │   action       │ │ • Rich Console  │ │ • Registry     │
        │ • ChatHistory  │ │ • Rich Output   │ │ • Services     │
        │ • ConfigManager│ │ • Color/Format  │ │ • 56 Commands  │
        │ • Persona      │ │ • Progress Bars │ │  (9 categories)│
        │ • UnifiedLogger│ │ • Help Systems  │ │ • /twist pipe  │
        │ • Utils        │ │ • Interactive   │ │ • Confirmations│
        └────────────────┘ └─────────────────┘ └────────────────┘
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │   Data Layer   │ │   Presentation  │ │   Extensions   │
        │                │ │                 │ │                │
        │ • Chat configs │ │ • Color schemes │ │ • Plugin Mgr   │
        │ • Global cfg   │ │ • Rich markup   │ │ • User plugins │
        │ • Log files    │ │ • Message fmt   │ │ • Built-ins    │
        │ • Personas     │ │ • Context views │ │ • Direct calls │
        │ • File I/O     │ │ • Prompts/Input │ │                │
        └────────────────┘ └─────────────────┘ └────────────────┘
```

### Socket Mode Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                   SOCKET MODE FLOW                              │
│  __main__.py --socket → Chat.listen_for_socket() → Unix Socket  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │  Core Services │ │  Output Capture │ │ Command System │
        │                │ │                 │ │                │
        │ • ModelInter-  │ │ • Stdout Redir  │ │ • Handler      │
        │   action       │ │ • ANSI Stripper │ │ • Registry     │
        │ • ChatHistory  │ │ • Buffer Mgmt   │ │ • Services     │
        │ • ConfigManager│ │ • Format Clean  │ │ • 56 Commands  │
        │ • Persona      │ │ • JSON Response │ │  (9 categories)│
        │ • UnifiedLogger│ │ • Error Capture │ │ • /twist pipe  │
        │ • Utils        │ │ • Non-interact  │ │ • Auto-confirm │
        └────────────────┘ └─────────────────┘ └────────────────┘
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │   Data Layer   │ │ Socket Interface│ │   Extensions   │
        │                │ │                 │ │                │
        │ • Chat configs │ │ • Unix Socket   │ │ • Plugin Mgr   │
        │ • Global cfg   │ │ • JSON Protocol │ │ • User plugins │
        │ • Log files    │ │ • Plain Text    │ │ • Built-ins    │
        │ • Personas     │ │ • Error Msgs    │ │ • External APIs│
        │ • File I/O     │ │ • No Rich Tags  │ │ • Client Apps  │
        └────────────────┘ └─────────────────┘ └────────────────┘
```

## Component Responsibilities

### Core Application (`app.py`)
- **Chat Class**: Main application logic, handles user input routing
- **Socket Server**: Implements Unix socket interface for external clients (cx-rust tool)
- **Dual Output System**: Captures Rich output for CLI, strips ANSI for socket clients
- **Single Responsibility**: Coordinate between UI, Model, Commands, and History
- **Size**: ~258 lines - includes socket handling and output capture
- **Status**: ✅ Well-structured, do not refactor

### Socket Interface Architecture
- **Unix Socket**: `/tmp/calous.sock` enables external client communication
- **Output Capture**: Global system captures all Rich console output
- **Format Stripping**: ANSI/Rich tags automatically removed for socket responses
- **Dual Format Support**: Same commands work in both CLI and socket modes
- **Protocol**: JSON-based message protocol for universal client compatibility
- **External Integration**: Any application can connect and interact with CALOUS

### UI Management (`ui.py`)
- **UIManager Class**: Centralized display logic and Rich console management
- **Dual-Format Methods**: Methods like `show_available_models()` return both Rich and plain text
- **Responsibilities**: User prompts, help menus, variable displays, context views
- **Size**: ~950+ lines - comprehensive UI management
- **Status**: ✅ Well-organized, represents good centralization
- **Rule**: All new display logic should be added here, with dual-format support

### Model Interaction (`model_interaction.py`)
- **ModelInteraction Class**: All Ollama model communication
- **Size**: 586 lines - large but logically cohesive
- **Responsibilities**:
  - Model metadata and context analysis (~150 lines)
  - Core model communication (~200 lines)
  - Function/tool calling (~80 lines)
  - Response processing & error handling (~100 lines)
  - Model selection UI (~50 lines)
- **Status**: ✅ Large but cohesive - **DO NOT FRAGMENT**
- **Rationale**: This file represents a complete, working model interaction system. Splitting it would create artificial boundaries and complicate the logic flow.

### Command System (`commands/`)
- **Current Architecture**: Registry → Handler → Service → Formatter pattern
- **Directory Structure**: Commands organized by category (chat/, file/, history/, etc.)
- **Status**: ✅ Feature-complete and stable
- **Commands**: 56 commands across 9 categories
- **Formatter Distribution**: 
  - Central base formatter (`commands/formatters.py`) with CommandFormatter base class
  - Specialized formatters in each category directory (`chat/formatters.py`, `file/formatters.py`, etc.)
- **Output Responsibility**: Formatters handle Rich formatting, UIManager handles dual-format output
- **Rule**: Focus on bug fixes and minor enhancements only
- **NO MAJOR RESTRUCTURING**: The current system works and is familiar to users

### Session Management (`session_manager.py`)
- **ChatSessionManager**: Manages multiple chat instances, global state
- **Responsibilities**: Chat switching, global config updates, startup/shutdown
- **Status**: ✅ Well-designed for multi-chat coordination

### External Rust Client (`cx_rust/`)
- **Rust Client**: Lightweight command-line tool (`cx`) for external interaction
- **Socket Communication**: Connects to CALOUS via Unix socket interface
- **Features**: 
  - Command mode (`-c`): Send commands directly
  - Interactive mode (`-i`): REPL-like interface
  - Stdin support: Pipe data from shell commands
  - Debug output: Enhanced logging with `-d` flag
- **Status**: ✅ Fully functional, provides seamless external integration
- **Architecture Role**: Reference implementation and primary external client

### Socket API for External Integration
- **Universal Interface**: Any application can connect to `/tmp/calous.sock`
- **JSON Protocol**: Standardized message format for interoperability
- **Potential Clients**: 
  - IDE extensions (VS Code, Neovim, Emacs)
  - Browser extensions for web development
  - Desktop applications and GUI frontends
  - Shell scripts and automation tools
  - Other programming language bindings
- **Future Expansion**: Socket interface designed for broad ecosystem integration

## Multi-Channel Architecture

### Channel Isolation
- **Independent Context**: Each chat channel (1-14) maintains its own isolated conversation context
- **No Shared Memory**: Channels do not run concurrently or share memory between sessions
- **Context Updates**: Channel context is updated only on invocation, preserving isolation
- **Persona Management**: Each channel can have its own distinct persona configuration

### The /twist Command
- **Purpose**: The only mechanism for piping output from one channel to another
- **Cross-Channel Communication**: Enables controlled data flow between isolated chat instances  
- **Architecture Role**: Serves as the single bridge in an otherwise completely isolated multi-channel system
- **Implementation**: Captures output from source channel and feeds it as input to target channel

### Session Management
- **ChatSessionManager**: Coordinates multiple chat instances and global state
- **Channel Switching**: Allows seamless switching between chat sessions
- **State Preservation**: Each channel retains its own history, configuration, and persona
- **Global Configuration**: Some settings (like logging) apply across all channels

## File Size Guidelines

### Acceptable Large Files
The following files are **intentionally large** and should not be fragmented:

1. **`model_interaction.py` (586 lines)**: Complete model interaction system
2. **`ui.py` (950+ lines)**: Comprehensive UI management
3. **`app.py` (~258 lines)**: Application coordination logic with socket handling

### When to Consider Splitting
Only split files if they meet **ALL** of these criteria:
- File exceeds 800+ lines
- Contains completely unrelated functionality
- Has clear, natural separation boundaries
- Splitting would improve, not complicate, the codebase

## Decision Framework

### Before Making Changes
Ask these questions:

1. **Is this fixing a bug or adding a feature?** ✅ Proceed
2. **Is this "cleaning up" or "organizing" code?** ⚠️ Proceed with extreme caution
3. **Will this make the code easier to understand?** Must be objectively yes
4. **Will this require changes to multiple files?** ⚠️ High risk of regression
5. **Is the current code actually broken?** If no, consider leaving it alone

### Refactoring Red Flags
**STOP** if someone suggests:
- "Separating concerns" when concerns are already logically separated
- Moving UI logic to command formatters (wrong direction)
- Breaking up `model_interaction.py` (it's cohesive as-is)
- Major command system restructuring
- Abstract base classes without clear benefit
- Service layers that just proxy to existing methods

## Architectural Evolution Guidelines

### What Should Change
- **Bug fixes**: Always welcome
- **New features**: Add thoughtfully without breaking existing patterns
- **Performance improvements**: Data shows actual performance issues
- **UI enhancements**: Add to `UIManager`, not formatters

### What Should Not Change
- **Working core systems**: Model interaction, command handling, session management
- **File organization**: Current structure is logical and familiar
- **Established patterns**: Unless they're demonstrably broken

## Plugin System

### Current State
- Plugin manager with builtin and user plugin support
- Extensible command system
- **Status**: ✅ Functional, allows for extensions without core changes

### Guidelines
- New functionality should consider plugins first
- Core system should remain stable
- Plugins allow experimentation without affecting base system

## Testing Strategy

### Current Coverage
- Integration tests for startup and basic functionality
- Command testing framework
- Manual testing documentation

### Principles
- Tests should verify behavior, not implementation details
- Focus on user-facing functionality
- Avoid brittle tests that break on refactoring

## Command Implementation Pattern

**IMPORTANT NOTE**: The pattern described below conflicts with the AI_README.md guidelines. According to AI_README.md, "Formatting logic lives ONLY in UIManager" and output should be routed through UIManager only. However, the current implementation uses specialized formatters within command modules.

To keep the codebase maintainable and consistent, commands are structured using three main components:

- **Command Functions** (`commands/*/commands.py`): Register the command, handle argument parsing, and coordinate the operation. Command functions should be concise and delegate logic and formatting.
- **Service Classes** (`commands/*/services.py`): Contain the business logic and data manipulation for the command. Service methods operate on the application state and perform actions like modifying history, saving files, etc.
- **Formatter Classes** (`commands/*/formatters.py`): Handle all user-facing output, prompts, and confirmation dialogs. This keeps UI logic separate from business logic.

**Current Reality vs. AI Guidelines**:
- **Current Pattern**: Commands → Formatters (Rich output) → Socket output capture (ANSI stripping)
- **AI_README Rule**: Commands → UIManager (dual-format output)
- **Socket Compatibility**: Achieved through global output capture and ANSI stripping in `app.py`

**Example Pattern:**

```python
@registry.register("history.purge", "Purge the most recent N entries from current chat history", category=CommandCategory.HISTORY)
def cmd_history_purge(handler, num_entries: int) -> CommandResult:
    service = HistoryService(handler.app)
    chat_info = service.get_chat_info()
    n = min(num_entries, len(handler.app.chat_history.history))
    if n == 0:
        HistoryFormatter.format_no_messages_to_purge()
        return CommandResult(ActionType.CONTINUE)
    HistoryFormatter.format_purge_warning(chat_info, n)
    if not HistoryFormatter.confirm_purge():
        return CommandResult(ActionType.CONTINUE)
    purged = service.purge_history(n)
    HistoryFormatter.format_purge_success(purged)
    return CommandResult(ActionType.CONTINUE)
```

**Why this pattern?**
- Keeps command files readable and focused on intent
- Makes it easy to update UI or logic independently
- Encourages code reuse and easier testing

**When in doubt:** Follow this pattern for new commands, and document any intentional deviations.

## Operational Mode Comparison

### CLI Mode Flow
1. **Startup**: `__main__.py` → `ChatSessionManager` → Interactive session with multiple chat instances
2. **User Interaction**: Direct terminal input/output with Rich formatting
3. **Output**: Full Rich markup with colors, progress bars, interactive prompts
4. **Command Processing**: Commands processed through formatters with Rich output
5. **Session Management**: Full multi-chat switching, history navigation
6. **User Experience**: Interactive prompts, confirmations, visual feedback

### Socket Mode Flow  
1. **Startup**: `__main__.py --socket` → Single chat instance → `listen_for_socket()`
2. **Client Connection**: External clients connect via Unix socket (`/tmp/calous.sock`)
3. **Output Capture**: All Rich output redirected to buffer, ANSI tags stripped
4. **Command Processing**: Same commands, but output cleaned for plain text
5. **Response**: JSON-formatted responses sent back to client
6. **User Experience**: Non-interactive, auto-confirmations, scriptable

### Key Architectural Differences

| Aspect | CLI Mode | Socket Mode |
|--------|----------|-------------|
| **Entry Point** | `ChatSessionManager.run()` | `Chat.listen_for_socket()` |
| **Output Handling** | Direct Rich console | Captured + ANSI stripped |
| **User Input** | Interactive prompts | JSON message protocol |
| **Multi-Chat** | Full session switching | Single chat instance |
| **Confirmations** | Interactive prompts | Auto-confirm (`non_interactive=True`) |
| **External Access** | Terminal only | Unix socket + Any client |
| **Response Format** | Rich markup | Plain text JSON |
| **Use Case** | Interactive use | Automation/scripting/integration |

## Data Flow Diagrams

### CLI Mode: User Input → Response Flow
```
User Input → UIManager.prompt() → CommandHandler.process() → Service.execute() 
    ↓
Formatter.format() → Rich Console → Terminal Display
    ↓
UnifiedLogger.log() → Daily Log File
```

### Socket Mode: Client → Server Flow
```
External Client → Unix Socket → JSON Parser → CommandHandler.process()
    ↓
Service.execute() → Formatter.format() → Output Capture Buffer
    ↓
ANSI Strip → JSON Response → Socket → External Client
    ↓
UnifiedLogger.log() → Daily Log File
```

### Multi-Channel Communication via /twist
```
Source Channel → /twist command → ModelInteraction.generate() 
    ↓
Capture Response → Target Channel Input → Continue Processing
    ↓
Both channels maintain separate histories
```

## Configuration & State Management

### Configuration Hierarchy
```
┌─────────────────────────────────────────────────────────────────┐
│                     CONFIGURATION LAYERS                        │
└─────────────────────────────────────────────────────────────────┘
    Global Config (affects all chats)
    ├── selected_model: Current Ollama model
    ├── num_ctx: Context window size  
    ├── temperature: Model creativity setting
    └── logging_enabled: Unified logging state
    
    Per-Chat Config (chat-specific)
    ├── system_prompt: Custom system instructions
    ├── saved_prompts: Quick-access prompt slots (1-9)
    ├── persona_slots: Persona components (0-9)
    └── chat_history: Conversation memory
```

### State Persistence
- **Global Settings**: Saved to `~/.calous/config.json`
- **Chat Configurations**: Saved per chat instance 
- **Unified Logs**: Daily files in `~/.calous/logs/YYYY-MM-DD.txt`
- **Model Context**: Maintained in-memory per chat session
- **Plugin State**: Managed by PluginManager, loaded at startup

## Development Guidelines & Common Patterns

### Adding a New Command
1. **Create command structure**: `commands/category/commands.py`
2. **Add service logic**: `commands/category/services.py`
3. **Create formatter**: `commands/category/formatters.py`
4. **Register command**: Use `@registry.register()` decorator
5. **Test both modes**: Ensure CLI and socket compatibility

### Common Pitfalls to Avoid
- **Rich formatting in services**: Keep business logic separate from display
- **Blocking socket operations**: Socket mode should be non-interactive
- **Cross-chat state sharing**: Maintain channel isolation
- **Direct print() calls**: Use formatters for consistent output
- **Hardcoded paths**: Use constants from `constants.py`

### Error Handling Patterns
- **Service Layer**: Return result objects with success/error states
- **Formatter Layer**: Display user-friendly error messages
- **Socket Mode**: Convert errors to JSON responses
- **Logging**: All errors logged to unified log system

### Performance Considerations
- **Model Loading**: Lazy loading, shared across chats
- **History Management**: Efficient in-memory storage with persistence
- **Socket Connections**: Single-threaded, one client at a time
- **Plugin System**: Loaded once at startup, cached function schemas

## Key Architectural Decisions & Rationale

### Why Unix Sockets vs HTTP API?
- **Performance**: Lower overhead for local communication
- **Security**: File system permissions control access
- **Simplicity**: No need for authentication, CORS, or web server complexity
- **Local-First**: Designed for same-machine integration, not web services

### Why Output Capture vs Dual Formatters?
- **Backward Compatibility**: Existing Rich formatters work unchanged
- **Maintainability**: Single formatter codebase, automatic socket compatibility
- **Consistency**: Same visual output in CLI translates to clean text in socket mode
- **Development Speed**: No need to maintain separate output paths

### Why Multi-Chat Support in Socket Mode?
- **Feature Parity**: Socket mode provides the same multi-chat capabilities as CLI mode
- **Session Management**: The `ChatSessionManager` handles multiple chat sessions seamlessly
- **Command Support**: All chat management commands (`/chat.switch`, `/chat.add`, `/chat.remove`) work in socket mode
- **State Synchronization**: Commands are processed through the same session manager as CLI mode
- **Consistent API**: External clients can manage multiple chats using the same command structure

**Implementation**: Socket server processes commands through `session_manager.process_command_result()` which handles `ActionType.SWITCH` and other chat actions identically to CLI mode.

### Why Registry Pattern for Commands?
- **Discoverability**: Automatic command enumeration for help systems
- **Extensibility**: Plugins can register new commands seamlessly
- **Type Safety**: Centralized argument parsing and validation
- **Debugging**: Clear command execution tracing

## Security & Access Control

### Socket Security Model
- **File Permissions**: Unix socket inherits filesystem permissions
- **Local Only**: No network exposure, local machine access only
- **Process Isolation**: Each socket connection runs in application context
- **No Authentication**: Relies on OS-level user permissions

### Input Validation
- **Command Parsing**: Strict argument validation via registry
- **File Operations**: Path traversal protection, size limits
- **Model Inputs**: Content filtering through Ollama's safety measures
- **JSON Protocol**: Schema validation for socket messages

### Data Privacy
- **Local Storage**: All data remains on user's machine
- **No Telemetry**: No external data transmission
- **Optional Logging**: User-controlled conversation logging
- **Model Communication**: Direct to local Ollama instance only