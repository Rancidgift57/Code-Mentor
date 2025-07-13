import subprocess
import ast

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
        return f"❌ Issues found:\n{result.stdout}"




files = "gemma.py"
with open(files,"r",encoding="utf8") as f:
    at = f.read()
    #print(at)
    try:
        print("All fine")

        if ast.parse(at):
            print(run_flake8(files))
    except SyntaxError as e:
        print(f"Syntax error: {e}")



