Dear AI collaborator,

I would like to familiarize you with this codebase. This project is a python front end for ollama through the ollama python api. It is experimental in nature, a way for me to learn how to programmatically work with LLMS and also a way to familiarize myself with working with AI coding agents (Such as yourself.)

This project is used only by me at the moment, and the repository on github is private. This project is not live code, and is not meant to ever be used as a public facing interface on the internet. That said, I do have a desire for the codebase to be polished and secure.

This codebase has been developed primarily by AI with my guidance. My knowledge of Python is actually rather basic, and I'm dependant on AI for the actual coding. I do however have some professional experience developing software for customers.

I've noticed when AI's look over the codebase they tend to pay far too much attention to the changelog, I'm more interested in the state of the actual code than anything you might find written in the changelog.

A Bit about HIOLLAMA:

This is a python application that allows the user to talk to a local LLM. One of the unique features of this project is that there can be many different chat channels, each with it's own context, which allows the user to quickly switch between different 'personas' defined by each channels system prompt, even though the same model is still being used.

The most interesting feature to me is the /twist command. This command takes the LLM's most recent response from your current chat channel, then automatically switches you to a specified chat channel (e.g., /twist 2) and sends that response as a new prompt to the LLM in the destination channel. This creates a seamless way to continue a conversation across different personas or contexts.

Chat channels are not agents, nothing happens on chat channels unless the user is on the chat.

## Technical Architecture Overview

**Core Dependencies:**
- `ollama` - Primary LLM API interface
- `rich` - Terminal UI and formatting
- `requests` - HTTP communications

**Main Architecture Components:**

1. **`ChatSessionManager`** (`session_manager.py`) - Orchestrates multiple AI personalities and handles the main application loop
2. **`HiOllamaChat`** (`app.py`) - Individual chat session/personality with isolated context and system prompt
3. **Command System** (`commands/`) - 23+ commands across 6 categories with registry pattern for extensibility
4. **Configuration System** (`config.py`) - Unified JSON configuration with global and per-chat settings
5. **Model Interaction** (`model_interaction.py`) - Single shared Ollama model serving all personalities
6. **Plugin System** (`plugins/`) - Extensible plugin architecture for adding functionality

**Entry Point:**
Run with `python -m hiollama [num_chats]` where num_chats defaults to 2, max 14.

**Key Command Categories:**
- **CORE**: `/new`, `/switch`, `/removechat` (chat management)
- **COMMUNICATION**: `/twist` (inter-personality messaging)
- **SESSION**: `/save`, `/load`, `/export` (persistence)
- **MODEL**: `/model`, `/system`, `/setctx` (configuration)
- **INFO**: `/help`, `/showvars`, `/status` (information)
- **ADVANCED**: `/history`, `/search`, `/debug` (power features)

**Configuration:**
- Global settings: `~/.hiollama_config_unified.json`
- Global model selection affects all personalities
- Per-chat system prompts and conversation histories
- Persistent thinking mode, logging, and other preferences

**Current Development State:**
- Stable multi-chat functionality with `/twist` command working
- Plugin system in place with built-in calculator and dice roller
- Comprehensive test suite including integration and manual testing
- Active development with version 0.6.4+ supporting native Ollama thinking API
- Extensive documentation in COMMANDS.md and ARCHITECTURE.md