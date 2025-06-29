# Calous VS Code Extension

A VS Code extension that connects to your Calous AI assistant via Unix socket.

## Features

- **Ask Calous**: Ask questions directly to your AI assistant (`Ctrl+Shift+C`)
- **Explain Code**: Right-click on selected code to get explanations
- **Generate Code**: Generate code based on descriptions
- **Multi-Chat Support**: Switch between different chat channels (1-14)

## Setup

1. **Install dependencies**:
   ```bash
   cd vscode-extension
   npm install
   ```

2. **Make sure Calous is running**:
   ```bash
   cd ..
   python -m calous --socket
   ```

3. **Compile the extension**:
   ```bash
   npm run compile
   ```

4. **Test the extension**:
   - Press `F5` to open a new VS Code window with the extension loaded
   - Or use the "Run Extension" launch configuration

## Configuration

The extension can be configured in VS Code settings:

- `calous.socketPath`: Path to the Unix socket (default: `/tmp/calous.sock`)
- `calous.defaultChatChannel`: Default chat channel to use (default: `1`)
- `calous.timeout`: Socket timeout in milliseconds (default: `30000`)

## Usage

### Commands

- `Calous: Ask Question` - Ask a question to the AI
- `Calous: Explain Code` - Explain selected code
- `Calous: Generate Code` - Generate code from description
- `Calous: Switch Chat Channel` - Switch to a different chat channel

### Keyboard Shortcuts

- `Ctrl+Shift+C` (or `Cmd+Shift+C` on Mac) - Ask Calous

### Context Menu

- Right-click on selected code → "Explain Code"

## Architecture

```
VS Code Extension → Unix Socket (/tmp/calous.sock) → Calous Python Server → Ollama
```

The extension communicates with your Calous server using the same JSON protocol as your `cx` Rust tool:

```json
{
  "type": "prompt",
  "data": "Your question here",
  "chat": 1,
  "format": "plain"
}
```

## Development

- `npm run compile` - Compile TypeScript
- `npm run watch` - Watch for changes and recompile
- `F5` - Launch extension in new VS Code window
