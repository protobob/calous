GLOBAL HELP

Hi, Ollama! is a multi-channel chat interface for local LLM models. Each chat 
channel (1-14) maintains its own conversation history and persona, allowing you 
to quickly switch between different AI contexts and personalities.

GETTING STARTED

First time? Try these commands:

Choose a model:      /model.switch
Switch channels:     /chat.switch 2
Name your AI:        /persona.name Assistant
Set a system prompt: /persona.set 0 You are a helpful coding assistant
Try twist feature:   /chat.twist 3
View chat history:   /history.show
Add a command alias: /alias.add h sys.help

CATEGORY HELP

Chat Management      (7 commands)  → /sys.help chat
Model Operations     (7 commands)  → /sys.help model
Persona Management  (11 commands)  → /sys.help persona
History Management   (3 commands)  → /sys.help history
Logging Operations   (5 commands)  → /sys.help log
Prompt Management    (4 commands)  → /sys.help prompt
File Operations      (1 command)   → /sys.help file
System Commands      (2 commands)  → /sys.help sys
Alias Management     (4 commands)  → /sys.help alias
Plugin System        (4 commands)  → /sys.help plugin

MORE HELP

/sys.help [category]    Detailed commands for a category
/sys.help [command]     Specific help for any command
/sys.help all           List of all commands by category.