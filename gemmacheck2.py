import sys
import json
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from io import StringIO
import parso

def analyze_code(file_path, mode='analyze', hint_num=1):
    errors = []
    hints = []

    # Run Pylint
    output = StringIO()
    reporter = TextReporter(output)
    Run([file_path, '--disable=all', '--enable=undefined-variable,invalid-name,too-few-public-methods,too-many-arguments,missing-function-docstring,too-many-locals,too-many-branches,too-many-statements'], reporter=reporter, exit=False)
    pylint_output = output.getvalue()

    for line in pylint_output.splitlines():
        if 'undefined-variable' in line:
            line_num = int(line.split(':')[1])
            errors.append({
                'type': 'error',
                'line': line_num,
                'message': 'Error: Variable used before definition.',
                'explanation': 'Hint: Check if you initialized it.'
            })
            if mode == 'hint':
                hints.append({
                    'message': f"Hint {hint_num}: Define the variable before using it.",
                    'explanation': 'Try setting it to a default value, like `x = 0`.'
                } if hint_num == 1 else {
                    'message': f"Hint {hint_num}: Check the line above this error.",
                    'explanation': 'Ensure the variable is assigned before use.'
                } if hint_num == 2 else {
                    'message': f"Hint {hint_num}: Use an assignment statement.",
                    'explanation': 'Add `x = 0` before the line.'
                })
            elif mode == 'step':
                hints.append({
                    'message': f"Step {hint_num}: Define the variable above this line.",
                    'explanation': 'Add `x = 0` before using `x`. Want the next step?' if hint_num < 3 else 'Try the solution now.'
                })
            elif mode == 'solution':
                hints.append({
                    'message': 'Solution: Add `x = 0` before using the variable.',
                    'explanation': 'This defines the variable to avoid NameError.'
                })
        elif 'invalid-name' in line:
            line_num = int(line.split(':')[1])
            hints.append({
                'type': 'suggestion',
                'line': line_num,
                'message': 'Hint: Variable name doesn’t follow PEP 8.',
                'explanation': 'Use snake_case, like `my_variable`.'
            })
            if mode == 'hint':
                hints.append({
                    'message': f"Hint {hint_num}: Rename to follow PEP 8.",
                    'explanation': 'Use underscores, e.g., `my_variable`.'
                } if hint_num == 1 else {
                    'message': f"Hint {hint_num}: Avoid camelCase.",
                    'explanation': 'Python prefers snake_case for variables.'
                } if hint_num == 2 else {
                    'message': f"Hint {hint_num}: Check PEP 8 guidelines.",
                    'explanation': 'See https://peps.python.org/pep-0008/.'
                })
            elif mode == 'step':
                hints.append({
                    'message': f"Step {hint_num}: Rename to snake_case.",
                    'explanation': 'Change `myVariable` to `my_variable`. Want the next step?' if hint_num < 3 else 'Try the solution now.'
                })
            elif mode == 'solution':
                hints.append({
                    'message': 'Solution: Rename to `my_variable`.',
                    'explanation': 'This follows PEP 8 for Python variable names.'
                })

    # Parse with Parso for missing arguments
    with open(file_path, 'r') as f:
        code = f.read()
    tree = parso.parse(code)
    for node in tree.iter_imports():
        errors.append({
            'type': 'error',
            'line': node.start_pos[0],
            'message': f"Error: Syntax error at line {node.start_pos[0]}.",
            'explanation': 'Hint: Check for missing arguments or syntax.'
        })
    for func_call in tree.iter_funcdefs():
        if func_call.name.value == 'add_numbers':
            args = len([arg for arg in func_call.children if arg.type == 'argument'])
            if args < 2:
                errors.append({
                    'type': 'error',
                    'line': func_call.start_pos[0],
                    'message': 'Error: Missing argument for `add_numbers`.',
                    'explanation': 'Hint: The function expects two parameters.'
                })
                if mode == 'hint':
                    hints.append({
                        'message': f"Hint {hint_num}: Check the number of arguments in `add_numbers`.",
                        'explanation': 'The function needs two inputs, like `add_numbers(5, 10)`.' if hint_num == 1 else
                                     'Count the parameters in the function definition.' if hint_num == 2 else
                                     'Look at the function’s signature for clues.'
                    })
                elif mode == 'step':
                    hints.append({
                        'message': f"Step {hint_num}: Check the function definition.",
                        'explanation': 'See how many parameters `add_numbers` expects.' if hint_num == 1 else
                                     'Add a second argument to the function call.' if hint_num == 2 else
                                     'Try calling `add_numbers` with two numbers.'
                    })
                elif mode == 'solution':
                    hints.append({
                        'message': 'Solution: Call `add_numbers(5, 10)`.',
                        'explanation': 'This provides the required second argument.'
                    })

    if mode == 'analyze':
        return errors + hints
    return hints

if __name__ == '__main__':
    file_path = "test.py"
    mode = sys.argv[2] if len(sys.argv) > 2 else 'analyze'
    hint_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    print(json.dumps(analyze_code(file_path, mode, hint_num)))