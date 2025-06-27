Dear AI Collaborator,

Welcome to the HiOllama codebase. This project is a Python frontend for Ollama using the Ollama Python API. It is experimental in nature, designed both as a learning tool for me to better understand how to programmatically interact with LLMs and as a way to become proficient in collaborating with AI coding agents (such as yourself).

This project is currently private and used only by me. While it is not intended to become a public-facing or production-grade system, I am committed to ensuring that the code is polished, maintainable, and secure.

Although I have some professional experience delivering software to clients, my Python skills are basic. Most of this project has been written by AI under my direction. You will find AI-written code throughout the repository.

A recurring issue I've encountered is that AI agents tend to over-focus on the changelog. I am far more interested in the actual source code and its current structure than any documentation or assumptions derived from the changelog. Please do not base your understanding or analysis of the system on the changelog unless I explicitly ask you to.

MANDATORY WORKFLOW FOR AI AGENTS:

Code First, Not Docs – Do not provide suggestions, analysis, or implementation plans unless you have explicitly reviewed the relevant source files. You may ask me to share specific files if necessary.

Request Before Act – If you have not yet seen the required files, ask for them. Do not generate speculative or generic suggestions.

Ignore Changelog – Do not use the changelog unless directly instructed.

Strict Compliance – If you bypass these steps, your output will be considered invalid. This rule is absolute.

Use this workflow every time you are asked to interact with the codebase.

About HiOllama

HiOllama is a Python terminal application for interacting with a local LLM. A defining feature is its support for multiple chat channels, each tied to a unique context/system prompt. This lets the user seamlessly switch between different AI "personas" within a single session, even though the underlying model remains the same.

A key feature is the /twist command:

It takes the last LLM response in the current chat channel

Sends it as the input prompt to a different channel (e.g., /twist 2)

This allows for contextual handoff between personas and layered interpretation

Important: Chat channels are not autonomous agents. Nothing happens in a channel unless the user actively switches to it.

Thank you for respecting these constraints.

Hi, Ollama! Architecture Vision

!Please read this ENTIRE file!

Executive Summary

Hi, Ollama! is a multi-chat CLI interface for Ollama language models. This document establishes the architectural vision to prevent conflicting refactoring approaches and maintain consistency as the codebase evolves.

🧠 Copilot / AI Agent Compliance Section (Read First!)

❗ Hard Rules for AI Agents

These rules apply to GitHub Copilot, GPT, and any other automated AI coding assistant used with this repository.

Do not suggest or generate changes unless you have seen the actual source code being referenced.

Do not suggest architectural restructuring or code movement based on best practices or assumptions.

DO NOT REFACTOR the following files:

model_interaction.py (586 lines): Large but cohesive

ui.py (320+ lines): All display logic belongs here

app.py (~150 lines): Entry point and coordination logic

Do not move UI logic into command formatters. It belongs in UIManager only.

Do not break or alter the Command System architecture. It is feature-complete.

Do not suggest abstract base classes, microservice-style fragmentation, or 'separation of concerns' where the code is already cleanly structured.

Do not assume that the human user will be making code changes. Suggestions should be framed assuming the AI is responsible for implementation and modification unless explicitly stated otherwise.

☑️ Safe Suggestions

You may suggest bug fixes.

You may suggest small enhancements to commands or UI, but must localize changes to relevant files.

You may recommend new commands using the existing pattern (Registry → Service → Formatter).

You may propose plugin-based extensions that do not affect core architecture.

✅ Enforcement

Violating these rules will cause your suggestions to be rejected.
If you're unsure whether a change violates a rule, ASK FIRST.

Core Principles

1. Pragmatic Simplicity Over Academic Purity

Favor working solutions over theoretical perfection

Monolithic cohesive code is preferable to hyper-fragmented architecture

If a file is large but logically coherent, leave it alone

Avoid refactoring for refactoring's sake

2. UI Centralization

All display/formatting logic should be concentrated in the UIManager class

Avoid scattering UI logic across multiple command formatter files

Rich console formatting should be managed centrally, not distributed

3. Command System Stability

The current command architecture is feature-complete and stable

Do not suggest major architectural changes to the command system

Focus on bug fixes and minor enhancements, not restructuring

4. Configuration Management

Global settings (model, context window) managed via ConfigManager

Chat-specific settings remain in individual Chat instances

Persona system replaces old system_prompt approach

5. File Path Consistency

All file paths, such as those for saved histories or configurations, should follow centralized patterns defined in constants.py.

Do not hardcode file paths in service, command, or formatter logic — always use the constant values.

