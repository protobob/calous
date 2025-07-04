#!/bin/bash

# Test script for all calousd commands - checking for ANSI color issues after Rich markup removal
# This script runs each command and logs any errors that occur

LOG_FILE="/home/aswin/python/calous/command_test_results.log"
ERROR_LOG="/home/aswin/python/calous/command_errors.log"
COMMANDS_FILE="/home/aswin/.calous/commands.txt"

# Clear previous logs
> "$LOG_FILE"
> "$ERROR_LOG"

echo "Testing all calousd commands for ANSI color issues..."
echo "Results will be logged to: $LOG_FILE"
echo "Errors will be logged to: $ERROR_LOG"
echo "Started at: $(date)" | tee -a "$LOG_FILE"
echo "=============================================" | tee -a "$LOG_FILE"

# Read commands from file and test each one
while IFS= read -r command; do
    # Skip empty lines
    if [[ -z "$command" ]]; then
        continue
    fi
    
    echo "Testing command: $command" | tee -a "$LOG_FILE"
    
    # Run the command with cx and capture both stdout and stderr
    # Use timeout to prevent hanging on interactive commands
    timeout 5s cx -c "$command" 2>&1 | tee -a "$LOG_FILE"
    
    # Check exit code
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        echo "ERROR: Command '$command' failed with exit code $exit_code" | tee -a "$ERROR_LOG"
        echo "Exit code: $exit_code" >> "$LOG_FILE"
    fi
    
    echo "---" >> "$LOG_FILE"
    
    # Small delay to prevent overwhelming the daemon
    sleep 0.1
    
done < "$COMMANDS_FILE"

echo "=============================================" | tee -a "$LOG_FILE"
echo "Test completed at: $(date)" | tee -a "$LOG_FILE"

# Count errors
error_count=$(grep -c "ERROR:" "$ERROR_LOG" 2>/dev/null || echo "0")
echo "Total errors found: $error_count" | tee -a "$LOG_FILE"

if [[ $error_count -gt 0 ]]; then
    echo "Errors found! Check $ERROR_LOG for details"
    echo "Summary of errors:"
    cat "$ERROR_LOG"
else
    echo "No errors found! All commands executed successfully."
fi