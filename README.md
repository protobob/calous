# HiOllama 🌈

A colorful, multi-chat CLI interface for interacting with Ollama AI models. Chat with multiple AI instances simultaneously, switch between conversations, and share responses across chats.

## What is HiOllama?

HiOllama lets you run multiple AI chat sessions at once, each with its own personality and conversation history. Think of it like having several AI assistants working on different tasks - you can switch between them instantly and even copy responses from one chat to another.

## Features ✨

- **Multiple Chat Sessions**: Run 1-14 concurrent AI conversations
- **Rainbow Color Coding**: Each chat has its own color for easy identification
- **Smart Chat Switching**: Jump between conversations instantly
- **Twist Operation**: Copy AI responses between chats
- **Flexible Configuration**: Customize each chat's behavior independently
- **Command System**: Rich set of commands for chat management
- **Conversation History**: Full history tracking with optional logging
- **System Prompts**: Give each chat its own personality or role

## Prerequisites

Before installing HiOllama, you need:

1. **Python 3.8 or higher**
   - Check if you have Python: Open terminal/command prompt and type `python --version`
   - If not installed, download from [python.org](https://python.org/downloads/)

2. **Ollama**
   - Download and install from [ollama.ai](https://ollama.ai)
   - Make sure it's running (you should see the Ollama icon in your system tray)
   - Pull at least one model: `ollama pull qwen2.5:0.5b` (recommended for testing)

## Installation

### Method 1: From PyPI (Recommended)
```bash
pip install hiollama
```

### Method 2: From Source
```bash
git clone https://github.com/yourusername/hiollama.git
cd hiollama
pip install -e .
```

## Quick Start

### Basic Usage
```bash
# Start with default 4 chats
hiollama

# Start with custom number of chats (max 14)
hiollama 8
```

### First Run Setup
1. When you first run HiOllama, it will create a configuration file at `~/.hiollama_config_unified.json`
2. If you don't have any Ollama models, run `/model` to select one
3. Each chat starts with a default system prompt - you can customize these with `/system`

## Using HiOllama

### The Interface

When you start HiOllama, you'll see:
- **HIOLLAMA!** header in rainbow colors
- **ACTIVE CHATS** overview showing all your chat sessions
- **Current chat summary** (if you have conversation history)
- **Colored prompt** showing which chat you're in

```
HIOLLAMA!
v.0.5.3.dev

ACTIVE CHATS: (/switch [1-4] to change)
► 1: You are a direct, technical assistant...
  2: You are a direct, technical assistant...
  3: You are a direct, technical assistant...
  4: You are a direct, technical assistant...

| CH:0/20 (/help for help)
| YOU
```

### Essential Commands

Type `/help` to see all commands. Here are the most important ones:

#### Navigation
- `/switch 2` - Switch to chat 2
- `/switch` - Switch to next chat
- `/twist 3` - Copy last AI response to chat 3
- `/twist` - Copy to next chat

#### Chat Management
- `/system New personality here` - Change the current chat's personality
- `/clear` - Clear current chat history
- `/history` - View conversation history

#### Model & Settings
- `/model` - Choose a different AI model
- `/showvars` - View current settings
- `/quit` - Exit and save configuration

### Example Workflow

1. **Start HiOllama**:
   ```bash
   hiollama 3
   ```

2. **Set up different chat personalities**:
   ```
   Chat 1: /system You are a Python coding expert
   Chat 2: /system You are a creative writing assistant  
   Chat 3: /system You are a technical documentation writer
   ```

3. **Work on different tasks**:
   - Chat with the coding expert about a bug
   - Switch to the writer for some creative ideas
   - Copy good explanations between chats with `/twist`

4. **Switch between conversations**:
   ```
   /switch 2    # Go to creative writing chat
   /switch      # Go to next chat (3)
   /switch 1    # Back to coding chat
   ```

## Configuration

HiOllama stores settings in `~/.hiollama_config_unified.json`. The configuration includes:

- **Global settings**: Model selection, number of chats
- **Per-chat settings**: System prompts, history limits, logging preferences

### Example Configuration Structure
```json
{
  "global": {
    "selected_model": "qwen2.5:0.5b",
    "num_chats": 4
  },
  "chats": {
    "0": {
      "system_prompt": "You are a Python expert...",
      "MAX_HISTORY": 20,
      "verbosity": true,
      "think_filtering": true
    }
  }
}
```

## Advanced Features

### Twist Operation
The "twist" feature copies the last AI response from your current chat to another chat as a new user message. This is useful for:
- Getting a second opinion on an answer
- Continuing a conversation in a different context
- Cross-pollinating ideas between specialized chats

### System Prompts
Each chat can have its own personality through system prompts:
- **Technical Assistant**: `You are a direct, technical assistant. No greetings, just facts.`
- **Creative Helper**: `You are an enthusiastic creative writing assistant.`
- **Code Reviewer**: `You are a senior developer reviewing code for bugs and improvements.`

### History Management
- Each chat maintains its own conversation history
- Set custom history limits with `/setmax 50`
- Clear history anytime with `/clear`
- Optional file logging to `~/hiollama_logs/`

## Troubleshooting

### Common Issues

**"No models found"**
- Make sure Ollama is running
- Pull a model: `ollama pull qwen2.5:0.5b`
- Check available models: `ollama list`

**"Connection refused"**
- Ensure Ollama is started and running on port 11434
- Try restarting Ollama

**Commands not working**
- Make sure commands start with `/`
- Use `/help` to see correct syntax
- Check for typos in command names

**Colors not showing**
- Your terminal might not support colors
- Try a modern terminal like Windows Terminal, iTerm2, or GNOME Terminal

### Getting Help

- Type `/help` in HiOllama for command reference
- Check the logs in `~/hiollama_logs/` for error details
- Report issues on GitHub

## Tips for New Users

1. **Start small**: Begin with 2-3 chats to get familiar
2. **Use different system prompts**: Give each chat a specific role
3. **Experiment with `/twist`**: It's great for comparing responses
4. **Save useful prompts**: Use `/setprompt` to save frequently used prompts
5. **Check `/showvars`**: See your current settings anytime

## Development

Want to contribute or modify HiOllama?

```bash
git clone https://github.com/yourusername/hiollama.git
cd hiollama
pip install -e ".[dev]"
```

See ARCHITECTURE.md for detailed technical documentation.

## License

MIT License - see LICENSE file for details.

---

Made with 🌈 for the Ollama community