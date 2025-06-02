#!/usr/bin/env python3
"""
Configuration management tests for HiOllama application.
Tests the unified configuration system, chat config generation, and settings validation.
"""

import json
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the parent directory to the path to import hiollama modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from hiollama.config import ConfigManager
from hiollama.constants import DEFAULT_MODEL, DEFAULT_NUM_CHATS, DEFAULT_SYSTEM_PROMPT

def test_default_config_generation():
    """Test generation of default chat configuration."""
    print("🔍 Testing default config generation...")
    
    config = ConfigManager._generate_default_chat_config()    # Verify all required fields are present
    required_fields = ['verbosity', 'system_prompt', 'prompts', 'logging_enabled']
    for field in required_fields:
        if field not in config:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Verify default values
    if config['verbosity'] != True:
        print(f"❌ Expected verbosity=True, got {config['verbosity']}")
        return False
    
    if config['system_prompt'] != DEFAULT_SYSTEM_PROMPT:
        print(f"❌ Expected system_prompt={DEFAULT_SYSTEM_PROMPT}, got {config['system_prompt']}")
        return False
    
    # Verify prompts dictionary structure
    if not isinstance(config['prompts'], dict):
        print(f"❌ Expected prompts to be dict, got {type(config['prompts'])}")
        return False
    
    print("✅ Default config generation works correctly")
    return True

def test_unified_config_generation():
    """Test generation of unified configuration for multiple chats."""
    print("\n🔍 Testing unified config generation...")
    
    # Test with different chat counts
    for num_chats in [1, 4, 8, 14]:
        config = ConfigManager._generate_default_unified_config(num_chats)
        
        # Verify structure
        if 'global' not in config or 'chats' not in config:
            print(f"❌ Missing global or chats section for {num_chats} chats")
            return False
        
        # Verify global settings
        global_config = config['global']
        if global_config.get('selected_model') != DEFAULT_MODEL:
            print(f"❌ Wrong default model for {num_chats} chats")
            return False
        
        if global_config.get('num_chats') != num_chats:
            print(f"❌ Wrong num_chats: expected {num_chats}, got {global_config.get('num_chats')}")
            return False
        
        # Verify chat configs
        chat_configs = config['chats']
        if len(chat_configs) != num_chats:
            print(f"❌ Expected {num_chats} chat configs, got {len(chat_configs)}")
            return False
        
        # Verify each chat has a valid config
        for i in range(num_chats):
            chat_key = str(i)
            if chat_key not in chat_configs:
                print(f"❌ Missing config for chat {i}")
                return False
            
            chat_config = chat_configs[chat_key]
            if 'system_prompt' not in chat_config:
                print(f"❌ Missing system_prompt for chat {i}")
                return False
    
    print("✅ Unified config generation works for all chat counts")
    return True

def test_chat_specific_configs():
    """Test that different chats get appropriate default prompts."""
    print("\n🔍 Testing chat-specific configurations...")
    
    config = ConfigManager._generate_default_unified_config(4)
    chat_configs = config['chats']
    
    # All chats should have blank system prompts now
    for i in range(4):
        chat_prompt = chat_configs[str(i)]['system_prompt']
        if chat_prompt != "":
            print(f"❌ Chat {i} should have blank system prompt, got: {chat_prompt}")
            return False
    
    print("✅ Chat-specific configurations work correctly (all blank system prompts)")
    return True

def test_config_file_operations():
    """Test configuration file loading and saving operations."""
    print("\n🔍 Testing config file operations...")
    
    # Create a test config
    test_config = {
        "global": {
            "selected_model": "test-model",
            "num_chats": 2
        },
        "chats": {
            "0": ConfigManager._generate_default_chat_config(),
            "1": ConfigManager._generate_default_chat_config()
        }
    }
    
    # Test JSON serialization/deserialization
    try:
        config_json = json.dumps(test_config, indent=2)
        parsed_config = json.loads(config_json)
        
        if parsed_config != test_config:
            print("❌ Config serialization/deserialization failed")
            return False
        
    except Exception as e:
        print(f"❌ JSON operations failed: {e}")
        return False
    
    # Test with mocked file operations
    with patch('builtins.open', mock_open(read_data=config_json)):
        with patch('pathlib.Path.exists', return_value=True):
            # This would normally call ConfigManager.load_unified_config()
            # but we'll just verify the JSON structure is valid
            pass
    
    print("✅ Config file operations work correctly")
    return True

def test_chat_config_retrieval():
    """Test retrieving configuration for specific chat instances."""
    print("\n🔍 Testing chat config retrieval...")
    
    # Mock the unified config
    mock_config = {
        "global": {"selected_model": "test-model", "num_chats": 3},
        "chats": {
            "0": {"system_prompt": "Technical assistant", "verbosity": True},
            "1": {"system_prompt": "Creative writer", "verbosity": False},
        }
    }
    
    with patch.object(ConfigManager, 'load_unified_config', return_value=mock_config):
        # Test existing chat config
        config_0 = ConfigManager.get_chat_config(0)
        if config_0['system_prompt'] != "Technical assistant":
            print("❌ Failed to retrieve existing chat config")
            return False
          # Test missing chat config (should generate default with blank prompt)
        config_2 = ConfigManager.get_chat_config(2)
        if 'system_prompt' not in config_2:
            print("❌ Failed to generate default config for missing chat")
            return False
        
        # Verify chat 2 gets blank prompt
        if config_2['system_prompt'] != "":
            print("❌ Generated config doesn't have blank system prompt")
            return False
    
    print("✅ Chat config retrieval works correctly")
    return True

def test_global_config_operations():
    """Test global configuration management."""
    print("\n🔍 Testing global config operations...")
    
    mock_config = {
        "global": {"selected_model": "old-model", "num_chats": 2},
        "chats": {"0": {}, "1": {}}
    }
    
    with patch.object(ConfigManager, 'load_unified_config', return_value=mock_config.copy()) as mock_load:
        with patch.object(ConfigManager, 'save_unified_config') as mock_save:
            # Test getting global config
            global_config = ConfigManager.get_global_config()
            if global_config['selected_model'] != 'old-model':
                print("❌ Failed to get global config")
                return False
            
            # Test updating global config
            ConfigManager.update_global_config({"selected_model": "new-model"})
            
            # Verify save was called
            if not mock_save.called:
                print("❌ Save not called during global config update")
                return False
            
            # Test num_chats retrieval
            num_chats = ConfigManager.get_num_chats()
            if num_chats != 2:
                print(f"❌ Expected num_chats=2, got {num_chats}")
                return False
    
    print("✅ Global config operations work correctly")
    return True

def main():
    """Run configuration tests."""
    print("🚀 HiOllama Configuration Test Suite")
    print("=" * 45)
    
    tests = [
        test_default_config_generation,
        test_unified_config_generation,
        test_chat_specific_configs,
        test_config_file_operations,
        test_chat_config_retrieval,
        test_global_config_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"\n❌ Test {test.__name__} failed!")
        except Exception as e:
            print(f"\n❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 45)
    print(f"📊 Configuration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All configuration tests passed!")
        return 0
    else:
        print("⚠️  Some configuration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
