# Changelog

## [0.6.8.dev] - 2025-05-31

### Fixed
- **Test Version Mismatch**: Integration tests now dynamically import APP_VERSION instead of using hardcoded version strings
- **Repository Cleanup**: Removed __pycache__ directories from working tree and enhanced .gitignore coverage

### Enhanced
- **Test Maintainability**: Tests are now more flexible and don't break when chat configuration changes
- **Development Environment**: Comprehensive .gitignore now covers PyInstaller, testing artifacts, and OS-specific files

### Technical
- Integration tests use dynamic version detection to prevent future version mismatch issues
- Improved test stability by making chat number expectations flexible rather than hardcoded

## [0.6.7.dev] - 2025-05-31

### Added
- **`/resetchat` command**: Reset current chat to factory defaults with confirmation prompt
- Improved confirmation dialogs for destructive operations using Rich prompts

### Enhanced  
- **`/clear` command**: Updated with colored chat identification and improved confirmation styling
- Consistent chat identification in command messages (e.g., "CHAT 1" in proper chat colors)
- All destructive commands now use Rich's `Prompt.ask()` for better UX and safety

## [0.6.6.dev] - 2025-05-31

### Added
- **Persistent Chat History**: Individual chat histories now automatically save to `~/hiollama/.history/` as JSONL files
- Automatic history loading on application restart - conversations persist across sessions
- History files survive chat reconfiguration (removing/adding chats preserves existing histories)

### Changed
- Reorganized data structure: moved from `~/hiollama_logs/` to `~/hiollama/logs/` and `~/hiollama/.history/`
- Restored confirmation prompt for `/clear` command to prevent accidental history deletion

### Fixed
- Better error handling for empty model selection with user-friendly messages instead of Pydantic validation errors

### Technical
- Chat history saved as JSONL format for efficient append operations and future tokenizer integration
- Each chat maintains independent history file (chat_001.jsonl, chat_002.jsonl, etc.)
- Immediate save on every message to prevent data loss

## [0.6.5.dev] - 2025-05-31

### Changed
- **Default System Prompts**: All chat instances now start with blank system prompts instead of predefined roles
- Users have complete control over chat personalities from the start
- Removed specialized prompts for technical, creative, and generic assistants

### Added
- `/addchat` command to dynamically add new chat sessions
- `/removechat [NUMBER]` command to dynamically remove chat sessions
- Chat configuration preservation when removing chats
- Persistent chat count preference - application remembers number of chats between sessions

### Enhanced
- Application startup now uses saved chat count preference when no argument provided
- Command line argument still overrides saved preference: `hiollama 6` always uses 6 chats
- Improved chat management with dynamic session control

## [0.6.4.dev] - 2025-05-31

### Added
- Native Ollama thinking API integration with `think` parameter support
- `/toggle_think` command to enable/disable model reasoning display
- Thinking mode status display in `/showvars` with color coding
- Persistent thinking mode configuration across sessions

### Changed
- Upgraded to ollama library 0.5.2.dev2 for native thinking support
- Model responses now use Ollama's native thinking separation instead of regex
- Thinking content displays in dim cyan during streaming when enabled
- Default thinking mode is disabled for clean output

### Removed
- Legacy `strip_thoughts` regex-based method from chat history
- Manual thought stripping from twist operations (now uses clean native API)
- Unused `re` import from chat_history.py

### Security
- Twist operations guaranteed to never send thinking content to other chats
- Last response always contains clean content regardless of thinking mode

## [0.6.3.dev] - 2025-05-30

### Changed
- **Simplified Think Filtering**: Removed user control over think filtering - it now always filters `<think></think>` blocks from chat history and twist operations while preserving them in streaming output
- Streaming now shows full model output including thoughts for transparency
- Chat history and `/twist` operations automatically strip thoughts for clean conversation flow

### Removed
- `/toggle_think` command - think filtering is now always enabled for history/twist but disabled for real-time display
- `think_filtering` configuration option - behavior is now consistent across all instances

### Fixed
- **Critical**: `/twist` command now properly filters out `<think></think>` blocks to prevent sending model reasoning to target chats
- Enhanced think filtering with robust regex pattern matching using `re.DOTALL` flag

### Technical
- Streamlined model interaction flow with automatic think filtering in `_handle_streaming`
- Updated command system to remove think filtering controls
- Improved user experience by showing model reasoning during streaming while keeping history clean
- **Note**: Thoughts are currently filtered from logs as well (this preserves the clean logging approach)

## [0.6.2.dev] - 2025-05-30

### Added
- Streaming response support for real-time model output
- Real-time token streaming for improved user experience

