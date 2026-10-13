"""Cloze frames: statements about a code base whose facts are filled in from the tree at read time.

A frame is a sentence with blanks. The sentence may not contain an identifier, number or literal;
every fact comes from a blank, and a blank is a selector (`path.py::Class.method`) plus a reducer
that a script evaluates with `ast` against whatever tree it is pointed at. Nothing a frame stores
can go stale: a blank that does not resolve withdraws its sentence and leaves the address.

frames.json: [{"section": "<heading>", "text": "Accepted names: {S}. Otherwise {E} is raised.",
               "blanks": {"S": {"at": "pkg/mod.py::Service.run", "reduce": "lines", "arg": "strategy"},
                          "E": {"at": "pkg/mod.py::Service.run", "reduce": "raises"}}}]

Selector: a path relative to the application directory, then `::` and a dotted chain of class and
function names. The last name may also be a variable assigned in that scope, an attribute assigned
as `self.name`, a class field, or a parameter of the function.

Reducers: signature, body (arg: max lines), value, members, methods, raises, calls, returns,
decorators, strings, keys, lines (arg: regular expression matched against the lines of the symbol).

usage: cloze.py check  --tree APP_DIR --frames frames.json
       cloze.py render --tree APP_DIR --frames frames.json --out behaviour.md [--report report.json]
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

DEFS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
BLOCK_REDUCERS = ("body", "lines")
MAX_ITEMS, MAX_ITEM_CHARS, MAX_BODY_LINES = 12, 160, 25
ALLOWED_CAPITALS = {"API", "HTTP", "LLM", "JSON", "UUID", "SQL", "ID", "URL"}
FORBIDDEN = [
    (re.compile(r"`"), "code span"),
    (re.compile(r"\d"), "digit"),
    (re.compile(r"\w_\w"), "identifier with an underscore"),
    (re.compile(r"[a-z][A-Z]"), "identifier in camel case"),
    (re.compile(r"/|\.py\b"), "path"),
    (re.compile(r"[\"“”]"), "quoted literal"),
]
BLANK = re.compile(r"\{(\w+)\}")


def lint(text):
    """Reasons why the sentence carries a fact outside its blanks."""
    bare = BLANK.sub(" ", text)
    problems = [reason for pattern, reason in FORBIDDEN if pattern.search(bare)]
    capitals = set(re.findall(r"\b[A-Z]{2,}\b", bare)) - ALLOWED_CAPITALS
    if capitals:
        problems.append("constant-like word: " + ", ".join(sorted(capitals)))
    return problems


def own_nodes(scope):
    """Nodes of a scope in source order, without entering nested classes and functions."""
    found, stack = [], list(ast.iter_child_nodes(scope))
    while stack:
        node = stack.pop()
        found.append(node)
        if not isinstance(node, DEFS):
            stack.extend(ast.iter_child_nodes(node))
    return sorted(found, key=position)


def position(node):
    return (getattr(node, "lineno", 0), getattr(node, "col_offset", 0))


def assigned(scope, name):
    """The statement or parameter that gives `name` its value inside `scope`."""
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = scope.args
        positional = args.posonlyargs + args.args
        defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
        pairs = [(arg, defaults[i]) for i, arg in enumerate(positional)] + [
            (arg, args.kw_defaults[i]) for i, arg in enumerate(args.kwonlyargs)]
        for arg, default in pairs:
            if arg.arg == name:
                return ("parameter", arg, default)
    for node in own_nodes(scope):
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else [])
        for target in targets:
            if (isinstance(target, ast.Name) and target.id == name) or (
                    isinstance(target, ast.Attribute) and target.attr == name):
                return ("assignment", node, None)
    return None


def find(module, parts):
    scope = module
    for index, part in enumerate(parts):
        inner = next((n for n in own_nodes(scope) if isinstance(n, DEFS) and n.name == part), None)
        if inner is None:
            return assigned(scope, part) if index == len(parts) - 1 else None
        scope = inner
    return ("symbol", scope, None)


class Tree:
    def __init__(self, root):
        self.root = Path(root)
        self.modules = {}
        for path in sorted(self.root.rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            try:
                self.modules[path.relative_to(self.root).as_posix()] = (source, ast.parse(source))
            except SyntaxError:
                continue

    def locate(self, selector):
        """(path, target, relocated) for a selector, or None. A symbol that is not where the
        selector says is accepted elsewhere only when exactly one file defines that chain."""
        path, _, chain = selector.partition("::")
        parts = [p for p in chain.split(".") if p]
        if path in self.modules:
            module = self.modules[path][1]
            target = find(module, parts) if parts else ("symbol", module, None)
            if target:
                return path, target, False
        if not parts:
            return None
        elsewhere = [(other, find(module, parts)) for other, (_, module) in self.modules.items()
                     if other != path]
        elsewhere = [(other, target) for other, target in elsewhere if target]
        if len(elsewhere) == 1:
            return elsewhere[0][0], elsewhere[0][1], True
        return None


def short(node):
    text = " ".join(ast.unparse(node).split())
    return text if len(text) <= MAX_ITEM_CHARS else text[:MAX_ITEM_CHARS - 1] + "…"


def unique(items, limit):
    seen = list(dict.fromkeys(items))
    return seen[:limit] + ([f"… {len(seen) - limit} more"] if len(seen) > limit else [])


def reduce(source, target, reducer, arg):
    """Lines of text for a blank, or None when the reducer does not apply or finds nothing."""
    kind, node, default = target
    limit = MAX_ITEMS
    if kind == "parameter":
        if reducer != "value":
            return None
        note = f": {short(node.annotation)}" if node.annotation else ""
        return [node.arg + note + (f" = {short(default)}" if default is not None else "")]
    inner = sorted(ast.walk(node), key=position)
    if reducer == "value":
        if kind != "assignment":
            return None
        return [short(node.value)] if node.value is not None else [short(node)]
    if reducer == "signature":
        if isinstance(node, ast.ClassDef):
            bases = ", ".join(short(b) for b in node.bases)
            return [f"class {node.name}({bases})" if bases else f"class {node.name}"]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            returns = f" -> {short(node.returns)}" if node.returns else ""
            return [f"def {node.name}({ast.unparse(node.args)}){returns}"]
        return None
    if reducer in BLOCK_REDUCERS:
        segment = (ast.get_source_segment(source, node) if not isinstance(node, ast.Module)
                   else source) or ""
        lines = segment.splitlines()
        if reducer == "body":
            cap = min(int(arg or MAX_BODY_LINES), 40)
            return lines[:cap] + (["# … cut"] if len(lines) > cap else []) or None
        pattern = re.compile(arg)
        return unique([line.strip() for line in lines if pattern.search(line)], limit) or None
    if reducer == "members":
        if not isinstance(node, ast.ClassDef):
            return None
        return unique([short(s) for s in node.body
                       if isinstance(s, (ast.Assign, ast.AnnAssign))], 30) or None
    if reducer == "methods":
        if not isinstance(node, (ast.ClassDef, ast.Module)):
            return None
        return unique([s.name for s in node.body if isinstance(s, DEFS)], 30) or None
    if reducer == "decorators":
        return [short(d) for d in getattr(node, "decorator_list", [])] or None
    if reducer == "raises":
        return unique([short(n.exc) for n in inner
                       if isinstance(n, ast.Raise) and n.exc is not None], limit) or None
    if reducer == "calls":
        return unique([short(n.func) for n in inner if isinstance(n, ast.Call)], 30) or None
    if reducer == "returns":
        return unique([short(n.value) for n in inner
                       if isinstance(n, ast.Return) and n.value is not None], limit) or None
    if reducer == "strings":
        docstring = ast.get_docstring(node, clean=False) if isinstance(
            node, (*DEFS, ast.Module)) else None
        return unique([repr(n.value) for n in inner
                       if isinstance(n, ast.Constant) and isinstance(n.value, str)
                       and len(n.value) >= 3 and n.value != docstring], 20) or None
    if reducer == "keys":
        first = next((n for n in inner if isinstance(n, ast.Dict)), None)
        return unique([short(k) for k in first.keys if k is not None], 30) if first else None
    raise ValueError(f"unknown reducer {reducer!r}")


def fill(tree, frame):
    """(filled blanks, addresses, failures) for one frame against one tree."""
    values, addresses, failures = {}, [], []
    for name, blank in frame["blanks"].items():
        located = tree.locate(blank["at"])
        if located is None:
            failures.append((name, "not found"))
            continue
        path, target, relocated = located
        lines = reduce(tree.modules[path][0], target, blank["reduce"], blank.get("arg"))
        if not lines:
            failures.append((name, "empty"))
            continue
        chain = blank["at"].partition("::")[2]
        addresses.append(f"src/app/{path}:{position(target[1])[0] or 1}"
                         + (f" ({chain})" if chain else ""))
        values[name] = {"lines": lines, "block": blank["reduce"] in BLOCK_REDUCERS,
                        "relocated": relocated}
    return values, addresses, failures


def render(tree, frames):
    out, section = ["# Backend behaviour", ""], None
    stats = {"frames": len(frames), "frames_rendered": 0, "blanks": 0, "blanks_filled": 0,
             "blanks_relocated": 0, "failures": []}
    for frame in frames:
        if frame["section"] != section:
            section = frame["section"]
            out.extend([f"## {section}", ""])
        values, addresses, failures = fill(tree, frame)
        stats["blanks"] += len(frame["blanks"])
        stats["blanks_filled"] += len(values)
        stats["blanks_relocated"] += sum(v["relocated"] for v in values.values())
        if failures:
            stats["failures"].extend(
                {"at": frame["blanks"][name]["at"], "why": why} for name, why in failures)
            paths = sorted({"src/app/" + b["at"].partition("::")[0]
                            for b in frame["blanks"].values()
                            if b["at"].partition("::")[0] in tree.modules})
            if paths:
                out.append("- Look at: " + "; ".join(paths))
            continue
        stats["frames_rendered"] += 1
        blocks = []

        def substitute(match, values=values, blocks=blocks):
            value = values[match.group(1)]
            if value["block"]:
                blocks.append(value["lines"])
                return "(code below)"
            return ", ".join(f"`{item}`" for item in value["lines"])

        out.append("- " + BLANK.sub(substitute, frame["text"])
                   + " [" + "; ".join(dict.fromkeys(addresses)) + "]")
        for block in blocks:
            out.extend(["  ```", *("  " + line for line in block), "  ```"])
    out.append("")
    text = "\n".join(out)
    stats["words"] = len(text.split())
    return text, stats


def check(tree, frames):
    problems = []
    for number, frame in enumerate(frames, 1):
        for reason in lint(frame["text"]):
            problems.append(f"frame {number}: sentence carries a fact outside its blanks ({reason})")
        used = set(BLANK.findall(frame["text"]))
        if not used:
            problems.append(f"frame {number}: no blank, so the sentence states nothing checkable")
        if used != set(frame["blanks"]):
            problems.append(f"frame {number}: blanks in the sentence and in `blanks` differ")
            continue
        for name, why in fill(tree, frame)[2]:
            problems.append(f"frame {number}: blank {name} {why}: {frame['blanks'][name]['at']}")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["check", "render"])
    parser.add_argument("--tree", required=True)
    parser.add_argument("--frames", required=True)
    parser.add_argument("--out")
    parser.add_argument("--report")
    args = parser.parse_args()
    tree = Tree(args.tree)
    frames = json.loads(Path(args.frames).read_text(encoding="utf-8"))
    text, stats = render(tree, frames)
    if args.command == "check":
        problems = check(tree, frames)
        print("\n".join(problems) or "all frames pass")
        print(f"frames {stats['frames']}, blanks {stats['blanks']}, rendered words {stats['words']}")
        sys.exit(1 if problems else 0)
    Path(args.out).write_text(text, encoding="utf-8")
    if args.report:
        Path(args.report).write_text(json.dumps(stats, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "failures"}))


if __name__ == "__main__":
    main()
