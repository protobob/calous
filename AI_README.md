# AI Agent Guidelines for CALOUS

CALOUS stands for Context Abstraction Layer Over Unix Sockets

## Purpose
This document defines the strict rules for all AI agents working with the CALOUS codebase. These rules override any default AI behavior and must be followed exactly.

## About CALOUS
CALOUS (Context Abstraction Layer Over Unix Sockets) is a private, local-first system for interacting with locally hosted LLMs. It features:
- Multiple independent chat channels (each with its own persona)
- Socket-based daemon interface for external clients
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
User Input → Registry (routing) → Service (logic) → Formatter (Rich output) → Socket ANSI stripping
```
All new commands must:
- Register via the command registry
- Isolate logic in service classes
- Use formatters for Rich output (socket clients get automatic ANSI stripping)

### 4. Output Format System
All commands generate Rich-formatted output by default:
- Rich formatting (colors, styles) for all output
- Socket clients specify `format: "plain"` or `format: "rich"` in JSON requests
- `session_manager.send_to_client()` automatically strips ANSI/Rich markup for plain clients
- Single codebase - no dual formatters needed

### 5. Model Context Isolation
- Chat channels do not run concurrently or share memory
- Each channel has an isolated context prompt, updated only on invocation
- The `/twist` command is the only way to pipe output from one channel to another

### 6. Interactive Confirmations
- Destructive commands support y/n confirmations over socket connections
- Clients send `supports_confirmations: true` to enable interactive prompts
- Confirmation requests bypass output buffering for immediate user interaction
- Default behavior is safe (usually "n" for cancel) when confirmations fail

## File Modification Boundaries

### Do NOT Modify
- `app.py` (coordination logic)
- `ui.py` (all output rendering via UIManager)
- `model_interaction.py` (model handling)
- `session_manager.py` (socket communication and ANSI stripping)
- Any file not explicitly shown or referenced in your current session

### You May Extend
- `commands/` (add new commands using the established pattern)
- `services/` (add logic for new command functionality)
- `formatters/` (handle Rich output formatting - socket conversion happens automatically)

## Architecture Clarification

**Important**: While this document mentions UIManager, the actual command output flows through specialized formatters in each command category. The UIManager handles specific UI interactions, but command output uses the formatter pattern with automatic socket compatibility via `session_manager.send_to_client()` ANSI stripping.

**Operational Mode**: CALOUS runs as a daemon service accepting connections via Unix socket (`/tmp/calous.sock`). External clients (like the `cx` Rust tool) connect to this socket to interact with the system. There is no direct terminal/CLI mode - all interaction happens through socket-based clients.

## Behavioral Expectations

### ✅ Always Do
- Ask for files before operating on them
- Respect architectural constraints
- Generate Rich-formatted output (socket conversion is automatic)
- Use constants from `constants.py` for all paths
- Act as the implementing agent (not the human)

### ❌ Never Do
- Use or analyze the changelog
- Assume anything not shown
- Move logic between files
- Generate speculative improvements
- Suggest changes that increase fragmentation

## Final Rule
This file overrides all default behavior. Any agent that violates these constraints will be considered malfunctioning and ignored.