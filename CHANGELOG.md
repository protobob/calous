# Changelog

All notable changes to CALOUS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Changelog

  ## [1.5.0.dev] - 2025-01-04

  ### Breaking Changes
  - **Replaced Rich markup with ANSI codes** - Migrated from Rich library markup to direct ANSI escape sequences for color formatting
  - **Simplified cx_rust client** - Removed Rich tag processing logic in favor of direct ANSI code display
  - **Updated socket protocol behavior** - Changed "plain" format to mean "send ANSI codes directly" instead of stripped text

  ### Added
  - **Single source of authority for colors** - All color formatting now handled exclusively by calousd using ANSI codes
  - **Direct ANSI code support** - Color constants now contain ANSI escape sequences instead of color names
  - **Simplified color handling** - Streamlined `get_chat_color()` function to return ANSI codes directly

  ### Removed
  - **Rich library dependency for markup** - Eliminated Rich tag patterns like `[bold red]`, `[/bold]`, etc.
  - **Dual formatting systems** - Removed redundant color conversion between Rich markup and ANSI codes
  - **Complex Rich text processing in cx_rust** - Removed `parse_and_print_rich_text()` and related formatting functions

  ### Technical Improvements
  - **Cleaner architecture** - Eliminated the "two sources of authority" problem for color formatting
  - **Reduced complexity** - Simplified both calousd and cx_rust codebases by removing Rich conversion logic
  - **Better performance** - Direct ANSI code output without intermediate markup processing
  - **Maintained protocol compatibility** - Kept socket protocol interface intact for backward compatibility

  ## [1.4.4.dev] - 2025-01-02

  ### Fixed
  - **Container configuration issues** - Updated Dockerfile to use correct ~/.calous directory structure instead of legacy /root/calous
  - **Signal handling robustness** - Enhanced CTRL-C shutdown in daemon mode to properly save configurations even when clients disconnect
  - **Rich markup parsing gaps** - Expanded cx_rust Rich tag parser to handle bold color variants and line-ending patterns
  - **Path consistency across deployment** - Aligned container volume mounts with updated .calous directory structure

  ### Technical Improvements
  - **Improved error handling in signal handlers** - Added comprehensive exception handling for config saving during daemon shutdown
  - **Enhanced Rich text parsing** - Added support for bold color combinations like `[bold white]` and `[bold grey50]`
  - **Container deployment fixes** - Fixed volume mount mappings and directory creation in containerized deployments

  ## [1.4.3-dev] - 2025-01-02

  ### Added
  - **Rich text support in cx_rust client** - Added ANSI color parsing with crossterm for enhanced terminal output
  - **Command history in interactive mode** - Added persistent command history using rustyline with ~/.calous/cx_history.txt
  - **Tab completion for commands** - Comprehensive auto-completion for all 56+ commands and aliases in interactive mode
  - **Command hints while typing** - Real-time command suggestions as you type
  - **Rich/plain output control** - Added -r/--rich and -p/--plain flags to control output formatting
  - **File-based command completion** - calousd automatically writes available commands to ~/.calous/commands.txt for client tab 
  completion

  ### Changed
  - **Unified directory structure** - All components now use ~/.calous instead of mixed ~/calousd/~/hiollama paths
  - **Renamed legacy references** - Updated HiCommand/HiResponse to CxCommand/CxResponse, removed old "hi" naming
  - **Cleaner Rich text architecture** - Single point of format conversion in send_to_client, removed duplicate markup stripping
  - **Updated Rust toolchain** - Fixed compatibility issues by upgrading from package manager Rust 1.63 to rustup-managed latest 
  version

  ### Fixed
  - **Hardcoded path references** - Removed hardcoded paths from utility scripts and docstrings
  - **Rich markup preservation** - Fixed Rich formatting being stripped multiple times in the processing pipeline
  - **Client format preference** - Socket clients can now properly request and receive rich or plain text formatting
  - **Command completion accuracy** - Tab completion now includes user aliases and stays in sync with available commands

  ### Technical Improvements
  - **Code deduplication** - Extracted helper functions for command creation and response handling
  - **Removed unused imports** - Cleaned up cx_rust dependencies and eliminated compiler warnings
  - **Better error handling** - Improved fallback behavior for readline initialization and command processing

## [1.4.2.dev] - 2025-07-01

### Removed
- **Deprecated Chat Management Commands**: Eliminated `/chat.add` and `/chat.remove` commands
  - Commands no longer make sense in service-only mode where chat count should be consistent
  - Removed command handlers, service methods, formatters, and UI help references
  - Simplified architecture by removing dynamic chat management complexity
- **Unused Constants**: Cleaned up deprecated configuration constants
  - Removed `MAX_CHATS` and `DEFAULT_NUM_CHATS` constants (replaced by `SERVER_DEFAULT_NUM_CHATS`)
  - Updated all imports and references to use the single server constant (14 chats)
  - Consistent daemon architecture with fixed chat count
- **Quit Command System**: Completely removed quit functionality for daemon mode
  - Removed `/sys.quit` command registration, service methods, and ActionType enum value
  - Eliminated quit handling logic in session manager and UI help references
  - Daemon services should not have quit functionality - managed by system process control
- **Auto-Confirm Workaround Code**: Removed obsolete `non_interactive` mode system
  - Eliminated auto-confirm code that was a workaround before socket confirmations worked
  - Removed `non_interactive` attribute setting/unsetting throughout the codebase
  - Simplified confirmation logic since socket-based y/n confirmations now work properly with cx client

### Fixed
- **Critical Daemon Output Issues**: Resolved print statements that would fail when stdout is disabled
  - Fixed `_output()` method in session manager to not fall back to print() in daemon mode
  - Updated utility functions (`print_rainbow_header`, `print_chat_header`, `print_message_with_bar`) to accept output callback parameters
  - Removed stdout dependencies that would cause daemon crashes when stdout is redirected/closed
  - All output now properly routes through socket system in daemon mode

### Code Quality
- **Major Dead Code Cleanup**: Removed 200+ lines of unused/deprecated code
  - Deleted 142-line deprecated `listen_for_socket_deprecated()` method from app.py
  - Removed unused `output.py` module entirely (placeholder code never used)
  - Fixed corrupted imports in `list_commands.py` (broken shebang and malformed imports)
  - Removed `CLI_HISTORY_PATH` constant - not needed in daemon-only mode
  - Cleaned up file structure and eliminated broken/obsolete code

### Changed
- **Entry Point Simplification**: Updated `__main__.py` for daemon-only operation
  - Removed dynamic chat management flags and deprecated constant references
  - Simplified argument parsing to reflect fixed server chat count
  - Clear indication that CALOUS runs only in service/daemon mode

