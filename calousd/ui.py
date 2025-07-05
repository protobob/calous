"""User interface elements for Hi, Ollama!"""
from .utils import get_chat_color, print_message_with_bar, find_last_messages
from .constants import APP_VERSION, MAX_PREVIEW_LENGTH
from .config import ConfigManager
from .unified_logger import unified_logger
from typing import Dict, Any
import os






class UIManager:
    def __init__(self, app):
        self.app = app
        
    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or discard if no client connected."""
        if hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode and self.app.session_manager.current_connection:
            self.app.session_manager.send_to_client(message, message_type)
        # In daemon mode with no client: discard output silently
        
    def help_menu(self):
        """Display the new streamlined help menu."""
        command_color = "grey50"
        
        help_text = f"\n[1;37mGLOBAL HELP[0m\n\n"
        help_text += f"[37mCALOUS is a multi-channel chat service for local LLM models. Each chat[0m\n"
        help_text += f"[37mchannel (1-14) maintains its own conversation history and persona, allowing you[0m\n"
        help_text += f"[37mto quickly switch between different AI contexts and personalities.[0m\n\n"
        help_text += f"[37mGETTING STARTED[0m\n\n"
        help_text += f"[37mFirst time? Try these commands:[0m\n\n"
        
        self._output(help_text)
        
        self._output(f"[37mChoose a model:      [0m\033[1m\033[90m/model.switch\033[0m")
        self._output(f"[37mSwitch channels:     [0m\033[1m\033[90m/chat.switch 2\033[0m")
        self._output(f"[37mSet a system prompt: [0m\033[1m\033[90m/persona.set 0 You are a helpful coding assistant\033[0m")
        self._output(f"[37mName your AI:        [0m\033[1m\033[90m/persona.name Assistant\033[0m")
        self._output(f"[37mTry twist feature:   [0m\033[1m\033[90m/chat.twist 3\033[0m")
        self._output(f"[37mView chat history:   [0m\033[1m\033[90m/history.show\033[0m")
        self._output(f"[37mAdd a command alias: [0m\033[1m\033[90m/alias.add h sys.help\033[0m")
        self._output("")
        self._output(f"[37mCATEGORY HELP[0m\n")
        self._output(f"[37mChat Management      (7 commands)   [0m\033[1m\033[90m/sys.help chat\033[0m")
        self._output(f"[37mModel Operations     (7 commands)   [0m\033[1m\033[90m/sys.help model\033[0m")
        self._output(f"[37mPersona Management  (11 commands)   [0m\033[1m\033[90m/sys.help persona\033[0m")
        self._output(f"[37mHistory Management   (9 commands)   [0m\033[1m\033[90m/sys.help history\033[0m")
        self._output(f"[37mLogging Operations   (5 commands)   [0m\033[1m\033[90m/sys.help log\033[0m")
        self._output(f"[37mPrompt Management    (4 commands)   [0m\033[1m\033[90m/sys.help prompt\033[0m")
        self._output(f"[37mFile Operations      (1 command)    [0m\033[1m\033[90m/sys.help file\033[0m")
        self._output(f"[37mSystem Commands      (2 commands)   [0m\033[1m\033[90m/sys.help sys\033[0m")
        self._output(f"[37mAlias Management     (4 commands)   [0m\033[1m\033[90m/sys.help alias\033[0m")
        self._output(f"[37mPlugin System        (4 commands)   [0m\033[1m\033[90m/sys.help plugin\033[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f"\033[1m\033[90m/sys.help category\033[0m     [37mDetailed commands for a category[0m")
        self._output(f"\033[1m\033[90m/sys.help command\033[0m      [37mSpecific help for any command[0m")
        self._output(f"\033[1m\033[90m/sys.help all\033[0m          [37mList of all commands[0m")
        self._output("")

    def help_menu_all(self):
        """Display the comprehensive help menu with all commands."""
        
        # Get num_chats dynamically from session manager
        num_chats = self.app.session_manager.num_chats if hasattr(self.app, 'session_manager') and self.app.session_manager else ConfigManager.get_num_chats()

        self._output(f"\n[1;37mGLOBAL HELP MENU[0m\n")
        
        # System Commands
        self._output("System Commands:")
        self._output("  /sys.help                Show streamlined help overview")
        self._output("  /sys.help all            Show this comprehensive help menu")
        self._output("")

        # Chat Commands
        self._output("Chat Commands:")
        self._output(f"  /chat.switch [NUMBER]    Switch between chats (1-{num_chats}). Default switches to next chat")
        self._output(f"  /chat.twist [NUMBER]     Copy AI's last response to target chat (1-{num_chats}). Default uses next chat")
        self._output("  /chat.reset              Reset chat to factory defaults")
        self._output("  /chat.vars               Display chat-specific variables only")
        self._output("")

        # Model Commands
        self._output("Model Commands:")
        self._output("  /model.switch [MODEL]    Select a different model. Use without arguments to see available models")
        self._output("  /model.setctx NUMBER     Set context window size")
        self._output("  /model.eval on/off       Toggle evaluation data display after responses")
        self._output("  /model.think on/off      Toggle thinking mode (show/hide model reasoning)")
        self._output("  /model.vars              Display model-related variables only")
        self._output("")

        # Prompt Commands
        self._output("Prompt Commands:")
        self._output("  /prompt.set NUM TEXT     Set a saved prompt")
        self._output("  /prompt.use NUMBER       Use a saved prompt")
        self._output("  /prompt.list [NUMBER]    Display saved prompts")
        self._output("")

        # Persona Commands
        self._output("Persona Commands:")
        self._output("  /persona.set SLOT TEXT   Set content for persona slot (0-9)")
        self._output("  /persona.get [SLOT]      Get content from persona slot or show all slots")
        self._output("  /persona.clear [SLOT]    Clear persona slot or all slots")
        self._output("  /persona.name [NAME]     Set or get persona name")
        self._output("  /persona.show            Show complete persona information")
        self._output("  /persona.reset           Reset persona to default state")
        self._output("  /persona.save            Save current persona to file")
        self._output("  /persona.load NAME       Load persona from file")
        self._output("  /persona.list            List all saved personas")
        self._output("  /persona.delete NAME     Delete a saved persona file")
        self._output("")

        # History Commands
        self._output("History Commands:")
        self._output("  /history.show            Display the current chat history")
        self._output("  /history.clear           Clear the current chat history")
        self._output("  /history.on              Enable chat history recording")
        self._output("  /history.off             Disable chat history recording")
        self._output("  /history.vars            Show history status and message count")
        self._output("  /history.save NAME       Save current chat history to a file")
        self._output("  /history.load NAME       Load chat history from a file (overwrites current history)")
        self._output("  /history.list            List all saved chat history files")
        self._output("  /history.delete NAME     Delete a saved chat history file")
        self._output("  /history.purge NUM       Delete the most recent N messages from current chat history")
        self._output("")

        # Context Commands
        self._output("Context Commands:")
        self._output("  /context.save NAME       Save current context (persona, prompts, history) to file")
        self._output("  /context.load NAME       Load context from file (overwrites current data)")
        self._output("  /context.list            List all saved context files")
        self._output("  /context.delete NAME     Delete a saved context file")
        self._output("")

        # Log Commands
        self._output("Log Commands:")
        self._output("  /log.on                  Enable logging of chat history")
        self._output("  /log.off                 Disable logging of chat history")
        self._output("  /log.today               View unified log for today")
        self._output("  /log.vars                Display logging-related variables only")
        self._output("")

        # File Commands
        self._output("File Commands:")
        self._output("  /file.load FILE PROMPT   Load a file as a prompt")
        self._output("")

        # Plugin Commands
        self._output("Plugin Commands:")
        self._output("  /plugin.list             List all available plugins")
        self._output("  /plugin.info NAME        Get information about a specific plugin")
        self._output("  /plugin.reload           Reload the plugin system")
        self._output("")

        # Alias Commands
        self._output("Alias Commands:")
        self._output("  /alias.add               Create a new command alias")
        self._output("  /alias.remove            Remove a command alias")
        self._output("  /alias.list              List all command aliases")
        self._output("")
    
    def display_active_chats_overview(self):
        """Display overview of all configured chats."""
        # Get num_chats and chat instances via session manager
        if hasattr(self.app, 'session_manager') and self.app.session_manager:
            num_chats = self.app.session_manager.num_chats
            chat_instances = self.app.session_manager.get_all_chats()
        else:
            # Fallback for standalone operation
            num_chats = ConfigManager.get_num_chats()
            chat_instances = [self.app]  # Just show current app
        
        # Always use the dynamic version
        switch_hint = f"/switch [1-{num_chats}] to change" if num_chats > 1 else ""
        
        self._output(f"[1;37mACTIVE CHATS:[0m [90m({switch_hint})[0m")        
        for i, chat in enumerate(chat_instances):
            chat_color_for_chat = get_chat_color(i)
            
            # Get persona name and truncate if needed
            if hasattr(chat, 'persona') and chat.persona:
                persona_text = chat.persona.name or '[Unnamed persona]'
            else:
                # Fallback to old system_prompt for backwards compatibility
                persona_text = '[Legacy system prompt]'
            if len(persona_text) > MAX_PREVIEW_LENGTH:
                persona_text = persona_text[:MAX_PREVIEW_LENGTH] + "..."
            
            # Mark active chat with arrow (using ASCII character for Windows compatibility)            
            prefix = ">" if i == self.app.active_chat_index else " "
            
            self._output(f"{prefix} \033[1m{chat_color_for_chat}{i + 1}:\033[0m [37m{persona_text}[0m")
        
        self._output("")  # Add spacing after overview
    
    def generate_prompt_text(self):
        """Generate the formatted prompt text shown before user input."""
        # Determine color based on chat index
        chat_index = getattr(self.app, 'active_chat_index', 0)
        chat_color = get_chat_color(chat_index)
        # Get context window usage percentage
        context_display = "Context: ??"
        if self.app.selected_model:
            usage_percentage = self.app.model.get_context_usage_percentage(self.app.selected_model)
            if usage_percentage is not None:
                # Determine color based on percentage ranges
                if usage_percentage <= 24:
                    percentage_color = "\033[32m"  # green
                elif usage_percentage <= 49:
                    percentage_color = "\033[33m"  # yellow
                elif usage_percentage <= 74:
                    percentage_color = "\033[38;5;208m"  # orange1
                else:  # 75-100
                    percentage_color = "\033[31m"  # red
                
                context_display = f"Context: {percentage_color}{usage_percentage:.0f}%\033[0m"
        # Remove the YOU: prompt entirely
        return (
            f"\n"
            f"[90m(type /help for help)[0m\n"
            f"\033[1m{chat_color}|\033[0m \033[3m[37m{context_display}[0m\033[0m - YOU:"
        )

    def get_user_input(self):
        """Get user input with formatted prompt."""
        prompt_text = self.generate_prompt_text()
        lines = prompt_text.splitlines()
        for line in lines:
            self._output(line)
        user_input = input()
        return user_input.strip()
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_model_variables(self):
        """Display model-related variables only."""
        chat_color = get_chat_color(getattr(self.app, 'active_chat_index', 0))
        
        self._output(f"\n[1mMODEL VARIABLES[0m\n")
        
        # Handle case where no model is selected
        if not self.app.selected_model:
            self._output(f"{'Selected Model:':<20} [31mNone selected[0m")
            self._output(f"{'Status:':<20} [33mUse /model.switch to select a model[0m")
        else:
            self._output(f"{'Selected Model:':<20} [32m{self.app.selected_model}[0m")
        
        # Show model info
        if self.app.selected_model:
            context_info = self.app.model.get_context_window_info(self.app.selected_model)
            if context_info:
                # Show model info (without tokenizer details)
                model_info = f"{context_info.architecture}"
                if context_info.parameter_count != 'unknown':
                    model_info += f" ({context_info.parameter_count}"
                    if context_info.quantization != 'unknown':
                        model_info += f", {context_info.quantization}"
                        model_info += ")"                
                    elif context_info.quantization != 'unknown':
                        model_info += f" ({context_info.quantization})"
                self._output(f"{'Model Info:':<20} [37m{model_info}[0m")        # Context window information (now global)
        from .config import ConfigManager
        global_num_ctx = ConfigManager.get_global_num_ctx()
        
        # Always show global context window setting
        self._output(f"{'Context Window:':<20} [1;36m{global_num_ctx:,} tokens[0m")
        
        # Show VRAM management settings
        keep_alive = ConfigManager.get_keep_alive()
        self._output(f"{'Keep Alive:':<20} [1;35m{keep_alive}[0m")
        
        if self.app.selected_model:
            context_info = self.app.model.get_context_window_info(self.app.selected_model)
            usage_percentage = self.app.model.get_context_usage_percentage(self.app.selected_model)            
            if context_info:
                # Display context window with model's max context for reference
                if global_num_ctx != context_info.max_context:
                    self._output(f"{'Model Max Context:':<20} [37m{context_info.max_context:,} tokens[0m")
                
                # Show usage percentage with visual indicator
                if usage_percentage is not None:
                    # Create visual progress bar
                    bar_length = 10
                    filled_length = int(bar_length * usage_percentage / 100)
                    bar = "█" * filled_length + "░" * (bar_length - filled_length)
                    # Color the percentage based on usage level
                    if usage_percentage <= 24:
                        percentage_color = "\033[32m"  # green
                    elif usage_percentage <= 49:
                        percentage_color = "\033[33m"  # yellow
                    elif usage_percentage <= 74:
                        percentage_color = "\033[38;5;208m"  # orange1
                    else:  # 75-100
                        percentage_color = "\033[31m"  # red
                    
                    self._output(f"{'Context Usage:':<20} {percentage_color}{bar} {usage_percentage:.1f}%\033[0m")
                  # Show estimated VRAM usage for global context window
                user_context_info = context_info._replace(actual_context=global_num_ctx)
                vram_estimate = self.app.model.estimate_context_vram_usage(user_context_info)                
                if vram_estimate != "unknown":
                    self._output(f"{'Context VRAM:':<20} [33m{vram_estimate}[0m [90m(est.)[0m")
        else:
            # Show message when no model is selected
            self._output(f"{'Context Usage:':<20} [90mN/A (no model selected)[0m")
            self._output(f"{'Context VRAM:':<20} [90mN/A (no model selected)[0m")
        
        self._output("")

    def show_chat_variables(self):
        """Display chat-specific variables."""
        active_chat_index = getattr(self.app, 'active_chat_index', 0)
        verbosity = self.app.verbosity
        thinking_enabled = self.app.thinking_enabled
        temperature = self.app.temperature

        # Print Rich-formatted output for CLI
        chat_color = get_chat_color(active_chat_index)
        
        self._output(f"\n\033[1m{chat_color}CHAT {active_chat_index + 1} VARIABLES\033[0m\n")
        verbosity_color = "\033[32m" if verbosity else "\033[31m"  # green if True, red if False
        self._output(f"\033[1m{chat_color}|\033[0m {'Verbosity:':<20} \033[1m{verbosity_color}{verbosity}\033[0m")
        thinking_color = "\033[32m" if thinking_enabled else "\033[31m"  # green if True, red if False
        self._output(f"\033[1m{chat_color}|\033[0m {'Thinking Mode:':<20} \033[1m{thinking_color}{thinking_enabled}\033[0m")
        # Determine temperature color based on value
        if temperature == 0.0:
            temp_color = "\033[34m"  # blue
        elif temperature < 0.7:
            temp_color = "\033[32m"  # green
        elif temperature <= 1.0:
            temp_color = "\033[33m"  # yellow
        elif temperature <= 1.5:
            temp_color = "\033[38;5;208m"  # orange1
        else:
            temp_color = "\033[31m"  # red
        self._output(f"\033[1m{chat_color}|\033[0m {'Temperature:':<20} \033[1m{temp_color}{temperature}\033[0m")
        self._output("")
    
    def show_log_variables(self):
        """Display logging-related variables only."""
        chat_color = get_chat_color(getattr(self.app, 'active_chat_index', 0))
        
        # Get the actual paths from constants and objects
        from .constants import CONFIG_PATH, LOG_DIR
        
        # Add error handling for path operations
        try:
            config_path = str(CONFIG_PATH.relative_to(CONFIG_PATH.home()))
        except ValueError:
            config_path = str(CONFIG_PATH)
            
        try:
            log_dir = str(LOG_DIR.relative_to(LOG_DIR.home()))
        except ValueError:
            log_dir = str(LOG_DIR)
        
        self._output(f"\n[1mLOGGING VARIABLES[0m\n")
        
        logging_color = "\033[32m" if self.app.logging_enabled else "\033[31m"  # green if True, red if False
        self._output(f"{'Logging Enabled:':<20} \033[1m{logging_color}{self.app.logging_enabled}\033[0m")
        self._output(f"{'Config Path:':<20} [37m~/{config_path}[0m")        
        self._output(f"{'Log Directory:':<20} [37m~/{log_dir}[0m")
        
        # Show log file sizes if available
        try:
            from pathlib import Path
            log_path = Path(LOG_DIR)
            if log_path.exists():
                log_files = list(log_path.glob("*.log"))
                if log_files:
                    self._output(f"{'Log Files:':<20} [36m{len(log_files)}[0m files found")
                    # Show most recent log file
                    most_recent = max(log_files, key=lambda f: f.stat().st_mtime)
                    size_kb = most_recent.stat().st_size / 1024
                    self._output(f"{'Latest Log:':<20} [37m{most_recent.name}[0m ([33m{size_kb:.1f} KB[0m)")
        except Exception:
            pass  # Ignore errors when checking log files
        
        self._output("")

    def display_chat_context(self, chat_color: str) -> None:
        """Display the current chat context with active chats overview first."""
        # Show active chats overview at the top
        self.display_active_chats_overview()
        
        # Find last messages using utility function
        last_messages = find_last_messages(self.app.chat_history)
        
        # Only show chat header and context if there are messages
        if last_messages:
            # Show the current chat's detailed context
            from .utils import print_chat_header
            print_chat_header(self.app.active_chat_index, self._output)
            
            # Use the passed chat_color parameter instead of recalculating
            # Display the last user message
            if last_messages.get('user'):
                print_message_with_bar(chat_color, "YOU", last_messages['user'].get('content', ''), self._output)
            
            # Display the last assistant message
            if last_messages.get('assistant'):
                print_message_with_bar(chat_color, "LLM", last_messages['assistant'].get('content', ''), self._output)
    
    def show_category_help(self, category: str):
        """Display help for a specific command category."""
        from calousd.commands.registry import registry
        from calousd.commands.types import CommandCategory        # Map user-friendly category names to internal categories
        category_mapping = {
            'chat': CommandCategory.NAVIGATION,
            'model': CommandCategory.MODEL,
            'provider': CommandCategory.PROVIDER,
            'prompt': CommandCategory.PROMPT,
            'persona': CommandCategory.PERSONA,  # persona commands now have their own category
            'history': CommandCategory.HISTORY,
            'log': CommandCategory.LOGGING,     # log commands now have their own category
            'file': CommandCategory.FILE,
            'plugin': CommandCategory.PLUGIN,   # plugin commands now have their own category
            'alias': CommandCategory.ALIAS,     # alias commands now have their own category
            'context': CommandCategory.CONTEXT, # context commands for saving/loading state
            'sys': CommandCategory.GENERAL,
        }
        
        internal_category = category_mapping.get(category.lower())        
        if not internal_category:
            self._output(f"[1;31mError:[0m Unknown category '{category}'")
            self._output(f"[90mAvailable categories:[0m {', '.join(category_mapping.keys())}")
            return
        
        # Get commands for this category
        all_commands = registry.get_all_commands()
        category_commands = [cmd for cmd in all_commands.values() if cmd.category == internal_category]
        
        if not category_commands:
            self._output(f"[1;31mError:[0m No commands found for category '{category}'")
            return        # Special handling for persona category to match HELP.md format
        if category.lower() == 'persona':
            self._show_persona_help()
            return
          # Special handling for model category to match HELP.md format
        if category.lower() == 'model':
            self._show_model_help()
            return
        
        # Special handling for provider category to match HELP.md format
        if category.lower() == 'provider':
            self._show_provider_help()
            return
        
        # Special handling for prompt category to match HELP.md format
        if category.lower() == 'prompt':
            self._show_prompt_help()
            return
        
        # Special handling for alias category to match HELP.md format
        if category.lower() == 'alias':
            self._show_alias_help()
            return
          # Special handling for chat category to match HELP.md format
        if category.lower() == 'chat':
            self._show_chat_help()
            return
          # Special handling for log category to match HELP.md format
        if category.lower() == 'log':
            self._show_log_help()
            return
          # Special handling for history category to match HELP.md format
        if category.lower() == 'history':
            self._show_history_help()
            return
          # Special handling for plugin category to match HELP.md format
        if category.lower() == 'plugin':
            self._show_plugin_help()
            return
          # Special handling for sys category to match HELP.md format
        if category.lower() == 'sys':
            self._show_sys_help()
            return
        
        # Special handling for file category to match HELP.md format
        if category.lower() == 'file':
            self._show_file_help()
            return
        
        # Display category help
        category_title = category.upper()
        self._output(f"\n[1;37m{category_title} COMMANDS HELP[0m\n")
        
        # Sort commands by name for consistent display
        sorted_commands = sorted(category_commands, key=lambda x: x.name)
        
        for cmd in sorted_commands:
            # Include aliases in display
            aliases_str = ""
            if cmd.aliases:
                aliases_str = f" (aliases: {', '.join(cmd.aliases)})"
            self._output(f"  /{cmd.name}{aliases_str} - {cmd.description}")
        
        self._output("")
        self._output(f"  /sys.help {category.lower()} - shows this help screen")
        self._output(f"\n[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"\033[90mExample: /sys.help {sorted_commands[0].name}\033[0m")
    
    def show_command_help(self, command_name: str):
        """Display detailed help for a specific command."""
        from calousd.commands.registry import registry
        from calousd.commands.model.formatters import ModelFormatter
        from calousd.commands.alias.formatters import AliasFormatter
        
        # Remove leading slash if present
        if command_name.startswith('/'):
            command_name = command_name[1:]
        
        # Check if command exists
        all_commands = registry.get_all_commands()
        command_def = all_commands.get(command_name)
        
        if not command_def:
            # Check aliases
            for cmd_name, cmd_def in all_commands.items():
                if cmd_def.aliases and command_name in cmd_def.aliases:
                    command_def = cmd_def
                    command_name = cmd_name
                    break
        
        if not command_def:
            self._output(f"[1;31mError:[0m Unknown command '{command_name}'")
            self._output(f"[90mUse /sys.help to see all available commands[0m")
            return        # Handle special cases with existing help screens
        if command_name == "model.setctx":
            self._output(f"\n[1;37m| DETAILED HELP: /model.setctx[0m\n")
            # Leverage existing comprehensive help
            from calousd.commands.model.services import ModelService
            service = ModelService(self.app)
            formatter = ModelFormatter()
            formatter.format_current_context(service.get_current_context(), self.app.selected_model, service)
            self._output(f"\n[90mThis command accepts an optional context size parameter (2048-32768)[0m")
            return
        
        elif command_name.startswith("alias"):
            self._output(f"\n[1;37m| DETAILED HELP: /{command_name}[0m\n")
            # Leverage existing alias help
            AliasFormatter.print_alias_help()
            return
        
        # Generic command help for other commands
        self._output(f"\n[1;37m| DETAILED HELP: /{command_name}[0m\n")
        
        # Basic command information
        self._output(f"[1mCommand:[0m /{command_name}")
        self._output(f"[1mDescription:[0m {command_def.description}")
        self._output(f"[1mCategory:[0m {command_def.category}")
        
        if command_def.aliases:
            self._output(f"[1mAliases:[0m {', '.join(f'/{alias}' for alias in command_def.aliases)}")
        
        # Show usage based on parser configuration
        if hasattr(command_def.parser, '_actions'):
            positional_args = []
            optional_args = []
            
            for action in command_def.parser._actions:
                if action.dest in ['help']:
                    continue
                    
                if action.option_strings:  # Optional argument
                    opt_str = '/'.join(action.option_strings)
                    if action.nargs in ['?', '*']:
                        optional_args.append(f"[{opt_str}]")
                    else:
                        optional_args.append(f"{opt_str} <value>")
                else:  # Positional argument
                    if action.nargs in ['?', '*']:
                        positional_args.append(f"[{action.dest}]")
                    else:
                        positional_args.append(f"<{action.dest}>")
            
            usage_parts = [f"/{command_name}"]
            usage_parts.extend(positional_args)
            usage_parts.extend(optional_args)
            
            self._output(f"[1mUsage:[0m {' '.join(usage_parts)}")
        
        # Add category-specific help tips
        self._add_category_specific_tips(command_name, command_def.category)
        
        self._output(f"\n[90mUse /sys.help {command_def.category.lower().replace(' ', '').replace('management', '').replace('operations', '')} to see all {command_def.category.lower()} commands[0m")

    def _add_category_specific_tips(self, command_name: str, category: str):
        """Add helpful tips based on command category."""
        
        if "chat" in command_name.lower():
            self._output(f"\n[1;36m💡 Chat Tips:[0m")
            if "switch" in command_name:
                self._output(f"  • Use without number to cycle to next chat")
                self._output(f"  • Current chat is marked with '>' in chat overview")
            elif "twist" in command_name:
                self._output(f"  • Copies the AI's last response to another chat")
                self._output(f"  • Useful for continuing conversations in different contexts")
            elif "add" in command_name:
                self._output(f"  • New chats start with empty history and default persona")
            elif "remove" in command_name:
                self._output(f"  • Removing a chat permanently deletes its history")
        
        elif "model" in command_name.lower():
            self._output(f"\n[1;36m💡 Model Tips:[0m")
            if "switch" in command_name:
                self._output(f"  • Model selection applies globally to all chats")
                self._output(f"  • Requires Ollama to be running with available models")
            elif "setctx" in command_name:
                self._output(f"  • Larger contexts use more VRAM and may slow performance")
                self._output(f"  • 4096-8192 tokens work well for most conversations")
            elif "eval" in command_name:
                self._output(f"  • Shows token counts and generation speed after responses")
            elif "think" in command_name:
                self._output(f"  • Reveals the model's reasoning process (if supported)")
        
        elif "prompt" in command_name.lower() or "persona" in command_name.lower():
            self._output(f"\n[1;36m💡 Prompt/Persona Tips:[0m")
            if "set" in command_name:
                self._output(f"  • Personas can have multiple slots (0-9) for different purposes")
                self._output(f"  • Slot 0 is typically used for the main system prompt")
            elif "save" in command_name or "load" in command_name:
                self._output(f"  • Saved personas persist between sessions")
                self._output(f"  • Use descriptive names for easy identification")
        
        elif "history" in command_name.lower() or "log" in command_name.lower():
            self._output(f"\n[1;36m💡 History/Logging Tips:[0m")
            if "clear" in command_name:
                self._output(f"  • Clearing history is permanent and cannot be undone")
                self._output(f"  • Consider using /log.today to backup important conversations")
            elif "today" in command_name:
                self._output(f"  • Shows unified log across all chats for current day")
                self._output(f"  • Use /history.save to export important conversations")
        
        elif "file" in command_name.lower():
            self._output(f"\n[1;36m💡 File Tips:[0m")
            self._output(f"  • File operations can process multiple formats")
            self._output(f"  • Use drag-and-drop for quick file loading")
        
        elif "plugin" in command_name.lower():
            self._output(f"\n[1;36m💡 Plugin Tips:[0m")
            self._output(f"  • Plugins extend Hi, Ollama! functionality")
            self._output(f"  • Use /plugin.info to see detailed plugin information")
    
    def _show_persona_help(self):
        """Display persona help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mPERSONA COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe persona system allows you to create and edit a modular collection of system prompts that define how the model responds to your input, along with a name to identify the persona. You can save these personas to files and load them into the same or different chat instances for later use.[0m\n")
        
        self._output(f"[37mPERSONA MANAGEMENT[0m\n")
        
        self._output(f" \033[1m\033[90m/persona.name\033[0m    [37mSet the persona name[0m")
        self._output(f" \033[1m\033[90m/persona.set\033[0m     [37mSet a system prompt at slot 0-9[0m")
        self._output(f" \033[1m\033[90m/persona.get\033[0m     [37mView contents of a specific slot[0m")
        self._output(f" \033[1m\033[90m/persona.clear\033[0m   [37mClear contents of a specific slot[0m")
        self._output(f" \033[1m\033[90m/persona.show\033[0m    [37mShow current name + all slot contents[0m")
        self._output(f" \033[1m\033[90m/persona.reset\033[0m   [37mClear name and all slot contents[0m")
        self._output("")
        
        self._output(f"[37mFILE OPERATIONS[0m\n")
        
        self._output(f" \033[1m\033[90m/persona.save\033[0m    [37mSave current persona to file[0m")
        self._output(f" \033[1m\033[90m/persona.load\033[0m    [37mLoad a saved persona from file[0m")
        self._output(f" \033[1m\033[90m/persona.list\033[0m    [37mList all saved persona files[0m")
        self._output(f" \033[1m\033[90m/persona.delete\033[0m  [37mDelete a saved persona file[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/persona.help\033[0m    [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help persona.clear[0m")
    
    def _show_model_help(self):
        """Display model help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mMODEL COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe model system allows you to select and configure AI models for your conversations. Global settings affect all chat instances, while per-chat settings let you customize behavior for individual conversations.[0m\n")
        
        self._output(f"[37mGLOBAL[0m\n")
        
        self._output(f" \033[1m\033[90m/model.switch\033[0m   [37mChange the current model (shows list or select by number/name)[0m")
        self._output(f" \033[1m\033[90m/model.setctx\033[0m   [37mSet max context window size[0m")
        self._output(f" \033[1m\033[90m/model.vars\033[0m     [37mShow model-related variables[0m")
        self._output("")
        
        self._output(f"[37mPER CHAT INSTANCE[0m\n")
        
        self._output(f" \033[1m\033[90m/model.settemp\033[0m  [37mSet temperature parameter[0m")
        self._output(f" \033[1m\033[90m/model.eval\033[0m     [37mToggle evaluation display[0m")
        self._output(f" \033[1m\033[90m/model.think\033[0m    [37mToggle thinking display[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/model.help\033[0m     [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help model.eval[0m")
    
    def _show_alias_help(self):
        """Display alias help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mALIAS COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe alias system allows you to create custom shortcuts for frequently used commands. Aliases can simplify complex commands or provide alternative names that are easier to remember.[0m\n")
        
        self._output(f"[37mALIAS MANAGEMENT[0m\n")
        
        self._output(f" \033[1m\033[90m/alias.add\033[0m     [37mCreate a new command alias[0m")
        self._output(f" \033[1m\033[90m/alias.remove\033[0m  [37mRemove a command alias[0m")
        self._output(f" \033[1m\033[90m/alias.list\033[0m    [37mList all command aliases[0m")
        self._output(f" \033[1m\033[90m/alias.clear\033[0m   [37mClear all command aliases[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/alias.help\033[0m    [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help alias.add[0m")
    
    def _show_chat_help(self):
        """Display chat help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mCHAT COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe chat system manages multiple independent conversation sessions within a single application instance. You can switch between numbered chat sessions (1-N), add or remove sessions dynamically, and transfer AI responses between chats. Each chat maintains its own conversation history and persona settings while sharing the same AI model selection globally.[0m\n")
        
        self._output(f"[37mSESSION MANAGEMENT[0m\n")
        
        self._output(f" \033[1m\033[90m/chat.switch\033[0m  [37mSwitch between chat sessions[0m")
        self._output(f" \033[1m\033[90m/chat.reset\033[0m", "[37mReset current chat to factory defaults.[0m")
        self._output("")
        
        self._output(f"[37mCONTENT OPERATIONS[0m\n")
        
        self._output(f" \033[1m\033[90m/chat.twist\033[0m   [37mCopy AI response to another chat[0m")
        self._output("")
        
        self._output(f"[37mINFORMATION & SETTINGS[0m\n")
        
        self._output(f" \033[1m\033[90m/chat.vars\033[0m    [37mShow chat-specific variables[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/chat.help\033[0m    [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help chat.add[0m")
    
    def _show_log_help(self):
        """Display log help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mLOG COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe unified logging system provides centralized conversation tracking across all chat sessions. It maintains daily log files that capture conversations from every chat instance, creating a new log file each day. Logs are stored in the user's home directory under ~/.calous/logs/, allowing you to review your interaction history organized by date.[0m\n")
        
        self._output(f"[37mLOGGING CONTROL[0m\n")
        
        self._output(f" \033[1m\033[90m/log.on\033[0m     [37mEnable unified logging[0m")
        self._output(f" \033[1m\033[90m/log.off\033[0m    [37mDisable unified logging[0m")
        self._output("")
        
        self._output(f"[37mLOG VIEWING[0m\n")
        
        self._output(f" \033[1m\033[90m/log.today\033[0m  [37mView today's unified log[0m")
        self._output("")
        
        self._output(f"[37mINFORMATION & SETTINGS[0m\n")
        
        self._output(f" \033[1m\033[90m/log.vars\033[0m   [37mShow logging-related variables[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/log.help\033[0m   [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help log.today[0m")
    
    def _show_history_help(self):
        """Display history help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mHISTORY COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe chat history system manages conversation records for individual chat sessions. Each chat maintains its own separate history that is automatically saved to file, ensuring your conversations persist between sessions and are not lost when you close and reopen the application. You can also control whether history recording is enabled or disabled per chat - useful for conversations with smaller models that have limited context capacity.[0m\n")
        
        self._output(f"[37mHISTORY MANAGEMENT[0m\n")
        
        self._output(f" \033[1m\033[90m/history.show\033[0m   [37mView the current chat history[0m")
        self._output(f" \033[1m\033[90m/history.clear\033[0m  [37mClear the current chat history[0m")
        self._output(f" \033[1m\033[90m/history.save\033[0m   [37mSave current chat history to a file[0m")
        self._output(f" \033[1m\033[90m/history.load\033[0m   [37mLoad chat history from a file (overwrites current history)[0m")
        self._output(f" \033[1m\033[90m/history.list\033[0m   [37mList all saved chat history files[0m")
        self._output(f" \033[1m\033[90m/history.delete\033[0m [37mDelete a saved chat history file[0m")
        self._output(f" \033[1m\033[90m/history.purge\033[0m  [37mDelete the most recent N messages from current chat history[0m")
        self._output("")
        self._output(f"[37mHISTORY CONTROL[0m\n")
        self._output(f" \033[1m\033[90m/history.on\033[0m     [37mEnable chat history recording[0m")
        self._output(f" \033[1m\033[90m/history.off\033[0m    [37mDisable chat history recording[0m")
        self._output("")
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/history.help\033[0m   [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help history.clear[0m")
    
    def _show_plugin_help(self):
        """Display plugin help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mPLUGIN COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe plugin system provides extensibility by allowing you to load and manage additional functionality modules. Plugins can extend the application's capabilities with custom commands, integrations, or specialized features. The system supports both built-in plugins and user-defined plugins for custom functionality.[0m\n")
        
        self._output(f"[37mPLUGIN DISCOVERY[0m\n")
        
        self._output(f" \033[1m\033[90m/plugin.list\033[0m    [37mList all available plugins[0m")
        self._output(f" \033[1m\033[90m/plugin.info\033[0m    [37mGet details for a specific plugin[0m")
        self._output("")
        
        self._output(f"[37mPLUGIN MANAGEMENT[0m\n")
        
        self._output(f" \033[1m\033[90m/plugin.reload\033[0m  [37mReload all plugins (for development)[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/plugin.help\033[0m    [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help plugin.info[0m")
    
    def _show_sys_help(self):
        """Display sys help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mSYS COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe system commands provide core application control and help functionality. These essential commands allow you to access help documentation and safely exit the application while preserving your configurations and settings.[0m\n")
        self._output(f"[37mAPPLICATION CONTROL[0m\n")
        
        self._output(f" \033[1m\033[90m/sys.help (aliases: help)\033[0m  [37mShow this command reference[0m")
        self._output(f" \033[1m\033[90m/sys.help all\033[0m              [37mShow comprehensive help menu[0m")
        self._output("")
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/sys.help\033[0m                  [37mshows this help screen[0m")
        self._output("")
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help sys.help[0m")
    
    def _show_file_help(self):
        """Display file help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mFILE COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe file system allows you to load and process external files within your conversations. You can upload various file types and send them along with prompts to the AI model, enabling document analysis, code review, image processing (if the model has vision support), and other file-based interactions. The system handles text documents, images, and code files seamlessly. WARNING: Processing large files or using vision features on low-end local LLM setups can be rather slow.[0m\n")
        
        self._output(f"[37mFILE OPERATIONS[0m\n")
        
        self._output(f" \033[1m\033[90m/file.load\033[0m  [37mLoad a file and send it with a prompt[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/file.help\033[0m  [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help file.load[0m")
    
    def _show_prompt_help(self):
        """Display prompt help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[1;37mPROMPT COMMANDS HELP[0m\n")
        
        self._output(f"[37mThe prompt system allows you to save and reuse frequently used prompts or prompt templates. You can store up to 10 numbered prompt slots (0-9) that persist between sessions, making it easy to quickly apply common instructions, writing styles, or analysis frameworks to your conversations. This system helps streamline repetitive tasks and maintain consistency in your interactions with the AI.[0m\n")
        
        self._output(f"[37mPROMPT MANAGEMENT[0m\n")
        
        self._output(f" \033[1m\033[90m/prompt.set\033[0m   [37mSave a prompt to a numbered slot (0-9)[0m")
        self._output(f" \033[1m\033[90m/prompt.use\033[0m   [37mApply a saved prompt from a slot[0m")
        self._output(f" \033[1m\033[90m/prompt.list\033[0m  [37mDisplay saved prompts by slot number[0m")
        self._output("")
        
        self._output(f"[37mMORE HELP[0m\n")
        
        self._output(f" \033[1m\033[90m/prompt.help\033[0m  [37mshows this help screen[0m")
        self._output("")
        
        self._output(f"[90mUse /sys.help <command> for detailed help on specific commands[0m")
        self._output(f"[90mExample: /sys.help prompt.set[0m")
    
    def _show_provider_help(self):
        """Display provider help in the custom format."""
        self._output(f"\n\033[1;37mPROVIDER COMMANDS HELP\033[0m\n")
        
        self._output(f"\033[37mProviders are LLM backends that CALOUS can connect to for model inference. The default provider is Ollama, which runs models locally on your machine. Provider plugins enable connections to cloud-based services like Groq. Provider plugins must be activated and require API key environment variables to be configured (e.g., GROQ_API_KEY).\033[0m\n")
        
        self._output(f"\033[37mPROVIDER MANAGEMENT\033[0m\n")
        
        self._output(f" \033[1m\033[90m/provider.list\033[0m    \033[37mList available LLM providers\033[0m")
        self._output(f" \033[1m\033[90m/provider.set\033[0m     \033[37mSwitch to a different LLM provider\033[0m")
        self._output(f" \033[1m\033[90m/provider.vars\033[0m    \033[37mShow provider-related variables\033[0m")
        self._output(f" \033[1m\033[90m/provider.help\033[0m    \033[37mShow help for provider commands\033[0m")
        self._output("")
        
        self._output(f"\033[37mMORE HELP\033[0m\n")
        
        self._output(f" \033[1m\033[90m/provider.help\033[0m    \033[37mshows this help screen\033[0m")
        self._output("")
        
        self._output(f"\033[90mUse /sys.help <command> for detailed help on specific commands\033[0m")
        self._output(f"\033[90mExample: /sys.help provider.set\033[0m")
    
    def display_shell_output(self, output: str):
        """Display shell command output in a system-style message."""
        self._output(f"\033[1m\033[35m[SHELL]\033[0m {output}")
    
    def _get_available_models_for_current_provider(self) -> list:
        """Get available models for the current provider."""
        # Always read provider from config to ensure consistency
        from .config import ConfigManager
        global_config = ConfigManager.get_global_config()
        current_provider = global_config.get('selected_provider', 'ollama')
        
        if current_provider == 'ollama':
            return self.app.model.list_ollama_models()
        else:
            # Get models from provider plugin
            if hasattr(self.app, 'plugin_manager') and self.app.plugin_manager:
                provider_plugin = self.app.plugin_manager.get_provider_plugin(current_provider)
                if provider_plugin and provider_plugin.loaded:
                    try:
                        return provider_plugin.get_available_models()
                    except Exception:
                        pass
            
            # Fallback to Ollama if provider fails
            return self.app.model.list_ollama_models()

    def show_available_models(self) -> str:
        """Display available models with dual output format."""
        models = self._get_available_models_for_current_provider()
        # Read provider from config to match the model list source
        from .config import ConfigManager
        global_config = ConfigManager.get_global_config()
        current_provider = global_config.get('selected_provider', 'ollama')
        
        if not models:
            # Rich output
            self._output("\n[1;31mNo models installed.[0m")
            self._output("[90mInstall a model with: 'ollama pull model-name'[0m")
            
            # Plain text output
            return "No models available. Install models with: ollama pull model-name"
        
        # Rich output
        provider_name = current_provider.title()
        self._output(f"\n\033[1mAvailable {provider_name} Models:\033[0m\n")
        
        plain_text_lines = ["Available Models:"]
        
        for i, model in enumerate(models, 1):
            # Only get context window info for Ollama models
            context_info = None
            if current_provider == 'ollama':
                context_info = self.app.model.get_context_window_info(model)
            if context_info:
                context_display = f"\033[36m{context_info.actual_context//1000}k\033[0m ctx"
                self._output(f"{i:2}. {model} [{context_display}]")
                plain_text_lines.append(f"{i}. {model} ({context_info.actual_context//1000}k ctx)")
            else:
                self._output(f"{i:2}. {model}")
                plain_text_lines.append(f"{i}. {model}")
        
        self._output(f"\n\033[90mUsage:\033[0m \033[1m/model.switch NUMBER\033[0m or \033[1m/model.switch MODEL_NAME\033[0m")
        self._output(f"\033[90mExample:\033[0m \033[1m/model.switch 1\033[0m or \033[1m/model.switch llama3\033[0m")
        
        plain_text_lines.append("")
        plain_text_lines.append("Usage: /model.switch NUMBER or /model.switch MODEL_NAME")
        plain_text_lines.append("Example: /model.switch 1 or /model.switch llama3")
        
        return "\n".join(plain_text_lines)