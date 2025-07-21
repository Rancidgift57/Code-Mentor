import subprocess
import ast
import sys
import os
import re
from huggingface_hub import login
from transformers import pipeline

def check_flake8_availability():
    try:
        subprocess.run(['flake8', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def run_flake8(file_path):
    if not check_flake8_availability():
        return "[!] Flake8 not found. Please install it with 'pip install flake8'."
    
    try:
        result = subprocess.run(
            ['flake8', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return "[+] No style issues found."
        else:
            issues = result.stdout.strip().split('\n')
            formatted_issues = "\n".join(f"  {issue}" for issue in issues if issue)
            return f"[!] Style issues:\n{formatted_issues}"
    except Exception as e:
        return f"[!] Error running flake8: {str(e)}"

def first_check(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code)
        return True, "[+] Syntax Correct", code
    except SyntaxError as e:
        return False, f"[X] Syntax Error: {str(e)}", code
    except UnicodeDecodeError:
        return False, f"[X] Error: Could not decode {file_path}. Ensure it is a valid text file.", ""
    except IOError as e:
        return False, f"[X] Error reading {file_path}: {str(e)}", ""

def fix_common_syntax_error(code, error_msg):
    """Fallback to fix common syntax errors if model fails."""
    if "expected ':'" in error_msg:
        lines = code.split('\n')
        line_num = int(re.search(r'line (\d+)', error_msg).group(1)) - 1 if re.search(r'line (\d+)', error_msg) else 0
        if line_num < len(lines):
            lines[line_num] = lines[line_num].rstrip() + ':'
            return '\n'.join(lines), "Added missing colon."
    return code, "No automatic fix available."

def generate_prompt(code, error_msg, mode, hint_num):
    """Generate prompt based on mode."""
    if mode == "explain":
        prompt = f"Analyze the following Python code and provide a detailed explanation of what it does, including any potential improvements:\n\n```python\n{code}\n```"
        if error_msg:
            prompt += f"\nThe code has the following error: {error_msg}"
    elif mode == "hint":
        prompt = f"Analyze the following Python code for errors or improvements. Provide a single concise hint (hint number {hint_num}) to help the user fix or improve the code without giving the full solution:\n\n```python\n{code}\n```"
        if error_msg:
            prompt += f"\nThe code has the following error: {error_msg}"
    else:  # solution
        prompt = f"Analyze the following Python code for errors or improvements. Provide the corrected or improved version of the code with a brief explanation of the changes:\n\n```python\n{code}\n```"
        if error_msg:
            prompt += f"\nThe code has the following error: {error_msg}. Please fix this error."
    return prompt

def get_mentor_feedback(code, error_msg, mode, hint_num):
    try:
        token = os.environ.get('HF_TOKEN')
        if not token:
            safe_print("[!] Error: No HF_TOKEN found in environment.")
            if mode == "solution" and error_msg:
                fixed_code, fix_explanation = fix_common_syntax_error(code, error_msg)
                return f"Corrected code:\n```python\n{fixed_code}\n```\nExplanation: {fix_explanation}"
            return "[!] Error: No HF_TOKEN found in environment."
        
        safe_print("[*] Authenticating with Hugging Face Hub...")
        login(token=token)
        safe_print("[*] Loading model 'distilgpt2'...")
        try:
            generator = pipeline('text-generation', model='distilgpt2')
        except Exception as model_error:
            safe_print(f"[!] Failed to load model 'distilgpt2': {str(model_error)}")
            if mode == "solution" and error_msg:
                fixed_code, fix_explanation = fix_common_syntax_error(code, error_msg)
                return f"Corrected code:\n```python\n{fixed_code}\n```\nExplanation: {fix_explanation}"
            return f"[!] Failed to load model: {str(model_error)}"
        
        prompt = generate_prompt(code, error_msg, mode, hint_num)
        safe_print(f"[*] Generating response for {mode} mode...")
        try:
            response = generator(prompt, max_length=500, num_return_sequences=1, truncation=True)
            response_text = response[0]['generated_text']
            # Validate response to ensure it’s not the prompt or garbage
            if response_text.strip().startswith(prompt.strip()) or "def add(" in response_text:
                safe_print("[!] Invalid model response detected.")
                if mode == "solution" and error_msg:
                    fixed_code, fix_explanation = fix_common_syntax_error(code, error_msg)
                    return f"Corrected code:\n```python\n{fixed_code}\n```\nExplanation: {fix_explanation}"
                return "[!] Invalid model response."
            return response_text
        except Exception as inference_error:
            safe_print(f"[!] Failed to generate response: {str(inference_error)}")
            if mode == "solution" and error_msg:
                fixed_code, fix_explanation = fix_common_syntax_error(code, error_msg)
                return f"Corrected code:\n```python\n{fixed_code}\n```\nExplanation: {fix_explanation}"
            return f"[!] Failed to generate response: {str(inference_error)}"
    except Exception as e:
        safe_print(f"[!] General error in mentor feedback: {str(e)}")
        if mode == "solution" and error_msg:
            fixed_code, fix_explanation = fix_common_syntax_error(code, error_msg)
            return f"Corrected code:\n```python\n{fixed_code}\n```\nExplanation: {fix_explanation}"
        return f"[!] General error in mentor feedback: {str(e)}"

def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        safe_print("Usage: python mentor.py <file_path> [mode] [hint_num]")
        sys.exit(1)

    file_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "explain"
    hint_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    safe_print(f"Processing file: {file_path}")
    
    ok, syntax_msg, code = first_check(file_path)
    safe_print(syntax_msg)
    
    if not ok:
        if mode == "hint":
            line_num = re.search(r'line (\d+)', syntax_msg)
            line_num = line_num.group(1) if line_num else "unknown"
            safe_print(f"Hint {hint_num}: Check the syntax error at line {line_num}. Ensure proper syntax for Python statements, such as colons and indentation.")
        elif mode == "solution":
            prompt = generate_prompt(code, syntax_msg, mode, hint_num)
            mentor_response = get_mentor_feedback(code, syntax_msg, mode, hint_num)
            safe_print(f"Solution:\n{mentor_response}")
        else:  # explain
            safe_print(f"Explanation: The code contains a syntax error: {syntax_msg}")
        sys.exit(0)
    
    flake_output = run_flake8(file_path)
    safe_print(flake_output)
    
    if "[!]" in flake_output and mode == "hint":
        safe_print(f"Hint {hint_num}: Address the style issues reported by flake8 to improve code quality.")
    elif "[!]" in flake_output and mode == "solution":
        safe_print("Solution: Run 'autopep8 --in-place <file_path>' to automatically fix style issues, then verify with flake8.")
    
    prompt = generate_prompt(code, "", mode, hint_num)
    mentor_response = get_mentor_feedback(code, "", mode, hint_num)
    safe_print(f"[*] Mentor Response ({mode} mode):\n{mentor_response}")

    