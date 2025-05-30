# Manual Command Testing Checklist

This file provides a manual testing checklist for HiOllama commands since automated testing of interactive commands can be complex.

## Quick Command Test

Run HiOllama and test these commands manually:

```bash
python -m hiollama 2
```

### Core Commands to Test:

1. **Help System**
   ```
   /help
   ```
   ✅ Should display: "GLOBAL HELP MENU" with all command categories

2. **Show Variables**
   ```
   /showvars
   ```
   ✅ Should display: "CHAT 1 VARIABLES" with model, history, settings

3. **Model Selection**
   ```
   /model
   ```
   ✅ Should display: "Available Ollama models:" with numbered list

4. **Show Prompts**
   ```
   /showprompt all
   ```
   ✅ Should display: "SYSTEM PROMPTS FOR ALL CHATS" with each chat's prompt

5. **History**
   ```
   /history
   ```
   ✅ Should display: "No messages in history" (for new session)

6. **Switch Chats**
   ```
   /switch 2
   ```
   ✅ Should switch to chat 2 (indicator changes from "> 1:" to "> 2:")

7. **Toggle Settings**
   ```
   /toggle_log
   /toggle_eval
   ```
   ✅ Each should show confirmation message about the setting change

8. **Exit Cleanly**
   ```
   /quit
   ```
   ✅ Should display: "Exiting and saving configurations."

## Extended Testing

### Multi-Chat Testing
Test with different chat counts:
- `python -m hiollama 1` (single chat)
- `python -m hiollama 4` (default)
- `python -m hiollama 14` (maximum)

### UI Elements
- ✅ Rainbow colored chat headers
- ✅ Active chat marked with ">" 
- ✅ System prompt previews truncated with "..."
- ✅ Proper switch hints: "(/switch [1-N] to change)"

### Error Handling
Test invalid commands:
- `/invalid` - Should show "Unknown command"
- `/switch 999` - Should show error for invalid chat number

## Expected Output Examples

### /help Output:
```
| GLOBAL HELP MENU General Commands:
 /help Show this help menu.
 /quit Exit the program and save the configuration.
 /showvars Display current system variables.
 ...
```

### /showvars Output:
```
| CHAT 1 VARIABLES

| Selected Model: gemma3:12b-it-q4_K_M
| Max History: 4
| Verbosity: True
| Think Filtering: True
| Logging Enabled: True
| Config Path: ~/.hiollama_config_unified.json
| Log Directory: ~/hiollama_logs
| System Prompt: [current prompt text]
```

---

**Note:** If you encounter any command that doesn't work as expected, it indicates a real bug that should be investigated.
