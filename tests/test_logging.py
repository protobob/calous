import unittest
from hiollama.plugins.builtin.dice_roller import DiceRollerPlugin
from hiollama.unified_logger import unified_logger

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.plugin = DiceRollerPlugin()

    def test_logging_function_call(self):
        # Prepare test data
        function_name = "roll_dice"
        arguments = {"dice_expression": "2d6+3", "verbose": True}

        # Execute the function
        result = self.plugin.execute_function(function_name, **arguments)

        # Check the log file for entries
        log_file_path = unified_logger._get_log_file_path()
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            logs = log_file.read()

        # Assert log entries exist
        self.assertIn("PLUGIN_FUNCTION_CALL", logs)
        self.assertIn("PLUGIN_FUNCTION_RESULT", logs)
        self.assertIn(function_name, logs)
        self.assertIn("2d6+3", logs)

if __name__ == "__main__":
    unittest.main()
