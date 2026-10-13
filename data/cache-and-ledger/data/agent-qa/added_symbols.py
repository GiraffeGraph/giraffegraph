"""List the classes, functions and methods of a tree that an earlier tree did not have.

usage: added_symbols.py <app dir at the earlier commit> <app dir at the current commit>
"""
import ast
import sys
from pathlib import Path

DEFS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def symbols(root):
    found = {}
    for path in sorted(Path(root).rglob("*.py")):
        try:
            module = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        stack = [(module, "")]
        while stack:
            scope, prefix = stack.pop()
            for node in scope.body:
                if isinstance(node, DEFS):
                    name = prefix + node.name
                    found.setdefault(name, (path.relative_to(root).as_posix(), node.lineno))
                    if isinstance(node, ast.ClassDef):
                        stack.append((node, name + "."))
    return found


earlier, current = symbols(sys.argv[1]), symbols(sys.argv[2])
added = {name: where for name, where in current.items() if name not in earlier}
by_file = {}
for name, (path, line) in sorted(added.items(), key=lambda item: item[1]):
    if name.split(".")[-1].startswith("__"):
        continue
    by_file.setdefault(path, []).append(f"{name}:{line}")
NOTE = ("Classes, functions and methods that exist in `src/` and did not exist when the statements "
        "above were written (name:line). No statement above describes them.")
lines = ["## Added since these statements were written", "", NOTE, ""]
lines += [f"- src/app/{path}: " + ", ".join(names) for path, names in by_file.items()]
print("\n".join(lines))
print(f"earlier {len(earlier)}, current {len(current)}, added {len(added)}", file=sys.stderr)
