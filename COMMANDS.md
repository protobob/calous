# CALOUS Commands Reference

Complete reference for all 38 available commands in CALOUS's hierarchical command system.

## 🎯 Chat Navigation Commands

### `/chat.add`
**Description**: Add a new chat session  
**Usage**: `/chat.add`  
**Example**: `/chat.add` - Creates a new chat session

### `/chat.switch [NUMBER]`
**Description**: Switch between chat sessions  
**Usage**: `/chat.switch [chat_number]`  
**Examples**: 
- `/chat.switch 2` - Switch to chat 2
- `/chat.switch` - Cycle to next chat

### `/chat.remove [NUMBER]`
**Description**: Remove a chat session  
**Usage**: `/chat.remove [chat_number]`  
**Examples**:
- `/chat.remove 3` - Removes chat 3
- `/chat.remove` - Removes the last chat

### `/chat.twist [NUMBER]`
**Description**: Copy the last AI response to another chat  
**Usage**: `/chat.twist [target_chat]`  
**Examples**:
- `/chat.twist 2` - Send last response to chat 2
- `/chat.twist` - Send to next available chat

### `/chat.reset`
**Description**: Reset current chat to factory defaults  
**Usage**: `/chat.reset`  
**Example**: `/chat.reset` - Resets current chat with confirmation

---

## 🤖 Model Management Commands

### `/model.switch`
**Description**: Change the current model  
**Usage**: `/model.switch`  
**Example**: `/model.switch` - Interactive model selection

### `/model.setctx [SIZE]`
**Description**: Set max context window size  
**Usage**: `/model.setctx [context_size]`  
**Examples**:
- `/model.setctx 4096` - Set context to 4096 tokens
- `/model.setctx` - Interactive context setting

### `/model.eval`
**Description**: Toggle evaluation display  
**Usage**: `/model.eval`  
**Example**: `/model.eval` - Toggle showing model evaluation metrics

### `/model.think`
**Description**: Toggle thinking display  
**Usage**: `/model.think`  
**Example**: `/model.think` - Show/hide model reasoning process

---

## 💬 Prompt Management Commands

### `/prompt.use <SLOT>`
**Description**: Use a saved prompt  
**Usage**: `/prompt.use <slot_number>`  
**Example**: `/prompt.use 1` - Use prompt saved in slot 1

### `/prompt.set <SLOT> <PROMPT>`
**Description**: Save a prompt to a slot  
**Usage**: `/prompt.set <slot_number> <prompt_text>`  
**Example**: `/prompt.set 1 You are a helpful coding assistant`

### `/prompt.list [SLOT]`
**Description**: List all saved prompts  
**Usage**: `/prompt.list [slot_number]`  
**Examples**:
- `/prompt.list` - Show all saved prompts
- `/prompt.list 1` - Show prompt in slot 1

---

## 👤 Persona Management Commands

### `/persona.name <NAME>`
**Description**: Set the persona name  
**Usage**: `/persona.name <persona_name>`  
**Example**: `/persona.name Assistant` - Set persona name to "Assistant"

### `/persona.set <SLOT> <CONTENT>`
**Description**: Set a system prompt at slot 0-9  
**Usage**: `/persona.set <slot> <content>`  
**Example**: `/persona.set 0 You are a helpful assistant`

### `/persona.get <SLOT>`
**Description**: View contents of a specific slot  
**Usage**: `/persona.get <slot_number>`  
**Example**: `/persona.get 0` - View slot 0 contents

### `/persona.clear <SLOT>`
**Description**: Clear contents of a specific slot  
**Usage**: `/persona.clear <slot_number>`  
**Example**: `/persona.clear 0` - Clear slot 0

### `/persona.show`
**Description**: Show current name and all slot contents  
**Usage**: `/persona.show`  
**Example**: `/persona.show` - Display complete persona state

### `/persona.save`
**Description**: Save current persona  
**Usage**: `/persona.save`  
**Example**: `/persona.save` - Save current persona configuration

### `/persona.load <NAME>`
**Description**: Load a saved persona by name  
**Usage**: `/persona.load <persona_name>`  
**Example**: `/persona.load Assistant` - Load "Assistant" persona

