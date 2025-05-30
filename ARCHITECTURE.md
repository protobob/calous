# HiOllama Architecture Documentation

## Overview

HiOllama is a multi-chat CLI application for interacting with Ollama models. It provides a session-based architecture supporting multiple concurrent chat instances with shared global configuration and individual chat customization.

## Core Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        HiOllama CLI                             │
├─────────────────────────────────────────────────────────────────┤
│  __main__.py (Entry Point)                                      │
│  ├── argparse for chat count                                    │
│  └── ChatSessionManager initialization                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ChatSessionManager                           │
│  ├── Manages N chat instances                                  │
│  ├── Handles switching between chats                           │
│  ├── Processes twist operations                                │
│  └── Main application loop                                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  HiOllamaChat   │ │  HiOllamaChat   │ │  HiOllamaChat   │
    │   (Instance 0)  │ │   (Instance 1)  │ │   (Instance N)  │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Component Structure

### 1. Entry Point (__main__.py)
```python
# Command line interface with configurable chat count
hiollama         # Default: 4 chats
hiollama 8       # Custom: 8 chats (max 14)
```

### 2. Session Management (session_manager.py)

The `ChatSessionManager` orchestrates all chat instances and inter-chat operations:

```
ChatSessionManager
├── chat_instances[]     # Array of HiOllamaChat instances
├── active_chat_index    # Currently active chat (0-based)
├── num_chats            # Total number of chat instances
└── Methods:
    ├── switch_to_chat(index)
    ├── twist_to_chat(content, target_index)
    ├── update_global_model(model)
    └── run() # Main application loop
```

### 3. Individual Chat Instance (app.py)

Each `HiOllamaChat` instance represents a single conversation thread:

```
HiOllamaChat
├── instance_index       # Unique identifier (0-based)
├── session_manager      # Reference to parent manager
├── selected_model       # Current AI model (global)
├── system_prompt        # Chat-specific system prompt
├── Components:
│   ├── ui               # UIManager instance
│   ├── chat_history     # ChatHistory instance
│   ├── model            # ModelInteraction instance
│   └── commands         # AdvancedCommandHandler instance
└── Configuration:    ├── verbosity
    ├── MAX_HISTORY
    └── prompts{}
```

## Component Interaction Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UIManager     │    │  ChatHistory    │    │ModelInteraction │
│                 │    │                 │    │                 │
│ • Console I/O   │    │ • Message store │    │ • Ollama API    │
│ • Formatting    │    │ • History mgmt  │    │ • Response proc │
│ • Spinners      │    │ • Logging       │    │ • Model talk    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                         ┌───────▼───────┐
                         │ HiOllamaChat  │
                         │   (Core App)  │
                         └───────┬───────┘
                                 │
                    ┌────────────▼────────────┐
                    │ AdvancedCommandHandler  │
                    │                         │
                    │ • Command parsing       │
                    │ • Registry system       │
                    │ • Argparse integration  │
                    └─────────────────────────┘
```

## Configuration Architecture

### Unified Configuration System

HiOllama uses a single JSON configuration file with global and per-chat sections:

```json
{
  "global": {
    "selected_model": "qwen3:0.6B",
    "num_chats": 4
  },
  "chats": {
    "0": {      "verbosity": true,
      "MAX_HISTORY": 20,
      "system_prompt": "...",
      "logging_enabled": true,
      "prompts": {"prompt1": "", "prompt2": "..."}
    },
    "1": { /* chat 1 config */ },
    "2": { /* chat 2 config */ }
  }
}
```

### Configuration Flow

```
ConfigManager
├── get_global_config()      # Shared across all chats
├── get_chat_config(index)   # Chat-specific settings
├── update_global_config()   # Updates all instances
└── update_chat_config()     # Updates single instance

