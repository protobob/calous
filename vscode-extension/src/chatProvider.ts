import * as vscode from 'vscode';
import { CalousClient } from './calousClient';

export class ChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'calousChat';  // Must match package.json view ID

    private _view?: vscode.WebviewView;
    private _chatChannel: number = 1;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _calousClient: CalousClient
    ) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'sendMessage':
                    await this.handleUserMessage(data.value);
                    break;
            }
        });
    }

    public addMessage(message: string, sender: 'user' | 'assistant') {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'addMessage',
                message: message,
                sender: sender
            });
        }
        
        if (sender === 'user') {
            this.handleUserMessage(message);
        }
    }

    public setChatChannel(channel: number) {
        this._chatChannel = channel;
        if (this._view) {
            this._view.webview.postMessage({
                type: 'chatChannelChanged',
                channel: channel
            });
        }
    }

    private async handleUserMessage(message: string) {
        try {
            const response = await this._calousClient.sendPrompt(message, this._chatChannel);
            this.addMessage(response, 'assistant');
        } catch (error) {
            this.addMessage(`Error: ${error}`, 'assistant');
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Calous Chat</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    margin: 0;
                    padding: 10px;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                
                #messages {
                    flex: 1;
                    overflow-y: auto;
                    margin-bottom: 10px;
                    padding: 10px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                }
                
                .message {
                    margin-bottom: 10px;
                    padding: 8px;
                    border-radius: 4px;
                }
                
                .user-message {
                    background-color: var(--vscode-inputOption-activeBackground);
                    text-align: right;
                }
                
                .assistant-message {
                    background-color: var(--vscode-textBlockQuote-background);
                }
                
                #input-container {
                    display: flex;
                    gap: 5px;
                }
                
                #message-input {
                    flex: 1;
                    padding: 8px;
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 2px;
                }
                
                #send-button {
                    padding: 8px 16px;
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 2px;
                    cursor: pointer;
                }
                
                #send-button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                
                #channel-info {
                    font-size: 0.8em;
                    color: var(--vscode-descriptionForeground);
                    margin-bottom: 5px;
                }
            </style>
        </head>
        <body>
            <div id="channel-info">Chat Channel: 1</div>
            <div id="messages"></div>
            <div id="input-container">
                <input type="text" id="message-input" placeholder="Type your message..." />
                <button id="send-button">Send</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const messages = document.getElementById('messages');
                const input = document.getElementById('message-input');
                const sendButton = document.getElementById('send-button');
                const channelInfo = document.getElementById('channel-info');

                function addMessage(message, sender) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ' + (sender === 'user' ? 'user-message' : 'assistant-message');
                    messageDiv.textContent = message;
                    messages.appendChild(messageDiv);
                    messages.scrollTop = messages.scrollHeight;
                }

                function sendMessage() {
                    const message = input.value.trim();
                    if (message) {
                        addMessage(message, 'user');
                        vscode.postMessage({
                            type: 'sendMessage',
                            value: message
                        });
                        input.value = '';
                    }
                }

                sendButton.addEventListener('click', sendMessage);
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });

                // Listen for messages from the extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.type) {
                        case 'addMessage':
                            if (message.sender === 'assistant') {
                                addMessage(message.message, 'assistant');
                            }
                            break;
                        case 'chatChannelChanged':
                            channelInfo.textContent = 'Chat Channel: ' + message.channel;
                            break;
                    }
                });
            </script>
        </body>
        </html>`;
    }
}
