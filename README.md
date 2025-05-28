# Hi, Ollama!

Version 0.1.11.dev -- May 28th, 2025

A friendly command-line interface for interacting with Ollama language models with multi-chat support.

## Overview

Hi, Ollama! is a Python-based tool that provides an intuitive terminal interface for communicating with locally-run Ollama models. It features a scalable multi-chat system, event-driven architecture, rich formatting, and a comprehensive set of commands for managing prompts, chat history, and configuration.

## Key Features

- **Multi-Chat System**: Run multiple simultaneous chat instances with independent histories (defaults to 2)
- **Enhanced Chat Switching**: Switch between chats with `/switch` or `/switch NUMBER` commands
- **Advanced Twist Functionality**: Copy AI responses between chats with `/twist` or `/twist NUMBER`
- **Global Model Selection**: Model changes apply to all chat instances simultaneously
- **Instance-Specific Configurations**: Each chat maintains its own settings and history
- **Rainbow Terminal UI**: Color-coded chats with rainbow progression (red, orange, yellow, green, blue, purple, magenta)
- **Event-Driven Architecture**: Clean command processing with structured results
- **Persistent Storage**: Configurations and logs saved per chat instance
- **Scalable Design**: Ready for N-chat expansion beyond the default 2-chat setup

## Installation

### Prerequisites

