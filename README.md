# Hi, Ollama!

Version 0.1.4.dev -- May 27th, 2025

A friendly dual-chat command-line interface for interacting with Ollama language models.

## Overview

Hi, Ollama! is a Python-based tool that provides an intuitive terminal interface for communicating with locally-run Ollama models. It features a unique dual-chat system, modular architecture, rich formatting, and a comprehensive set of commands for managing prompts, chat history, and configuration.

## Key Features

- **Dual-Chat System**: Run two simultaneous chat instances (Chat 1 and Chat 2) with independent histories
- **Chat Switching**: Seamlessly switch between chats with `/switch` command
- **Twist Functionality**: Copy AI responses between chats with `/twist` for creative workflows
- **Global Model Selection**: Model changes apply to both chat instances
- **Instance-Specific Configurations**: Each chat maintains its own settings and history
- **Rich Terminal UI**: Color-coded chats with formatted output using Rich library
- **Persistent Storage**: Configurations and logs saved per chat instance
- **Modular Architecture**: Well-organized code structure for maintainability

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

The application starts with two chat instances. Chat 1 (green) begins active. Use `/switch` to move between chats or `/twist` to copy responses between them.

### Example Interaction
```
HIOLLAMA!
v.0.1.4.dev

CHAT 1: SUMMARY
| SYS: You are a direct, technical assistant...
| YOU: Tell me about quantum computing

| CH:5/20 (Type /help for help.)
| YOU: Tell me about quantum computing

| 1)qwen3:0.6B:

Quantum computing uses quantum bits (qubits) to perform calculations...
```

## Commands

### General Commands
- `/help` - Show the comprehensive help menu
- `/quit` - Exit the program and save all configurations
- `/showvars` - Display current system variables for the active chat
- `/switch` - Switch between Chat 1 and Chat 2
- `/twist` - Copy the last AI response to the other chat and switch to it

### Model Commands
- `/model` - Select a different model (applies globally to both chats)
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

## Dual-Chat System

The application's unique dual-chat system allows for:

### Independent Chat Instances
- **Chat 1** (green): Maintains its own history, settings, and logs
- **Chat 2** (blue): Completely separate chat with independent configuration
- Each chat saves to its own log directory and config file

### Chat Interaction
- **Switching**: Use `/switch` to move between chats instantly
- **Twisting**: Use `/twist` to copy the last AI response to the other chat as a new prompt
- **Global Settings**: Model selection applies to both chats simultaneously

### Use Cases
- **Comparative Analysis**: Test different approaches to the same problem
- **Collaborative Workflow**: Use one chat for brainstorming, another for refinement
- **Context Switching**: Maintain separate conversations for different topics
- **Creative Iteration**: Twist responses between chats to build on ideas

## Configuration

The application uses separate configuration files for each chat instance:

- **Global Config**: `~/.hiollama_config_global.json` (shared model selection)
- **Chat 1 Config**: `~/.hiollama_config_0.json` (Chat 1 specific settings)
- **Chat 2 Config**: `~/.hiollama_config_1.json` (Chat 2 specific settings)

### Per-Chat Settings
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

Chat logs are organized by instance:
- **Chat 1**: `~/hiollama_logs/chat_0/YYYY-MM-DD.txt`
- **Chat 2**: `~/hiollama_logs/chat_1/YYYY-MM-DD.txt`

Each log includes timestamps and is saved automatically when logging is enabled.

## Project Structure

The project uses a modular architecture for maintainability:

```
hiollama/
├── __init__.py          - Package initialization
├── __main__.py          - Entry point and multi-chat orchestration
├── app.py               - Main HiOllamaChat class with global model management
├── chat_history.py      - Instance-specific chat history management
├── commands.py          - Command handlers with chat-aware functionality
├── config.py            - Configuration management (global + per-instance)
├── constants.py         - Shared constants and defaults
├── model_interaction.py - Ollama API communication
├── ui.py                - Rich-based user interface with chat colors
└── utils.py             - Utility functions for formatting and chat management
```

## Technical Features

### Modern Ollama Integration
- Uses native `ollama.list()` function for model enumeration
- Leverages `ollama.chat()` for streamlined communication
- Proper error handling for API interactions

### Rich Terminal UI
- Color-coded chat instances (green/blue)
- Formatted output with proper alignment
- Interactive spinners during model inference
- Rainbow header with version display

### Advanced State Management
- Class-level global configuration sharing
- Instance registration for synchronized updates
- Proper cleanup and configuration saving on exit

## Contributing

Contributions are welcome! The modular structure makes it easy to extend functionality:

1. Fork the repository
2. Create a feature branch
3. Follow the existing code organization patterns
4. Add appropriate error handling
5. Update documentation as needed
6. Submit a pull request

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