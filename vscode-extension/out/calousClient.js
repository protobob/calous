"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CalousClient = void 0;
const net = require("net");
const vscode = require("vscode");
class CalousClient {
    constructor() {
        const config = vscode.workspace.getConfiguration('calous');
        this.socketPath = config.get('socketPath', '/tmp/calous.sock');
        this.defaultChatChannel = config.get('defaultChatChannel', 1);
        this.timeout = config.get('timeout', 30000);
    }
    async sendPrompt(prompt, chatChannel) {
        const request = {
            type: 'prompt',
            data: prompt,
            chat: chatChannel || this.defaultChatChannel,
            format: 'plain'
        };
        return this.sendRequest(request);
    }
    async sendCommand(command, chatChannel) {
        const request = {
            type: 'cmd',
            data: JSON.stringify({ action: command }),
            chat: chatChannel || this.defaultChatChannel,
            format: 'plain'
        };
        return this.sendRequest(request);
    }
    async sendRequest(request) {
        return new Promise((resolve, reject) => {
            const client = new net.Socket();
            let responseData = '';
            // Set timeout
            const timeoutId = global.setTimeout(() => {
                client.destroy();
                reject(new Error('Socket timeout'));
            }, this.timeout);
            client.connect(this.socketPath, () => {
                console.log('Connected to Calous socket');
                const requestJson = JSON.stringify(request);
                client.write(requestJson);
            });
            client.on('data', (data) => {
                responseData += data.toString();
            });
            client.on('close', () => {
                global.clearTimeout(timeoutId);
                try {
                    const response = JSON.parse(responseData);
                    if (response.error) {
                        reject(new Error(response.error));
                    }
                    else {
                        resolve(response.response || '');
                    }
                }
                catch (error) {
                    // If JSON parsing fails, return raw response
                    resolve(responseData);
                }
            });
            client.on('error', (error) => {
                global.clearTimeout(timeoutId);
                reject(new Error(`Socket error: ${error.message}`));
            });
        });
    }
    setDefaultChatChannel(channel) {
        this.defaultChatChannel = channel;
    }
    disconnect() {
        // Nothing to do for stateless connections
    }
    async testConnection() {
        try {
            await this.sendPrompt('Hello');
            return true;
        }
        catch (error) {
            return false;
        }
    }
}
exports.CalousClient = CalousClient;
//# sourceMappingURL=calousClient.js.map