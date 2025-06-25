Hi, Ollama! Architecture Vision

Executive Summary

Hi, Ollama! is a multi-chat CLI interface for Ollama language models. This document establishes the architectural vision to prevent conflicting refactoring approaches and maintain consistency as the codebase evolves.

🧠 Copilot / AI Agent Compliance Section (Read First!)

❗ Hard Rules for AI Agents

These rules apply to GitHub Copilot, GPT, and any other automated AI coding assistant used with this repository.

Do not suggest or generate changes unless you have seen the actual source code being referenced.

Do not suggest architectural restructuring or code movement based on best practices or assumptions.

DO NOT REFACTOR the following files:

model_interaction.py (586 lines): Large but cohesive

ui.py (320+ lines): All display logic belongs here

app.py (~150 lines): Entry point and coordination logic

Do not move UI logic into command formatters. It belongs in UIManager only.

Do not break or alter the Command System architecture. It is feature-complete.

Do not suggest abstract base classes, microservice-style fragmentation, or 'separation of concerns' where the code is already cleanly structured.

Do not assume that the human user will be making code changes. Suggestions should be framed assuming the AI is responsible for implementation and modification unless explicitly stated otherwise.

☑️ Safe Suggestions

You may suggest bug fixes.

You may suggest small enhancements to commands or UI, but must localize changes to relevant files.

You may recommend new commands using the existing pattern (Registry → Service → Formatter).

You may propose plugin-based extensions that do not affect core architecture.

✅ Enforcement

Violating these rules will cause your suggestions to be rejected.
If you're unsure whether a change violates a rule, ASK FIRST.

Core Principles

1. Pragmatic Simplicity Over Academic Purity

Favor working solutions over theoretical perfection

Monolithic cohesive code is preferable to hyper-fragmented architecture

If a file is large but logically coherent, leave it alone

Avoid refactoring for refactoring's sake

2. UI Centralization

All display/formatting logic should be concentrated in the UIManager class

Avoid scattering UI logic across multiple command formatter files

Rich console formatting should be managed centrally, not distributed

3. Command System Stability

The current command architecture is feature-complete and stable

Do not suggest major architectural changes to the command system

Focus on bug fixes and minor enhancements, not restructuring

4. Configuration Management

Global settings (model, context window) managed via ConfigManager

Chat-specific settings remain in individual Chat instances

Persona system replaces old system_prompt approach

5. File Path Consistency

All file paths, such as those for saved histories or configurations, should follow centralized patterns defined in constants.py.

Do not hardcode file paths in service, command, or formatter logic — always use the constant values.

Architecture Overview

[unchanged – diagram and rest of content continues here...]



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

*Last Updated: June 9, 2025*  
*Version: 1.0*  
*Status: Living Document*