### Technical
- **Architecture Consistency**: Streamlined codebase for daemon-only operation
  - All chat management now uses fixed `SERVER_DEFAULT_NUM_CHATS` (14) consistently
  - Removed redundant/conflicting configuration constants and their references
  - Eliminated interactive CLI remnants and auto-confirm workarounds
  - Proper separation between socket output routing and legacy print fallbacks

### Impact
- **Improved Daemon Reliability**: Fixed critical stdout dependencies that could crash daemon
- **Cleaner Architecture**: Removed confusion between interactive and daemon modes
- **Better Maintainability**: Eliminated 200+ lines of dead code and simplified configuration
- **Consistent Operation**: Fixed server chat count at 14 with no dynamic add/remove operations

## [1.4.1.dev] - 2025-07-01

### Fixed
- **Daemon Output System**: Comprehensive refactoring of output handling for socket/daemon safety
  - Fixed broken `_output()` methods across multiple core modules that were causing type and runtime errors
  - Replaced direct print statements with socket-aware output routing via callback system
  - Implemented unified logging fallback for daemon mode when no client is connected
  - Removed all interactive input dependencies for full daemon compatibility
  - Fixed `CommandFormatter._output()` calls throughout the codebase
  - Updated PersonaManager and PluginManager to use callback-based output systems
- **Type Safety**: Resolved numerous type annotation and attribute access errors
  - Fixed missing class attributes and method signatures in core modules
  - Added proper type ignore comments where necessary for plugin instantiation
  - Corrected session manager and plugin manager attribute typing

### Changed
- **Output Architecture**: Replaced stdout-dependent output with daemon-safe alternatives
  - All user-facing output now routes through session manager or unified logger
  - Interactive confirmations removed from daemon code paths for safety
  - Plugin and persona managers now use callback-based output with logging fallback

## [1.4.0.dev] - 2025-07-01

### Added
- **Interactive Confirmation System**: Implemented y/n confirmation support for destructive commands over socket connections
  - Added `supports_confirmations` field to client requests for enabling interactive prompts
  - Confirmation requests bypass output buffering for immediate user interaction
  - Default behavior is safe (usually "n" for cancel) when confirmations fail or are unavailable
  - Works seamlessly in both command-line and interactive modes of the `cx` Rust client
- **Enhanced Socket Protocol**: Extended the socket communication protocol to support confirmation round-trips
  - Added `confirmation_request` and `confirmation_response` message types
  - Confirmation requests include unique IDs for proper request/response matching
  - Socket connections remain open throughout the confirmation flow

### Enhanced
- **Rust Client (`cx`)**: Major improvements to socket handling and user interaction
  - Implemented chunked socket reading to handle confirmation requests properly
  - Added interactive y/n prompts with default value support
  - Enhanced error handling and debug output for socket communication
  - Fixed socket connection lifecycle to support confirmation round-trips
- **Python Daemon**: Improved session management and output handling
  - Modified output buffering system to send confirmation requests immediately
  - Enhanced `request_confirmation()` method with proper timeout and fallback handling
  - Added confirmation ID generation and response tracking

### Fixed
- **History Commands**: Fixed file handling and message count tracking
  - Fixed `/history.load` to properly overwrite history file in .history folder and update message count
  - Fixed `/context.load` to properly handle chat_history loading
- **Socket Communication**: Resolved hanging issues with destructive commands
  - Fixed output buffering preventing confirmation requests from being sent
  - Improved socket read/write cycle for interactive operations

### Technical
- **Confirmation Protocol**: Established robust confirmation system architecture
  - Unique confirmation IDs prevent request/response mix-ups
  - Timeout handling ensures commands don't hang indefinitely
  - Fallback to safe defaults when confirmations are not supported
- **Socket Handling**: Enhanced both client and server socket implementations
  - Improved partial message handling in Rust client
  - Better connection lifecycle management
  - Enhanced debug output for troubleshooting socket communication

## [1.3.0.dev] - 2025-07-01

### Fixed
- **Rich Dependency Removal**: Complete removal of Rich library from codebase for container compatibility
  - Removed all Rich imports from 17+ files including core modules (app.py, session_manager.py, model_interaction.py)
  - Fixed `/sys.help.all` error by replacing Rich Table with simple text formatting
  - Updated all command formatters to use standard Python I/O instead of Rich markup
- **Chat.twist Command**: Fixed incomplete implementation that wasn't sending twisted content to models
  - Fixed `handle_regular_input()` method to store response in `self.last_response`
  - Fixed `process_input()` to call `handle_regular_input()` for non-command input
- **Directory Path Consistency**: Updated commands to use proper directory constants
  - Added `CHAT_HISTORY_DIR` constant pointing to `~/calousd/chat_history`
  - Fixed history commands to use centralized constants instead of hardcoded paths

### Added
- **History Status Command**: New `/history.vars` command showing history recording status and message count
- **Context Management System**: Complete new command category for saving/loading persona, prompts, and chat history
  - `/context.save <name>` - Save current context to JSON file
  - `/context.load <name>` - Load context from file (overwrites current data)
  - `/context.list` - List all saved contexts
  - `/context.delete <name>` - Delete saved context file
  - Added `CONTEXT_DIR` constant for consistent file storage

### Enhanced
- **Multi-word Argument Support**: Fixed argument parsing for commands with multi-word filenames
  - Updated registry to handle context and history commands with `nargs='+'`
  - Commands now properly join multi-word arguments (e.g., `/context.save admin panel`)
- **Directory Structure**: Updated constants to use `~/calousd/` instead of `~/calous/`
  - All file operations now use centralized directory constants
  - Consistent path handling across context, history, and persona commands

### Technical
- **Command Architecture**: Enhanced command registry with special argument handling
- **Service Layer**: Added `ContextService` for context operations with proper error handling
- **Formatter System**: Context commands follow established formatter patterns for consistent output
- **Path Management**: Centralized all directory paths in `constants.py` for maintainability

## [1.2.0-dev] - 2025-06-30

### Changed
- **Debug Flag Rename**: Changed `-i`/`--interactive` flag to `--debug` for clearer intent
- **Debug Output Control**: All debug messages now properly respect the `--debug` flag
  - Plugin loading debug messages (directory scanning, plugin discovery, configuration)
  - Chat history loading messages
  - Socket communication debug output
- **Complete Daemon Mode**: Eliminated all CLI/terminal mode remnants, application runs purely in daemon mode
- **Enhanced Output Buffering**: Fixed "invalid response" errors by implementing proper command output buffering
  - Commands now send consolidated JSON responses instead of multiple separate responses
  - Improved socket client compatibility and user experience

