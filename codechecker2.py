import subprocess
import ast
import time
import os
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
            return "✅ No syntax or style issues found."
        else:
            # Clean up flake8 output for readability
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
        return True, "✅ Syntax Correct"
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}"
    except UnicodeDecodeError:
        return False, f"❌ Error: Could not decode {file_path}. Ensure it is a valid text file."
    except IOError as e:
        return False, f"❌ Error reading {file_path}: {str(e)}"

class CodeMonitor(FileSystemEventHandler):
    def __init__(self):
        self.last_processed = {}  # Track last processed time for debouncing
        self.debounce_interval = 1.0  # Seconds to wait before re-processing

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        current_time = time.time()
        if event.src_path in self.last_processed:
            if current_time - self.last_processed[event.src_path] < self.debounce_interval:
                return  # Skip if modified too recently

        print(f"\n🔍 Detected change in: {event.src_path}")
        ok, syntax_msg = first_check(event.src_path)
        print(syntax_msg)
        if ok:
            flake_output = run_flake8(event.src_path)
            print(flake_output)

        self.last_processed[event.src_path] = current_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Python files for syntax and style issues.")
    parser.add_argument("path", nargs="?", default=".", help="Directory to monitor (default: current directory)")
    parser.add_argument("--no-recursive", action="store_false", dest="recursive", help="Disable recursive monitoring")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"❌ Error: '{args.path}' is not a valid directory.")
        exit(1)

    observer = Observer()
    observer.schedule(CodeMonitor(), path=args.path, recursive=args.recursive)
    observer.start()
    print(f"👀 Monitoring Python files in '{args.path}' (recursive: {args.recursive})... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Syntax watchdog stopped.")
    observer.join()