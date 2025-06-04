# HiOllama Command Reference

A unified and structured command reference for managing HiOllama chat sessions, models, prompts, history, files, and plugins.

---

## 🔄 Chat Session Management

| Command        | Description                         |
| -------------- | ----------------------------------- |
| `/chat.add`    | Start a new chat session            |
| `/chat.switch` | Switch to a different session       |
| `/chat.remove` | Remove a session                    |
| `/chat.twist`  | Copy AI response to another session |
| `/chat.reset`  | Reset session to defaults           |

## 🧠 Model Control

| Command            | Description                 |
| ------------------ | --------------------------- |
| `/model.switch`    | Change the current model    |
| `/model.setctx`    | Set max context window size |
| `/model.eval on`   | Enable evaluation display   |
| `/model.eval off`  | Disable evaluation display  |
| `/model.think on`  | Enable thinking display     |
| `/model.think off` | Disable thinking display    |

## 💬 Prompt Management

| Command               | Description             |
| --------------------- | ----------------------- |
| `/prompt.use <#>`     | Use a saved prompt      |
| `/prompt.set <#>`     | Save the current prompt |
| `/prompt.list`        | List all saved prompts  |

## 📜 History & Logging

| Command           | Description                    |
| ----------------- | ------------------------------ |
| `/history.clear`  | Clear the current chat history |
| `/history.show`   | View the current chat history  |
| `/history.export` | Export the chat log            |
| `/log.on`         | Enable unified logging         |
| `/log.off`        | Disable unified logging        |
| `/log.today`      | View today's unified log       |

## 📂 File Management

| Command      | Description                           |
| ------------ | ------------------------------------- |
| `/file.load` | Load a file and send it with a prompt |

## 🛠️ Plugin System

| Command               | Description                          |
| --------------------- | ------------------------------------ |
| `/plugin.list`        | List all available plugins           |
| `/plugin.info <name>` | Get details for a specific plugin    |
| `/plugin.reload`      | Reload all plugins (for development) |

## ⚙️ System & Misc

| Command     | Description                   |
| ----------- | ----------------------------- |
| `/sys.vars` | Show current system variables |
| `/sys.help` | Show this command reference   |
| `/sys.quit` | Exit and save configuration   |

## 🗺️ Command Mapping (Old → New)

| Old Command       | New Command           |
| ----------------- | --------------------- |
| `/addchat`        | `/chat.add`           |
| `/switch`         | `/chat.switch`        |
| `/removechat`     | `/chat.remove`        |
| `/twist`          | `/chat.twist`         |
| `/model`          | `/model.switch`       |
| `/setctx`         | `/model.setctx`       |
| `/toggle_eval`    | `/model.eval on/off`  |
| `/toggle_think`   | `/model.think on/off` |
| `/prompt`         | `/prompt.use <name>`  |
| `/setprompt`      | `/prompt.save <name>` |
| `/showprompt`     | `/prompt.list`        |
| `/clear`          | `/history.clear`      |
| `/history`        | `/history.show`       |
| `/export`         | `/history.export`     |
| `/toggle_log`     | `/log.on/off`         |
| `/unified_log`    | `/log.today`          |
| `/load`           | `/file.load`          |
| `/help`           | `/sys.help`           |
| `/quit`           | `/sys.quit`           |
| `/resetchat`      | `/chat.reset`         |
| `/showvars`       | `/sys.vars`           |
| `/plugins`        | `/plugin.list`        |
| `/plugin`         | `/plugin.info <name>` |
| `/reload_plugins` | `/plugin.reload`      |

/system prompt is not to be touched, we will be changing it drastically in the future which at that point we will change it's name