Storage: ~/.hiollama_config_unified.json
```

## Command System Architecture

### Command Registration System

Commands use a decorator-based registration system organized by category:

```
commands/
├── __init__.py          # Module initialization & imports
├── registry.py          # @registry.register decorator
├── handler.py           # AdvancedCommandHandler
├── types.py             # CommandCategory enum
└── Command Modules:    ├── general.py       # /help, /quit, /showvars
    ├── navigation.py    # /switch, /twist
    ├── model.py         # /model, /toggle_eval
    ├── prompt.py        # /prompt, /setprompt, /system
    ├── history.py       # /history, /clear, /setmax
    └── file.py          # /load
```

### Command Processing Flow

```
User Input "/command args"
          ↓
AdvancedCommandHandler.parse_and_execute()
          ↓
Registry lookup & argparse validation
          ↓
Command function execution
          ↓
CommandResult(ActionType, data)
          ↓
ChatSessionManager.process_command_result()
          ↓
Action execution (CONTINUE, SWITCH, TWIST, QUIT)
```

## Visual Identity System

### Chat Color Coding

HiOllama uses an extended rainbow color system for visual chat identification:

```python
# Primary colors (Chats 1-7)
RAINBOW_COLORS = ["red", "orange1", "yellow1", "green", "blue", "purple", "magenta"]

# Extended colors (Chats 8-14)  
EXTENDED_RAINBOW_COLORS = [
    "red", "orange1", "yellow1", "green", "blue", "purple", "magenta",
    "dark_red", "orange3", "yellow3", "dark_green", "blue3", "purple3", "magenta3"
]
```

### UI Color Application

```
Chat 1: [red]     ► 1: System prompt preview...
Chat 2: [orange1] 2: System prompt preview...
Chat 3: [yellow1] 3: System prompt preview...
```

## Multi-Chat Operations

### Switch Operation Flow

```
/switch 3
    ↓
ChatSessionManager.switch_to_chat(2)  # 0-based indexing
    ↓
1. Update active_chat_index = 2
2. Clear screen
3. Display chat context for Chat 3
4. Show prompt for user input
```

### Twist Operation Flow

```
/twist 2
    ↓
1. Extract last AI response from current chat
2. Switch to target chat (Chat 2)
3. Display twist preview with source chat color
4. Send content as user input to target chat
5. AI responds in target chat context
```

## File Organization

```
hiollama/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point
├── app.py                   # HiOllamaChat class
├── session_manager.py       # ChatSessionManager
├── config.py                # ConfigManager
├── constants.py             # Application constants
├── types.py                 # Shared type definitions
├── ui.py                    # UIManager
├── utils.py                 # Utility functions
├── chat_history.py          # ChatHistory management
├── model_interaction.py     # Ollama API interface
└── commands/                # Command system
    ├── __init__.py
    ├── registry.py
    ├── handler.py
    ├── types.py
    └── [command modules]
```

## Data Flow Example

### Complete User Interaction Flow

```
1. User types: "Hello, how are you?"
   └── app.py: process_input()

2. Input processing:
   └── Not a command, so handle_regular_input()

3. Message handling:
   ├── chat_history.py: add_message("user", input)
   └── model_interaction.py: talk_to_model()

4. API interaction:
   ├── Build conversation history
   ├── Call ollama.chat()
   └── Receive response

5. Response processing:
   ├── model_interaction.py: process_response()
   ├── Filter thoughts if enabled
   ├── Display formatted response
   ├── chat_history.py: add_message("assistant", response)
   └── Log to file if enabled

6. UI update:
   └── ui.py: Display response with chat colors
```

## Error Handling Strategy

### Graceful Degradation

- **Config errors**: Generate default configs for missing chat instances
- **API errors**: Clear error messages with recovery suggestions  
- **Command errors**: Detailed usage information via argparse
- **File errors**: Relative path fallbacks and error reporting

### User Feedback

All errors follow consistent formatting:
```
[bold red]Error:[/bold red] Description of issue
```

This architecture provides a scalable, maintainable foundation for multi-chat AI interactions with clear separation of concerns and extensible command system.