Great! Now that the basic command functionality is working well, here are some ideas to make the client even more useful:


## Useful Features
5. **Output format control**: `hi -j` for JSON-only output (useful for scripts that parse responses)
6. **Timeout option**: `hi -t 30` to set connection timeout
7. **Socket path override**: `hi -s /custom/path.sock` for different socket locations

## Power User Features
9. **Batch mode**: `hi -b commands.txt` to run multiple commands from a file
10. **Pipe-friendly**: Better handling when used in shell pipelines
11. **Config file**: `~/.hirc` for default settings (socket path, timeout, etc.)

## Convenience
12. **Command history**: Store recent commands for easy re-running
13. **Tab completion**: For command names (though this gets complex)

Which of these sound most useful to you? The quiet mode and help flag would probably be the easiest wins and most immediately useful for scripting.
