# HiOllama Commands Reference

> **Complete guide to HiOllama's command system**  
> *22 commands across 6 categories for multi-chat AI management*

HiOllama provides a comprehensive command system to manage multiple AI chat sessions and enable them to communicate with each other. All commands start with `/` and can be used from any active chat session.

## 📖 Quick Reference

| Command | Category | Description |
|---------|----------|-------------|
| `/addchat` | Navigation | Add a new chat session |
| `/switch` | Navigation | Switch between different chat sessions |
| `/removechat` | Navigation | Remove a chat session |
| `/twist` | Navigation | Copy AI response to another chat |
| `/model` | Model | Switch the underlying Ollama model |
| `/system` | Model | Set/update system prompts for chat sessions |
| `/setctx` | Model | Set context window size |
| `/toggle_eval` | Model | Toggle evaluation data display |
| `/toggle_think` | Model | Toggle thinking mode display |
| `/prompt` | Prompt | Use a saved prompt |
| `/setprompt` | Prompt | Save a prompt to a slot |
| `/showprompt` | Prompt | Display saved prompts |
| `/clear` | History | Reset conversation history |
| `/history` | History | Show chat history |
| `/export` | History | Export chat history |
| `/toggle_log` | History | Toggle unified logging |
| `/unified_log` | History | View unified log for today |
| `/load` | File | Load and send file with prompt |
| `/help` | General | Show comprehensive command reference |
| `/quit` | General | Exit and save configuration |
| `/resetchat` | General | Reset chat to factory defaults |
| `/showvars` | General | Display current system variables |

## 🎯 Navigation & Chat Management

Commands for managing multiple chat sessions and switching between them.

### `/addchat`
**Purpose**: Add a new chat session  
**Usage**: `/addchat`  
**Details**:
- Creates a new isolated chat session (up to maximum limit)
- Each session maintains separate conversation history
- Automatically switches to the new session after creation

### `/switch [chat_number]`
**Purpose**: Switch between different chat sessions  
**Usage**:
```bash
/switch 1    # Switch to chat 1
/switch 3    # Switch to chat 3
/switch      # Cycle to next chat
```
**Details**:
- Switch to any existing session by number (1-based)
- If no number provided, cycles to the next chat
- Current conversation context changes to target session

### `/removechat [chat_number]`
**Purpose**: Remove a chat session  
**Usage**:
```bash
/removechat 2    # Remove chat 2
/removechat      # Remove the last chat
```
**Details**:
- Permanently removes session and all conversation history
- Cannot remove if only one chat remains
- If no number specified, removes the last chat
- Confirmation required for safety

### `/twist <target_chat> [message]`
**Purpose**: Copy AI response to another chat  
**Usage**:
```bash
/twist 2 "Can you help me debug this Python code?"
/twist 1 "What do you think about this creative concept?"
```
**Details**:
- **Core Feature**: Enables cross-chat communication
- Sends message to target chat and copies response back
- Each chat maintains its own context and system prompt
- Creates collaborative AI workflows between different chat sessions

## ⚙️ Model Configuration

Commands for managing the shared Ollama model and chat session settings.

### `/model [model_name]`
**Purpose**: Switch the underlying Ollama model (affects all chat sessions)  
**Usage**:
```bash
/model                    # List available models
/model llama2            # Switch to llama2
/model mistral:latest    # Switch to specific model version
```
**Details**:
- **Global Effect**: Changes model for ALL chat sessions
- All sessions immediately use new model
- Maintains individual system prompts and histories

### `/system [new_prompt]`
**Purpose**: Set/update system prompts for current chat session  
**Usage**:
```bash
/system                                    # View current system prompt
/system You are a senior software architect specializing in Python microservices
```
**Details**:
- Defines chat session's AI role, expertise, and behavior
- Changes take effect immediately for new messages
- Core mechanism for creating distinct AI personalities

### `/setctx <context_size>`
**Purpose**: Set context window size  
**Usage**: `/setctx 4096`  
**Details**:
- Controls how much conversation history the model remembers
- Affects memory usage and response quality
- Larger contexts = better memory but slower responses

### `/toggle_eval`
**Purpose**: Toggle evaluation data display  
**Usage**: `/toggle_eval`  
**Aliases**: `/eval`  
**Details**:
- Shows/hides model evaluation metrics during responses
- Useful for monitoring model performance

### `/toggle_think`
**Purpose**: Toggle thinking mode display  
**Usage**: `/toggle_think`  
**Aliases**: `/think`  
**Details**:
- Shows/hides model reasoning process during responses
- Useful for understanding how the AI arrives at answers

## 📝 Prompt Management

Commands for saving, managing, and using prompt templates.

### `/prompt <slot_number>`
**Purpose**: Use a saved prompt  
**Usage**: `/prompt 1`  
**Details**:
- Loads and uses a previously saved prompt
- Prompts are saved in numbered slots
- Useful for frequently used system prompts or templates

### `/setprompt <slot> <prompt_text>`
**Purpose**: Save a prompt to a slot  
**Usage**: `/setprompt 1 You are a Python expert specializing in web development`  
**Details**:
- Saves prompt text to a numbered slot for later use
- Create reusable prompt templates
- No quotes needed around prompt text

### `/showprompt`
**Purpose**: Display saved prompts  
**Usage**: `/showprompt`  
**Aliases**: `/prompts`  
**Details**:
- Lists all saved prompt slots and their contents
- Shows which slots are available for new prompts
- Helps manage your prompt library

## 📚 History & Logging

Commands for managing conversation history and logging.

### `/clear`
**Purpose**: Reset conversation history  
**Usage**: `/clear`  
**Details**:
- Removes all conversation history from current chat session
- Preserves system prompt and chat configuration
- Useful for starting fresh conversations with same setup

