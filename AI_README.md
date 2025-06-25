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
