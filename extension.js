const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function activate(context) {
    const outputChannel = vscode.window.createOutputChannel('CodeMentor');
    outputChannel.appendLine('CodeMentor extension activated at ' + new Date().toISOString());
    outputChannel.appendLine(`VS Code version: ${vscode.version}`);
    outputChannel.appendLine(`Node.js version: ${process.version}`);
    const secretStorage = context.secrets;
    checkAndPromptForToken(secretStorage, outputChannel);

    let recentEvents = new Map(); // Track recent file events

    let mentorCommand = vscode.commands.registerCommand('codementor.getFeedback', async () => {
        const editor = vscode.window.activeTextEditor;
        outputChannel.appendLine('codementor.getFeedback command triggered');
        if (!editor || !editor.document.fileName.endsWith('.py')) {
            outputChannel.appendLine('Error: No active Python file found');
            vscode.window.showErrorMessage('Please open a Python (.py) file to get mentor feedback.');
            return;
        }

        const filePath = editor.document.fileName;
        const code = editor.document.getText();
        const token = await secretStorage.get('huggingFaceToken');
        if (!token) {
            outputChannel.appendLine('Error: No Hugging Face token found');
            vscode.window.showErrorMessage('Hugging Face token not found. Please set it using the "CodeMentor: Set Hugging Face Token" command.');
            return;
        }

        outputChannel.appendLine(`Running feedback for: ${filePath}`);
        await runMentorFeedback(filePath, code, token, outputChannel);
    });

    let setTokenCommand = vscode.commands.registerCommand('codementor.setToken', async () => {
        outputChannel.appendLine('codementor.setToken command triggered');
        const token = await vscode.window.showInputBox({
            prompt: 'Enter your Hugging Face API token',
            placeHolder: 'hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            password: true
        });
        if (token) {
            await secretStorage.store('huggingFaceToken', token);
            outputChannel.appendLine('✅ Hugging Face token saved successfully.');
            vscode.window.showInformationMessage('Hugging Face token saved. You can now use CodeMentor.');
        } else {
            outputChannel.appendLine('Warning: No token provided');
        }
    });

    let testCommand = vscode.commands.registerCommand('codementor.test', () => {
        outputChannel.appendLine('Test command executed successfully');
    });

    let setModeExplain = vscode.commands.registerCommand('codementor.setModeExplain', async () => {
        await vscode.workspace.getConfiguration('codementor').update('mode', 'explain', vscode.ConfigurationTarget.Global);
        outputChannel.appendLine('Mode set to: explain');
        vscode.window.showInformationMessage('CodeMentor mode set to Explain');
    });

    let setModeHint = vscode.commands.registerCommand('codementor.setModeHint', async () => {
        await vscode.workspace.getConfiguration('codementor').update('mode', 'hint', vscode.ConfigurationTarget.Global);
        outputChannel.appendLine('Mode set to: hint');
        vscode.window.showInformationMessage('CodeMentor mode set to Hint');
    });

    let setModeSolution = vscode.commands.registerCommand('codementor.setModeSolution', async () => {
        await vscode.workspace.getConfiguration('codementor').update('mode', 'solution', vscode.ConfigurationTarget.Global);
        outputChannel.appendLine('Mode set to: solution');
        vscode.window.showInformationMessage('CodeMentor mode set to Solution');
    });

    setupFileWatcher(context, secretStorage, outputChannel, recentEvents);

    context.subscriptions.push(mentorCommand, setTokenCommand, testCommand, setModeExplain, setModeHint, setModeSolution);
}

async function checkAndPromptForToken(secretStorage, outputChannel) {
    const token = await secretStorage.get('huggingFaceToken');
    if (!token) {
        outputChannel.appendLine('No Hugging Face token found, prompting user');
        vscode.window.showInformationMessage(
            'CodeMentor requires a Hugging Face API token. Please provide it to continue.',
            'Set Token'
        ).then(selection => {
            if (selection === 'Set Token') {
                vscode.commands.executeCommand('codementor.setToken');
            }
        });
    } else {
        outputChannel.appendLine('✅ Hugging Face token found.');
    }
}

