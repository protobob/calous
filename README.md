What is CALOUS?

What if you could have a multi-persona context manager for your ollama and your local LLM's that sits right on top of your operating system and lives in your terminal?

That's what CALOUS does. It consists of:

calousd: a mutli-chat context manager service that's written in python and takes very few resources to run. It defaults to starting with fourteen channels, each with it's own context (name, modular system prompt, chat-history, prompt library, model settings) which you can switch between any time. And you can save all of these settings to disk and reload them later.

cx: a unix tool written in rust that you use in your terminal. It lets you send prompts, send commands to calous AND you can use it with unix pipes to send data to your model or save prompts to disk.

    examples:

        # Send a prompt to your model:
        cx "What is the flag for ls that shows file details?"

        # Send commands to calous:
        cx -c "/sys.help"

        # specify channel:
        cx -n 2 "Hello Astraea! WRite me a poem about mars!"
        
        # use unix pipes to create complex commands:
        ls -l | cx "What is the largest file in this directory?"
        textfile > cx "Summarize this file for me" > summaryfile

        # start the CALOUS REPL:
        cx -i

CALOUS has over 55+ commands, and while that sounds confusing they are broken up into categories with comphrensive online help.

        # change your ollama mode:
        /sys.model 7

        # see help for chat commands:
        /sys.help chat
        
        # show your chat history:
        /history.chat

        # create a command alias
        /alias.add s chat.switch

        # set a system prompt (0-9):
        /persona.set 0 You are a helpful assistant