### Fixed
- **Debug Message Consistency**: Debug messages no longer appear without the `--debug` flag
- **Socket Response Consolidation**: Commands now properly buffer output and send single JSON responses
- **Plugin Manager Integration**: Plugin manager now properly inherits debug flag setting
- **Chat History Verbosity**: History loading messages only appear in debug mode

### Technical
- Updated argument parsing to use `--debug` instead of `-i`/`--interactive`
- Enhanced session manager to pass debug flag throughout the system
- Improved plugin manager with debug-controlled output
- Fixed output buffering implementation in socket command processing
- Centralized debug flag propagation from main entry point through all subsystems

## [1.1.0.dev] - 2025-06-30

### Changed
- **Socket Mode Default**: The application now starts in socket (daemon) mode by default. CLI/terminal mode has been removed.
- **Channel Count Configurable**: The number of chat channels is now configurable via a constant in `constants.py` and can still be set via command-line argument.
- **Output Method Refactor**: Introduced a new method to handle output in place of direct `print` statements, but existing `print` calls have not yet been replaced.


## [1.0.0.dev] - 2025-06-29

### Added - Client (cx)
- Config file support at `~/.calous/cx.json` with defaults for debug, chat targeting, and truncation
- `--no-truncate` (`-t`) flag for one-time truncation override
- Automatic version syncing with `Cargo.toml`

### Added - Server Protocol  
- `format` field in socket protocol for dual-format (rich/plain) output support
- Enhanced session manager to handle client output format requests

### Changed - Client (cx)
- Truncation now applies only to stdin data, not prompt text
- Help output cleaned up to show only client options, refers to `cx -c sys.help` for server commands

### Changed - Both
- **Version Synchronization**: Both client and server now use unified `1.0.0-dev` version for ecosystem consistency
- Protocol enhancement enables clients to request specific output formats

### Ecosystem Vision
- **VS Code Extension**: GitHub Copilot modification for CALOUS integration
- **Rich Python REPL**: Interactive Python environment with Rich formatting
- **Ollama API Bridge**: Context management layer translating HTTP API calls to CALOUS socket protocol

## [0.14.0.dev] - 2025-06-29

### Changed
- **BREAKING**: Complete project rebranding from HiOllama to CALOUS
  - Renamed all references throughout codebase, documentation, and command outputs
  - Updated environment variable from `HIOLLAMA_DEBUG` to `CALOUS_DEBUG`
  - Changed all import paths from `hiollama.*` to `calous.*`
  - Updated log messages from `[hiollama]` to `[calous]`
  - Renamed Rust client command examples from `hi` to `cx`
  - Updated plugin system references and documentation
  - Changed directory references from `~/hiollama/` to `~/calous/`
  - Updated container image name from `localhost/hiollama:latest` to `calous:latest`

### Technical
- Complete systematic renaming across 50+ files including Python modules, tests, scripts, and configuration
- Updated all plugin import paths and service references
- Modernized project identity while maintaining full backward compatibility of functionality
- All features and commands remain identical, only names and references changed

### License
- **IMPORTANT**: Project is now licensed under GNU General Public License v3.0 (GPL3)
- Updated LICENSE file with proper copyright notice and GPL3 terms

## [0.13.0.dev] - 2025-06-27

### Added
- **Protocol-Level Chat Targeting**: Implemented server-side chat targeting for socket clients
  - Socket server now accepts `"chat"` field in JSON messages to target specific channels
  - Automatically switches to requested chat channel before processing messages
  - Enables true multi-chat support for Rust client and other socket clients
  - Example: `{"type": "message", "chat": 3, "content": "Hello"}` targets chat 3

### Changed
- **Socket Server Architecture**: Moved socket server logic from `Chat` class to `ChatSessionManager`
  - Centralized socket handling in session manager for better multi-chat support
  - Old `Chat.start_socket_server()` method deprecated in favor of manager-based approach
  - Improved separation of concerns between chat instances and socket communication
- **Rust Client Protocol**: Updated Rust client to use new chat targeting protocol
  - Removed legacy chat switching commands from client-side logic
  - Now sends `"chat"` field directly in socket messages for server-side targeting
  - Cleaner protocol implementation with better error handling

### Fixed
- **Socket Mode Confirmations**: Fixed confirmation prompts to always default to "yes" in socket mode
  - File operations, history clearing, and plugin management now auto-confirm
  - Prevents socket clients from hanging on destructive operations
  - Applies to history commands, file operations, and plugin management
- **Socket Message Handling**: Fixed "Unknown message type" errors in socket server
  - Corrected message type validation logic in socket server
  - Improved error handling for malformed or unexpected message types

## [0.12.21] - 2025-06-27

### Added
- **VRAM Management**: Added `keep_alive` configuration for Ollama model persistence
  - Default setting: 30 minutes to balance performance and memory usage
  - Configurable via global config and visible in `/model.vars`
  - Automatically sent with all Ollama API calls to keep models loaded longer
- **Rust Client Chat Targeting**: Added `-n/--chat <NUM>` flag to target specific chat channels (1-14)
  - Example: `hi -n 2 Hello` sends message to chat channel 2
  - Example: `hi -n 3 -c chat.vars` shows variables for chat 3
  - Updated help documentation with chat channel examples

### Fixed
- **Socket Mode Stability**: Fixed socket mode to always use 14 chat instances
  - Ignores `num_chats` argument in socket mode for predictable behavior
  - Shows warning when chat count argument is ignored
  - Provides stable foundation for chat targeting features
- **Debug Output Control**: Fixed debug messages to only appear with `-i` flag
  - Socket mode now runs silently by default (`--socket`)
  - Verbose debug output only with explicit flag (`--socket -i`)
  - Fixed unconditional debug prints in both `app.py` and `model_interaction.py`

### Changed
- **Socket Mode Chat Management**: Disabled `/chat.add` and `/chat.remove` commands in socket mode
  - Prevents dynamic chat changes that could break client targeting
  - Matches existing pattern used for `/sys.quit` command blocking
  - Maintains stable 14-chat architecture for socket clients

### Technical
- **Socket Server Architecture**: Migrated socket server logic from individual `Chat` instances to `ChatSessionManager`
  - Enables true multi-chat support for socket clients and the Rust CLI tool
  - Chat switching via socket commands (`/chat.switch`) now works reliably across all 14 channels
  - Centralized socket command processing with proper session-level operations
  - All chat instances remain synchronized during socket operations
- Updated Rust client dependencies and help documentation
- Enhanced error handling for chat channel validation (1-14 range)
- Improved socket mode initialization and configuration management
- Added `keep_alive` parameter integration throughout the model interaction pipeline
- Fixed socket mode confirmation handling for destructive operations like `/history.purge`

