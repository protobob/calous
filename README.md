# Hi, Ollama!

A friendly command-line interface for interacting with Ollama models.

## Overview

Hi, Ollama! is a Python-based tool that provides an intuitive interface for communicating with Ollama language models through your terminal. It features a rich set of commands for managing prompts, chat history, and configuration.

## Installation

### Prerequisites

- Python 3.6+
- [Ollama](https://ollama.ai/) installed and running locally
- Required Python packages:
  - ollama
  - requests
  - rich

### Setup

1. Clone this repository or download hiollama.py
2. Install required packages:
```
pip install ollama requests rich
```
3. Ensure Ollama is running (typically on localhost:11434)

## Usage

Run the program from your terminal:
```
python hiollama.py
```

The application will start with your configured model and display a prompt where you can enter messages.

## Features

- **Chat with AI models**: Communicate with any model available in your Ollama installation
- **Save and reuse prompts**: Store up to 10 custom prompts for easy reuse
- **Chat history management**: View, clear, and manage your conversation history
- **Thought filtering**: Toggle filtering of "thought" text in model responses
- **File processing**: Send file contents as prompts to the model
- **Customizable system prompts**: Set the tone and behavior of the model
- **Logging**: Save conversations to log files for future reference

## Commands

### General Commands
- `/help` - Show the help menu
- `/quit` - Exit the program and save the configuration
- `/clear` - Clear the current chat history
- `/history` - Display the current chat history

### Model Commands
- `/model` - Select a different model
- `/verbosity` - Toggle evaluation data display after responses
- `/togglethink` - Toggle filtering of LLM 'thoughts' (for reasoning models)

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

## Example Usage

To chat with a model:
```
You: Tell me about quantum computing.
qwen3:0.6B: Quantum computing uses quantum bits (qubits) to perform calculations. Unlike classical bits, qubits can exist in multiple states simultaneously through superposition. This allows quantum computers to solve certain problems exponentially faster than classical computers.

Key quantum computing concepts:
- Qubits: The basic unit of quantum information
- Superposition: Qubits can be in multiple states at once
- Entanglement: Qubits can be correlated, even at a distance
- Quantum gates: Operations that manipulate quantum states

Current quantum computers are noisy and limited in qubit count. They excel at specific tasks like factoring large numbers, quantum simulation, and optimization problems.
```

To use a saved prompt:
```
> /prompt
Enter prompt number (1-10): 3

You: [Prompt text appears here]
```

## License

[Specify license information here]

## Contributing

[Specify contribution guidelines here]