### `/persona.list`
**Description**: List all saved personas  
**Usage**: `/persona.list`  
**Example**: `/persona.list` - Show all available personas

### `/persona.delete <NAME>`
**Description**: Delete a saved persona file  
**Usage**: `/persona.delete <persona_name>`  
**Example**: `/persona.delete Assistant` - Delete "Assistant" persona

### `/persona.reset`
**Description**: Clear name and all slot contents  
**Usage**: `/persona.reset`  
**Example**: `/persona.reset` - Reset entire persona to defaults

---

## 📜 Chat History Commands

### `/history.show`
**Description**: View the current chat history  
**Usage**: `/history.show`  
**Example**: `/history.show` - Display current chat's message history

### `/history.clear`
**Description**: Clear the current chat history  
**Usage**: `/history.clear`  
**Example**: `/history.clear` - Clear current chat with confirmation

### `/log.on`
**Description**: Enable unified logging  
**Usage**: `/log.on`  
**Example**: `/log.on` - Enable logging of all chat activities

### `/log.off`
**Description**: Disable unified logging  
**Usage**: `/log.off`  
**Example**: `/log.off` - Disable unified logging

### `/log.today`
**Description**: View today's unified log  
**Usage**: `/log.today`  
**Example**: `/log.today` - Show today's complete activity log

---

## 📁 File Operations Commands

### `/file.load <PATH> <PROMPT>`
**Description**: Load a file and send it with a prompt  
**Usage**: `/file.load <filepath> <prompt_text>`  
**Example**: `/file.load script.py Explain this code` - Load and analyze a Python file

---

## ⚙️ System Commands

### `/sys.help` (alias: `/help`)
**Description**: Show command reference  
**Usage**: `/sys.help` or `/help`  
**Example**: `/help` - Display comprehensive help menu

### `/sys.quit` (alias: `/quit`)
**Description**: Exit and save configuration  
**Usage**: `/sys.quit` or `/quit`  
**Example**: `/quit` - Exit application and save settings

### `/sys.vars`
**Description**: Show current system variables  
**Usage**: `/sys.vars`  
**Example**: `/sys.vars` - Display current configuration values

---

## 🔗 Alias Management Commands

### `/alias.add <ALIAS> <COMMAND>`
**Description**: Create a new command alias  
**Usage**: `/alias.add <alias_name> <target_command>`  
**Example**: `/alias.add t chat.twist` - Create "t" as shortcut for twist

### `/alias.remove <ALIAS>`
**Description**: Remove a command alias  
**Usage**: `/alias.remove <alias_name>`  
**Example**: `/alias.remove t` - Remove the "t" alias

### `/alias.list`
**Description**: List all command aliases  
**Usage**: `/alias.list`  
**Example**: `/alias.list` - Show all defined aliases

### `/alias`
**Description**: Show alias command help  
**Usage**: `/alias`  
**Example**: `/alias` - Display alias management help

---

## 🔌 Plugin Commands

### `/plugin.list`
**Description**: List all available plugins  
**Usage**: `/plugin.list`  
**Example**: `/plugin.list` - Show all plugins and their status

### `/plugin.info <NAME>`
**Description**: Get details for a specific plugin  
**Usage**: `/plugin.info <plugin_name>`  
**Example**: `/plugin.info calculator` - Show calculator plugin details

### `/plugin.reload`
**Description**: Reload all plugins (for development)  
**Usage**: `/plugin.reload`  
**Example**: `/plugin.reload` - Refresh all plugins from disk

---

## 📝 Notes

- **Command Format**: All commands start with `/` and use dot notation (e.g., `/chat.add`)
- **Optional Parameters**: Parameters in `[brackets]` are optional
- **Required Parameters**: Parameters in `<brackets>` are required
- **Multi-word Arguments**: Use quotes for arguments with spaces, or commands will handle multiple words automatically
- **Case Sensitivity**: Commands are case-sensitive
- **Aliases**: Some commands have shortcuts (shown in parentheses)
- **Help**: Use `/help` or `/sys.help` for interactive help within the application

**Total Commands**: 38 registered commands across 7 categories
