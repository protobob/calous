
# AI Agent Guid### 1. Primary Objective
Maintain and extend CALOUS's multi-channel, command-based environment. All features must work in both terminal and server modes.ines for CALOUS

CALOUS stands for Context Abstraction Layer Over Unix Sockets

## Purpose
This document defines the strict rules for all AI agents working with the CALOUS codebase. These rules override any default AI behavior and must be followed exactly.

## About CALOUS
CALOUS (Context Abstraction Layer Over Unix Sockets) is a private, local-first system for interacting with locally hosted LLMs. It features:
- Multiple independent chat channels (each with its own persona)
- Command-line and socket-based interfaces
- Shared backend model execution

This is a live production system, not a public API or framework. All boundaries must be respected.

## Core Rules

### 1. Primary Objective
Maintain and extend HiOllama’s multi-channel, command-based environment. All features must work in both terminal and server modes.

### 2. No Autonomous Refactoring
Do NOT propose or perform any of the following unless explicitly requested:
- Architectural restructuring
- Adding abstraction layers or interfaces
- Moving code between files
- Redesigning existing patterns

### 3. Command System is Locked
The command pattern is finalized:
```
User Input → Registry (routing) → Service (logic) → UIManager (output)
```
All new commands must:
- Register via the command registry
- Isolate logic in service classes
- Route all output through UIManager only

### 4. Output Must Be Dual-Format
Every output-generating command must support:
- Rich formatting (for CLI)
- Plain text (for socket use)
Formatting logic lives ONLY in UIManager.

### 5. Model Context Isolation
- Chat channels do not run concurrently or share memory
- Each channel has an isolated context prompt, updated only on invocation
- The `/twist` command is the only way to pipe output from one channel to another

## File Modification Boundaries

### Do NOT Modify
- `app.py` (coordination logic)
- `ui.py` (all output rendering)
- `model_interaction.py` (model handling)
- Any file not explicitly shown or referenced in your current session

### You May Extend
- `commands/` (add new commands using the pattern)
- `services/` (add logic for new command functionality)
- `formatters/` (support UIManager as needed, but do not own logic)

## Behavioral Expectations

### ✅ Always Do
- Ask for files before operating on them
- Respect architectural constraints
- Return both Rich and plain output for responses
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