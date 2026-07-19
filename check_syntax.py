import os
import py_compile

errors = []
for root, dirs, files in os.walk('.'):
    # skip virtualenv and .git folders
    if '.venv' in root.split(os.sep) or 'venv' in root.split(os.sep) or '.git' in root.split(os.sep):
        continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append((path, str(e)))

if errors:
    print('SYNTAX_ERRORS_FOUND')
    for p, err in errors:
        print(p)
        print(err)
    exit(2)
else:
    print('NO_SYNTAX_ERRORS')
    exit(0)
