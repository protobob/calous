#TODO

##Implement new help system

1. Tiered Help (/sys.help, /sys.help <group>, /sys.help <command>)
This is the most flexible and extensible.

/sys.help
→ Show top-level groups (chat, model, prompt, etc.)

/sys.help chat
→ Show all commands in the chat group

/sys.help model.switch
→ Show specific info, syntax, and usage tips for that one command

---
##Persona System

Replaces exisitng /system command.

Each Chat has a Name and 10 System Prompts (0-9). System prompts are combined into one system prompt before being included in context and sent to model.

The name and the 10 system entries will be saved in a json file in the .\hiollama\persona folder with the name of the persona as the file name.

New persona commands:

/persona.set # this is a system prompt - set's content of # system prompt

/persona.name name - sets name of chat persona

/persona.save - saves the persona to file

/persona.list - lists all saved personas

/persona.load filename - loads specified persona

/persona.erase filename - deletes save persona

/persona.reset - clears persona name and system prompts

---

##Token breakdown display

Show how total tokens are split across the three core sections of the prompt