- Python 3.6+
- [Ollama](https://ollama.ai/) installed and running locally
- Required Python packages:
  - `ollama`
  - `rich`

### Setup

#### Option 1: Run as a Module
```bash
# Clone the repository
git clone https://github.com/protobob/hiollama.git

# Install dependencies
cd hiollama
pip install ollama rich

# Run the application
python -m hiollama
```

#### Option 2: Install as a Package
```bash
# Clone the repository
git clone https://github.com/protobob/hiollama.git
cd hiollama

# Install in development mode
pip install -e .

# Now you can run from anywhere
hiollama
```

## Usage

Run the program from your terminal:
```bash
python -m hiollama
```

The application starts with a rainbow header and displays an overview of all active chats. Chat 1 (red) begins active. Use `/switch` to cycle between chats or `/switch NUMBER` to jump to a specific chat.

### Example Interaction
```
HIOLLAMA!
v.0.1.11.dev

ACTIVE CHATS: (/switch to change)
► 1: You are a direct, technical assistant. Don't be enthusiastic...
  2: You are a creative writing assistant who helps with storytelling...

CHAT 1: SUMMARY
| YOU: Tell me about quantum computing
| LLM: Quantum computing uses quantum bits (qubits) to perform calculations...

| CH:2/20 (/help for help)
| YOU: /switch 2

ACTIVE CHATS: (/switch to change)
  1: You are a direct, technical assistant. Don't be enthusiastic...
► 2: You are a creative writing assistant who helps with storytelling...

| CH:0/20 (/help for help)
| YOU: Write a short story about time travel
```

## Commands

### General Commands
- `/help` - Show the comprehensive help menu
- `/quit` - Exit the program and save all configurations
- `/showvars` - Display current system variables for the active chat

#### Multi-Chat Commands
- `/switch` - Cycle to the next chat
- `/switch NUMBER` - Switch to a specific chat (e.g., `/switch 2`)
- `/twist` - Copy the last AI response to the next chat and switch to it
- `/twist NUMBER` - Copy the last AI response to a specific chat (e.g., `/twist 1`)

### Model Commands
- `/model` - Select a different model (applies globally to all chats)
- `/toggle_eval` - Toggle evaluation data display after responses
- `/toggle_think` - Toggle filtering of LLM "thoughts" (for reasoning models)

### Prompt Commands
- `/setprompt NUMBER PROMPT_TEXT` - Set a saved prompt (1-10)
  - Example: `/setprompt 1 Explain this code step by step.`
- `/prompt NUMBER` - Use a saved prompt (1-10)
  - Example: `/prompt 1` 
- `/showprompt NUMBER|all` - Display saved prompts
  - Example: `/showprompt 1` or `/showprompt all`
- `/system NEW_SYSTEM_PROMPT` - Change the system prompt for the active chat
  - Example: `/system You are a creative writing assistant.`

### Chat History Commands
- `/history` - Display the current chat history
- `/clear` - Clear the current chat history (with confirmation)
- `/setmax NUMBER` - Set the maximum chat history (even number between 2-100)
  - Example: `/setmax 20`
- `/toggle_log` - Toggle logging of chat history

### File Commands
- `/load FILENAME PROMPT` - Load a file as a prompt with instructions
  - Example: `/load example.py Analyze this code for bugs.`

## Multi-Chat System

The application's scalable multi-chat system allows for:

### Enhanced Chat Management
- **Multiple Instances**: Defaults to 2 chats, easily configurable for more
- **Rainbow Color Coding**: Each chat has a distinct color (red, orange, yellow, green, blue, purple, magenta)
- **Active Chat Indicators**: Visual indicators (►) show which chat is currently active
- **Independent Operation**: Each chat maintains completely separate history, settings, and logs

### Advanced Chat Interaction
- **Flexible Switching**: 
  - `/switch` cycles to the next chat
  - `/switch 3` jumps directly to chat 3
- **Enhanced Twisting**: 
  - `/twist` copies response to the next chat
  - `/twist 2` copies response to chat 2 specifically
- **Global Coordination**: Model selection applies to all chats simultaneously

### Use Cases
- **Comparative Analysis**: Test different approaches to the same problem across multiple chats
- **Specialized Workflows**: Dedicate chats to specific tasks (coding, writing, analysis, brainstorming)
- **Context Switching**: Maintain separate conversations for different topics or projects
- **Creative Iteration**: Use twist functionality to build on ideas across different chat contexts
- **Multi-Perspective Discussions**: Explore topics from different angles using different system prompts

## Configuration

The application uses a dual-layer configuration system:

- **Global Config**: `~/.hiollama_config_global.json` (shared model selection)
- **Chat Instance Configs**: `~/.hiollama_config_0.json`, `~/.hiollama_config_1.json`, etc.

### Global Settings (Shared Across All Chats)
- Selected model

### Per-Chat Settings (Independent)
- System prompt
- Verbosity settings  
- Think filtering toggle
- Maximum history size
- Saved prompts (1-10)
- Logging preferences

### Default System Prompt
```
You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code.
```

## Logs

Chat logs are organized by instance with rainbow color coordination:
- **Chat 1 (Red)**: `~/hiollama_logs/chat_0/YYYY-MM-DD.txt`
- **Chat 2 (Orange)**: `~/hiollama_logs/chat_1/YYYY-MM-DD.txt`
- **Chat N**: `~/hiollama_logs/chat_N-1/YYYY-MM-DD.txt`

Each log includes timestamps and is saved automatically when logging is enabled.

## Project Structure

The project uses an event-driven architecture for scalability and maintainability:

```
hiollama/
├── __init__.py          - Package initialization
├── __main__.py          - Entry point (creates ChatSessionManager)
├── session_manager.py   - Central session coordination and multi-chat orchestration
├── app.py               - HiOllamaChat class with simplified, focused responsibilities
├── chat_history.py      - Instance-specific chat history management
├── commands.py          - Event-driven command handlers with structured results
├── config.py            - Dual-layer configuration management (global + per-instance)
├── constants.py         - Shared constants, rainbow colors, and defaults
├── model_interaction.py - Ollama API communication
├── ui.py                - Rich-based user interface with rainbow theming
└── utils.py             - Utility functions for formatting and chat management
```

## Technical Features

### Event-Driven Architecture
- Commands return structured `CommandResult` objects
- Centralized session management through `ChatSessionManager`
- Clean separation between command logic and multi-chat coordination
- Eliminates complex state flag management

### Enhanced Multi-Chat Support
- Configurable number of chat instances (defaults to 2)
- Rainbow color progression for unlimited chat visual distinction
- Backward-compatible command syntax with optional arguments
- Scalable architecture ready for N-chat expansion

### Modern Ollama Integration
- Uses native `ollama.list()` function for model enumeration
- Leverages `ollama.chat()` for streamlined communication
- Proper error handling for API interactions
- Structured response processing

### Rich Terminal UI
- Rainbow color-coded chat instances with consistent theming
- Active chat overview with system prompt previews
- Interactive spinners during model inference
- Formatted help menus and variable displays
- Chat context visualization with last message summaries

### Advanced State Management
- Centralized session coordination
- Event-driven command processing
- Clean chat instance separation
- Global configuration synchronization

## Contributing

Contributions are welcome! The event-driven architecture makes it easy to extend functionality:

1. Fork the repository
2. Create a feature branch
3. Follow the existing event-driven patterns
4. Add appropriate `CommandResult` types for new actions
5. Update the `ChatSessionManager` to handle new event types
6. Add appropriate error handling and documentation
7. Submit a pull request

## Future Enhancements

The current architecture is designed to support:
- **N-Chat Expansion**: Easy scaling beyond 2 chats
- **Chat Comparison Views**: Side-by-side chat displays
- **Advanced Workflow Features**: Chat forking, merging, and collaboration
- **Cross-Chat Search**: Search across all chat histories
- **Chat Templates**: Predefined chat configurations for specific use cases

## License

MIT License

Copyright (c) 2025 Ollie McDaniel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.