async function setupFileWatcher(context, secretStorage, outputChannel, recentEvents) {
    if (!vscode.workspace.workspaceFolders) {
        outputChannel.appendLine('Error: No workspace folder open. Please open a folder to enable file watching.');
        vscode.window.showErrorMessage('Please open a workspace folder to use CodeMentor.');
        return;
    }

    outputChannel.appendLine(`Workspace folders: ${vscode.workspace.workspaceFolders.map(f => f.uri.fsPath).join(', ')}`);
    const watcher = vscode.workspace.createFileSystemWatcher('**/*.py', false, false, false);
    
    const debouncedRunMentorFeedback = debounce(async (uri, token) => {
        const filePath = uri.fsPath;
        const now = Date.now();
        if (recentEvents.has(filePath) && now - recentEvents.get(filePath) < 3000) {
            outputChannel.appendLine(`Skipping redundant event for ${filePath}`);
            return;
        }
        recentEvents.set(filePath, now);
        
        outputChannel.appendLine(`FileSystemWatcher: Change detected for ${filePath}`);
        const code = await fs.readFile(filePath, 'utf-8').catch(err => {
            outputChannel.appendLine(`Error reading file ${filePath}: ${err.message}`);
            return null;
        });
        if (code) {
            await runMentorFeedback(filePath, code, token, outputChannel);
        }
    }, 3000);

    watcher.onDidChange(async (uri) => {
        const token = await secretStorage.get('huggingFaceToken');
        if (!token) {
            outputChannel.appendLine('Error: No Hugging Face token for file change');
            return;
        }
        debouncedRunMentorFeedback(uri, token);
    });

    watcher.onDidCreate(async (uri) => {
        outputChannel.appendLine(`FileSystemWatcher: Create detected for ${uri.fsPath}`);
        const token = await secretStorage.get('huggingFaceToken');
        if (!token) {
            outputChannel.appendLine('Error: No Hugging Face token for file creation');
            return;
        }
        
        const filePath = uri.fsPath;
        const code = await fs.readFile(filePath, 'utf-8').catch(err => {
            outputChannel.appendLine(`Error reading file ${filePath}: ${err.message}`);
            return null;
        });
        if (code) {
            await runMentorFeedback(filePath, code, token, outputChannel);
        }
    });

    watcher.onDidDelete(async (uri) => {
        outputChannel.appendLine(`FileSystemWatcher: Delete detected for ${uri.fsPath}`);
        recentEvents.delete(uri.fsPath);
    });

    outputChannel.appendLine('File watcher initialized for Python files');
    context.subscriptions.push(watcher);
}

async function runMentorFeedback(filePath, code, token, outputChannel) {
    const pythonScript = path.join(__dirname, 'mentor.py');
    const mode = vscode.workspace.getConfiguration('codementor').get('mode', 'explain');
    const hintNum = vscode.workspace.getConfiguration('codementor').get('hintNum', 1);
    outputChannel.appendLine(`Attempting to spawn mentor.py for ${filePath} with mode: ${mode}, hintNum: ${hintNum}`);
    
    const pythonPath = 'C:\\Users\\NIKHIL\\AppData\\Local\\Programs\\Python\\Python313\\python.exe';
    outputChannel.appendLine(`Using Python path: ${pythonPath}`);
    outputChannel.appendLine(`Using mentor.py path: ${pythonScript}`);
    try {
        await fs.access(pythonPath);
        outputChannel.appendLine(`Python executable verified at: ${pythonPath}`);
    } catch (err) {
        outputChannel.appendLine(`⚠️ Python executable not found at ${pythonPath}: ${err.message}`);
        vscode.window.showErrorMessage(`Python executable not found at ${pythonPath}. Check the CodeMentor output channel.`);
        return;
    }
    try {
        await fs.access(pythonScript);
        outputChannel.appendLine(`mentor.py verified at: ${pythonScript}`);
    } catch (err) {
        outputChannel.appendLine(`⚠️ mentor.py not found at ${pythonScript}: ${err.message}`);
        vscode.window.showErrorMessage(`mentor.py not found at ${pythonScript}. Check the CodeMentor output channel.`);
        return;
    }

    const pythonProcess = spawn(pythonPath, [`"${pythonScript}"`, `"${filePath}"`, mode, hintNum.toString()], {
        env: { ...process.env, HF_TOKEN: token, PYTHONIOENCODING: 'utf-8' },
        shell: true
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        outputChannel.appendLine(`[stdout] ${text}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        const text = data.toString();
        errorOutput += text;
        outputChannel.appendLine(`[stderr] ${text}`);
    });

    pythonProcess.on('error', (err) => {
        outputChannel.appendLine(`⚠️ Failed to spawn mentor.py: ${err.message}`);
        vscode.window.showErrorMessage(`Failed to run mentor.py: ${err.message}. Check the CodeMentor output channel.`);
    });

    pythonProcess.on('close', (code) => {
        outputChannel.appendLine(`mentor.py exited with code: ${code}`);
        if (code !== 0) {
            outputChannel.appendLine(`⚠️ Error processing ${filePath}:\n${errorOutput || 'No error output captured'}`);
            vscode.window.showErrorMessage(`Error processing ${filePath}. Check the CodeMentor output channel.`);
        } else if (!output) {
            outputChannel.appendLine(`⚠️ Warning: No output received from mentor.py for ${filePath}`);
            vscode.window.showErrorMessage(`No output received from mentor.py. Check the CodeMentor output channel.`);
        } else {
            const feedbackFile = path.join(path.dirname(filePath), 'CodeMentor_Feedback.txt');
            fs.writeFile(feedbackFile, output).then(() => {
                vscode.workspace.openTextDocument(feedbackFile).then(doc => {
                    vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.Beside });
                });
            });
            vscode.window.showInformationMessage(`Feedback generated for ${path.basename(filePath)}. Check the CodeMentor output channel or CodeMentor_Feedback.txt.`);
        }
    });
}

function deactivate() {
    console.log('CodeMentor extension deactivated');
}

module.exports = {
    activate,
    deactivate
};