Great! Now that the basic command functionality is working well, here are some ideas to make the client even more useful:

## Quick Wins
1. **Quiet mode**: `hi -q` or `--quiet` to suppress debug output for cleaner scripting
2. **Help flag**: `hi -h` or `--help` to show usage without needing to connect to the server
3. **Version flag**: `hi -v` or `--version`

## Useful Features
4. **Direct file input**: `hi -f file.txt` to send file contents as prompt
5. **Output format control**: `hi -j` for JSON-only output (useful for scripts that parse responses)
6. **Timeout option**: `hi -t 30` to set connection timeout
7. **Socket path override**: `hi -s /custom/path.sock` for different socket locations

## Power User Features
8. **Interactive mode**: `hi -i` for a simple REPL-like interface
9. **Batch mode**: `hi -b commands.txt` to run multiple commands from a file
10. **Pipe-friendly**: Better handling when used in shell pipelines
11. **Config file**: `~/.hirc` for default settings (socket path, timeout, etc.)

## Convenience
12. **Command history**: Store recent commands for easy re-running
13. **Tab completion**: For command names (though this gets complex)
14. **Aliases**: Short aliases for common commands (`hi -c h` → `hi -c /sys.help`)

Which of these sound most useful to you? The quiet mode and help flag would probably be the easiest wins and most immediately useful for scripting.