### Changed
- Replaced non-streaming model interactions with streaming-only implementation
- Removed spinner functionality to prevent conflicts with streaming output

### Removed
- All spinner-related code and methods from UIManager
- Non-streaming response handling paths
- `run_with_spinner` method and related functionality

## [0.6.1.dev] - 2025-05-30

### Changed
- Updated `/showprompt` command UI to match `/showvar` styling
  - Added chat color coordination with colored `|` prefix
  - Consistent formatting with 20-character left-aligned labels
  - Grey text for prompt content display
  - Styled headers showing "CHAT X SAVED PROMPTS" and "CHAT X PROMPT Y"
  - Shows all prompt slots including "(not set)" for empty slots
- Improved `/prompt` command output formatting
  - Added chat color styling to "Using Prompt X:" messages
  - Consistent `|` prefix formatting
  - Added proper newline spacing before messages

### Technical
- Enhanced prompt command UI consistency across the application
- Improved visual hierarchy and readability of prompt-related output

## [0.6.0.dev] - 2025-05-30

### Added
- **Unified logging system** for comprehensive activity tracking
  - Single log file captures all chat activities, switches, and system events
  - Logs saved to `~/hiollama_logs/YYYY-MM-DD.txt`
  - Includes session start/end, channel switches, conversations, commands, and system changes
  - Added `/viewlog` command to display today's unified log
  - Thread-safe logging with automatic log file creation

### Enhanced
- Updated `/toggle_log` command to control unified logging (replaces per-chat logging control)
- Integrated unified logging into chat history, navigation, prompt, and model commands
- Added comprehensive event tracking across all chat operations

### Technical
- Added `UnifiedLogger` class with formatted log entry system
- Integrated unified logging throughout session manager and command handlers
- Maintained structured log format with timestamps and chat context information

## [0.5.4.dev] - 2025-05-30

### Added
- Comprehensive test suite with automated CLI testing
  - Added `tests/test_cli.py` with full command-line argument validation
  - Created organized test infrastructure with `tests/run_tests.py`
  - Manual testing checklist for interactive commands in `tests/MANUAL_TESTING.md`

### Fixed
- Fixed critical Unicode compatibility issue for Windows
  - Replaced problematic `►` character with ASCII `>` in chat indicators
  - Ensures application starts correctly on all Windows systems

### Enhanced
- Updated README.md with comprehensive testing documentation
- Created structured test directory with proper module organization
- Added test runner supporting multiple execution modes (`--quick`, specific suites)

### Technical
- Enhanced error handling and validation in test infrastructure
- Improved cross-platform compatibility through ASCII character usage
- Established foundation for future automated testing expansion

## [0.5.3.dev] - 2025-05-30

### Added
- Command line argument support for specifying number of chat channels
  - Usage: `hiollama 5` for 5 chats, `hiollama` defaults to 4
  - Added validation with configurable max chat limit (14)
- Extended rainbow color palette for chat identification beyond 7 chats
  - Added darker variants of original colors for chats 8-14
- Centralized chat session constants (TWIST_PREVIEW_LENGTH, SWITCH_PREVIEW_LENGTH)

### Changed
- ChatSessionManager now accepts dynamic num_chats parameter instead of hardcoded value
- Updated __main__.py entry point with argparse for better CLI experience
- Moved hardcoded preview lengths to constants.py for maintainability

### Technical
- Enhanced get_chat_color() to use EXTENDED_RAINBOW_COLORS for better visual distinction
- Improved separation of concerns by centralizing configuration defaults

## [0.5.2.dev] - 2025-05-30

### Fixed
- Fixed command system import path from `.commands` to `.commands.handler`
- Removed duplicate `get_chat_color` imports in session manager that caused UnboundLocalError
- Fixed `display_chat_context` method to properly use passed chat_color parameter
- Added error handling for path operations in `show_variables` method
- Restored command module imports in `commands/__init__.py` to ensure decorator registration

### Technical
- Resolved circular import issues in session manager
- Improved chat color consistency across UI components
- Enhanced robustness of file path handling

## [0.5.1.dev] - 2025-05-30

### Fixed
- Fixed `/showvars` command to properly display config and log directory paths using relative paths from home directory
- Removed unused `display_variables()` method that was causing confusion with `/showvars` functionality

## [0.5.0.dev] - 2025-05-30

### Changed
- **Major Refactor**: Split monolithic command_system.py into modular command structure
  - Commands now organized by category: general.py, navigation.py, model.py, prompt.py, history.py, file.py
  - Improved maintainability and easier testing of individual command groups
  - Better separation of concerns between registry, handler, and commands

