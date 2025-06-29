import pytest
import json
from unittest.mock import Mock, MagicMock
from calous.plugins.builtin.dice_roller import DiceRollerPlugin
from calous.model_interaction import ModelInteraction
from calous.unified_logger import unified_logger

@pytest.fixture
def dice_plugin():
    return DiceRollerPlugin()

@pytest.fixture
def mock_app():
    """Mock app with plugin manager."""
    app = Mock()
    plugin_manager = Mock()
    
    # Create a real dice plugin for testing
    dice_plugin = DiceRollerPlugin()
    dice_plugin.initialize()
    
    plugin_manager.get_function_calling_plugins.return_value = [dice_plugin]
    app.plugin_manager = plugin_manager
    return app

@pytest.fixture
def model_interaction(mock_app):
    """Create ModelInteraction with mocked app."""
    return ModelInteraction(mock_app)

@pytest.fixture
def mock_logger(mocker):
    """Mock the unified logger's _write_log_entry method."""
    return mocker.patch("calous.unified_logger.UnifiedLogger._write_log_entry")

def test_centralized_function_call_logging(model_interaction, mock_logger):
    """Test that function calls are logged in the centralized location."""
    tool_calls = [{
        "id": "test_call_1",
        "function": {
            "name": "roll_dice",
            "arguments": {"dice_expression": "2d6+3", "verbose": True}
        }
    }]
    
    # Execute the function call through the centralized handler
    results = model_interaction._handle_function_calls(tool_calls)
    
    # Verify that logging occurred for the function call
    mock_logger.assert_any_call(
        entry_type="PLUGIN_FUNCTION_CALL",
        content="Function: roll_dice, Args: {'dice_expression': '2d6+3', 'verbose': True}"
    )
    
    # Verify that logging occurred for the result
    calls = mock_logger.call_args_list
    result_calls = [call for call in calls if call[1]['entry_type'] == 'PLUGIN_FUNCTION_RESULT']
    assert len(result_calls) > 0, "Expected PLUGIN_FUNCTION_RESULT log entry"
    
    # Verify the result is correctly formatted
    assert len(results) == 1
    assert results[0]["role"] == "tool"
    assert results[0]["tool_call_id"] == "test_call_1"
    
    # Parse the content to verify it's valid JSON
    content = json.loads(results[0]["content"])
    assert "result" in content or "error" in content

def test_function_not_found_logging(model_interaction, mock_logger):
    """Test that function not found errors are logged."""
    tool_calls = [{
        "id": "test_call_2", 
        "function": {
            "name": "nonexistent_function",
            "arguments": {}
        }
    }]
    
    results = model_interaction._handle_function_calls(tool_calls)
    
    # Verify error logging
    mock_logger.assert_any_call(
        entry_type="PLUGIN_FUNCTION_ERROR",
        content="Function: nonexistent_function, Error: Function not found"
    )
    
    # Verify error result
    assert len(results) == 1
    content = json.loads(results[0]["content"])
    assert "error" in content
    assert content["success"] is False