### Known Issues
- Chat channel switching via Rust client requires architectural improvements
- Socket connections don't persist chat state between separate commands
- Multi-chat support in socket mode needs session manager integration

## [0.12.20.dev] - 2025-06-27

### Added - Python Server
- Model debug output showing full conversation sent to models
- Enhanced socket server handling for large payloads (>8KB)
- Protection against `/quit` command execution in socket mode

### Enhanced - Rust Client
- Fixed piped input with prompt arguments (`ls | hi "analyze this"`)
- Improved error handling for connection issues and large data
- Better argument parsing to prioritize command-line prompts over stdin
- Enhanced debug output and error messages

### Fixed - Python Server
- Socket buffer handling for commands with large piped input
- Rich markup parsing errors in server debug output
- User prompt inclusion in debug output when chat history disabled
- JSON parsing errors with incomplete socket data

### Fixed - Rust Client  
- Connection reset issues when sending large piped data
- Panic handling replaced with graceful error messages
- Proper handling of mixed stdin and command-line arguments

### Technical
- Improved socket communication protocol for reliable large message transmission
- Enhanced debug visibility for model interactions and data flow
- Better separation of server vs client functionality in codebase

## [0.12.19.dev] - 2025-06-27

### Fixed
- **model.switch**: Removed blocking interactive prompts that broke socket client compatibility
- **model.switch**: Now supports both CLI and socket usage patterns with dual-format output

### Changed
- **model.switch**: Command now accepts optional model selection parameter
- **model.switch**: Shows available models when used without arguments
- **model.switch**: Supports selection by number, exact name, or partial name matching
- **Help system**: Updated all help documentation to reflect new model.switch usage

### Technical
- Added `show_available_models()` method to UIManager with Rich and plain text output
- Added `select_model_by_input()` method to ModelService for flexible model selection
- Maintained backwards compatibility while fixing socket client issues

## [0.12.18.dev] - 2025-06-27

### Added

- **Rust Client Integration**: `hi` - a lightweight Rust-based Unix tool client that communicates with the daemon mode via Unix sockets, providing seamless command-line integration.
- **Global Output Capture**: Implemented system-wide capture and stripping of Rich/ANSI formatting tags for all command outputs, ensuring clean plain text delivery to socket clients.
- **Enhanced Variable Display**: Added `/chat.vars` and improved `/model.vars` commands to output configuration variables in plain text format compatible with external clients.

### Fixed

- **CommandResult Consistency**: Resolved critical bugs where `CommandResult` objects were missing required `action` arguments across multiple service modules (`model/services.py`, `log/services.py`).
- **Output Formatting**: Fixed Rich/ANSI tag stripping to work globally across all commands without requiring manual intervention in individual command handlers.
- **Confirmation Prompts**: Standardized confirmation logic for destructive operations (`/chat.reset`, `/history.clear`, `/alias.add` overwrite) to auto-confirm in daemon mode while preserving interactive prompts in terminal mode.

### Changed

- **Command Registry**: Enhanced the command execution pipeline with automatic output capture and formatting, making all commands socket-client compatible by default.
- **Socket Server Logic**: Improved daemon mode to capture and process all command outputs, including post-command context displays, ensuring complete plain text transmission.
- **Confirmation System**: Refactored confirmation prompts to use `app.confirm()` method, which intelligently handles interactive vs non-interactive modes based on the `--socket` flag.

### Technical Improvements

- **Mode-Agnostic Design**: Commands now work seamlessly in both terminal and daemon modes without requiring mode-specific code paths.
- **Output Pipeline**: Implemented stdout capture with Rich tag stripping in the command registry, ensuring consistent plain text output for all commands.
- **Error Handling**: Enhanced robustness by ensuring all service methods properly construct `CommandResult` objects with required parameters.

### Impact

- **Universal Compatibility**: All existing commands now work flawlessly with external clients like the Rust `hi` tool without any Rich formatting interference.
- **Streamlined Integration**: External tools can reliably parse and process command outputs, enabling better automation and scripting capabilities.
- **Maintainability**: The global output capture system eliminates the need for manual Rich tag handling in individual commands, reducing maintenance overhead.


## [0.12.19.dev] - 2025-06-27

### Fixed
- **model.switch**: Removed blocking interactive prompts that broke socket client compatibility
- **model.switch**: Now supports both CLI and socket usage patterns with dual-format output

### Changed
- **model.switch**: Command now accepts optional model selection parameter
- **model.switch**: Shows available models when used without arguments
- **model.switch**: Supports selection by number, exact name, or partial name matching
- **Help system**: Updated all help documentation to reflect new model.switch usage

### Technical
- Added `show_available_models()` method to UIManager with Rich and plain text output
- Added `select_model_by_input()` method to ModelService for flexible model selection
- Maintained backwards compatibility while fixing socket client issues

## [0.12.18.dev] - 2025-06-27

### Added

- **Rust Client Integration**: `hi` - a lightweight Rust-based Unix tool client that communicates with the daemon mode via Unix sockets, providing seamless command-line integration.
- **Global Output Capture**: Implemented system-wide capture and stripping of Rich/ANSI formatting tags for all command outputs, ensuring clean plain text delivery to socket clients.
- **Enhanced Variable Display**: Added `/chat.vars` and improved `/model.vars` commands to output configuration variables in plain text format compatible with external clients.

### Fixed

- **CommandResult Consistency**: Resolved critical bugs where `CommandResult` objects were missing required `action` arguments across multiple service modules (`model/services.py`, `log/services.py`).
- **Output Formatting**: Fixed Rich/ANSI tag stripping to work globally across all commands without requiring manual intervention in individual command handlers.
- **Confirmation Prompts**: Standardized confirmation logic for destructive operations (`/chat.reset`, `/history.clear`, `/alias.add` overwrite) to auto-confirm in daemon mode while preserving interactive prompts in terminal mode.

### Changed

- **Command Registry**: Enhanced the command execution pipeline with automatic output capture and formatting, making all commands socket-client compatible by default.
- **Socket Server Logic**: Improved daemon mode to capture and process all command outputs, including post-command context displays, ensuring complete plain text transmission.
- **Confirmation System**: Refactored confirmation prompts to use `app.confirm()` method, which intelligently handles interactive vs non-interactive modes based on the `--socket` flag.

### Technical Improvements

- **Mode-Agnostic Design**: Commands now work seamlessly in both terminal and daemon modes without requiring mode-specific code paths.
- **Output Pipeline**: Implemented stdout capture with Rich tag stripping in the command registry, ensuring consistent plain text output for all commands.
- **Error Handling**: Enhanced robustness by ensuring all service methods properly construct `CommandResult` objects with required parameters.

### Impact

