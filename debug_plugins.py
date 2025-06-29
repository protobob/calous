"""Debug plugin loading"""
import sys
import os
from pathlib import Path

# Add the calous directory to the path
calous_dir = Path(__file__).parent
sys.path.insert(0, str(calous_dir))

print("Python path:")
for p in sys.path[:3]:
    print(f"  {p}")

try:
    print("Importing PluginManager...")
    from calous.plugins.manager import PluginManager
    print("PluginManager imported successfully")
except Exception as e:
    print(f"Error importing PluginManager: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test plugin loading
plugin_dir = calous_dir / 'calous' / 'plugins'
print(f"\nPlugin directory: {plugin_dir}")
print(f"Plugin directory exists: {plugin_dir.exists()}")

builtin_dir = plugin_dir / 'builtin'
print(f"Builtin directory: {builtin_dir}")
print(f"Builtin directory exists: {builtin_dir.exists()}")

if builtin_dir.exists():
    print("Files in builtin directory:")
    for file in builtin_dir.iterdir():
        print(f"  {file.name}")

print("\n--- Testing Plugin Manager ---")
manager = PluginManager()
print(f"PluginManager created: {manager}")

try:
    print("Calling discover_and_load_plugins...")
    manager.discover_and_load_plugins(plugin_dir)
    print("discover_and_load_plugins completed")
    
    print(f"Loaded plugins: {list(manager.plugins.keys())}")
    print(f"Function plugins: {list(manager.function_plugins.keys())}")
    
    if manager.plugins:
        for name, plugin in manager.plugins.items():
            print(f"\nPlugin {name}:")
            print(f"  Active: {plugin.is_active}")
            print(f"  Capabilities: {[cap.name for cap in plugin.capabilities]}")
    else:
        print("No plugins loaded")
        
except Exception as e:
    print(f"Error loading plugins: {e}")
    import traceback
    traceback.print_exc()
