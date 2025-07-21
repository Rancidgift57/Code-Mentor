# CodeMentor VS Code Extension
![logocode](https://github.com/user-attachments/assets/54d3d224-f08d-429b-ac62-601782b87613)


**CodeMentor** is an AI-powered Visual Studio Code extension that provides real-time analysis, hints, and solutions for Python code using Hugging Face's `distilgpt2` model. It helps developers debug syntax errors, improve code quality, and understand their code through detailed explanations.

## Features
- **Explain Mode** (`Ctrl+E`): Get detailed explanations of your Python code, including functionality and potential improvements.
- **Hint Mode** (`Ctrl+Y`): Receive concise hints to fix errors or optimize code without revealing the full solution.
- **Solution Mode** (`Ctrl+Shift+S`): Obtain corrected code with explanations for syntax errors or enhancements.
- **Set Hugging Face Token** (`Ctrl+Shift+T`): Configure your Hugging Face API token for AI-powered feedback.
- **Flake8 Integration**: Automatically checks for PEP 8 style violations and suggests fixes.

## Installation
1. **Install from Marketplace**:
   - Search for `CodeMentor` in the VS Code Extensions view (`Ctrl+Shift+X`) or visit [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=nikhil-codementor.codementor).
   - Click **Install**.

2. **Set Up Python Environment**:
   - Install Python 3.11 (recommended for compatibility) or 3.13:
     ```bash
     # Windows
     python --version
     # Install Python 3.11 if needed: https://www.python.org/downloads/
     ```
   - Install required dependencies:
     ```bash
     pip install watchdog flake8 requests autopep8 huggingface_hub transformers==4.44.2 torch
     ```

3. **Configure Hugging Face Token**:
   - Obtain a token from [Hugging Face Settings](https://huggingface.co/settings/tokens).
   - In VS Code, press `Ctrl+Shift+T` and enter your token when prompted.
   - Alternatively, set the environment variable:
     ```bash
     # Windows
     set HF_TOKEN=your_hf_token
     ```

4. **System Requirements**:
   - ~2GB RAM for `distilgpt2` (default model).
   - ~50GB RAM or GPU for `mistralai/Mixtral-8x7B-Instruct-v0.1` (optional, edit `mentor.py` line 88).

## Usage
1. Open a Python file (e.g., `test.py`) in VS Code.
2. Use the following commands:
   - `Ctrl+E`: Explain the code’s functionality and suggest improvements.
   - `Ctrl+Y`: Get a hint to fix errors or optimize code.
   - `Ctrl+Shift+S`: Receive corrected code with an explanation.
3. Feedback is saved to `CodeMentor_Feedback.txt` in the same directory as your Python file.

### Example
For a file `test.py`:
```python
def add(a, b)  # Missing colon
    return a + b
```
- **Solution Mode** (`Ctrl+Shift+S`) output:
  ```
  Solution: Corrected code:
  ```python
  def add(a, b):
      return a + b
  ```
  Explanation: Added missing colon after the function definition.
  ```

## Setting Up a GitHub Repository
To contribute to or publish updates for CodeMentor, set up a GitHub repository to host the source code.

### Prerequisites
- **Git**: Install from [Git](https://git-scm.com) and verify:
  ```bash
  git --version
  ```
- **Node.js**: Install from [Node.js](https://nodejs.org) and verify:
  ```bash
  node --version
  npm --version
  ```
- **VS Code**: Install from [Visual Studio Code](https://code.visualstudio.com).
- **VSCE**: Install the VS Code Extension CLI:
  ```bash
  npm install -g vsce
  vsce --version
  ```
- **GitHub Account**: Create an account at [GitHub](https://github.com).

### Steps to Create and Push to GitHub
1. **Initialize a Git Repository**:
   Navigate to your project directory:
   ```bash
   cd "C:\Users\NIKHIL\OneDrive - South Indian Education Society\python practice\codebunny"
   git init
   ```

2. **Create `.gitignore`**:
   Create a `.gitignore` file to exclude unnecessary files:
   ```bash
   echo "node_modules/
   *.vsix
   CodeMentor_Feedback.txt
   .vscode/
   *.log" > .gitignore
   ```

3. **Add and Commit Files**:
   Add all relevant files (`package.json`, `extension.js`, `mentor.py`, `README.md`, `LICENSE`, `images/codementor.png`):
   ```bash
   git add .
   git commit -m "Initial commit: Add CodeMentor extension files"
   ```

4. **Create a GitHub Repository**:
   - Go to [GitHub](https://github.com/new).
   - Set:
     - **Repository Name**: `codementor`
     - **Description**: "AI-powered VS Code extension for Python code analysis"
     - **Visibility**: Public (recommended for open-source) or Private
     - **Initialize with README**: Uncheck (since you have your own `README.md`)
   - Click **Create repository**.

5. **Link Local Repository to GitHub**:
   Copy the repository URL (e.g., `https://github.com/yourusername/codementor.git`) and run:
   ```bash
   git remote add origin https://github.com/yourusername/codementor.git
   git branch -M main
   git push -u origin main
   ```

6. **Verify**:
   - Visit `https://github.com/yourusername/codementor` to confirm all files (`README.md`, `LICENSE`, etc.) are uploaded.
   - Update `package.json` with the repository URL:
     ```json
     "repository": {
       "type": "git",
       "url": "https://github.com/yourusername/codementor"
     }
     ```

### Publishing to Visual Studio Marketplace
To publish updates (e.g., version `0.0.3` with `README.md` and `LICENSE`), follow these steps:

1. **Create a Publisher Account**:
   - Go to [Visual Studio Marketplace](https://marketplace.visualstudio.com/manage).
   - Sign in with a Microsoft account.
   - Click **Create publisher**:
     - **ID**: `nikhil-codementor`
     - **Name**: `NikhilCodeMentor`
   - Save.

2. **Create a Personal Access Token (PAT)**:
   - Go to [Azure DevOps](https://dev.azure.com/{your_organization}).
   - Profile > **Personal access tokens** > **New Token**.
   - Set:
     - **Name**: `VSCodeExtensionPublish`
     - **Organization**: **All accessible organizations**
     - **Expiration**: 1 year
     - **Scopes**: **Marketplace** > **Acquire** and **Publish**
   - Copy the token securely.

3. **Resolve Git Working Directory Error**:
   If you see `npm error Git working directory not clean`:
   - Check uncommitted changes:
     ```bash
     git status
     ```
   - Add and commit changes:
     ```bash
     git add README.md LICENSE package.json images/codementor.png
     git commit -m "Add README.md, LICENSE, and update package.json for v0.0.3"
     ```
   - Verify clean status:
     ```bash
     git status
     # Should show: nothing to commit, working tree clean
     ```

4. **Package the Extension**:
   ```bash
   vsce package
   ```
   - Creates `codementor-0.0.2.vsix` (or `0.0.3` if version updated).
   - Verify files are included:
     ```bash
     vsce ls
     ```
     Expected: `README.md`, `LICENSE`, `package.json`, `extension.js`, `mentor.py`, `images/codementor.png`.

5. **Test Locally**:
   ```bash
   code --install-extension codementor-0.0.2.vsix
   ```
   - Test with a Python file (e.g., `test.py`):
     ```python
     def add(a, b)  # Missing colon
         return a + b
     ```
   - Run `Ctrl+Shift+S` and check `CodeMentor_Feedback.txt`:
     ```
     Solution: Corrected code:
     ```python
     def add(a, b):
         return a + b
     ```
     Explanation: Added missing colon.
     ```
   - Verify `README.md` appears in the Extensions view (`Ctrl+Shift+X`).

6. **Publish**:
   ```bash
   vsce login nikhil-codementor
   vsce publish patch
   ```
   - Enter your PAT when prompted.
   - This increments `package.json` to `0.0.3` and publishes.
   - Alternatively:
     ```bash
     vsce publish -p your_personal_access_token
     ```

7. **Verify**:
   - Visit [Marketplace](https://marketplace.visualstudio.com/items?itemName=nikhil-codementor.codementor).
   - Confirm `README.md` and `LICENSE` appear on the extension page.
   - Check version `0.0.3` in VS Code Extensions view (`Ctrl+Shift+X`).

## Automating Publishing with GitHub Actions
To automate publishing updates to the Marketplace, set up a GitHub Action.

1. **Create Workflow File**:
   Create `.github/workflows/publish.yml`:
   ```yaml
   name: Publish to Visual Studio Marketplace
   on:
     push:
       tags:
         - "v*"
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
           with:
             node-version: 20
         - run: npm ci
         - name: Publish
           uses: HaaLeo/publish-vscode-extension@v2
           with:
             pat: ${{ secrets.VS_MARKETPLACE_TOKEN }}
             registryUrl: https://marketplace.visualstudio.com
   ```

2. **Add PAT to GitHub Secrets**:
   - Go to `https://github.com/yourusername/codementor/settings/secrets/actions`.
   - Click **New repository secret**.
   - Name: `VS_MARKETPLACE_TOKEN`.
   - Value: Your Azure DevOps PAT.

3. **Tag and Push**:
   ```bash
   git tag v0.0.3
   git push origin v0.0.3
   ```
   - This triggers the workflow to publish version `0.0.3`.

## Requirements
- **Python**: 3.11 (preferred) or 3.13.
- **Dependencies**: `watchdog`, `flake8`, `requests`, `autopep8`, `huggingface_hub`, `transformers==4.44.2`, `torch`.
- **Hugging Face Token**: Required for `distilgpt2`.
- **System**: ~2GB RAM for `distilgpt2` or ~50GB for `mistralai/Mixtral-8x7B-Instruct-v0.1`.

## Known Issues
- **Git Working Directory Not Clean**:
  - Error during `vsce publish patch`: `npm error Git working directory not clean`.
  - Fix: Commit or stash changes (see "Publishing" step 3).
  - Check log: `C:\Users\NIKHIL\AppData\Local\npm-cache\_logs\2025-07-21T13_28_31_345Z-debug-0.log`.
- **Model Loading**: `distilgpt2` may fail on low-memory systems. Edit `mentor.py` (line 88) to use `gpt2`:
  ```python
  generator = pipeline('text-generation', model='gpt2')
  ```
- **Python 3.13**: Compatibility issues with `transformers`. Use Python 3.11:
  ```bash
  C:\Users\NIKHIL\AppData\Local\Programs\Python\Python311\python.exe -m pip install watchdog flake8 requests autopep8 huggingface_hub transformers==4.44.2 torch
  ```
  Update `extension.js` (line 166):
  ```javascript
  const pythonPath = 'C:\\Users\\NIKHIL\\AppData\\Local\\Programs\\Python\\Python311\\python.exe';
  ```
- **IntelliCode/Pylance**: Disable via `Ctrl+Shift+X` if conflicts occur.


## Contributing
- File issues or submit pull requests at [GitHub](https://github.com/Rancidgift57/Code-Mentor.git).
- 
## License
[MIT](LICENSE)

## Contact
For support, contact email: nnair7598@gmail.com.