- **Universal Compatibility**: All existing commands now work flawlessly with external clients like the Rust `hi` tool without any Rich formatting interference.
- **Streamlined Integration**: External tools can reliably parse and process command outputs, enabling better automation and scripting capabilities.
- **Maintainability**: The global output capture system eliminates the need for manual Rich tag handling in individual commands, reducing maintenance overhead.


## [0.12.17.dev] - 2025-06-26

### Added
- **Daemon Mode**: Introduced `--socket` daemon mode, allowing the app to run as a server that listens for input via Unix sockets. This enables seamless integration with lightweight tools like the Rust-based `hi` Unix utility.
- **Debug Output**: Added `-i` flag to daemon mode for enhanced debug message output, providing better visibility into server operations.

### Impact
- **Enhanced Workflow**: Users can now send prompts and commands directly to the daemon using external tools, streamlining automation and scripting.
- **Flexibility**: The app remains fully functional in non-daemon mode, ensuring backward compatibility and versatility for diverse use cases.

### Technical
- **Unix Socket Integration**: Implemented robust socket handling for reliable communication between the daemon and external clients.
- **Debugging Enhancements**: Improved logging and debug output for daemon mode, aiding in troubleshooting and performance monitoring.

## [0.12.16.dev] - 2025-06-25

### Added
- MCPClientPlugin for Model Control Protocol client support (but not tested)

## [0.12.15.dev] - 2025-06-25
### Added
- General-purpose shell command execution plugin (`!command`) for container debugging and other use cases.

## [0.12.14.dev] - 2025-06-25
### Changed
- Bumped APP_VERSION to 0.12.14.dev in constants.py
- Calculator plugin: separated LLM-facing and user-facing descriptions in function schema to prevent LLM prompt preamble from showing to users

## [0.12.13.dev] - 2025-06-24

### Added
- Improved CLI history and command completion using prompt_toolkit
- Centralized CLI history file location using CLI_HISTORY_PATH constant
``
```
## [0.12.12.dev] - 2025-06-24`
### Added`
- `/history.purge` command: Purge the most recent N entries from current chat history, with confirmation and permanent deletion.
- Improved help screens for history commands, including usage explanations.
- Updated `ARCHITECTURE.md` to document command implementation patterns for future maintainers.


## [0.12.11.dev] - 2025-06-24
### Added
- New `/history.save` command to save current chat history to a file.
- New `/history.load` command to load chat history from a file (overwrites current history).
- New `/history.list` command to list all saved chat history files (shows base names only).
- New `/history.delete` command to delete a saved chat history file with confirmation.
- All new history commands are now documented in both the global and history-specific help menus.

### Changed
- `/history.save` now prompts for confirmation before overwriting existing files.
- `/history.list` output now hides `.jsonl` extension for consistency with load/delete commands.

### Fixed
- Improved filename sanitization and user feedback for history file operations.

## [0.12.10.dev] - 2025-06-24

### Added
- `/history.on` and `/history.off` commands to enable/disable chat history recording per chat.
- Updated help system to document new history control commands in both global and category-specific help.
- History command count in help now reflects new commands.

### Changed
- Bumped version to 0.12.19.dev.

## [0.12.9.dev] - 2025-06-24

### Fixed
- Fixed `/chat.reset` command not properly resetting persona data
- The command now correctly calls `self.app.persona.reset()` to clear persona name and all slot contents
- Chat reset functionality now works as intended, clearing both chat history and persona system

## [0.12.8.dev] - 2025-06-23

### Changed
- Moved config file from `~/.hiollama_config_unified.json` to `~/hiollama/config.json` for better containerization support
- All HiOllama files now centralized in `~/hiollama/` directory (config, logs, history, personas)

### Technical
- Updated CONFIG_PATH in constants.py to use HIOLLAMA_DIR consistently
- Improves deployment and data management for containerized environments

## [0.12.7.dev] - 2025-01-09

### Added
- New streamlined `/sys.help` command showing concise getting-started guide
- New `/sys.help all` command for comprehensive command reference
- Improved help system architecture with better user experience for new users

### Changed
- Restructured main help screen to focus on essential first-time user commands
- Updated help system to provide progressive disclosure (overview → categories → details)
- Improved formatting and alignment in help screens
- Enhanced sys category help to include both help commands

### Technical
- Refactored `UIManager.help_menu()` for streamlined experience
- Added `UIManager.help_menu_all()` for comprehensive command listing
- Updated help command routing in system services
- Maintained backwards compatibility with existing help infrastructure

## [0.12.6.dev] - 2025-01-08

### Added
- Complete custom help system overhaul with organized, readable command documentation
- Custom help screens for all major command categories (persona, model, alias, chat, log, history, plugin, sys, file, prompt)
- Descriptive introductions for each command category explaining their purpose and functionality
- Logical command grouping with section headers (e.g., "SESSION MANAGEMENT", "PLUGIN DISCOVERY", etc.)
- Consistent Rich markup formatting with proper color schemes (grey50 commands, white descriptions)
- Improved help navigation with category-specific help commands (e.g., `/persona.help`, `/model.help`)

### Changed
- Replaced auto-generated table-based help with custom formatted help screens for better readability
- Updated help text colors from grey to white for improved visibility
- Reorganized command displays to be more intuitive and user-friendly
- Enhanced help descriptions with specific details about file locations, persistence, and usage patterns

### Fixed
- Fixed help command access issues where category help commands were trying to access non-existent `ui_manager` attribute
- Corrected all help commands to use proper `handler.app.ui` instead of `handler.app.ui_manager`
- Resolved Rich markup processing issues by using `print()` instead of `self.console.print()` for help displays

## [0.12.5.dev] - 2025-06-09

### Changed
- Renamed main class from `HiOllamaChat` to `Chat` for cleaner, more concise naming
- Updated all imports and type annotations to reflect the new class name

## [0.12.4.dev] - 2025-06-09

### Fixed
- Fixed `/model.setctx` command crash caused by missing `log_system_event` method in UnifiedLogger
- Corrected success message for `/model.setctx` to properly indicate global scope instead of "for this chat"

## [0.12.3.dev] - 2025-06-09

### Added
- Split `/sys.vars` into focused commands: `/model.vars`, `/chat.vars`, `/log.vars`
- Global context window management across all chat instances

### Changed
- Context window (`num_ctx`) is now a global setting instead of per-chat
- New chat instances automatically inherit current global context window
- Reorganized help menu: removed headers, moved vars commands to end of sections
- Cleaned up variable displays by removing excessive "*GLOBAL*" indicators
- Moved evaluation mode (verbosity) from model variables to chat variables

### Removed
- `/sys.vars` command (replaced by specific variable commands)