### `/history [limit]`
**Purpose**: Show chat history  
**Usage**:
```bash
/history        # Show recent history
/history 20     # Show last 20 messages
```
**Aliases**: `/hist`  
**Details**:
- Displays conversation history for current session
- Optionally limit number of messages shown
- Useful for reviewing previous conversations

### `/export [filename]`
**Purpose**: Export chat history  
**Usage**:
```bash
/export                    # Export with default filename
/export my_conversation    # Export with custom filename
```
**Details**:
- Saves conversation history to file
- Creates portable backup of conversations
- Useful for sharing or archiving important discussions

### `/toggle_log`
**Purpose**: Toggle unified logging  
**Usage**: `/toggle_log`  
**Aliases**: `/log`  
**Details**:
- Enable/disable logging of all conversations to unified log
- When enabled, all chats are logged to a daily file
- Useful for keeping comprehensive records

### `/unified_log`
**Purpose**: View unified log for today  
**Usage**: `/unified_log`  
**Aliases**: `/viewlog`  
**Details**:
- Shows today's unified log containing all chat activity
- Useful for reviewing all conversations across sessions
- Only available when unified logging is enabled

## 📁 File Operations

Commands for working with external files.

### `/load <filepath> <prompt>`
**Purpose**: Load and send file with prompt  
**Usage**: `/load code.py "Please review this Python code"`  
**Details**:
- Loads content from specified file
- Combines file content with your prompt
- Supports text files with automatic encoding detection
- Useful for code review, document analysis, etc.

## 🔧 General Commands

Essential system commands for help, configuration, and application control.

### `/help [command]`
**Purpose**: Show comprehensive command reference  
**Usage**:
```bash
/help              # Show all commands
/help twist        # Detailed help for specific command
```
**Aliases**: `/h`  
**Details**:
- Interactive command documentation
- Examples and usage patterns
- Category-based organization

### `/quit`
**Purpose**: Exit and save configuration  
**Usage**: `/quit`  
**Aliases**: `/q`, `/exit`  
**Details**:
- Safely exits the application
- Automatically saves current configuration
- Preserves all chat sessions and settings

### `/resetchat`
**Purpose**: Reset chat to factory defaults  
**Usage**: `/resetchat`  
**Details**:
- Resets current chat session to default settings
- Clears conversation history and system prompt
- Confirmation required for safety

### `/showvars`
**Purpose**: Display current system variables  
**Usage**: `/showvars`  
**Aliases**: `/vars`  
**Details**:
- Shows current configuration settings
- Displays model parameters and session info
- Useful for troubleshooting and system monitoring

## 🔧 Command Aliases

Many commands have shorter aliases for faster typing:

| Command | Aliases |
|---------|---------|
| `/help` | `/h` |
| `/quit` | `/q`, `/exit` |
| `/history` | `/hist` |
| `/showprompt` | `/prompts` |
| `/showvars` | `/vars` |
| `/toggle_eval` | `/eval` |
| `/toggle_think` | `/think` |
| `/toggle_log` | `/log` |
| `/unified_log` | `/viewlog` |

## 💡 Usage Patterns

### Creating Specialized AI Teams
```bash
# Create a development team
/addchat
/system You are a senior Python developer focusing on clean, maintainable code

/addchat  
/system You are a QA engineer specializing in test automation and edge cases

/addchat
/system You are a technical writer who creates clear, comprehensive documentation

# Have them collaborate
/switch 1
User: "Here's my code for review"
/twist 2 "Can you create test cases for this code?"
/twist 3 "Please document this function"
```

### Multi-Perspective Analysis
```bash
# Create different analytical perspectives
/addchat
/system You are an optimistic business analyst focusing on opportunities

/addchat
/system You are a risk-averse security expert identifying potential threats

/addchat
/system You are a pragmatic engineer focused on implementation feasibility

# Cross-reference insights
/switch 1
User: "What opportunities do you see in this project?"
/twist 2 "What are the main security concerns?"
/twist 3 "How feasible is implementation given current constraints?"
```

### Creative Collaboration
```bash
# Creative writing team
/addchat
/system You are a plot-driven storyteller focused on compelling narratives

/addchat
/system You are a character development expert creating deep, relatable personalities

/addchat
/system You are a dialogue specialist crafting authentic conversations

# Collaborative story creation
/switch 1
User: "Create an opening scene for a sci-fi thriller"
/twist 2 "Develop the main character based on this opening"
/twist 3 "Write dialogue that reveals character motivation"
```

## 🚀 Tips for Power Users

1. **Use `/setprompt` for templates**: Save frequently used system prompts
2. **Leverage `/twist` for complex workflows**: Chain multiple AI experts together
3. **Monitor with `/showvars`**: Keep track of current settings and model
4. **Use `/export` regularly**: Backup important conversations
5. **Experiment with system prompts**: Small changes create dramatically different AI behaviors
6. **Enable `/toggle_log`**: Keep comprehensive records of all interactions

## 🔮 Upcoming Commands

Future command additions being considered:

- `/rename` - Give descriptive names to chat sessions
- `/list` - View all active chat sessions with their names
- `/copy` - Duplicate chat session configurations
- `/save` - Save specific chat sessions to files
- `/config` - Advanced configuration management
- `/status` - Show detailed system status
- `/debug` - Technical diagnostics and troubleshooting
- `/search` - Find content across all chat sessions
- `/merge` - Combine insights from multiple chat sessions
- `/template` - Save/load chat session templates
- `/collaborate` - Multi-session group conversations

---

**Command System**: *Orchestrating AI personalities for maximum collaboration* 🎭⚡✨
