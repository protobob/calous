#!/usr/bin/env python3
"""Test script to demonstrate the enhanced UnifiedLogger functionality."""

import sys
import os
from pathlib import Path

# Add the calousd module to the path
sys.path.insert(0, str(Path(__file__).parent))

from calousd.unified_logger import UnifiedLogger
from calousd.constants import LOG_DIR

def test_enhanced_logger():
    """Test the enhanced logger functionality."""
    print("🧪 Testing Enhanced UnifiedLogger")
    print("=" * 50)
    
    # Create a test logger instance
    logger = UnifiedLogger(debug_enabled=True)
    
    print(f"📁 Log directory: {LOG_DIR}")
    print(f"🔧 Debug enabled: {logger.debug_enabled}")
    print(f"📊 Structured format: {logger.structured_format}")
    print()
    
    # Test basic logging methods
    print("📝 Testing basic logging methods...")
    logger.info("Application started", stream='app', component='test')
    logger.debug("This is debug info that should go to debug.log", component='test')
    logger.warning("This is a warning", stream='app', component='test')
    logger.error("This is an error", component='test')
    
    # Test debug routing methods
    print("🔍 Testing debug routing methods...")
    logger.debug_socket("Socket connection established", connection_id="conn_123")
    logger.debug_command("/test.command", args="arg1 arg2", chat_channel=1)
    logger.debug_model("Test prompt", response="Test response", metadata={'model': 'test-model'})
    
    # Test audit logging
    print("📋 Testing audit logging...")
    logger.audit("test.command", user_info="test_user", result="success", chat_channel=1)
    
    # Test model interaction logging
    print("🤖 Testing model interaction logging...")
    logger.model_interaction(
        request="What is the meaning of life?",
        response="42",
        timing=150.5,
        model="test-model",
        chat_channel=1
    )
    
    # Test context manager
    print("🔗 Testing context manager...")
    with logger.log_context(chat_channel=2, user_id="test_user", session="test_session"):
        logger.info("Message with context", stream='app')
        logger.debug("Debug message with context")
    
    # Test legacy compatibility methods
    print("🔄 Testing legacy compatibility methods...")
    logger.log_conversation(1, "user", "Hello, world!")
    logger.log_conversation(1, "assistant", "Hello! How can I help you?", model="test-model")
    logger.log_channel_switch(1, 2, "user_request")
    logger.log_command_execution(1, "/test.command", "success")
    
    # List created log files
    print("\n📂 Created log files:")
    if LOG_DIR.exists():
        log_files = list(LOG_DIR.glob("*.log")) + list(LOG_DIR.glob("*.txt"))
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"  📄 {log_file.name} ({size} bytes)")
            
            # Show first few lines of each log file
            if size > 0:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:3]  # First 3 lines
                        for line in lines:
                            print(f"     {line.strip()}")
                        if len(lines) == 3:
                            print(f"     ... ({len(f.readlines()) + 3} total lines)")
                except Exception as e:
                    print(f"     Error reading file: {e}")
                print()
    else:
        print("  No log directory found!")
    
    print("✅ Enhanced logger test completed!")
    print("\n🎯 Key Benefits Demonstrated:")
    print("  • Debug info routes to log files, NOT client output")
    print("  • Multi-stream logging (app, debug, model, audit, error)")
    print("  • Structured logging with context")
    print("  • Legacy compatibility maintained")
    print("  • Context managers for grouped logging")
    print("  • Specialized debug routing methods")

if __name__ == "__main__":
    test_enhanced_logger()