### Technical
- Updated `ConfigManager` to handle global `num_ctx` setting
- Modified `SessionManager` to propagate context window changes to all chats
- Refactored `ModelService.set_context_size()` to operate globally
- Updated UI methods for cleaner, focused variable displays

## [0.12.2.dev] - 2025-06-09

### Fixed
- **Model Thinking API**: Improved error handling for unsupported thinking models
  - Enhanced exception handling in `_handle_streaming` method to catch both `TypeError` (older ollama client) and `ollama.ResponseError` (unsupported model versions)
  - Added helpful error messaging suggesting model updates with `ollama pull {model_name}` when thinking is not supported
  - Resolved issue where thinking content was displayed even when `model.think` was set to "off"
  - Fixed API errors for models that don't support thinking mode without proper fallback

### Technical
- **Exception Handling**: More robust error detection for Ollama thinking API compatibility
- **User Experience**: Better guidance for users when models need updates to support new features

## [0.12.1.dev] - 2025-06-07

### Fixed
- **Legacy Command Cleanup**: Removed all legacy wrapper functions from command refactoring
  - Eliminated backward compatibility wrappers (`cmd_model`, `cmd_toggle_eval`, `cmd_toggle_think`, etc.)
  - Cleaned up obsolete `__pycache__` files from old command structure
- **Command Test Suite**: Updated test files to use new dotted command format
  - Fixed `test_commands.py` and `test_commands_simple.py` to test `/sys.help`, `/model.switch`, etc.
  - Created comprehensive `test_new_commands.py` for validating command registration and categorization
- **Test Infrastructure**: All 38 commands now properly tested with new hierarchical structure
  - Verified zero legacy commands remain in system
  - Confirmed all command categories are correctly organized

### Technical
- **Complete Legacy Removal**: Final cleanup phase of major command restructuring
- **Enhanced Testing**: Robust test coverage for new command architecture
- **Validation**: Comprehensive verification that refactoring left no obsolete code

## [0.12.0.dev] - 2025-01-07

### MAJOR ARCHITECTURAL RESTRUCTURING 🏗️

#### Added
- **Hierarchical Command Organization**: Complete migration from flat command files to category-based directory structure
- **Service Layer Architecture**: Implemented dedicated service classes for business logic separation
  - `AliasService`, `ChatService`, `ModelService`, `PersonaService`, `HistoryService`, `LogService`, `FileService`, `PluginService`, `PromptService`, `SysService`
- **Specialized Formatters**: Category-specific formatter classes for consistent UI presentation
  - Individual formatters for each command category with Rich markup support
- **Enhanced Command Registration**: All 39 commands successfully reorganized into 10 logical categories:
  - `alias/` (4 commands), `chat/` (5 commands), `file/` (1 command), `history/` (2 commands)
  - `log/` (3 commands), `model/` (5 commands), `persona/` (10 commands), `plugin/` (3 commands)  
  - `prompt/` (3 commands), `sys/` (3 commands)

#### Changed
- **BREAKING**: Complete restructuring of command file organization
  - Migrated from flat files (`general.py`, `navigation.py`, `model.py`, etc.) to hierarchical structure
  - Each category now contains: `commands.py`, `services.py`, `formatters.py`, `__init__.py`
- **Separation of Concerns**: Clear division between command handling, business logic, and UI formatting
- **Import Structure**: Updated `commands/__init__.py` to import from new hierarchical modules
- **Error Handling**: Consistent validation and user feedback across all command categories

#### Removed
- Legacy command files: `general.py`, `navigation.py`, `model.py`, `history.py`, `persona.py`, `file.py`
- Obsolete import paths and flat command organization

#### Technical
- **Code Organization**: Each command category follows consistent structure:
  - Commands handle user interaction and argument parsing
  - Services contain business logic and validation
  - Formatters manage UI presentation and Rich markup
- **Enhanced Maintainability**: Modular architecture enables easier testing and future development
- **Consistent Patterns**: Standardized error handling, result objects, and user guidance

### Impact
This represents a foundational architectural improvement that enhances code maintainability, testability, and extensibility while preserving all existing functionality. The new structure provides a solid foundation for future command development.

## [0.11.2.dev] - 2025-06-06

### Added
- **Image Loading Support for Vision Models**: JPG, PNG, and other image files can now be loaded with `file.load` and automatically passed to vision models (llama3.2-vision, llava, etc.)
- Added `IMAGE_EXTENSIONS` constant for supported image formats (.jpg, .jpeg, .png, .gif, .bmp, .webp, .tiff, .tif, .svg)
- Created `ImageService` for handling image file operations with base64 encoding
- Enhanced file type validation to properly categorize images vs binary files

### Changed
- Modified `handle_regular_input()` and `talk_to_model()` to support images embedded in message content
- Updated file loading logic to detect and handle image files differently from text files
- Images are now embedded in message content following Ollama's multimodal API format
- Moved file extension constants from inline definitions to `constants.py` for better organization

### Technical
- Refactored `handler.py` following established patterns with `HandlerFormatter` and service classes
- Created `CommandParsingService` and `CommandExecutionService` for better separation of concerns
- Enhanced error handling for image loading operations with standardized formatting
- Images passed via message `images` field rather than separate API parameter

## [0.11.1.dev] - 2025-06-06

### Added
- New service layer architecture with `AliasService` and `ChatService`
- Comprehensive `CommandFormatter` system for consistent UI output
- Specialized `AliasFormatter` and `FileFormatter` classes
- Enhanced error handling with standardized formatting
- Confirmation utilities in formatters

### Changed
- Refactored `general.py` commands to use service layer pattern
- Refactored `file.py` commands to use `FileFormatter`
- Eliminated duplicate wrapper functions in command registration
- Improved separation of concerns between UI and business logic
- All error messages now consistently start with newline character
- Enhanced type hints and documentation

### Improved
- Code maintainability through better separation of concerns
- Testability by extracting business logic from UI concerns
- Consistency across all command output formatting
- File size management - kept modules under 150 lines for better readability

### Technical
- Added `alias_service.py` for alias management logic
- Added `chat_service.py` for chat operations
- Added `formatters.py` for centralized UI formatting
- Updated constants with new UI formatting classes

## [0.11.0.dev] - 2025-01-XX

### Added
- Comprehensive file loading safety checks with configurable size limits
- Multi-encoding support (UTF-8, UTF-8 BOM, Latin-1, CP1252, ASCII) for robust file reading
- File type validation with warnings for binary/executable files
- Content preview functionality for loaded files
- User confirmation prompts for large files and potentially problematic file types

