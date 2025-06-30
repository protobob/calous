CALOUS: Context Abstraction Layer Over Unix Sockets

CALOUS is a CLI context management layer that sits between you and your local llm's run by ollama. It's not a model, an ai or a replacement for ollama. Instead it handles system prompts, chat history, prompt library and model settings. It fetures over 55+ commands divided into categories.

It includes three(four) main software applications:

calousd: minimal python daemon that listens over unix sockets for CALOUS clients and manages context and sends prompts to ollama

cx: a minimal rust unix tool that lets you send prompts, calous commands and data through unix pipes, it also includes a basic REPL mode.

cxi: a minmal python repl for CALOUS that features rich text, tab completion and command history (not made yet)

cxgui: a gui app that lets you talk to your local models using CALOUS context management. (not made yet)

CX is the star of the show, it lets your bring you models down into any terminal.

Examples:

ps aux | head -n 10 | cx "what is the top process?"
textfile > cx "summarize this text file" > newtextfile
cx -c "/sys.help"