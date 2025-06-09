#!/usr/bin/env python3
"""Test script for the contextual help system."""

import sys
import os

# Add the hiollama package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hiollama.app import Chat
from hiollama.ui import UIManager

def test_contextual_help():
    """Test the new contextual help functionality."""
    
    # Create app instance
    app = Chat(0)
    
    # Test category help
    print("=" * 60)
    print("Testing /sys.help persona:")
    print("=" * 60)    app.ui.show_category_help("persona")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help prompt:")
    print("=" * 60)
    app.ui.show_category_help("prompt")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help chat:")
    print("=" * 60)
    app.ui.show_category_help("chat")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help model:")
    print("=" * 60)
    app.ui.show_category_help("model")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help history:")
    print("=" * 60)
    app.ui.show_category_help("history")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help log:")
    print("=" * 60)
    app.ui.show_category_help("log")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help alias:")
    print("=" * 60)
    app.ui_manager.show_category_help("alias")
    
    print("\n" + "=" * 60)
    print("Testing /sys.help plugin:")    print("=" * 60)
    app.ui.show_category_help("plugin")
    
    print("\n" + "=" * 60)
    print("Testing command-specific help:")
    print("=" * 60)
    app.ui.show_command_help("persona.set")

if __name__ == "__main__":
    test_contextual_help()
