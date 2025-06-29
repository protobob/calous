import * as net from 'net';
import * as vscode from 'vscode';

interface CalousRequest {
    type: 'prompt' | 'cmd';
    data: string;
    chat?: number;
    format?: 'plain' | 'json';
}

interface CalousResponse {
    response?: string;
    error?: string;
}

export class CalousClient {
    private socketPath: string;
    private defaultChatChannel: number;
    private timeout: number;

    constructor() {
        const config = vscode.workspace.getConfiguration('calous');
        this.socketPath = config.get('socketPath', '/tmp/calous.sock');
        this.defaultChatChannel = config.get('defaultChatChannel', 1);
        this.timeout = config.get('timeout', 30000);
    }

    async sendPrompt(prompt: string, chatChannel?: number): Promise<string> {
        const request: CalousRequest = {
            type: 'prompt',
            data: prompt,
            chat: chatChannel || this.defaultChatChannel,
            format: 'plain'
        };

        return this.sendRequest(request);
    }

    async sendCommand(command: string, chatChannel?: number): Promise<string> {
        const request: CalousRequest = {
            type: 'cmd',
            data: JSON.stringify({ action: command }),
            chat: chatChannel || this.defaultChatChannel,
            format: 'plain'
        };

        return this.sendRequest(request);
    }

    private async sendRequest(request: CalousRequest): Promise<string> {
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

            client.on('data', (data: Buffer) => {
                responseData += data.toString();
            });

            client.on('close', () => {
                global.clearTimeout(timeoutId);
                try {
                    const response: CalousResponse = JSON.parse(responseData);
                    if (response.error) {
                        reject(new Error(response.error));
                    } else {
                        resolve(response.response || '');
                    }
                } catch (error) {
                    // If JSON parsing fails, return raw response
                    resolve(responseData);
                }
            });

            client.on('error', (error: Error) => {
                global.clearTimeout(timeoutId);
                reject(new Error(`Socket error: ${error.message}`));
            });
        });
    }

    setDefaultChatChannel(channel: number) {
        this.defaultChatChannel = channel;
    }

    disconnect() {
        // Nothing to do for stateless connections
    }

    async testConnection(): Promise<boolean> {
        try {
            await this.sendPrompt('Hello');
            return true;
        } catch (error) {
            return false;
        }
    }
}