### Changed
- **BREAKING**: Removed obsolete `system`, `setprompt`, and `load` commands from command registry
- Made file loading prompt parameter optional (now defaults to empty string)
- Improved file extension validation with explicit handling for files without extensions
- Enhanced error messages for file operations with resolved path information
- Moved file size constants (`MAX_FILE_SIZE`, `LARGE_FILE_WARNING_SIZE`) to centralized constants.py

### Fixed
- Markdown injection vulnerability in file content formatting (now uses safe indentation)
- Command system argument parsing for obsolete commands
- File loading robustness with comprehensive encoding fallback chain

### Security
- Prevented markdown injection attacks through secure content indentation
- Added file size limits to prevent memory exhaustion
- Enhanced path resolution and validation

### Refactored
- Complete overhaul of `hiollama/commands/file.py` with modular utility functions
- Extracted file reading, validation, and formatting logic into separate functions
- Improved code organization and maintainability

## [0.10.0.dev] - Previous Release

### Added
- **Persona System**: Complete replacement for the old `/system` command
  - Modular persona system with 10 slots (0-9) for building layered system prompts
  - Named personas saved as JSON files in `~/hiollama/persona/`
  - Commands: `/persona.set`, `/persona.get`, `/persona.clear`, `/persona.name`, `/persona.show`, `/persona.reset`
  - Persistence: `/persona.save`, `/persona.load`, `/persona.list`, `/persona.delete`
  - Multi-word support for persona names and content (no quotes needed)
  - Per-chat persona storage - each chat maintains its own persona data
  - Automatic prompt concatenation with double newlines for optimal model parsing

### Changed
- Active chat display now shows persona names instead of system prompt content
- Updated UI help menu to include comprehensive persona commands
- File paths now use centralized constants from `constants.py`

### Removed
- **BREAKING**: Removed deprecated `/system` command (replaced by persona system)
- No backwards compatibility - clean migration to persona system

### Fixed
- Proper filename character validation for persona names
- Overwrite protection for saved personas with confirmation prompts

---

## [0.9.1.dev] - 2025-06-04

### Added
- User-defined alias system with persistent storage in config
- Built-in aliases: `/quit` for `/sys.quit`, `/help` for `/sys.help`
- New alias commands:
  - `/alias.add <alias> <command>` - Create custom command aliases
  - `/alias.remove <alias>` - Remove user-defined aliases
  - `/alias.list` - Display all current aliases
  - `/alias` - Show alias command help

### Technical
- Extended ConfigManager with alias persistence methods
- Enhanced CommandRegistry to support both built-in and user-defined aliases
- User aliases stored in global config section alongside other settings

---

## [0.9.0.dev] - 2025-06-04

### MAJOR CHANGES
- **Complete Command System Overhaul**: Replaced all single-word commands with hierarchical dot-notation system
- **Breaking Change**: Removed all legacy commands - users must now use new command structure

### Added
- Hierarchical command structure with logical grouping:
  - **Chat Management**: `/chat.add`, `/chat.switch`, `/chat.remove`, `/chat.twist`, `/chat.reset`
  - **Model Control**: `/model.switch`, `/model.setctx`, `/model.eval on/off`, `/model.think on/off` 
  - **Prompt Management**: `/prompt.use`, `/prompt.set`, `/prompt.list`
  - **History & Logging**: `/history.show`, `/history.clear`, `/log.on`, `/log.off`, `/log.today`
  - **File Management**: `/file.load`
  - **Plugin System**: `/plugin.list`, `/plugin.info`, `/plugin.reload`
  - **System Commands**: `/sys.help`, `/sys.vars`, `/sys.quit`

### Changed
- Updated help menu to reflect new hierarchical command organization
- Improved command categorization and organization
- Enhanced command descriptions for better clarity

### Removed
- All legacy single-word commands (26+ commands removed)

### Fixed
- `/file.load` now properly handles multi-word prompts
- Logging commands now use correct attribute names

---

## [0.8.2.dev] - 2025-06-04

### Added
- `/reload_plugins` command for dynamic plugin reloading during development
- Plugin reload functionality exposed to users through command interface
- Enhanced plugin development workflow with hot-reload capability

### Fixed
- Plugin dependencies in setup.py (removed unused beautifulsoup4, added missing asteval)
- Plugin system dependency management improved

## 0.8.1.dev (2025-06-03)

### Changed
- **Plugin Manager Architecture Refactor**: Moved plugin manager ownership from first chat instance to session manager
  - Plugin manager now initialized and owned by `ChatSessionManager`
  - All chat instances receive plugin manager via dependency injection
  - Eliminated asymmetric design where Chat 1 had special responsibilities
  - Improved plugin lifecycle management and maintainability

### Fixed
- **Plugin Registration Logging**: Fixed inconsistent success message printing for hook plugins
  - Corrected print statement placement in plugin registration logic
  - All plugin types now receive consistent success feedback

### Technical
- Enhanced session manager with `_initialize_plugin_manager()` method
- Updated `add_chat()` method to properly inject shared plugin manager
- Cleaner separation of concerns between session management and plugin management
- Improved architectural consistency across chat instances

### Impact
- More robust multi-chat plugin sharing
- Cleaner codebase with better separation of concerns
- Foundation for future plugin system enhancements
- Safer dynamic chat operations without affecting plugin system

## 0.8.0.dev (2025-06-03)

### Added
- **Centralized Plugin Function Call Logging**: Implemented unified logging system for all plugin function calls
- Enhanced plugin architecture with improved base class design
- Comprehensive function call tracking with arguments, results, and error logging
- Automated test suite for centralized logging functionality

### Changed
- **Plugin Architecture Enhancement**: Modified `FunctionCallingPlugin` base class structure
  - Made `execute_function()` non-abstract with default JSON conversion implementation
  - Added abstract `call_function()` method that plugins must implement
  - Improved plugin instantiation and error handling
- Centralized all function call logging in `model_interaction.py`

### Fixed
- Resolved abstract method instantiation errors for function calling plugins
- Improved consistency of logging format across all plugin function calls

### Technical
- Added centralized logging in `ModelInteraction._handle_function_calls()` method
- Enhanced plugin base class with backward compatibility
- Implemented comprehensive test coverage for logging functionality
- Updated plugin architecture to support cleaner, more maintainable code

### Impact
- All plugin function calls (dice roller, calculator, future plugins) now automatically logged
- Developers can create plugins without implementing logging code
- Improved debugging and auditing capabilities for plugin usage
- Foundation for enhanced plugin development and monitoring

## 0.7.1.dev (2025-06-02)

### Added
- Plugin configuration system with selective plugin loading
- Enhanced plugin logging with unified_logger integration
- Plugin metadata and capability display in UI
- Improved dice_roller plugin with better error handling and validation

