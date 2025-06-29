"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const calousClient_1 = require("./calousClient");
let calousClient;
function activate(context) {
    console.log('Calous extension is now active!');
    // Initialize the Calous client
    calousClient = new calousClient_1.CalousClient();
    // Register a simple command that opens a chat panel
    const openChatCommand = vscode.commands.registerCommand('calous.openChat', () => {
        createChatPanel();
    });
    // Register commands
    const askQuestion = vscode.commands.registerCommand('calous.askQuestion', async () => {
        const question = await vscode.window.showInputBox({
            prompt: 'What would you like to ask Calous?',
            placeHolder: 'Enter your question...'
        });
        if (question) {
            try {
                const response = await calousClient.sendPrompt(question);
                vscode.window.showInformationMessage(`Calous: ${response}`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Calous error: ${error}`);
            }
        }
    });
    context.subscriptions.push(askQuestion, openChatCommand);
}
exports.activate = activate;
function createChatPanel() {
    const panel = vscode.window.createWebviewPanel('calousChat', 'CALOUS Chat', vscode.ViewColumn.Beside, { enableScripts: true });
    panel.webview.html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: var(--vscode-font-family); 
            padding: 10px; 
            height: 100vh;
            margin: 0;
            display: flex;
            flex-direction: column;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        #messages { 
            flex: 1;
            overflow-y: auto; 
            border: 1px solid var(--vscode-panel-border); 
            padding: 10px; 
            margin-bottom: 10px; 
            background: var(--vscode-editor-background);
        }
        .user { 
            background: var(--vscode-inputOption-activeBackground); 
            margin: 5px 0; 
            padding: 8px; 
            border-radius: 4px; 
            text-align: right;
        }
        .assistant { 
            background: var(--vscode-textBlockQuote-background); 
            margin: 5px 0; 
            padding: 8px; 
            border-radius: 4px; 
        }
        #inputContainer {
            display: flex;
            gap: 5px;
        }
        #input { 
            flex: 1;
            padding: 8px; 
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
        }
        #input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        #send { 
            padding: 8px 15px; 
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        #send:hover {
            background: var(--vscode-button-hoverBackground);
        }
        h3 {
            color: #ffffff;
            margin-top: 0;
        }
        .context-info {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <h3>CALOUS Chat</h3>
    <div id="messages"></div>
    <div id="inputContainer">
        <input type="text" id="input" placeholder="Ask CALOUS anything..." />
        <button id="send">Send</button>
    </div>
    
    <script>
        (function() {
            const vscode = acquireVsCodeApi();
            const messages = document.getElementById('messages');
            const input = document.getElementById('input');
            const send = document.getElementById('send');
            
            function addMessage(text, sender) {
                const div = document.createElement('div');
                div.className = sender;
                div.textContent = text;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function sendMessage() {
                const text = input.value.trim();
                if (text) {
                    addMessage(text, 'user');
                    vscode.postMessage({ type: 'message', text: text });
                    input.value = '';
                }
            }
            
            send.addEventListener('click', sendMessage);
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            window.addEventListener('message', function(event) {
                const message = event.data;
                if (message.type === 'response') {
                    addMessage(message.text, 'assistant');
                } else if (message.type === 'context') {
                    // Add context info message
                    const div = document.createElement('div');
                    div.className = 'context-info';
                    div.textContent = message.text;
                    messages.appendChild(div);
                    messages.scrollTop = messages.scrollHeight;
                }
            });
            
            // Focus the input field
            input.focus();
            
            // Welcome message
            addMessage('Connected to CALOUS! I can see your currently open file and any text you have selected. Commands starting with / are sent directly to CALOUS. I can also edit files when you ask me to make changes.', 'assistant');
        })();
    </script>
</body>
</html>`;
    panel.webview.onDidReceiveMessage(async (message) => {
        if (message.type === 'message') {
            try {
                let prompt = message.text;
                let contextInfo = '';
                // Check if this is a command (starts with /)
                if (prompt.trim().startsWith('/')) {
                    // Send as command without file context
                    contextInfo = '🔧 Command mode';
                    panel.webview.postMessage({ type: 'context', text: contextInfo });
                    const response = await calousClient.sendCommand(prompt.trim());
                    panel.webview.postMessage({ type: 'response', text: response });
                    return;
                }
                // Add current file context if available for regular prompts
                const editor = vscode.window.activeTextEditor;
                const visibleEditors = vscode.window.visibleTextEditors;
                const workspaceFolders = vscode.workspace.workspaceFolders;
                // Enhanced debugging
                console.log('=== FILE DETECTION DEBUG ===');
                console.log('Active editor exists:', !!editor);
                console.log('Visible editors count:', visibleEditors.length);
                console.log('Workspace folders:', workspaceFolders?.length || 0);
                if (editor) {
                    console.log('Editor document exists:', !!editor.document);
                    console.log('Document URI scheme:', editor.document.uri.scheme);
                    console.log('Document file path:', editor.document.fileName);
                    console.log('Document language ID:', editor.document.languageId);
                    console.log('Document is untitled:', editor.document.isUntitled);
                }
                // Try multiple ways to get file context
                let fileInfo = null;
                if (editor && editor.document && !editor.document.isUntitled) {
                    fileInfo = {
                        fileName: editor.document.fileName,
                        content: editor.document.getText(),
                        selection: editor.selection,
                        languageId: editor.document.languageId
                    };
                }
                else if (visibleEditors.length > 0) {
                    // Try the first visible editor
                    const firstEditor = visibleEditors[0];
                    if (firstEditor.document && !firstEditor.document.isUntitled) {
                        fileInfo = {
                            fileName: firstEditor.document.fileName,
                            content: firstEditor.document.getText(),
                            selection: firstEditor.selection,
                            languageId: firstEditor.document.languageId
                        };
                        console.log('Using first visible editor instead of active editor');
                    }
                }
                if (fileInfo) {
                    const fileName = fileInfo.fileName;
                    const fileContent = fileInfo.content;
                    const selection = fileInfo.selection;
                    console.log('File detected:', fileName);
                    console.log('File content length:', fileContent.length);
                    console.log('Selection empty:', selection.isEmpty);
                    console.log('Language ID:', fileInfo.languageId);
                    if (!selection.isEmpty) {
                        // User has selected text
                        const selectedText = editor?.document.getText(selection) || '';
                        prompt = `Current file: ${fileName}\nSelected code:\n\`\`\`\n${selectedText}\n\`\`\`\n\nQuestion: ${message.text}\n\nIf you want to edit this file, format your response with:\n\`\`\`EDIT_FILE:${fileName}\n[new file content here]\n\`\`\``;
                        contextInfo = `📄 ${fileName.split('/').pop()} (selection: ${selectedText.split('\n').length} lines)`;
                    }
                    else if (fileContent.length < 5000) {
                        // File is small enough to include entirely
                        prompt = `Current file: ${fileName}\n\`\`\`\n${fileContent}\n\`\`\`\n\nQuestion: ${message.text}\n\nIf you want to edit this file, format your response with:\n\`\`\`EDIT_FILE:${fileName}\n[new file content here]\n\`\`\``;
                        contextInfo = `📄 ${fileName.split('/').pop()} (full file: ${fileContent.split('\n').length} lines)`;
                    }
                    else {
                        // Just mention the file name for large files
                        prompt = `Current file: ${fileName}\nQuestion: ${message.text}\n\nIf you want to edit this file, format your response with:\n\`\`\`EDIT_FILE:${fileName}\n[new file content here]\n\`\`\``;
                        contextInfo = `📄 ${fileName.split('/').pop()} (large file, name only)`;
                    }
                }
                else {
                    contextInfo = '📄 No file open';
                    console.log('No file context available');
                }
                // Send context info to webview
                panel.webview.postMessage({ type: 'context', text: contextInfo });
                const response = await calousClient.sendPrompt(prompt);
                // Check if the response contains file edit instructions
                await handlePotentialFileEdit(response, fileInfo);
                panel.webview.postMessage({ type: 'response', text: response });
            }
            catch (error) {
                panel.webview.postMessage({ type: 'response', text: `Error: ${error}` });
            }
        }
    });
}
async function handlePotentialFileEdit(response, fileInfo) {
    // Look for file edit markers in the response
    const editMarkers = [
        '```EDIT_FILE:',
        '```edit_file:',
        '```REPLACE_FILE:',
        '```replace_file:',
        '<!-- EDIT_FILE:',
        '<!-- REPLACE_FILE:'
    ];
    for (const marker of editMarkers) {
        const markerIndex = response.indexOf(marker);
        if (markerIndex !== -1) {
            try {
                // Extract filename and content
                let startIndex = markerIndex + marker.length;
                let endMarker = marker.includes('```') ? '```' : '-->';
                let endIndex = response.indexOf(endMarker, startIndex);
                if (endIndex === -1)
                    continue;
                let content = response.substring(startIndex, endIndex).trim();
                let lines = content.split('\n');
                let filename = lines[0].trim();
                let fileContent = lines.slice(1).join('\n').trim();
                // If no specific filename, use current file
                if (!filename || filename === '' && fileInfo) {
                    filename = fileInfo.fileName;
                }
                if (filename && fileContent) {
                    const choice = await vscode.window.showWarningMessage(`CALOUS wants to edit file: ${filename.split('/').pop()}`, 'Allow', 'Deny', 'Preview');
                    if (choice === 'Allow') {
                        await applyFileEdit(filename, fileContent);
                    }
                    else if (choice === 'Preview') {
                        await showEditPreview(filename, fileContent);
                    }
                }
            }
            catch (error) {
                console.error('Error handling file edit:', error);
            }
            break;
        }
    }
}
async function applyFileEdit(filename, content) {
    try {
        const uri = vscode.Uri.file(filename);
        const document = await vscode.workspace.openTextDocument(uri);
        const editor = await vscode.window.showTextDocument(document);
        // Replace entire file content
        const edit = new vscode.WorkspaceEdit();
        const fullRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
        edit.replace(uri, fullRange, content);
        const success = await vscode.workspace.applyEdit(edit);
        if (success) {
            await document.save();
            vscode.window.showInformationMessage(`✅ File updated: ${filename.split('/').pop()}`);
        }
        else {
            vscode.window.showErrorMessage(`❌ Failed to update file: ${filename.split('/').pop()}`);
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`❌ Error editing file: ${error}`);
    }
}
async function showEditPreview(filename, content) {
    const uri = vscode.Uri.parse(`untitled:${filename.split('/').pop()}-preview`);
    const document = await vscode.workspace.openTextDocument(uri);
    const editor = await vscode.window.showTextDocument(document, vscode.ViewColumn.Beside);
    const edit = new vscode.WorkspaceEdit();
    edit.insert(uri, new vscode.Position(0, 0), content);
    await vscode.workspace.applyEdit(edit);
}
function deactivate() {
    if (calousClient) {
        calousClient.disconnect();
    }
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map