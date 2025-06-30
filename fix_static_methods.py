#!/usr/bin/env python3
"""
Fix self._output calls in static methods
"""

import os
import re
from pathlib import Path

def fix_static_methods(file_path):
    """Fix self._output calls in static methods."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find static methods that have self._output calls
    # Pattern: @staticmethod followed by function definition, then self._output calls
    static_method_pattern = r'(@staticmethod\s+def\s+[^:]+:.*?)(?=@|\nclass|\Z)'
    
    def fix_method(match):
        method_content = match.group(1)
        # Replace self._output with CommandFormatter._output in static methods
        fixed_content = re.sub(
            r'\bself\._output\(',
            'CommandFormatter._output(',
            method_content
        )
        return fixed_content
    
    content = re.sub(static_method_pattern, fix_method, content, flags=re.DOTALL)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fix all Python files in the calous directory."""
    calous_dir = Path('/home/aswin/python/calous/calous')
    
    fixed_files = []
    
    # Find all Python files
    for py_file in calous_dir.rglob('*.py'):
        try:
            if fix_static_methods(py_file):
                fixed_files.append(py_file)
                print(f"Fixed: {py_file}")
        except Exception as e:
            print(f"Error fixing {py_file}: {e}")
    
    print(f"\nFixed {len(fixed_files)} files.")

if __name__ == '__main__':
    main()