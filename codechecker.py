import subprocess
import ast
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def run_flake8(file_path):
    result = subprocess.run(
        ['flake8', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode == 0:
        return "✅ No syntax or style issues found."
    else:
        return f"⚠️ Style issues:\n{result.stdout}"

def first_check(files):
    with open(files, "r", encoding="utf8") as f:
        at = f.read()
        try:
            ast.parse(at)
            return True, "✅ Syntax Correct"
        except SyntaxError as e:
            return False, f"❌ Syntax Error: {e}"

class CodeMonitor(FileSystemEventHandler):
    def on_modified(self, event):  
        if event.src_path.endswith(".py") and not event.is_directory:
            print(f"\n🔍 Detected change in: {event.src_path}")
            ok, syntax_msg = first_check(event.src_path)
            print(syntax_msg)
            if ok:
                flake_output = run_flake8(event.src_path)
                print(flake_output)

if __name__ == "__main__":
    path = "."  
    observer = Observer()
    observer.schedule(CodeMonitor(), path=path, recursive=True)
    observer.start()
    print(f"👀 Monitoring Python files in '{path}'... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
