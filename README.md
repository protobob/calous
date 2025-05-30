# Hi, Ollama! 🌈

A colorful, multi-chat command-line interface for interacting with Ollama language models. Experience seamless conversations across multiple chat instances with rainbow-themed visual distinction and powerful cross-chat features.

## Features

### 🌈 Multi-Chat Architecture
- **Configurable Chat Instances**: Run up to N concurrent chat sessions (default: 4)
- **Rainbow Color Coding**: Each chat gets a unique color (red, orange, yellow, green, blue, purple, magenta)
- **Smart Chat Switching**: Cycle through chats or jump to specific instances
- **Twist Functionality**: Copy AI responses between chats for cross-pollination of ideas

### 🎯 Intelligent Chat Types
- **Chat 1 (Red)**: Technical assistant for coding and debugging
- **Chat 2 (Orange)**: Creative writing and storytelling assistant
- **Chat 3+ (Rainbow)**: General-purpose helpers with customizable prompts

### ⚡ Advanced Features
- **Event-Driven Architecture**: Clean command processing with structured results
- **Unified Configuration**: Single config file managing all chat instances
- **Rich Terminal UI**: Spinners, colored output, and interactive prompts
- **Thought Filtering**: Hide AI reasoning for cleaner responses
- **Evaluation Metrics**: Optional performance data display
- **Persistent History**: Configurable message limits per chat
- **File Loading**: Import text files as prompts with syntax highlighting

### 🛠 Command System
- **Dynamic Help**: Context-aware help menu showing available chat ranges
- **Saved Prompts**: Store and reuse up to 10 custom prompts per chat
- **System Prompt Management**: Customize AI behavior per chat instance
- **Model Selection**: Easy switching between available Ollama models
- **History Management**: View, clear, and manage conversation history

## Installation

### Prerequisites
- Python 3.7+
- [Ollama](https://ollama.ai/) installed and running
- At least one Ollama model pulled (e.g., `ollama pull qwen2.5:0.5b`)

### Install Hi, Ollama!

```bash
# Clone the repository
git clone https://github.com/yourusername/hiollama.git
cd hiollama

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

### Quick Start

```bash
# Start the application
python -m hiollama

# Or if installed globally
hiollama
```

## Usage

### Basic Commands

```bash
# General Commands
/help           # Show complete help menu
/quit           # Exit and save configuration
/showvars       # Display current system variables

# Chat Navigation
/switch         # Cycle to next chat
/switch 3       # Switch to chat 3
/twist          # Copy last AI response to next chat
/twist 2        # Copy last AI response to chat 2

# Model Management
/model          # Select a different Ollama model
/toggle_eval    # Toggle evaluation data display
/toggle_think   # Toggle AI thought filtering

# Prompt Management
/setprompt 1 Your prompt here    # Save prompt to slot 1
/prompt 1                        # Use saved prompt 1
/showprompt all                  # Show all saved prompts
/system                          # Change system prompt

# Chat History
/clear          # Clear current chat history
/history        # Display conversation history
/toggle_log     # Toggle conversation logging

# File Operations
/load path/to/file.txt           # Load file as prompt
/load code.py "Review this code" # Load with instructions
```

### Multi-Chat Workflow Examples

#### Collaborative Development
```bash
# Chat 1 (Technical): Get code structure
> "Create a Python class for user authentication"

# Copy response to Chat 2 (Creative)
/twist 2

# Chat 2: Enhance with documentation
> "Add comprehensive docstrings and examples to this code"

# Switch back to technical chat
/switch 1

# Continue technical discussion
> "Now add unit tests for this class"
```