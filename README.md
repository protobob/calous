# Hi, Ollama!

Version 0.5 -- May 20th, 2025

A friendly command-line interface for interacting with Ollama language models.

## Overview

Hi, Ollama! is a Python-based tool that provides an intuitive terminal interface for communicating with locally-run Ollama models. It features a modular architecture, rich formatting, and a comprehensive set of commands for managing prompts, chat history, and configuration.

## Features

- **Chat with AI models**: Communicate with any model available in your Ollama installation
- **Save and reuse prompts**: Store up to 10 custom prompts for quick access
- **Chat history management**: View, clear, and set the maximum history length
- **Thought filtering**: Toggle filtering of "thought" sections in model responses
- **File processing**: Send file contents as prompts with custom instructions
- **Customizable system prompts**: Set the tone and behavior of the model
- **Logging**: Save conversations to log files for future reference
- **Modular architecture**: Well-organized code structure for better maintainability

## Installation

### Prerequisites

- Python 3.6+
- [Ollama](https://ollama.ai/) installed and running locally
- Required Python packages:
  - `ollama`
  - `requests`
  - `rich`

### Setup

#### Option 1: Run as a Module
```bash
# Clone the repository
git clone https://github.com/protobob/hiollama.git

# Install dependencies
cd hiollama
pip install ollama requests rich

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

The application will start with your configured model and display a prompt where you can enter messages.

### Example Interaction
```
Model: qwen3:0.6B

Max:20 (Type /help for help.)
You: Tell me about quantum computing.

qwen3:0.6B: Quantum computing uses quantum bits (qubits) to perform calculations. Unlike classical bits, qubits can exist in multiple states simultaneously through superposition...
```

## Commands

### General Commands
- `/help` - Show the help menu
- `/quit` - Exit the program and save the configuration

### Model Commands
- `/model` - Select a different model
- `/verbosity` - Toggle evaluation data display after responses
- `/togglethink` - Toggle filtering of LLM "thoughts" (for reasoning models)

### Prompt Commands
- `/setprompt` - Set a saved prompt (1-10)
- `/prompt` - Use a saved prompt (1-10)
- `/showprompt` - Display saved prompts (1-10 or all)
- `/system` - Change the system prompt

### Chat History Commands
- `/history` - Display the current chat history
- `/clear` - Clear the current chat history
- `/setmax` - Set the maximum chat history (even number between 2-100)
- `/togglelog` - Toggle logging of chat history

### File Commands
- `/load <filename>` - Load a file as a prompt

## Configuration

The application saves its configuration to a file at `~/.hiollama_config.json`. This includes:

- Selected model
- Verbosity settings
- Think filtering toggle
- Maximum history size
- System prompt
- Saved prompts

### Default System Prompt

The default system prompt is:
```
You are a direct, technical assistant. Don't be enthusiastic. No greetings, no apologies. No emojis or other symbols! Answer like you're helping a peer debug code.
```

You can change this with the `/system` command.

## Logs

Chat logs are saved to `~/hiollama_logs/` with filenames based on the current date.

## Project Structure

The project is organized into modular components:

```
hiollama/
├── __init__.py        - Package initialization
├── __main__.py        - Entry point
├── app.py             - Main application class
├── chat_history.py    - Chat history management
├── commands.py        - Command handlers
├── config.py          - Configuration management
├── model_interaction.py - Model communication logic
├── ui.py              - User interface elements
└── utils.py           - Utility functions
```

This modular structure makes the code more maintainable and easier to extend.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a pull request

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