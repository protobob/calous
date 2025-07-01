"""User interface elements for Hi, Ollama!"""
from .utils import get_chat_color, print_message_with_bar, find_last_messages
from .constants import APP_VERSION, MAX_PREVIEW_LENGTH, CLI_HISTORY_PATH
from .config import ConfigManager
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
        
        help_text = f"\n[bold white]GLOBAL HELP[/bold white]\n\n"
        help_text += f"[white]CALOUS is a multi-channel chat service for local LLM models. Each chat[/white]\n"
        help_text += f"[white]channel (1-14) maintains its own conversation history and persona, allowing you[/white]\n"
        help_text += f"[white]to quickly switch between different AI contexts and personalities.[/white]\n\n"
        help_text += f"[white]GETTING STARTED[/white]\n\n"
        help_text += f"[white]First time? Try these commands:[/white]\n\n"
        
        self._output(help_text)
        
        self._output(f"[white]Choose a model:      [/white][bold {command_color}]/model.switch[/bold {command_color}]")
        self._output(f"[white]Switch channels:     [/white][bold {command_color}]/chat.switch 2[/bold {command_color}]")
        self._output(f"[white]Set a system prompt: [/white][bold {command_color}]/persona.set 0 You are a helpful coding assistant[/bold {command_color}]")
        self._output(f"[white]Name your AI:        [/white][bold {command_color}]/persona.name Assistant[/bold {command_color}]")
        self._output(f"[white]Try twist feature:   [/white][bold {command_color}]/chat.twist 3[/bold {command_color}]")
        self._output(f"[white]View chat history:   [/white][bold {command_color}]/history.show[/bold {command_color}]")
        self._output(f"[white]Add a command alias: [/white][bold {command_color}]/alias.add h sys.help[/bold {command_color}]")
        self._output("")
        self._output(f"[white]CATEGORY HELP[/white]\n")
        self._output(f"[white]Chat Management      (7 commands)   [/white][bold {command_color}]/sys.help chat[/bold {command_color}]")
        self._output(f"[white]Model Operations     (7 commands)   [/white][bold {command_color}]/sys.help model[/bold {command_color}]")
        self._output(f"[white]Persona Management  (11 commands)   [/white][bold {command_color}]/sys.help persona[/bold {command_color}]")
        self._output(f"[white]History Management   (9 commands)   [/white][bold {command_color}]/sys.help history[/bold {command_color}]")
        self._output(f"[white]Logging Operations   (5 commands)   [/white][bold {command_color}]/sys.help log[/bold {command_color}]")
        self._output(f"[white]Prompt Management    (4 commands)   [/white][bold {command_color}]/sys.help prompt[/bold {command_color}]")
        self._output(f"[white]File Operations      (1 command)    [/white][bold {command_color}]/sys.help file[/bold {command_color}]")
        self._output(f"[white]System Commands      (2 commands)   [/white][bold {command_color}]/sys.help sys[/bold {command_color}]")
        self._output(f"[white]Alias Management     (4 commands)   [/white][bold {command_color}]/sys.help alias[/bold {command_color}]")
        self._output(f"[white]Plugin System        (4 commands)   [/white][bold {command_color}]/sys.help plugin[/bold {command_color}]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f"[bold {command_color}]/sys.help category[/bold {command_color}]     [white]Detailed commands for a category[/white]")
        self._output(f"[bold {command_color}]/sys.help command[/bold {command_color}]      [white]Specific help for any command[/white]")
        self._output(f"[bold {command_color}]/sys.help all[/bold {command_color}]          [white]List of all commands[/white]")
        self._output("")

    def help_menu_all(self):
        """Display the comprehensive help menu with all commands."""
        
        # Get num_chats dynamically from session manager
        num_chats = self.app.session_manager.num_chats if hasattr(self.app, 'session_manager') and self.app.session_manager else ConfigManager.get_num_chats()

        self._output(f"\n[bold grey70]GLOBAL HELP MENU[/bold grey70]\n")
        
        # System Commands
        self._output("System Commands:")
        self._output("  /sys.help                Show streamlined help overview")
        self._output("  /sys.help all            Show this comprehensive help menu")
        self._output("  /sys.quit                Exit the program and save configuration")
        self._output("")

        # Chat Commands
        self._output("Chat Commands:")
        self._output(f"  /chat.switch [NUMBER]    Switch between chats (1-{num_chats}). Default switches to next chat")
        self._output(f"  /chat.twist [NUMBER]     Copy AI's last response to target chat (1-{num_chats}). Default uses next chat")
        self._output("  /chat.add                Add a new chat session")
        self._output("  /chat.remove             Remove a chat session")
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
        
        self._output(f"[bold white]ACTIVE CHATS:[/bold white] [grey50]({switch_hint})[/grey50]")        
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
            
            self._output(f"{prefix} [bold {chat_color_for_chat}]{i + 1}:[/bold {chat_color_for_chat}] [grey70]{persona_text}[/grey70]")
        
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
                    percentage_color = "green"
                elif usage_percentage <= 49:
                    percentage_color = "yellow"
                elif usage_percentage <= 74:
                    percentage_color = "orange1"
                else:  # 75-100
                    percentage_color = "red"
                
                context_display = f"Context: [{percentage_color}]{usage_percentage:.0f}%[/{percentage_color}]"
        # Remove the YOU: prompt entirely
        return (
            f"\n"
            f"[grey50](type /help for help)[/grey50]\n"
            f"[bold {chat_color}]|[/bold {chat_color}] [italic][white]{context_display}[/white][/italic] - YOU:"
        )

    def get_user_input(self):
        """Get user input with formatted prompt."""
        prompt_text = self.generate_prompt_text()
        lines = prompt_text.splitlines()
        for line in lines:
            print(line)
        user_input = input()
        return user_input.strip()
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_model_variables(self):
        """Display model-related variables only."""
        chat_color = get_chat_color(getattr(self.app, 'active_chat_index', 0))
        
        self._output(f"\n[bold]MODEL VARIABLES[/bold]\n")
        
        # Handle case where no model is selected
        if not self.app.selected_model:
            self._output(f"{'Selected Model:':<20} [red]None selected[/red]")
            self._output(f"{'Status:':<20} [yellow]Use /model.switch to select a model[/yellow]")
        else:
            self._output(f"{'Selected Model:':<20} [green]{self.app.selected_model}[/green]")
        
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
                self._output(f"{'Model Info:':<20} [grey70]{model_info}[/grey70]")        # Context window information (now global)
        from .config import ConfigManager
        global_num_ctx = ConfigManager.get_global_num_ctx()
        
        # Always show global context window setting
        self._output(f"{'Context Window:':<20} [bold cyan]{global_num_ctx:,} tokens[/bold cyan]")
        
        # Show VRAM management settings
        keep_alive = ConfigManager.get_keep_alive()
        self._output(f"{'Keep Alive:':<20} [bold magenta]{keep_alive}[/bold magenta]")
        
        if self.app.selected_model:
            context_info = self.app.model.get_context_window_info(self.app.selected_model)
            usage_percentage = self.app.model.get_context_usage_percentage(self.app.selected_model)            
            if context_info:
                # Display context window with model's max context for reference
                if global_num_ctx != context_info.max_context:
                    self._output(f"{'Model Max Context:':<20} [grey70]{context_info.max_context:,} tokens[/grey70]")
                
                # Show usage percentage with visual indicator
                if usage_percentage is not None:
                    # Create visual progress bar
                    bar_length = 10
                    filled_length = int(bar_length * usage_percentage / 100)
                    bar = "█" * filled_length + "░" * (bar_length - filled_length)
                    # Color the percentage based on usage level
                    if usage_percentage <= 24:
                        percentage_color = "green"
                    elif usage_percentage <= 49:
                        percentage_color = "yellow"
                    elif usage_percentage <= 74:
                        percentage_color = "orange1"
                    else:  # 75-100
                        percentage_color = "red"
                    
                    self._output(f"{'Context Usage:':<20} [{percentage_color}]{bar} {usage_percentage:.1f}%[/{percentage_color}]")
                  # Show estimated VRAM usage for global context window
                user_context_info = context_info._replace(actual_context=global_num_ctx)
                vram_estimate = self.app.model.estimate_context_vram_usage(user_context_info)                
                if vram_estimate != "unknown":
                    self._output(f"{'Context VRAM:':<20} [yellow]{vram_estimate}[/yellow] [grey50](est.)[/grey50]")
        else:
            # Show message when no model is selected
            self._output(f"{'Context Usage:':<20} [grey50]N/A (no model selected)[/grey50]")
            self._output(f"{'Context VRAM:':<20} [grey50]N/A (no model selected)[/grey50]")
        
        self._output("")

    def show_chat_variables(self):
        """Display chat-specific variables."""
        active_chat_index = getattr(self.app, 'active_chat_index', 0)
        verbosity = self.app.verbosity
        thinking_enabled = self.app.thinking_enabled
        temperature = self.app.temperature

        # Print Rich-formatted output for CLI
        chat_color = get_chat_color(active_chat_index)
        
        self._output(f"\n[bold {chat_color}]CHAT {active_chat_index + 1} VARIABLES[/bold {chat_color}]\n")
        self._output(f"[bold {chat_color}]|[/bold {chat_color}] {'Verbosity:':<20} [bold][{'green' if verbosity else 'red'}]{verbosity}[/{'green' if verbosity else 'red'}][/bold]")
        self._output(f"[bold {chat_color}]|[/bold {chat_color}] {'Thinking Mode:':<20} [bold][{'green' if thinking_enabled else 'red'}]{thinking_enabled}[/{'green' if thinking_enabled else 'red'}][/bold]")
        self._output(f"[bold {chat_color}]|[/bold {chat_color}] {'Temperature:':<20} [bold {'blue' if temperature == 0.0 else 'green' if temperature < 0.7 else 'yellow' if temperature <= 1.0 else 'orange1' if temperature <= 1.5 else 'red'}]{temperature}[/bold {'blue' if temperature == 0.0 else 'green' if temperature < 0.7 else 'yellow' if temperature <= 1.0 else 'orange1' if temperature <= 1.5 else 'red'}]")
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
        
        self._output(f"\n[bold]LOGGING VARIABLES[/bold]\n")
        
        self._output(f"{'Logging Enabled:':<20} [bold][{'green' if self.app.logging_enabled else 'red'}]{self.app.logging_enabled}[/{'green' if self.app.logging_enabled else 'red'}][/bold]")
        self._output(f"{'Config Path:':<20} [grey70]~/{config_path}[/grey70]")        
        self._output(f"{'Log Directory:':<20} [grey70]~/{log_dir}[/grey70]")
        
        # Show log file sizes if available
        try:
            from pathlib import Path
            log_path = Path(LOG_DIR)
            if log_path.exists():
                log_files = list(log_path.glob("*.log"))
                if log_files:
                    self._output(f"{'Log Files:':<20} [cyan]{len(log_files)}[/cyan] files found")
                    # Show most recent log file
                    most_recent = max(log_files, key=lambda f: f.stat().st_mtime)
                    size_kb = most_recent.stat().st_size / 1024
                    self._output(f"{'Latest Log:':<20} [grey70]{most_recent.name}[/grey70] ([yellow]{size_kb:.1f} KB[/yellow])")
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
            print_chat_header(self.app.active_chat_index)
            
            # Use the passed chat_color parameter instead of recalculating
            # Display the last user message
            if last_messages.get('user'):
                print_message_with_bar(chat_color, "YOU", last_messages['user'].get('content', ''))
            
            # Display the last assistant message
            if last_messages.get('assistant'):
                print_message_with_bar(chat_color, "LLM", last_messages['assistant'].get('content', ''))
    
    def show_category_help(self, category: str):
        """Display help for a specific command category."""
        from calousd.commands.registry import registry
        from calousd.commands.types import CommandCategory        # Map user-friendly category names to internal categories
        category_mapping = {
            'chat': CommandCategory.NAVIGATION,
            'model': CommandCategory.MODEL,
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
            self._output(f"[bold red]Error:[/bold red] Unknown category '{category}'")
            self._output(f"[grey50]Available categories:[/grey50] {', '.join(category_mapping.keys())}")
            return
        
        # Get commands for this category
        all_commands = registry.get_all_commands()
        category_commands = [cmd for cmd in all_commands.values() if cmd.category == internal_category]
        
        if not category_commands:
            self._output(f"[bold red]Error:[/bold red] No commands found for category '{category}'")
            return        # Special handling for persona category to match HELP.md format
        if category.lower() == 'persona':
            self._show_persona_help()
            return
          # Special handling for model category to match HELP.md format
        if category.lower() == 'model':
            self._show_model_help()
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
        self._output(f"\n[bold grey70]{category_title} COMMANDS HELP[/bold grey70]\n")
        
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
        self._output(f"\n[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help {sorted_commands[0].name}[/grey50]")
    
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
            self._output(f"[bold red]Error:[/bold red] Unknown command '{command_name}'")
            self._output(f"[grey50]Use /sys.help to see all available commands[/grey50]")
            return        # Handle special cases with existing help screens
        if command_name == "model.setctx":
            self._output(f"\n[bold grey70]| DETAILED HELP: /model.setctx[/bold grey70]\n")
            # Leverage existing comprehensive help
            from calousd.commands.model.services import ModelService
            service = ModelService(self.app)
            formatter = ModelFormatter()
            formatter.format_current_context(service.get_current_context(), self.app.selected_model, service)
            self._output(f"\n[grey50]This command accepts an optional context size parameter (2048-32768)[/grey50]")
            return
        
        elif command_name.startswith("alias"):
            self._output(f"\n[bold grey70]| DETAILED HELP: /{command_name}[/bold grey70]\n")
            # Leverage existing alias help
            AliasFormatter.print_alias_help()
            return
        
        # Generic command help for other commands
        self._output(f"\n[bold grey70]| DETAILED HELP: /{command_name}[/bold grey70]\n")
        
        # Basic command information
        self._output(f"[bold]Command:[/bold] /{command_name}")
        self._output(f"[bold]Description:[/bold] {command_def.description}")
        self._output(f"[bold]Category:[/bold] {command_def.category}")
        
        if command_def.aliases:
            self._output(f"[bold]Aliases:[/bold] {', '.join(f'/{alias}' for alias in command_def.aliases)}")
        
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
            
            self._output(f"[bold]Usage:[/bold] {' '.join(usage_parts)}")
        
        # Add category-specific help tips
        self._add_category_specific_tips(command_name, command_def.category)
        
        self._output(f"\n[grey50]Use /sys.help {command_def.category.lower().replace(' ', '').replace('management', '').replace('operations', '')} to see all {command_def.category.lower()} commands[/grey50]")

    def _add_category_specific_tips(self, command_name: str, category: str):
        """Add helpful tips based on command category."""
        
        if "chat" in command_name.lower():
            self._output(f"\n[bold cyan]💡 Chat Tips:[/bold cyan]")
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
            self._output(f"\n[bold cyan]💡 Model Tips:[/bold cyan]")
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
            self._output(f"\n[bold cyan]💡 Prompt/Persona Tips:[/bold cyan]")
            if "set" in command_name:
                self._output(f"  • Personas can have multiple slots (0-9) for different purposes")
                self._output(f"  • Slot 0 is typically used for the main system prompt")
            elif "save" in command_name or "load" in command_name:
                self._output(f"  • Saved personas persist between sessions")
                self._output(f"  • Use descriptive names for easy identification")
        
        elif "history" in command_name.lower() or "log" in command_name.lower():
            self._output(f"\n[bold cyan]💡 History/Logging Tips:[/bold cyan]")
            if "clear" in command_name:
                self._output(f"  • Clearing history is permanent and cannot be undone")
                self._output(f"  • Consider using /log.today to backup important conversations")
            elif "today" in command_name:
                self._output(f"  • Shows unified log across all chats for current day")
                self._output(f"  • Use /history.save to export important conversations")
        
        elif "file" in command_name.lower():
            self._output(f"\n[bold cyan]💡 File Tips:[/bold cyan]")
            self._output(f"  • File operations can process multiple formats")
            self._output(f"  • Use drag-and-drop for quick file loading")
        
        elif "plugin" in command_name.lower():
            self._output(f"\n[bold cyan]💡 Plugin Tips:[/bold cyan]")
            self._output(f"  • Plugins extend Hi, Ollama! functionality")
            self._output(f"  • Use /plugin.info to see detailed plugin information")
    
    def _show_persona_help(self):
        """Display persona help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]PERSONA COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The persona system allows you to create and edit a modular collection of system prompts that define how the model responds to your input, along with a name to identify the persona. You can save these personas to files and load them into the same or different chat instances for later use.[/white]\n")
        
        self._output(f"[white]PERSONA MANAGEMENT[/white]\n")
        
        self._output(f" [bold {command_color}]/persona.name[/bold {command_color}]    [white]Set the persona name[/white]")
        self._output(f" [bold {command_color}]/persona.set[/bold {command_color}]     [white]Set a system prompt at slot 0-9[/white]")
        self._output(f" [bold {command_color}]/persona.get[/bold {command_color}]     [white]View contents of a specific slot[/white]")
        self._output(f" [bold {command_color}]/persona.clear[/bold {command_color}]   [white]Clear contents of a specific slot[/white]")
        self._output(f" [bold {command_color}]/persona.show[/bold {command_color}]    [white]Show current name + all slot contents[/white]")
        self._output(f" [bold {command_color}]/persona.reset[/bold {command_color}]   [white]Clear name and all slot contents[/white]")
        self._output("")
        
        self._output(f"[white]FILE OPERATIONS[/white]\n")
        
        self._output(f" [bold {command_color}]/persona.save[/bold {command_color}]    [white]Save current persona to file[/white]")
        self._output(f" [bold {command_color}]/persona.load[/bold {command_color}]    [white]Load a saved persona from file[/white]")
        self._output(f" [bold {command_color}]/persona.list[/bold {command_color}]    [white]List all saved persona files[/white]")
        self._output(f" [bold {command_color}]/persona.delete[/bold {command_color}]  [white]Delete a saved persona file[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/persona.help[/bold {command_color}]    [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help persona.clear[/grey50]")
    
    def _show_model_help(self):
        """Display model help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]MODEL COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The model system allows you to select and configure AI models for your conversations. Global settings affect all chat instances, while per-chat settings let you customize behavior for individual conversations.[/white]\n")
        
        self._output(f"[white]GLOBAL[/white]\n")
        
        self._output(f" [bold {command_color}]/model.switch[/bold {command_color}]   [white]Change the current model (shows list or select by number/name)[/white]")
        self._output(f" [bold {command_color}]/model.setctx[/bold {command_color}]   [white]Set max context window size[/white]")
        self._output(f" [bold {command_color}]/model.vars[/bold {command_color}]     [white]Show model-related variables[/white]")
        self._output("")
        
        self._output(f"[white]PER CHAT INSTANCE[/white]\n")
        
        self._output(f" [bold {command_color}]/model.settemp[/bold {command_color}]  [white]Set temperature parameter[/white]")
        self._output(f" [bold {command_color}]/model.eval[/bold {command_color}]     [white]Toggle evaluation display[/white]")
        self._output(f" [bold {command_color}]/model.think[/bold {command_color}]    [white]Toggle thinking display[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/model.help[/bold {command_color}]     [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help model.eval[/grey50]")
    
    def _show_alias_help(self):
        """Display alias help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]ALIAS COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The alias system allows you to create custom shortcuts for frequently used commands. Aliases can simplify complex commands or provide alternative names that are easier to remember.[/white]\n")
        
        self._output(f"[white]ALIAS MANAGEMENT[/white]\n")
        
        self._output(f" [bold {command_color}]/alias.add[/bold {command_color}]     [white]Create a new command alias[/white]")
        self._output(f" [bold {command_color}]/alias.remove[/bold {command_color}]  [white]Remove a command alias[/white]")
        self._output(f" [bold {command_color}]/alias.list[/bold {command_color}]    [white]List all command aliases[/white]")
        self._output(f" [bold {command_color}]/alias.clear[/bold {command_color}]   [white]Clear all command aliases[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/alias.help[/bold {command_color}]    [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help alias.add[/grey50]")
    
    def _show_chat_help(self):
        """Display chat help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]CHAT COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The chat system manages multiple independent conversation sessions within a single application instance. You can switch between numbered chat sessions (1-N), add or remove sessions dynamically, and transfer AI responses between chats. Each chat maintains its own conversation history and persona settings while sharing the same AI model selection globally.[/white]\n")
        
        self._output(f"[white]SESSION MANAGEMENT[/white]\n")
        
        self._output(f" [bold {command_color}]/chat.switch[/bold {command_color}]  [white]Switch between chat sessions[/white]")
        self._output(f" [bold {command_color}]/chat.add[/bold {command_color}]     [white]Add a new chat session[/white]")
        self._output(f" [bold {command_color}]/chat.remove[/bold {command_color}]", "[white]Remove a chat session.[/white]")
        self._output(f" [bold {command_color}]/chat.reset[/bold {command_color}]", "[white]Reset current chat to factory defaults.[/white]")
        self._output("")
        
        self._output(f"[white]CONTENT OPERATIONS[/white]\n")
        
        self._output(f" [bold {command_color}]/chat.twist[/bold {command_color}]   [white]Copy AI response to another chat[/white]")
        self._output("")
        
        self._output(f"[white]INFORMATION & SETTINGS[/white]\n")
        
        self._output(f" [bold {command_color}]/chat.vars[/bold {command_color}]    [white]Show chat-specific variables[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/chat.help[/bold {command_color}]    [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help chat.add[/grey50]")
    
    def _show_log_help(self):
        """Display log help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]LOG COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The unified logging system provides centralized conversation tracking across all chat sessions. It maintains daily log files that capture conversations from every chat instance, creating a new log file each day. Logs are stored in the user's home directory under ~/.calous/logs/, allowing you to review your interaction history organized by date.[/white]\n")
        
        self._output(f"[white]LOGGING CONTROL[/white]\n")
        
        self._output(f" [bold {command_color}]/log.on[/bold {command_color}]     [white]Enable unified logging[/white]")
        self._output(f" [bold {command_color}]/log.off[/bold {command_color}]    [white]Disable unified logging[/white]")
        self._output("")
        
        self._output(f"[white]LOG VIEWING[/white]\n")
        
        self._output(f" [bold {command_color}]/log.today[/bold {command_color}]  [white]View today's unified log[/white]")
        self._output("")
        
        self._output(f"[white]INFORMATION & SETTINGS[/white]\n")
        
        self._output(f" [bold {command_color}]/log.vars[/bold {command_color}]   [white]Show logging-related variables[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/log.help[/bold {command_color}]   [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help log.today[/grey50]")
    
    def _show_history_help(self):
        """Display history help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]HISTORY COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The chat history system manages conversation records for individual chat sessions. Each chat maintains its own separate history that is automatically saved to file, ensuring your conversations persist between sessions and are not lost when you close and reopen the application. You can also control whether history recording is enabled or disabled per chat - useful for conversations with smaller models that have limited context capacity.[/white]\n")
        
        self._output(f"[white]HISTORY MANAGEMENT[/white]\n")
        
        self._output(f" [bold {command_color}]/history.show[/bold {command_color}]   [white]View the current chat history[/white]")
        self._output(f" [bold {command_color}]/history.clear[/bold {command_color}]  [white]Clear the current chat history[/white]")
        self._output(f" [bold {command_color}]/history.save[/bold {command_color}]   [white]Save current chat history to a file[/white]")
        self._output(f" [bold {command_color}]/history.load[/bold {command_color}]   [white]Load chat history from a file (overwrites current history)[/white]")
        self._output(f" [bold {command_color}]/history.list[/bold {command_color}]   [white]List all saved chat history files[/white]")
        self._output(f" [bold {command_color}]/history.delete[/bold {command_color}] [white]Delete a saved chat history file[/white]")
        self._output(f" [bold {command_color}]/history.purge[/bold {command_color}]  [white]Delete the most recent N messages from current chat history[/white]")
        self._output("")
        self._output(f"[white]HISTORY CONTROL[/white]\n")
        self._output(f" [bold {command_color}]/history.on[/bold {command_color}]     [white]Enable chat history recording[/white]")
        self._output(f" [bold {command_color}]/history.off[/bold {command_color}]    [white]Disable chat history recording[/white]")
        self._output("")
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/history.help[/bold {command_color}]   [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help history.clear[/grey50]")
    
    def _show_plugin_help(self):
        """Display plugin help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]PLUGIN COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The plugin system provides extensibility by allowing you to load and manage additional functionality modules. Plugins can extend the application's capabilities with custom commands, integrations, or specialized features. The system supports both built-in plugins and user-defined plugins for custom functionality.[/white]\n")
        
        self._output(f"[white]PLUGIN DISCOVERY[/white]\n")
        
        self._output(f" [bold {command_color}]/plugin.list[/bold {command_color}]    [white]List all available plugins[/white]")
        self._output(f" [bold {command_color}]/plugin.info[/bold {command_color}]    [white]Get details for a specific plugin[/white]")
        self._output("")
        
        self._output(f"[white]PLUGIN MANAGEMENT[/white]\n")
        
        self._output(f" [bold {command_color}]/plugin.reload[/bold {command_color}]  [white]Reload all plugins (for development)[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/plugin.help[/bold {command_color}]    [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help plugin.info[/grey50]")
    
    def _show_sys_help(self):
        """Display sys help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]SYS COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The system commands provide core application control and help functionality. These essential commands allow you to access help documentation and safely exit the application while preserving your configurations and settings.[/white]\n")
        self._output(f"[white]APPLICATION CONTROL[/white]\n")
        
        self._output(f" [bold {command_color}]/sys.help (aliases: help)[/bold {command_color}]  [white]Show this command reference[/white]")
        self._output(f" [bold {command_color}]/sys.help all[/bold {command_color}]              [white]Show comprehensive help menu[/white]")
        self._output(f" [bold {command_color}]/sys.quit (aliases: quit)[/bold {command_color}]  [white]Exit and save configuration[/white]")
        self._output("")
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/sys.help[/bold {command_color}]                  [white]shows this help screen[/white]")
        self._output("")
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help sys.quit[/grey50]")
    
    def _show_file_help(self):
        """Display file help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]FILE COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The file system allows you to load and process external files within your conversations. You can upload various file types and send them along with prompts to the AI model, enabling document analysis, code review, image processing (if the model has vision support), and other file-based interactions. The system handles text documents, images, and code files seamlessly. WARNING: Processing large files or using vision features on low-end local LLM setups can be rather slow.[/white]\n")
        
        self._output(f"[white]FILE OPERATIONS[/white]\n")
        
        self._output(f" [bold {command_color}]/file.load[/bold {command_color}]  [white]Load a file and send it with a prompt[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/file.help[/bold {command_color}]  [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help file.load[/grey50]")
    
    def _show_prompt_help(self):
        """Display prompt help in the custom format from HELP.md."""
        command_color = "grey50"
        
        self._output(f"\n[bold white]PROMPT COMMANDS HELP[/bold white]\n")
        
        self._output(f"[white]The prompt system allows you to save and reuse frequently used prompts or prompt templates. You can store up to 10 numbered prompt slots (0-9) that persist between sessions, making it easy to quickly apply common instructions, writing styles, or analysis frameworks to your conversations. This system helps streamline repetitive tasks and maintain consistency in your interactions with the AI.[/white]\n")
        
        self._output(f"[white]PROMPT MANAGEMENT[/white]\n")
        
        self._output(f" [bold {command_color}]/prompt.set[/bold {command_color}]   [white]Save a prompt to a numbered slot (0-9)[/white]")
        self._output(f" [bold {command_color}]/prompt.use[/bold {command_color}]   [white]Apply a saved prompt from a slot[/white]")
        self._output(f" [bold {command_color}]/prompt.list[/bold {command_color}]  [white]Display saved prompts by slot number[/white]")
        self._output("")
        
        self._output(f"[white]MORE HELP[/white]\n")
        
        self._output(f" [bold {command_color}]/prompt.help[/bold {command_color}]  [white]shows this help screen[/white]")
        self._output("")
        
        self._output(f"[grey50]Use /sys.help <command> for detailed help on specific commands[/grey50]")
        self._output(f"[grey50]Example: /sys.help prompt.set[/grey50]")
    
    def display_shell_output(self, output: str):
        """Display shell command output in a system-style message."""
        self._output(f"[bold magenta][SHELL][/bold magenta] {output}")
    
    def show_available_models(self) -> str:
        """Display available models with dual output format."""
        models = self.app.model.list_ollama_models()
        
        if not models:
            # Rich output
            self._output("\n[bold red]No models installed.[/bold red]")
            self._output("[grey50]Install a model with: 'ollama pull model-name'[/grey50]")
            
            # Plain text output
            return "No models available. Install models with: ollama pull model-name"
        
        # Rich output
        self._output("\n[bold]Available Ollama Models:[/bold]\n")
        
        plain_text_lines = ["Available Models:"]
        
        for i, model in enumerate(models, 1):
            # Get context window info for display
            context_info = self.app.model.get_context_window_info(model)
            if context_info:
                context_display = f"[cyan]{context_info.actual_context//1000}k[/cyan] ctx"
                self._output(f"{i:2}. {model} [{context_display}]")
                plain_text_lines.append(f"{i}. {model} ({context_info.actual_context//1000}k ctx)")
            else:
                self._output(f"{i:2}. {model}")
                plain_text_lines.append(f"{i}. {model}")
        
        self._output(f"\n[grey50]Usage:[/grey50] [bold]/model.switch NUMBER[/bold] or [bold]/model.switch MODEL_NAME[/bold]")
        self._output(f"[grey50]Example:[/grey50] [bold]/model.switch 1[/bold] or [bold]/model.switch llama3[/bold]")
        
        plain_text_lines.append("")
        plain_text_lines.append("Usage: /model.switch NUMBER or /model.switch MODEL_NAME")
        plain_text_lines.append("Example: /model.switch 1 or /model.switch llama3")
        
        return "\n".join(plain_text_lines)