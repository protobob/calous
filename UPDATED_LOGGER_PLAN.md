# Enhanced UnifiedLogger Implementation Plan

## Overview
Enhance the existing `UnifiedLogger` class in CALOUS to provide structured, multi-stream logging with configurable levels and proper debug routing separation.

## Prerequisites
- Python standard library `logging` module
- Existing `UnifiedLogger` class in unified_logger.py
- Constants file at constants.py
- Current daily log file structure in `~/.calous/logs/`

## Implementation Steps

### Phase 1: Read Current Implementation
1. **Read unified_logger.py** - Understand current structure, methods, and usage patterns
2. **Read constants.py** - Find log directory constants and paths
3. **Search codebase for UnifiedLogger usage** - Find all current call sites to understand API compatibility needs

### Phase 2: Design Enhanced Structure
4. **Define new log streams**:
   - `app.log` - General application events
   - `debug.log` - Debug information (daemon internals, socket handling)
   - `model.log` - Model interactions, API calls, responses
   - `audit.log` - Command execution, user actions
   - `error.log` - Errors and exceptions

5. **Define log levels**:
   - `DEBUG` - Detailed diagnostic info
   - `INFO` - General operational messages
   - `WARNING` - Warning conditions
   - `ERROR` - Error conditions
   - `CRITICAL` - Critical failures

### Phase 3: Enhance UnifiedLogger Class
6. **Add new attributes**:
   ```python
   self.debug_enabled = debug_flag  # From daemon startup
   self.loggers = {}  # Dictionary of stream-specific loggers
   self.log_level = logging.INFO  # Default level
   ```

7. **Add new methods**:
   - `debug(message, stream='debug', **kwargs)` - Debug-level logging
   - `info(message, stream='app', **kwargs)` - Info-level logging
   - `warning(message, stream='app', **kwargs)` - Warning-level logging
   - `error(message, stream='error', **kwargs)` - Error-level logging
   - `audit(command, user_info, result, **kwargs)` - Audit logging
   - `model_interaction(request, response, timing, **kwargs)` - Model logging

8. **Add structured logging support**:
   - JSON formatting for machine-readable logs
   - Context fields (timestamp, chat_channel, user_session, etc.)
   - Correlation IDs for tracking related events

### Phase 4: Implement Core Functionality
9. **Create log file rotation**:
   - Daily rotation (existing pattern)
   - Size-based rotation for high-volume streams
   - Configurable retention (e.g., keep 30 days)

10. **Add configuration support**:
    - Read log level from config file or environment
    - Stream enable/disable flags
    - Output format selection (JSON vs plain text)

11. **Maintain backward compatibility**:
    - Keep existing `log()` method unchanged
    - Ensure existing call sites continue working
    - Gradual migration path for enhanced features

### Phase 5: Integration Points
12. **Add debug routing methods**:
    ```python
    def debug_socket(message, connection_id=None):
        # Route socket debug info to debug.log, not client
    
    def debug_command(command, args, chat_channel):
        # Route command processing debug info
    
    def debug_model(prompt, response, metadata):
        # Route model interaction debug info
    ```

13. **Create context managers**:
    ```python
    @contextmanager
    def log_context(chat_channel=None, user_id=None):
        # Add context to all log messages in this block
    ```

### Phase 6: Testing and Validation
14. **Write test cases**:
    - Verify backward compatibility
    - Test log rotation and cleanup
    - Validate structured logging format
    - Test debug routing (debug info goes to logs, not client)

15. **Test with existing codebase**:
    - Start daemon with enhanced logger
    - Verify existing functionality works
    - Check that debug info routes to files properly
    - Confirm client output remains clean

### Phase 7: Documentation and Migration
16. **Update constants.py** with new log file paths if needed

17. **Create migration guide** for updating existing log calls:
    ```python
    # Old way
    logger.log("Debug info")
    
    # New way (optional, for enhanced features)
    logger.debug("Debug info", stream='socket', connection_id=123)
    ```

## File Modifications Required

### Files to Read First:
- unified_logger.py (current implementation)
- constants.py (log paths)
- config.py (configuration patterns)

### Files to Modify:
- unified_logger.py (enhance existing class)
- constants.py (add new log file constants if needed)

### Files NOT to Modify (per AI_README.md):
- `app.py`, `ui.py`, `model_interaction.py`, `session_manager.py`

## Success Criteria
1. **Backward Compatibility**: All existing UnifiedLogger calls work unchanged
2. **Debug Separation**: Debug info routes to log files, not client output
3. **Structured Logging**: JSON-formatted logs available for automation
4. **Configurable**: Can enable/disable debug logging via config
5. **Performance**: No significant performance impact on daemon operations
6. **Clean Client Output**: Socket clients receive only intended output, no debug leakage

## Implementation Notes
- Use Python's standard `logging` module internally for robustness
- Maintain the existing daily log file pattern users expect
- Add new features as optional enhancements, not breaking changes
- Focus on solving the "debug info going to client" problem as primary goal
- Keep within CALOUS architectural constraints (no new abstraction layers)

This plan provides a complete roadmap for enhancing UnifiedLogger while respecting CALOUS's architectural boundaries and maintaining system stability.