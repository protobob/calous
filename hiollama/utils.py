"""Utility functions for Hi, Ollama!"""
from pathlib import Path
from rich import print

class Utils:
    @staticmethod
    def load_file_as_prompt(filepath, filenotes):
        """Load a file and format it as a prompt with instructions."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"{filenotes}:\n\n{content}"
    
    @staticmethod
    def get_numeric_input(prompt, min_val, max_val):
        """Get a validated numeric input within a specified range."""
        while True:
            try:
                value = input(prompt).strip()
                if not value and min_val is None:  # Allow empty for optional inputs
                    return None
                num_value = int(value)
                if min_val <= num_value <= max_val:
                    return num_value
                print(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    
    @staticmethod
    def handle_error(error, context=""):
        """Handle and log errors consistently."""
        error_message = f"{context}: {error}" if context else f"Error: {error}"
        print(error_message)
        return error_message