# Changelog

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