### Fixed
- Fixed `/system` command to properly parse multi-word prompts (e.g., `/system this is the prompt`)
- Restored missing `setmax` command with history trimming functionality
- Fixed `/history` command to use existing chat_history.print_history() method

### Technical
- Implemented decorator-based command registration system
- Added argparse integration with nargs='+' for multi-word arguments
- Maintained backward compatibility with existing command functionality

## [0.4.0.dev] - 2025-05-29

### Added
- **New Command System**: Complete rewrite of command handling with argparse integration
- **Decorator-Based Registration**: Commands now use `@registry.register()` for clean registration
- **Advanced Argument Parsing**: Full argparse support with type checking and validation
- **Improved /load Command**: No quotes needed for prompts (`/load file.py review this code`)
- **Type Safety**: Created `types.py` with shared `ActionType` and `CommandResult` classes
- **Command Categories**: Organized commands into logical categories (General, Navigation, Model, etc.)

### Changed
- **Command Architecture**: Moved from manual parsing to argparse-based system
- **Import Structure**: Eliminated unnecessary `commands.py` wrapper, direct imports from `command_system.py`
- **Help System**: Preserved existing beautiful help menu while integrating with new command registry

### Fixed
- **Circular Import Issues**: Resolved circular dependencies between app, command_system, and session_manager
- **Duplicate Config Saving**: Fixed multiple config save messages on `/quit` command
- **Command Validation**: Proper error handling and usage display for invalid command syntax

### Technical
- **Removed**: `commands.py` file (redundant wrapper)
- **Enhanced**: Command handler with robust argument parsing and error handling
- **Improved**: Type annotations and error messages throughout command system

## [0.3.1.dev] - 2025-05-29

### Fixed
- **Configuration System**: Fixed missing JSON import in config.py that caused runtime errors
- **Unified Config Path**: Removed redundant UNIFIED_CONFIG_PATH causing double "unified" in filenames
- **Command Handler**: Fixed showvars command attempting to access non-existent ConfigManager.UNIFIED_CONFIG_PATH
- **Import Consistency**: Ensured all modules properly import required dependencies

### Technical
- **Simplified Config Management**: ConfigManager now uses CONFIG_PATH directly from constants
- **Cleaner Architecture**: Eliminated redundant path constants and improved code consistency

## [0.3.0.dev] - 2025-05-29

### Added
- **Full N-Chat Support**: Application now supports any number of concurrent chat sessions (configurable via `DEFAULT_NUM_CHATS`)
- **Dynamic Chat Configuration**: Configuration system automatically generates configs for any number of chats
- **Enhanced Chat Management**: Improved session manager with better chat instance handling
- **Smart Default Prompts**: New chats get appropriate default system prompts (technical, creative, generic helper)

### Changed
- **BREAKING**: Increased default chat count from 2 to 4 for better testing and demonstration
- **Architecture Overhaul**: Removed circular references between chat instances for better memory management
- **Simplified Model Updates**: Streamlined global model update mechanism through session manager
- **UI Improvements**: Chat overview and switching now properly handles variable chat counts
- **Configuration Migration**: Enhanced config system to handle missing chat configurations gracefully

### Fixed
- **Circular Reference Memory Issues**: Eliminated chat instances holding references to all other chats
- **Dynamic UI Elements**: Help menu and chat switching now show correct chat ranges (1-N instead of hardcoded 1-2)
- **Configuration Scalability**: Chat configs are now generated on-demand for any chat index
- **TWIST Content Coloring**: TWIST CONTENT now displays in source chat color instead of target chat color
- **Session Manager Logic**: Cleaned up chat initialization and cross-chat communication

### Technical
- **Removed Dependencies**: Eliminated problematic circular references in session management
- **Enhanced Fallback Handling**: Better error handling for missing configurations
- **Improved Code Organization**: Better separation of concerns between UI, session management, and configuration

## [0.2.3.dev] - 2025-05-29

### Enhanced

- **Unified Configuration System**: Replaced individual chat config files with a single unified configuration file.
- All chat instances now store their configurations in `~/.hiollama_config_unified.json` with clear global and per-chat sections.
- Global settings (like selected model) are now shared across all chat instances while maintaining per-chat customization.
- Simplified configuration management with atomic saves and better organization.

### Technical

- Complete refactor of `ConfigManager` class to use unified JSON structure with global and per-chat sections.
- Updated `HiOllamaChat` initialization to load from unified config system.
- Enhanced configuration API with methods like `get_chat_config()`, `update_chat_config()`, and `update_global_config()`.
- Improved config file structure enables future features like chat templates and presets.
- Number of chat instances is now configurable through the global config section.

