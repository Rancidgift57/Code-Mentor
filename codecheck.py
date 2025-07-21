import subprocess
import ast
import time
import os
import argparse
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

# Authenticate with Hugging Face (assumes HF_TOKEN is set in environment or user provides it)
try:
    login()  # Will use HF_TOKEN from environment or prompt user
except Exception as e:
    print(f"❌ Failed to authenticate with Hugging Face: {e}")
    sys.exit(1)

# Load Gemma model
model_id = "google/gemma-1.1-2b-it"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
except Exception as e:
    print(f"❌ Failed to load Gemma model: {e}")
    sys.exit(1)

def get_mentor_response(code, mode='explain', hint_num=1):
    try:
        if mode == 'explain':
            prompt = f"""You are a Python code assistant. Explain this code like a mentor, providing hints for improvement without giving full solutions:

```python
{code}
```"""
        elif mode == 'hint':
            prompt = f"""You are a Python code assistant. Review this code and provide hint {hint_num} to fix any errors or improve it, without giving the full solution:

```python
{code}
```"""
        elif mode == 'solution':
            prompt = f"""You are a Python code assistant. Review this code and provide the full solution to fix any errors:

```python
{code}
```"""
        response = generator(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)
        return response[0]['generated_text'].split("```")[0].strip()
    except Exception as e:
        return f"⚠️ Couldn’t get mentor response: {str(e)}. Hint: Check your code for syntax errors or try breaking it into smaller parts."

def check_flake8_availability():
    try:
        subprocess.run(['flake8', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def run_flake8(file_path):
    if not check_flake8_availability():
        return "⚠️ Flake8 not found. Please install it with 'pip install flake8'."
    
    try:
        result = subprocess.run(
            ['flake8', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return "✅ No style issues found."
        else:
            issues = result.stdout.strip().split('\n')
            formatted_issues = "\n".join(f"  {issue}" for issue in issues if issue)
            return f"⚠️ Style issues:\n{formatted_issues}"
    except Exception as e:
        return f"⚠️ Error running flake8: {str(e)}"

def first_check(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code)
        return True, "✅ Syntax Correct", code
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}", None
    except UnicodeDecodeError:
        return False, f"❌ Error: Could not decode {file_path}. Ensure it is a valid text file.", None
    except IOError as e:
        return False, f"❌ Error reading {file_path}: {str(e)}", None

class CodeMonitor(FileSystemEventHandler):
    def __init__(self, mode='explain', hint_num=1):
        self.last_processed = {}  # Track last processed time for debouncing
        self.debounce_interval = 1.0  # Seconds to wait before re-processing
        self.mode = mode
        self.hint_num = hint_num

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        current_time = time.time()
        if event.src_path in self.last_processed:
            if current_time - self.last_processed[event.src_path] < self.debounce_interval:
                return  # Skip if modified too recently

        print(f"\n🔍 Detected change in: {event.src_path}")
        ok, syntax_msg, code = first_check(event.src_path)
        print(syntax_msg)
        
        if ok and code:
            # Run flake8
            flake_output = run_flake8(event.src_path)
            print(flake_output)
            
            # Get mentor response from Gemma
            mentor_response = get_mentor_response(code, self.mode, self.hint_num)
            print(f"🧑‍🏫 Mentor Response ({self.mode} mode):\n{mentor_response}")

        self.last_processed[event.src_path] = current_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Python files with syntax, style, and mentor feedback.")
    parser.add_argument("path", nargs="?", default=".", help="Directory to monitor (default: current directory)")
    parser.add_argument("--mode", choices=['explain', 'hint', 'solution'], default='explain', help="Mentor response mode")
    parser.add_argument("--hint-num", type=int, default=1, help="Hint number for 'hint' mode")
    parser.add_argument("--no-recursive", action="store_false", dest="recursive", help="Disable recursive monitoring")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"❌ Error: '{args.path}' is not a valid directory.")
        sys.exit(1)

    observer = Observer()
    observer.schedule(CodeMonitor(mode=args.mode, hint_num=args.hint_num), path=args.path, recursive=args.recursive)
    observer.start()
    print(f"👀 Monitoring Python files in '{args.path}' (recursive: {args.recursive}, mode: {args.mode})... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Code mentor watchdog stopped.")
    observer.join()