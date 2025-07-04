#!/usr/bin/env python3
"""Test debug functionality specifically."""

import logging
from pathlib import Path

# Simulate the LOG_DIR constant
HOME_DIR = Path.home()
CALOUS_DIR = HOME_DIR / ".calous"
LOG_DIR = CALOUS_DIR / "logs"

def test_debug_specifically():
    """Test debug logging specifically."""
    print("🔍 Testing Debug Logging Specifically")
    print("=" * 40)
    
    # Clear existing debug.log
    debug_log = LOG_DIR / "debug.log"
    if debug_log.exists():
        debug_log.unlink()
    
    # Create logger with explicit debug level
    logger = logging.getLogger("calous.debug")
    logger.setLevel(logging.DEBUG)  # Explicitly set DEBUG level
    logger.propagate = False
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create new file handler
    handler = logging.FileHandler(debug_log, encoding='utf-8')
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [DEBUG] %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Test debug messages
    logger.debug("Debug message 1: Socket connection test")
    logger.debug("Debug message 2: Command processing test")
    logger.info("Info message to debug stream")
    logger.warning("Warning message to debug stream")
    
    print(f"📁 Debug log file: {debug_log}")
    print(f"📄 File exists: {debug_log.exists()}")
    
    if debug_log.exists():
        size = debug_log.stat().st_size
        print(f"📊 File size: {size} bytes")
        
        if size > 0:
            print("📖 Debug log content:")
            with open(debug_log, 'r') as f:
                for line in f:
                    print(f"   {line.strip()}")
        else:
            print("⚠️  Debug log file is empty!")
    else:
        print("❌ Debug log file was not created!")

if __name__ == "__main__":
    test_debug_specifically()