### Changedn
- Renamed "Functions" to "LLM Tools" in plugin UI for clarity
- Updated plugin discovery system documentation
- Enhanced plugin loading with detailed logging and error messages
- Improved plugin status reporting in log files

### Technical
- Added `plugin_config.py` for centralized plugin enablement control
- Implemented selective plugin loading with ENABLED_PLUGINS configuration
- Enhanced dice_roller plugin implementation with validation and error handling
- Added plugin loading summary with capability reporting

## 0.7.0.dev (2025-06-02)

### Added
- Comprehensive plugin system architecture with function calling support
- Plugin management and discovery system
- Plugin commands: `/plugins` to list available plugins, `/plugin <name>` for details
- D&D-style dice roller plugin as first example plugin
- Function calling integration with Ollama API
- Plugin capability framework (function calling, commands, hooks)

### Changed
- Enhanced model interaction to support function calling capabilities
- Updated command system to handle plugin-provided commands

## [0.6.16.dev] - 2025-06-02

### Improved
- Enhanced `/showvars` command output formatting
- Reorganized variable display with clear sections for global settings and chat-specific variables
- Improved readability with "GLOBAL SETTINGS" and "CHAT # VARIABLES" sections

## [0.6.15.dev] - 2025-06-02

### Added
- **Temperature Control**: New `/settemp` command for per-chat temperature control (0.0-2.0)
- Temperature setting persists in chat configuration and displays in `/showvars` output
- Uses Ollama's default temperature of 0.8 for consistent behavior with Ollama defaults
- Temperature validation with helpful error messages for out-of-range values
- Updated help menu to include temperature command documentation

### Enhanced
- **Model Parameter Control**: Extended model interaction to pass temperature parameter to Ollama API
- **Configuration System**: Temperature included in unified config save/load operations
- **UI Consistency**: Temperature display follows existing `/showvars` formatting patterns

### Technical
- Added `DEFAULT_TEMPERATURE` (0.8), `MIN_TEMPERATURE` (0.0), `MAX_TEMPERATURE` (2.0) constants
- Enhanced `ModelInteraction._handle_streaming()` to pass temperature in options dictionary
- Extended chat configuration schema to include temperature per chat instance
- Updated version to 0.6.15.dev

## [0.6.14.dev] - 2025-06-01

### Documentation
- **Major documentation overhaul**: Complete rewrite of README.md and ARCHITECTURE.md
- **NEW**: Created comprehensive COMMANDS.md with all 22 implemented commands
- **Enhanced**: Updated TODO.md with organized roadmap and 50+ enhancement ideas
- **Fixed**: Corrected command documentation to reflect actual implementation
- **Improved**: Better project structure and user onboarding experience

### Architecture
- **Clarified**: Single global model architecture across all chat sessions
- **Documented**: Complete technical deep dive with Mermaid diagrams
- **Enhanced**: Command registry and extensibility guidelines

### Commands
- **Verified**: All 22 commands now accurately documented
- **Organized**: Commands categorized by functionality
- **Planned**: Added /rename command to development roadmap

## [0.6.13.dev] - 2025-06-01

### Removed
- **Deprecated `/setmax` system**: Removed old message-count-based history management
- `MAX_HISTORY` configuration option and related trimming logic
- `/setmax` command from chat history commands
- Max History display from `/showvars` output

### Changed
- **Simplified context management**: Chat history now grows naturally, limited only by context window (`/setctx`)
- Context usage is now controlled exclusively through token-based `/setctx` command (2048-32768 tokens)
- Cleaner user experience with single context control instead of dual history/context limits

### Technical
- Removed `DEFAULT_MAX_HISTORY` constant and all related code
- Updated documentation to reflect streamlined context management
- All tests updated to remove `MAX_HISTORY` references

## [0.6.12.dev] - 2025-06-01

### Added
- **VRAM Estimation**: Context window VRAM usage estimation now displays in `/showvars`
- Real-time VRAM estimates based on user-set context window size from `/setctx`
- Intelligent model parameter detection for accurate memory calculations

### Enhanced
- **Improved `/setctx` guidance**: Updated with realistic VRAM usage estimates and better warnings
- Context window recommendations with performance impact warnings
- VRAM estimates now account for model size, quantization, and context length

### Fixed
- VRAM estimation quantization handling for integer values from model metadata
- Context VRAM calculation uses proper KV cache + attention overhead formula
- Display indentation issues in `/showvars` output

### Technical
- Enhanced `estimate_context_vram_usage()` with realistic attention overhead calculation (20% of KV cache)
- Improved error handling for model metadata parsing
- Better parameter count and quantization detection from Ollama model info

## [0.6.11] - 2025-06-01

### Added
- `/setctx` command to set custom context window size (2048-32768 tokens)
- User-controlled context window overrides Ollama's default 2048 limit
- Context usage percentage now reflects user-set context window instead of model metadata
- VRAM estimation updated to use user-defined context size
- Input validation with helpful error messages for context limits

### Changed
- Default context window explicitly set to 2048 tokens
- UI context displays now based on user settings rather than model defaults
- Context percentage calculations use actual user-set values

### Technical
- Added `num_ctx` parameter to Ollama API calls via options
- Enhanced configuration system to persist context window settings
- Updated help menu with new context management command

## [0.6.10.dev] - 2025-05-31

### Enhanced
- **Context Color Coding**: Added color indicators for context usage (0-24% green, 25-49% yellow, 50-74% orange, 75-100% red)
- **UI Cleanup**: Removed technical tokenizer information from user-facing displays for cleaner interface

### Technical
- Tokenizer data still collected internally for accurate token counting while hiding technical details from users
- Improved visual feedback for context window management with intuitive color coding

## [0.6.9.dev] - 2025-05-31

### Added
- **Context Window Detection**: Automatic detection of model context window sizes from Ollama metadata
- **Context Usage Percentage**: Real-time display of context window usage in input prompt and `/showvars`
- **Tokenizer Integration**: Automatic tokenizer selection based on model metadata for accurate token counting
- **Enhanced Model Information**: Display context window, tokenizer type, and model architecture in `/showvars`

### Enhanced
- **Input Prompt**: Replaced old `CH:#/#` format with intuitive `Context: X%` display
- **Model Selection**: Shows context window size and tokenizer type during model selection
- **Variables Display**: Added comprehensive context window information with visual progress bar

### Technical
- Added `ContextWindowInfo` dataclass for structured model metadata
- Implemented `get_context_window_info()` and `get_context_usage_percentage()` methods
- Token counting includes system prompt and full chat history
- Support for multiple tokenizer types (gpt2, llama, mistral, etc.)

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
- Upgraded to olloma library 0.5.2.dev2 for native thinking support
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
