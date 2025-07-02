#!/usr/bin/env python3
"""
Script to convert print() statements to use send_to_client() routing.
This will convert the codebase from CLI mode to daemon-only mode.
"""

import os
import re
import sys
from pathlib import Path

def convert_file(file_path):
    """Convert print statements in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Skip files that shouldn't be converted
    if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'convert_prints.py']):
        return False
    
    # Skip test files and setup files
    if any(skip in str(file_path) for skip in ['test_', 'setup.py', '__init__.py']):
        return False
    
    # Convert rich.print imports
    content = re.sub(r'from rich import print', 'from rich import print as rich_print', content)
    
    # Convert standalone print() statements
    # Handle multiline prints and f-strings
    
    # Pattern 1: Simple print statements
    content = re.sub(
        r'^(\s+)print\((.*?)\)$',
        r'\1self._output(\2)',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 2: Print statements with method calls (like in formatters)
    # Replace print( with self._output( for formatter classes
    if 'Formatter' in content or 'UIManager' in content:
        content = re.sub(
            r'(\s+)print\(',
            r'\1self._output(',
            content
        )
    
    # Pattern 3: For files that don't have self context, use a different approach
    else:
        # Add import for session manager access
        if 'print(' in content and 'def ' in content:
            # Add the output helper function
            if '_output_helper' not in content:
                import_section = """
def _output_helper(message, message_type="response"):
    \"\"\"Helper to route output to client or console.\"\"\"
    try:
        # Try to get session manager from various contexts
        import inspect
        frame = inspect.currentframe()
        while frame:
            local_vars = frame.f_locals
            if 'self' in local_vars:
                obj = local_vars['self']
                if hasattr(obj, 'session_manager') and obj.session_manager and obj.session_manager.socket_mode:
                    obj.session_manager.send_to_client(message, message_type)
                    return
                elif hasattr(obj, 'app') and hasattr(obj.app, 'session_manager') and obj.app.session_manager and obj.app.session_manager.socket_mode:
                    obj.app.session_manager.send_to_client(message, message_type)
                    return
            frame = frame.f_back
        # Fallback to rich print for now
        from rich import print as rich_print
        rich_print(message)
    except:
        from rich import print as rich_print
        rich_print(message)

"""
                # Insert after imports
                import_pattern = r'((?:from|import).*?\n(?:(?:from|import).*?\n)*)'
                if re.search(import_pattern, content):
                    content = re.sub(import_pattern, r'\1' + import_section, content, count=1)
                else:
                    content = import_section + content
            
            # Replace print statements with helper
            content = re.sub(
                r'(\s+)print\(',
                r'\1_output_helper(',
                content
            )
    
    # Add _output method to classes that don't have it
    if ('print(' in original_content or 'self._output(' in content) and 'class ' in content:
        # Check if _output method already exists
        if 'def _output(' not in content:
            # Find class definitions and add _output method
            class_pattern = r'(class\s+\w+.*?:\s*\n(?:\s*""".*?"""\s*\n)?)'
            
            output_method = '''    def _output(self, message: str, message_type: str = "response"):
        """Send output to client or print to console."""
        if hasattr(self, 'session_manager') and self.session_manager and self.session_manager.socket_mode:
            self.session_manager.send_to_client(message, message_type)
        elif hasattr(self, 'app') and hasattr(self.app, 'session_manager') and self.app.session_manager and self.app.session_manager.socket_mode:
            self.app.session_manager.send_to_client(message, message_type)
        else:
            from rich import print as rich_print
            rich_print(message)
    
'''
            
            def replace_class(match):
                return match.group(1) + output_method
            
            content = re.sub(class_pattern, replace_class, content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Convert all Python files in the calous directory."""
    calous_dir = Path('/home/aswin/python/calous/calousd')
    
    if not calous_dir.exists():
        print(f"Directory {calous_dir} not found!")
        sys.exit(1)
    
    converted_files = []
    
    # Find all Python files
    for py_file in calous_dir.rglob('*.py'):
        try:
            if convert_file(py_file):
                converted_files.append(py_file)
                print(f"Converted: {py_file}")
        except Exception as e:
            print(f"Error converting {py_file}: {e}")
    
    print(f"\nConversion complete! Converted {len(converted_files)} files.")
    
    if converted_files:
        print("\nConverted files:")
        for f in converted_files:
            print(f"  {f}")

if __name__ == '__main__':
    main()