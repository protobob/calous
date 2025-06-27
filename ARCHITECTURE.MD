## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION ENTRY                        │
│  __main__.py → ChatSessionManager → Chat instances (1-14)       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │  Core Services │ │   UI Management │ │ Command System │
        │                │ │                 │ │                │
        │ • ModelInter-  │ │ • UIManager     │ │ • Handler      │
        │   action       │ │ • Rich Console  │ │ • Registry     │
        │ • ChatHistory  │ │ • Formatters    │ │ • Services     │
        │ • ConfigMgr    │ │ • Display Logic │ │ • 38 Commands  │
        │ • Persona      │ │                 │ │  (9 categories)│
        └────────────────┘ └─────────────────┘ └────────────────┘
                │                   │                   │
        ┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
        │   Data Layer   │ │   Presentation  │ │   Extensions   │
        │                │ │                 │ │                │
        │ • Chat configs │ │ • Color schemes │ │ • Plugin Mgr   │
        │ • Global cfg   │ │ • Progress bars │ │ • User plugins │
        │ • Log files    │ │ • Message fmt   │ │ • Built-ins    │
        │ • Personas     │ │ • Context views │ │                │
        └────────────────┘ └─────────────────┘ └────────────────┘
```

## Component Responsibilities

### Core Application (`app.py`)
- **Chat Class**: Main application logic, handles user input routing
- **Single Responsibility**: Coordinate between UI, Model, Commands, and History
- **Size**: ~150 lines - appropriate for its coordination role
- **Status**: ✅ Well-structured, do not refactor

### UI Management (`ui.py`)
- **UIManager Class**: Centralized display logic and Rich console management
- **Responsibilities**: User prompts, help menus, variable displays, context views
- **Size**: ~320 lines - appropriate for comprehensive UI management
- **Status**: ✅ Well-organized, represents good centralization
- **Rule**: All new display logic should be added here, not to command formatters

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
- **Status**: ✅ Feature-complete and stable
- **Commands**: 38 commands across 9 categories
- **Rule**: Focus on bug fixes and minor enhancements only
- **NO MAJOR RESTRUCTURING**: The current system works and is familiar to users

### Session Management (`session_manager.py`)
- **ChatSessionManager**: Manages multiple chat instances, global state
- **Responsibilities**: Chat switching, global config updates, startup/shutdown
- **Status**: ✅ Well-designed for multi-chat coordination

## File Size Guidelines

### Acceptable Large Files
The following files are **intentionally large** and should not be fragmented:

1. **`model_interaction.py` (586 lines)**: Complete model interaction system
2. **`ui.py` (320+ lines)**: Comprehensive UI management
3. **`app.py` (~150 lines)**: Application coordination logic

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

To keep the codebase maintainable and consistent, commands are structured using three main components:

- **Command Functions** (`commands.py`): Register the command, handle argument parsing, and coordinate the operation. Command functions should be concise and delegate logic and formatting.
- **Service Classes** (`services.py`): Contain the business logic and data manipulation for the command. Service methods operate on the application state and perform actions like modifying history, saving files, etc.
- **Formatter Classes** (`formatters.py`): Handle all user-facing output, prompts, and confirmation dialogs. This keeps UI logic separate from business logic.

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

---

### Instructions for Handling Commands with Dual Output (Rich and Plain Text)

#### Objective:
Ensure commands like `/chat.vars` generate both Rich-formatted output for interactive use and plain text output for server-client communication, while keeping the code agnostic about whether it is running interactively or as a server.

---

### Workflow for AI Agents

#### 1. **Command Handler Responsibilities**
- **Rich Output**: Use the `UIManager` class to generate Rich-formatted output for interactive use.
- **Plain Text Output**: Generate plain text output alongside Rich output, ensuring compatibility with server-client communication.
- **No Context Awareness**: Command handlers must not include logic to determine whether the code is running interactively or as a server.

#### 2. **UIManager Responsibilities**
- **Centralized Formatting**: All Rich and plain text formatting logic must reside in the `UIManager` class.
- **Dual Output**: Methods like `show_chat_variables` must generate both Rich and plain text outputs. Rich output is printed, while plain text is returned as a string.

#### 3. **Socket Server Responsibilities**
- **Plain Text Handling**: The `listen_for_socket` method must extract plain text output from the command handler's response and send it to the client.
- **No Command-Specific Logic**: The socket server must remain agnostic about specific commands. It simply routes the plain text output to the client.

---

### Implementation Steps

#### 1. **Command Handler**
- Call the appropriate `UIManager` method (e.g., `show_chat_variables`) to generate Rich output.
- Return plain text output from the `UIManager` method as part of the `CommandResult`.

#### Example:
```python
@registry.register("chat.vars", "Display chat-specific variables", category=CommandCategory.CHAT)
def cmd_chat_vars(handler) -> CommandResult:
    service = ChatService(handler.app)
    plain_text_output = handler.app.ui.show_chat_variables()
    handler.app.ui.show_chat_variables()  # Rich output for interactive use
    return CommandResult(ActionType.CONTINUE, message=plain_text_output)
```

---

#### 2. **UIManager**
- Add methods to generate both Rich and plain text outputs.
- Rich output is printed directly, while plain text is returned as a string.

#### Example:
```python
def show_chat_variables(self) -> str:
    """Generate both Rich and plain text outputs for chat variables."""
    active_chat_index = getattr(self.app, 'active_chat_index', 0)
    verbosity = self.app.verbosity
    thinking_enabled = self.app.thinking_enabled
    temperature = self.app.temperature

    # Rich output
    chat_color = get_chat_color(active_chat_index)
    print(f"\n[bold {chat_color}]CHAT {active_chat_index + 1} VARIABLES[/bold {chat_color}]\n")
    print(f"[bold {chat_color}]|[/bold {chat_color}] {'Verbosity:':<20} [bold][{'green' if verbosity else 'red'}]{verbosity}[/{'green' if verbosity else 'red'}][/bold]")
    print(f"[bold {chat_color}]|[/bold {chat_color}] {'Thinking Mode:':<20} [bold][{'green' if thinking_enabled else 'red'}]{thinking_enabled}[/{'green' if thinking_enabled else 'red'}][/bold]")
    print(f"[bold {chat_color}]|[/bold {chat_color}] {'Temperature:':<20} [bold yellow]{temperature}[/bold yellow]")

    # Plain text output
    return (
        f"CHAT {active_chat_index + 1} VARIABLES\n"
        f"Verbosity: {verbosity}\n"
        f"Thinking Mode: {thinking_enabled}\n"
        f"Temperature: {temperature}\n"
    )
```

---

#### 3. **Socket Server**
- Extract plain text output from the `CommandResult` and send it to the client.
- Avoid embedding command-specific logic.

#### Example:
```python
if msg_type == "cmd":
    cmd_result = self.process_input(action)
    response = {"response": cmd_result.message}  # Plain text output
```

---

### Key Principles
1. **Dual Output**: Always generate both Rich and plain text outputs for commands.
2. **Centralized Formatting**: Keep all formatting logic in the `UIManager` class.
3. **Agnostic Code**: Ensure the code does not differentiate between interactive and server modes.

---

### Testing Strategy
1. **Interactive Mode**: Run the command in the CLI and verify Rich output is displayed correctly.
2. **Server Mode**: Run the command via the socket server and verify plain text output is sent to the client.

---

*Last Updated: June 27, 2025*