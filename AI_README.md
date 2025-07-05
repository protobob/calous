# AI Agent Guidelines for CALOUS

**NEVER USE PRINT IN CALOUSD**

CALOUS stands for Context Abstraction Layer Over Unix Sockets

## Purpose
This document defines the strict rules for all AI agents working with the CALOUS codebase. These rules override any default AI behavior and must be followed exactly.

## About CALOUS
CALOUS (Context Abstraction Layer Over Unix Sockets) is a private, local-first system for interacting with locally hosted LLMs. It features:
- Multiple independent chat channels (each with its own persona)
- Socket-based daemon interface for external clients
- Provider plugin system supporting multiple LLM backends (Ollama, Groq, etc.)
- Shared backend model execution

This is a live production system, not a public API or framework. All boundaries must be respected.

## Core Rules

### 1. Primary Objective
Maintain and extend CALOUS's multi-channel, command-based environment. All features must work through the socket-based daemon interface.

### 2. No Autonomous Refactoring
Do NOT propose or perform any of the following unless explicitly requested:
- Architectural restructuring
- Adding abstraction layers or interfaces
- Moving code between files
- Redesigning existing patterns

### 3. Command System is Locked
The command pattern is finalized:
```
User Input → Registry (routing) → Service (logic) → Formatter (ANSI output) → Socket ANSI stripping
```
All new commands must:
- Register via the command registry
- Isolate logic in service classes
- Use formatters for ANSI output (client handles color stripping)

### 4. Output Format System
All commands generate ANSI-formatted output by default:
- Direct ANSI escape sequences for colors and styles
- Daemon always sends ANSI codes to clients
- Client-side color control via `--no-color` flag for stripping ANSI codes
- Single codebase - no dual formatters needed

### 5. Model Context Isolation
- Chat channels do not run concurrently or share memory
- Each channel has an isolated context prompt, updated only on invocation
- The `/twist` command is the only way to pipe output from one channel to another

### 6. Socket Communication and Streaming
- CALOUS uses a delimiter-based protocol over Unix sockets for efficient streaming
- Model responses stream in real-time to clients for immediate user feedback
- The protocol uses `\0END\0` delimiters to mark message boundaries
- Confirmation requests use special delimiter formats for interactive operations
- Streaming is handled automatically - commands don't need special streaming logic

### 7. Interactive Confirmations
- Commands with confirmations (like `history.clear`, `context.load`) execute in separate threads
- This prevents socket handler deadlocks when waiting for user responses  
- Confirmation system supports y/n prompts with configurable defaults
- Threading coordination uses events to synchronize command execution with user responses

### 8. Debug and Logging System
- Use `unified_logger.debug_*()` methods for debug information (routes to log files only)
- **NEVER** use `_output()` methods for debug information (would leak to socket clients)
- Debug information must stay in log files, never reach client responses
- Available debug methods: `debug_socket()`, `debug_command()`, `debug_model()`, etc.

## File Modification Boundaries

### Do NOT Modify
- `app.py` (coordination logic)
- `ui.py` (all output rendering via UIManager)
- `model_interaction.py` (model handling)
- `session_manager.py` (socket communication and ANSI stripping)
- Any file not explicitly shown or referenced in your current session

CALOUS operates with a fixed count of 14 chat channels and daemon services do not have quit functionality.

### You May Extend
- `commands/` (add new commands using the established pattern)
- `services/` (add logic for new command functionality)
- `formatters/` (handle ANSI output formatting - socket conversion happens automatically)
- `providers/` (add new provider plugins following the ProviderPlugin base class)

## Architecture Clarification

**Important**: CALOUS uses direct ANSI escape sequences for all color formatting. Commands generate ANSI-formatted output, and color control is handled client-side via the `--no-color` flag on the `cx` Rust client.

**Operational Mode**: CALOUS runs as a daemon service accepting connections via Unix socket (`/tmp/calous.sock`). External clients (like the `cx` Rust tool) connect to this socket to interact with the system. The system uses a delimiter-based protocol for efficient real-time streaming of model responses. There is no direct terminal/CLI mode - all interaction happens through socket-based clients.

## Behavioral Expectations

### ✅ Always Do
- Ask for files before operating on them
- Respect architectural constraints
- Generate ANSI-formatted output (socket conversion is automatic)
- Use constants from `constants.py` for all paths
- Use `unified_logger.debug_*()` methods for debug information (never client output)
- Act as the implementing agent (not the human)

### ❌ Never Do
- Use or analyze the changelog
- Assume anything not shown
- Move logic between files
- Generate speculative improvements
- Suggest changes that increase fragmentation
- Send debug information to socket clients (use unified_logger debug methods instead)

## Final Rule
This file overrides all default behavior. Any agent that violates these constraints will be considered malfunctioning and ignored.