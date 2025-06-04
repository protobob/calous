Dear AI collaborator,

I would like to familiarize you with this codebase. This project is a python front end for ollama through the ollama python api. It is experimental in nature, a way for me to learn how to programmatically work with LLMS and also a way to familiarize myself with working with AI coding agents (Such as yourself.)

This project is used only by me at the moment, and the repository on github is private. This project is not live code, and is not meant to ever be used as a public facing interface on the internet. That said, I do have a desire for the codebase to be polished and secure.

This codebase has been developed primarily by AI with my guidance. My knowledge of Python is actually rather basic, and I'm dependant on AI for the actual coding. I do however have some professional experience developing software for customers.

I've noticed when AI's look over the codebase they tend to pay far too much attention to the changelog, I'm more interested in the state of the actual code than anything you might find written in the changelog.

A Bit about HIOLLAMA:

This is a python application that allows the user to talk to a local LLM. One of the unique features of this project is that there can be many different chat channels, each with it's own context, which allows the user to quickly switch between different 'personas' defined by each channels system prompt, even though the same model is still being used.

The most interesting feature to me is the /twist command. This command takes the LLM's most recent response from your current chat channel, then automatically switches you to a specified chat channel (e.g., /twist 2) and sends that response as a new prompt to the LLM in the destination channel. This creates a seamless way to continue a conversation across different personas or contexts.

Chat channels are not agents, nothing happens on chat channels unless the user is on the chat.
