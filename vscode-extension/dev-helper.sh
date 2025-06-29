#!/bin/bash

# Calous VS Code Extension Development Helper

echo "🚀 Calous VS Code Extension Development Helper"
echo "=============================================="

# Check if calous is running
if ! pgrep -f "calous.*--socket" > /dev/null; then
    echo "⚠️  Calous socket server is not running!"
    echo "   Start it with: python -m calous --socket"
    echo ""
    read -p "❓ Start calous socket server now? (y/n): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Starting calous socket server..."
        cd ..
        python -m calous --socket --interactive &
        CALOUS_PID=$!
        echo "✅ Calous started with PID: $CALOUS_PID"
        cd vscode-extension
        sleep 2
    else
        echo "❌ Cannot run extension without calous server"
        exit 1
    fi
fi

# Check if socket exists
if [[ ! -S "/tmp/calous.sock" ]]; then
    echo "❌ Socket /tmp/calous.sock not found"
    echo "   Make sure calous is running with --socket flag"
    exit 1
fi

echo "✅ Calous socket found at /tmp/calous.sock"

# Compile extension
echo "🔧 Compiling extension..."
npm run compile

if [[ $? -eq 0 ]]; then
    echo "✅ Extension compiled successfully"
else
    echo "❌ Extension compilation failed"
    exit 1
fi

echo ""
echo "🎯 Ready to test! Choose an option:"
echo "   1. Press F5 in VS Code to launch extension host"
echo "   2. Or run: code --extensionDevelopmentPath=$(pwd)"
echo ""
echo "🎮 Extension Commands:"
echo "   - Ctrl+Shift+C: Ask Calous"
echo "   - Right-click selected code: Explain Code"
echo "   - Command Palette: Search for 'Calous'"
echo ""
echo "⚙️  Configuration (VS Code Settings):"
echo "   - calous.socketPath: /tmp/calous.sock"
echo "   - calous.defaultChatChannel: 1"
echo "   - calous.timeout: 30000"