### Breaking Changes

- Configuration file format has changed from separate `~/.hiollama_config_N.json` files to unified `~/.hiollama_config_unified.json`.
- Previous configuration files will need to be manually recreated (automatic migration not implemented).

## [0.2.2.dev] - 2025-05-28

### Enhanced

- **Improved Ollama Error Handling**: Enhanced error handling specifically for Ollama library interactions.
- Better error messages for model-not-found scenarios with suggested available models.
- Improved connection error handling with specific guidance for Ollama server issues.
- Enhanced model selection validation with better user feedback and cancellation support.

### Technical

- Added proper `ollama.ResponseError` exception handling in `model_interaction.py`.
- Improved `list_ollama_models()` with comprehensive error handling for API failures.
- Enhanced `select_model()` with input validation and graceful cancellation support.
- Better timeout and connection error messaging with actionable recovery suggestions.

## [0.2.1.dev] - 2025-05-28

### Enhanced

- **Improved Error Formatting**: All error messages now start with a newline (`\n`) for better visual separation.
- Enhanced readability of error output across all modules including model interaction, configuration, and commands.

### Fixed

- **Code Cleanup**: Removed dead code including unused `get_rainbow_chat_color()` function and `CHAT_COLORS` constant.
- **RAINBOW_COLORS**: Fixed duplicate colors at the end of the array for cleaner 7-color cycling.
- **Version Consistency**: Updated `__version__` in `__init__.py` to properly import from `APP_VERSION` constant.

### Technical

- Updated error message formatting in `model_interaction.py`, `config.py`, `commands.py`, `utils.py`, and `session_manager.py`.
- Cleaned up constants.py by removing redundant color definitions and functions.
- Centralized version management through constants.py import in __init__.py.
- Consistent error display formatting throughout the application for improved user experience.

## [0.2.0.dev] - 2025-05-28

### Major Refactor: Event-Driven Architecture

- **Complete Architecture Overhaul**: Replaced state-flag system with event-driven command processing.
- **Centralized Session Management**: New `ChatSessionManager` class coordinates all multi-chat operations.
- **Enhanced Multi-Chat Support**: Commands now accept optional chat numbers (`/switch 3`, `/twist 2`).
- **Backward Compatibility**: Existing 2-chat behavior preserved when no arguments provided.
- **Scalable Design**: Ready for N-chat expansion beyond default 2-chat setup.

### Enhanced

- **Advanced Switch/Twist Commands**: 
  - `/switch` cycles to next chat or `/switch NUMBER` jumps to specific chat
  - `/twist` copies to next chat or `/twist NUMBER` copies to specific chat
  - Automatic cycling behavior when no target specified
- **Event-Driven Command Processing**: Commands return `CommandResult` objects with structured action intentions.
- **Simplified Chat Instances**: Removed all switching state flags and coordination logic from individual chats.
- **Rainbow Header Display**: Startup shows colorful HIOLLAMA! header with version.

### Technical

- **New `ChatSessionManager` Class**: Centralized orchestration of multi-chat functionality and main application loop.
- **`CommandResult` System**: Structured command responses with `ActionType` enum (CONTINUE, SWITCH, TWIST, QUIT).
- **Eliminated State Flags**: Removed `switch_requested`, `twist_content`, and related state management functions.
- **Clean Event Processing**: Single `process_command_result()` method handles all command outcomes.
- **Enhanced Multi-Chat Coordination**: Centralized switch/twist logic with proper context display management.
- **Future-Ready Architecture**: Event system easily extensible for new inter-chat features.

### Removed

- **Deprecated State Management**: Eliminated boolean flags and manual state reset functions.
- **Distributed Switch Logic**: Consolidated all switching logic into `ChatSessionManager`.
- **Complex Main Loop**: Replaced flag-checking loops with clean event processing.

## [0.1.11.dev] - 2025-05-28

### Fixed

- **Chat History Order**: Fixed chronological order of messages in chat history.
- User messages now appear before assistant responses in the in-memory history while maintaining correct API functionality.
- Eliminated double-prompt issue by leveraging user input already added to history for API calls.
- File logging continues to maintain correct conversational order as before.

### Technical

- Restructured message flow in `handle_regular_input()` to add user input to history before API call.
- Modified `talk_to_model()` to use existing chat history (which now includes current user input) instead of appending user prompt separately.
- Maintains API compatibility while fixing historical message ordering.

## [0.1.10.dev] - 2025-05-28

### Enhanced

