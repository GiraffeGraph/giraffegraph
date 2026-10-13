"""Scholia: one-line notes placed inside the source tree an agent searches.

A note is a claim of at most 130 characters plus the symbols it is about. A sandbox gets the notes
either as one comment-only file at the top of the search root (`file`) or as comments directly above
the symbols (`woven`). Every note line starts with `#~ `, so a tool result that shows one can be
recognised afterwards. With `--only-valid` a note is kept only when each of its symbols has the same
source text in the tree the note was written from and in the tree it is placed in.

lines.json: [{"claim": "segmentation strategy: ...", "symbols": ["Service.method", "helper"]}]

usage: scholia.py check lines.json
       scholia.py build --lines lines.json --written-from APP_DIR --current APP_DIR
                        --base SANDBOX --out SANDBOX --form file|woven [--only-valid]
       scholia.py surfaced --work DIR --arm LABEL --condition NAME
"""
import argparse
import ast
import json
import shutil
import sys
from pathlib import Path

DEFS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
MARK = "#~ "
MAX_CLAIM = 130
NOTES_FILE = "_scholia.py"
HEADER = "# Notes on the behaviour of this code, one per line, each followed by where to look.\n"


def symbol_index(root):
    """qualified name -> [(path, first line, source text)] for every class and function."""
    index = {}
    for path in sorted(Path(root).rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        try:
            module = ast.parse(source)
        except SyntaxError:
            continue
        stack = [(module, "")]
        while stack:
            scope, prefix = stack.pop()
            for node in ast.iter_child_nodes(scope):
                if isinstance(node, DEFS):
                    name = prefix + node.name
                    first = min([node.lineno, *(d.lineno for d in node.decorator_list)])
                    index.setdefault(name, []).append(
                        (path.relative_to(root).as_posix(), first,
                         ast.get_source_segment(source, node)))
                    stack.append((node, name + "."))
    return index


def resolve(index, name):
    """The one symbol a name refers to: an exact qualified name, else a unique suffix of one."""
    name = name.strip().strip("`").removesuffix("()")
    hits = index.get(name) or [hit for qualified, found in index.items()
                               if qualified.endswith("." + name) for hit in found]
    return hits[0] if len(hits) == 1 else None


def place(notes, written_from, current, only_valid):
    """[(claim, path, line)] for the notes that are shown; path is None for a note without an
    anchor in the current tree."""
    placed, stats = [], {"notes": len(notes), "anchored": 0, "valid": 0, "shown": 0}
    for note in notes:
        before = [resolve(written_from, s) for s in note["symbols"]]
        after = [resolve(current, s) for s in note["symbols"]]
        anchored = bool(before) and all(before)
        valid = anchored and all(a and a[2] == b[2] for a, b in zip(after, before))
        stats["anchored"] += anchored
        stats["valid"] += valid
        if only_valid and not valid:
            continue
        first = next((a for a in after if a), None)
        placed.append((note["claim"], *(first[:2] if first else (None, None))))
    stats["shown"] = len(placed)
    return placed, stats


def build(args):
    notes = json.loads(Path(args.lines).read_text(encoding="utf-8"))
    placed, stats = place(notes, symbol_index(args.written_from), symbol_index(args.current),
                          args.only_valid)
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(args.base, out)
    app = out / "src" / "app"
    loose = [(claim, path, line) for claim, path, line in placed
             if args.form == "file" or path is None]
    if args.form == "woven":
        by_file = {}
        for claim, path, line in placed:
            if path is not None:
                by_file.setdefault(path, []).append((line, claim))
        for path, items in by_file.items():
            lines = (app / path).read_text(encoding="utf-8").split("\n")
            for line, claim in sorted(items, reverse=True):
                indent = lines[line - 1][:len(lines[line - 1]) - len(lines[line - 1].lstrip())]
                lines.insert(line - 1, f"{indent}{MARK}{claim}")
            (app / path).write_text("\n".join(lines), encoding="utf-8")
    if loose:
        body = "".join(f"{MARK}{claim}" + (f" @src/app/{path}:{line}" if path else "") + "\n"
                       for claim, path, line in loose)
        (app / NOTES_FILE).write_text(HEADER + body, encoding="utf-8")
    stats["in_notes_file"] = len(loose)
    print(json.dumps({"sandbox": out.name, **stats}))


def check(args):
    notes = json.loads(Path(args.lines).read_text(encoding="utf-8"))
    problems = [f"note {n}: claim has {len(note['claim'])} characters"
                for n, note in enumerate(notes, 1) if len(note["claim"]) > MAX_CLAIM]
    problems += [f"note {n}: claim spans several lines"
                 for n, note in enumerate(notes, 1) if "\n" in note["claim"]]
    print("\n".join(problems) or "all notes pass")
    print(f"notes {len(notes)}, words {sum(len(note['claim'].split()) for note in notes)}")
    sys.exit(1 if problems else 0)


def surfaced(args):
    """Replay the stored tool calls of an arm and count the runs in which a note was shown."""
    sys.path.insert(0, str(Path(__file__).parent))  # `python -I` leaves the script folder out
    from run_agent_qa import execute

    work = Path(args.work)
    root = work / "sandbox" / args.condition
    runs = sorted((work / "runs").glob(f"{args.arm}__{args.condition}__*.json"))
    shown = opened = 0
    for path in runs:
        calls = json.loads(path.read_text(encoding="utf-8"))["tool_calls"]
        shown += any(MARK in execute(root, call["tool"], call["input"]) for call in calls)
        opened += any(call["tool"] == "read_file" and NOTES_FILE in str(call["input"].get("path"))
                      for call in calls)
    print(json.dumps({"arm": args.arm, "condition": args.condition, "runs": len(runs),
                      "runs_showing_a_note": shown, "runs_reading_the_notes_file": opened}))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check")
    c.add_argument("lines")
    b = sub.add_parser("build")
    for name in ("lines", "written-from", "current", "base", "out"):
        b.add_argument(f"--{name}", required=True)
    b.add_argument("--form", choices=["file", "woven"], required=True)
    b.add_argument("--only-valid", action="store_true")
    s = sub.add_parser("surfaced")
    for name in ("work", "arm", "condition"):
        s.add_argument(f"--{name}", required=True)
    args = parser.parse_args()
    {"check": check, "build": build, "surfaced": surfaced}[args.command](args)


if __name__ == "__main__":
    main()