- **Active Chats Overview**: Added new UI section showing all configured chats with system prompts.
- Shows active chat with arrow indicator (►) and displays truncated system prompts for quick reference.
- Added "/switch to change" hint next to ACTIVE CHATS header for better user guidance.
- Conditional display of CHAT # SUMMARY section - only shows when chat history exists.

### Technical

- Moved `display_chat_context()` functionality from `__main__.py` to `UIManager` class for better organization.
- Added `display_active_chats_overview()` method to `UIManager` for multi-chat UI preparation.
- Moved `find_last_messages()` utility function to `utils.py` for better code organization.
- Updated UI styling consistency with grey50 color for help hints.

## [0.1.9.dev] - 2025-05-28

### Enhanced

- **Rainbow Chat Colors**: Chat colors now use the rainbow progression from the HIOLLAMA logo.
- Chat 1 displays in red, Chat 2 in orange1, with future expansion ready for yellow1, green, blue, purple, magenta.
- Improved visual consistency between app branding and chat color scheme.

### Technical

- Updated `get_chat_color()` function to use `RAINBOW_COLORS` array with modulo cycling.
- Added `DEFAULT_NUM_CHATS` constant and enhanced `setup_chats()` for future multi-chat expansion.
- Maintained backward compatibility with existing 2-chat system and switch/twist functionality.

## [0.1.8.dev] - 2025-05-27

### Changed

- Updated `/history` command output to match `/showvars` style formatting.
- Chat history now displays with colored bars, role color-coding, and consistent START/END headers.
- USER messages shown in bold, ASSISTANT messages in cyan, message content in grey70.

### Technical

- Modified `ChatHistory.print_history()` method to use consistent UI styling across commands.
- Enhanced readability with clear START CHAT # HISTORY and END CHAT # HISTORY delimiters.

## [0.1.7.dev] - 2025-05-27

### Fixed

- Fixed `/showprompt` command to properly default to "all" when no arguments provided.
- Restored invalid command detection for malformed commands starting with `/`.

### Technical

- Updated command parsing logic to handle `/showprompt` without arguments.
- Added proper fallback handling for unrecognized commands starting with `/`.

## [0.1.6.dev] - 2025-05-27

### Changed

- Simplified global model management by removing redundant instance registration system.
- Updated `update_global_model()` to use existing `chat_instances` instead of separate `_all_instances`.
- Streamlined dual-chat architecture by leveraging already available instance references.

### Technical

- Removed unnecessary `register_instance()` class method from `HiOllamaChat`.
- Eliminated redundant `_all_instances` class variable.
- Improved code clarity by using single source of truth for chat instance management.

## [0.1.5.dev] - 2025-05-27

### Added

- Implemented global model management across all chat instances.
- Added `ConfigManager.load_global_config()` and `ConfigManager.save_global_config()` methods.
- Added class-level instance registration system for synchronized model updates.

### Changed

- Model selection with `/model` command now applies globally to both Chat 1 and Chat 2.
- Separated configuration into global settings (`~/.hiollama_config_global.json`) and instance-specific settings.
- Updated `HiOllamaChat` class with class-level global configuration management.
- Modified `/model` command to provide feedback on number of instances updated.

### Technical

- Refactored configuration architecture to support global vs per-instance settings.
- Added `update_global_model()` and `register_instance()` class methods to `HiOllamaChat`.
- Enhanced configuration separation to prevent `selected_model` duplication in instance configs.

## [0.1.4.dev] - 2025-05-27

### Changed

- Updated `list_ollama_models()` to use native `olloma.list()` function instead of manual HTTP requests.
- Simplified model listing by removing requests-specific exception handling and timeout parameters.
- Improved code maintainability by leveraging the olloma library's built-in functionality.

## [0.1.3.dev] - 2025-05-26

### Changed

- Refactored `main` function for improved readability and modularity.
- Added `handle_twist_if_present` to process twisted content during chat switching.
- Improved `initialize_chat_context` for better context initialization.

## [0.1.2.dev] - 2025-05-24

### Changed

- Updated `/twist` command to use the last response dictionary instead of assistant chat history.
- Added `last_response` attribute to store the most recent AI response for better handling of twist functionality.

## [0.1.1-dev] - 2025-05-24

### Updated

- Improved the `/help` menu:
  - Updated command colors to `dark yellow` for better distinction.
  - Enhanced section headers with consistent formatting.
  - Clarified references to `CHAT1` and `CHAT2` in their respective colors.

## [0.1.0-dev] - 2025-05-24

### Added

- Added support for instance-specific config and log files.

### Changed

- Updated prompt text to align `YOU:` with `CH:`.

### Fixed

- Resolved Rich markup errors in `/showvars`
