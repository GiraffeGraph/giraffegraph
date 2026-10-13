"""When does stored documentation help, do nothing for, or mislead an LLM agent?

An agent (Claude Haiku, effort low) answers questions about a code tree with three read-only tools
(list_dir, read_file, grep). Conditions differ ONLY in the files placed in the sandbox's `docs/`
folder; the system prompt and tools are identical.

    none            docs/ holds a note that there is no documentation
    decisions       docs/decisions.md
    fresh           decisions + behaviour.md written from the current code
    fresh_witness   the same page; each section carries the result of an automatic witness check
    stale           decisions + behaviour.md written from an earlier commit
    stale_witness   the stale page; each section carries the result of an automatic witness check
    stale_generic   the stale page; each section carries the same generic "verify" note
    map_fresh       decisions + symbol_map.md generated from the current code
    map_stale       decisions + symbol_map.md generated from the earlier commit
    pointers_fresh  decisions + pointers.md: the fresh page's headings and cited slices, no claims
    pointers_stale  the same from the stale page

Two regimes: `pull` (the agent must open docs/ itself) and `push` (the docs are also placed in the
system prompt, the way agent context files are loaded).

A witness check compares the code slices a section cites (`Sources:` line) with the current tree:
a slice is unchanged when its exact text still occurs in the same file.

usage:
  run_agent_qa.py build   --earlier APP_DIR --current APP_DIR --doc-earlier F --doc-current F
                          --decisions F --work DIR
  run_agent_qa.py run     --work DIR --questions questions.json --env .env [--reps 2]
                          [--conditions a,b] [--limit N] [--max-usd 3.0]
  run_agent_qa.py judge   --work DIR --questions questions.json --env .env
  run_agent_qa.py report  --work DIR --questions questions.json --out results.json
"""

import argparse
import ast
import hashlib
import json
import re
import shutil
import statistics
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL = "claude-haiku-5-5"
PRICE = {"input": 0.10, "output": 0.50, "cache_write": 0.125, "cache_read": 0.01}  # USD per MTok
MAX_TOOL_CALLS = 14
CONDITIONS = ["none", "decisions", "fresh", "fresh_witness", "stale", "stale_witness",
              "stale_generic", "map_fresh", "map_stale", "pointers_fresh", "pointers_stale"]
SYSTEM = (
    "You answer one question about the Python code under `src/`. Use the tools to look things up. "
    "Documentation, if any, is in `docs/`{caveat}. Answer for the code as "
    "it is in `src/` now. When you are done, reply with the answer only, in at most 120 words, and "
    "state facts plainly. If you could not find out, say so."
)
CAVEAT = {"caveat": "; it may be incomplete or outdated", "plain": ""}
TOOLS = [
    {
        "name": "list_dir",
        "description": "List the entries of a directory in the sandbox (non-recursive).",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "e.g. 'docs' or 'src/app'"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": "Read lines of a text file. At most 200 lines are returned per call.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer", "description": "1-based, default 1"},
                "end_line": {"type": "integer", "description": "inclusive, default start+199"},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "grep",
        "description": "Search files under a path with a Python regular expression. Returns up to "
                       "40 matching lines as path:line:text.",
        "input_schema": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
            "required": ["pattern", "path"],
            "additionalProperties": False,
        },
    },
]
GENERIC_NOTE = "> Note: this section may be outdated. Verify against the code."
SOURCES = re.compile(r"^`?Sources:\s*(.+?)`?\s*$")
SLICE = re.compile(r"([\w./-]+\.py):(\d+)-(\d+)")


# ---------------------------------------------------------------- building the conditions


def symbol_map(app_dir):
    lines = ["# Symbol map", "", "Generated from the source tree: file, then top-level classes "
             "(with methods) and functions.", ""]
    for path in sorted(Path(app_dir).rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        names = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                           and not n.name.startswith("__")]
                names.append(f"class {node.name}" + (f" ({', '.join(methods)})" if methods else ""))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.append(f"def {node.name}")
        if names:
            lines.append(f"- `src/app/{path.relative_to(app_dir)}`: " + "; ".join(names))
    return "\n".join(lines) + "\n"


def witness_status(doc_text, written_from, current):
    """Per section: (heading, slices, unchanged). A slice is unchanged when its text, as it was in
    the tree the page was written from, still occurs verbatim in the same file of `current`."""
    sections, heading = [], None
    for line in doc_text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
        match = SOURCES.match(line.strip())
        if not (match and heading):
            continue
        changed, unchanged = [], []
        for path, start, end in SLICE.findall(match.group(1)):
            origin = Path(written_from) / path
            target = Path(current) / path
            same = False
            if origin.is_file() and target.is_file():
                lines = origin.read_text(encoding="utf-8").splitlines()[int(start) - 1:int(end)]
                text = "\n".join(lines)
                same = bool(text.strip()) and text in target.read_text(encoding="utf-8")
            (unchanged if same else changed).append(f"{path}:{start}-{end}")
        sections.append((heading, changed, unchanged))
    return sections


def with_notes(doc_text, note_for):
    out = []
    for line in doc_text.splitlines():
        out.append(line)
        if line.startswith("## "):
            out.extend(["", note_for(line[3:].strip()), ""])
    return "\n".join(out) + "\n"


def witness_note(status):
    by_heading = {heading: (changed, unchanged) for heading, changed, unchanged in status}

    def note(heading):
        changed, unchanged = by_heading.get(heading, ([], []))
        total = len(changed) + len(unchanged)
        if not total:
            return "> Witness check (automatic): this section cites no code slices."
        if not changed:
            return (f"> Witness check (automatic): all {total} code slices this section was "
                    "written from are unchanged in the current code.")
        return (f"> Witness check (automatic): {len(changed)} of the {total} code slices this "
                "section was written from have changed in the current code, so statements resting "
                "on them may be STALE. Changed: " + "; ".join(changed) + "."
                + (" Unchanged: " + "; ".join(unchanged) + "." if unchanged else ""))
    return note


def pointers_only(doc_text):
    """Keep the section headings and the cited code slices; drop every statement."""
    lines = ["# Where to look", "", "Code locations per topic. No description of behaviour.", ""]
    for line in doc_text.splitlines():
        if line.startswith("## "):
            lines.extend([line, ""])
        elif SOURCES.match(line.strip()):
            lines.extend([rooted(line).strip().replace("Sources:", "Look at:"), ""])
    return "\n".join(lines) + "\n"


def rooted(text):
    """Write the cited slices as sandbox paths, so an agent can open them as given."""
    return "\n".join(
        SLICE.sub(lambda m: f"src/app/{m.group(1)}:{m.group(2)}-{m.group(3)}", line)
        if "Sources:" in line or line.startswith("> Witness check") else line
        for line in text.splitlines()) + "\n"


def build(args):
    work = Path(args.work)
    stale_doc = Path(args.doc_earlier).read_text(encoding="utf-8")
    fresh_doc = Path(args.doc_current).read_text(encoding="utf-8")
    decisions = Path(args.decisions).read_text(encoding="utf-8")
    stale_status = witness_status(stale_doc, args.earlier, args.current)
    fresh_status = witness_status(fresh_doc, args.current, args.current)
    docs = {
        "none": {"README.md": "There is no documentation for this repository.\n"},
        "decisions": {"decisions.md": decisions},
        "fresh": {"decisions.md": decisions, "behaviour.md": fresh_doc},
        "fresh_witness": {"decisions.md": decisions,
                          "behaviour.md": with_notes(fresh_doc, witness_note(fresh_status))},
        "stale": {"decisions.md": decisions, "behaviour.md": stale_doc},
        "stale_witness": {"decisions.md": decisions,
                          "behaviour.md": with_notes(stale_doc, witness_note(stale_status))},
        "stale_generic": {"decisions.md": decisions,
                          "behaviour.md": with_notes(stale_doc, lambda _: GENERIC_NOTE)},
        "map_fresh": {"decisions.md": decisions, "symbol_map.md": symbol_map(args.current)},
        "map_stale": {"decisions.md": decisions, "symbol_map.md": symbol_map(args.earlier)},
        "pointers_fresh": {"decisions.md": decisions, "pointers.md": pointers_only(fresh_doc)},
        "pointers_stale": {"decisions.md": decisions, "pointers.md": pointers_only(stale_doc)},
    }
    for condition, files in docs.items():
        root = work / "sandbox" / condition
        if root.exists():
            shutil.rmtree(root)
        (root / "docs").mkdir(parents=True)
        shutil.copytree(args.current, root / "src" / "app",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for name, text in files.items():
            if args.rooted_paths and name == "behaviour.md":
                text = rooted(text)
            (root / "docs" / name).write_text(text, encoding="utf-8")
    summary = {
        "stale_page_sections": [
            {"section": h, "slices": len(c) + len(u), "unchanged": len(u)}
            for h, c, u in stale_status],
        "fresh_page_sections": [
            {"section": h, "slices": len(c) + len(u), "unchanged": len(u)}
            for h, c, u in fresh_status],
        "doc_words": {"stale": len(stale_doc.split()), "fresh": len(fresh_doc.split()),
                      "decisions": len(decisions.split())},
    }
    (work / "build.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


# ---------------------------------------------------------------- tools


def inside(root, path):
    target = (root / path).resolve()
    if root.resolve() not in (target, *target.parents):
        raise ValueError("path is outside the sandbox")
    return target


def execute(root, name, arguments):
    try:
        if name == "list_dir":
            target = inside(root, arguments["path"])
            if not target.is_dir():
                return "not a directory"
            return "\n".join(sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir()))
        if name == "read_file":
            target = inside(root, arguments["path"])
            if not target.is_file():
                return "no such file"
            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            start = max(int(arguments.get("start_line") or 1), 1)
            end = min(int(arguments.get("end_line") or start + 199), start + 199, len(lines))
            body = "\n".join(f"{n}\t{lines[n - 1]}" for n in range(start, end + 1))
            return f"[{arguments['path']} lines {start}-{end} of {len(lines)}]\n{body}"
        if name == "grep":
            target = inside(root, arguments["path"])
            pattern = re.compile(arguments["pattern"])
            files = [target] if target.is_file() else sorted(
                p for p in target.rglob("*") if p.is_file() and p.suffix in (".py", ".md"))
            hits = []
            for path in files:
                for number, line in enumerate(
                        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if pattern.search(line):
                        hits.append(f"{path.relative_to(root)}:{number}:{line.strip()[:200]}")
                        if len(hits) >= 40:
                            return "\n".join(hits) + "\n[more matches not shown]"
            return "\n".join(hits) or "no matches"
    except (ValueError, KeyError, re.error, OSError) as error:
        return f"error: {error}"
    return "unknown tool"


# ---------------------------------------------------------------- running the agent


def api_client(env_path):
    import anthropic

    for line in Path(env_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return anthropic.Anthropic(
                api_key=line.split("=", 1)[1].strip().strip('"').strip("'"), timeout=180)
    sys.exit("ANTHROPIC_API_KEY not found in the env file")


def usage_cost(usage):
    return (usage["input"] * PRICE["input"] + usage["output"] * PRICE["output"]
            + usage["cache_write"] * PRICE["cache_write"]
            + usage["cache_read"] * PRICE["cache_read"]) / 1e6


def system_prompt(root, regime, wording):
    base = SYSTEM.format(caveat=CAVEAT[wording])
    if regime == "pull":
        return base
    parts = [f"--- docs/{path.name} ---\n{path.read_text(encoding='utf-8')}"
             for path in sorted((root / "docs").iterdir())]
    return base + "\n\nThe contents of `docs/`:\n\n" + "\n\n".join(parts)


def answer_question(client, root, question, regime, wording="caveat", max_calls=MAX_TOOL_CALLS):
    messages = [{"role": "user", "content": question}]
    system = system_prompt(root, regime, wording)
    usage = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    calls, turns, answer, stop = [], 0, "", None
    while True:
        exhausted = len(calls) >= max_calls
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=system,
            tools=TOOLS,
            tool_choice={"type": "none"} if exhausted else {"type": "auto"},
            messages=messages,
            cache_control={"type": "ephemeral"},
            output_config={"effort": "low"},
        )
        turns += 1
        usage["input"] += response.usage.input_tokens
        usage["output"] += response.usage.output_tokens
        usage["cache_write"] += response.usage.cache_creation_input_tokens or 0
        usage["cache_read"] += response.usage.cache_read_input_tokens or 0
        stop = response.stop_reason
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if stop != "tool_use" or not tool_uses:
            answer = "\n".join(b.text for b in response.content if b.type == "text").strip()
            break
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in tool_uses:
            calls.append({"tool": block.name, "input": block.input})
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": execute(root, block.name, block.input)})
        if len(calls) >= max_calls:
            results.append({"type": "text", "text": "Tool budget used up. Give your answer now."})
        messages.append({"role": "user", "content": results})
    return {"answer": answer, "stop_reason": stop, "turns": turns, "tool_calls": calls,
            "usage": usage, "cost_usd": round(usage_cost(usage), 6)}


def run(args):
    work = Path(args.work)
    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    if args.limit:
        questions = questions[:args.limit]
    conditions = args.conditions.split(",") if args.conditions else CONDITIONS
    out_dir = work / "runs"
    out_dir.mkdir(exist_ok=True)
    client = api_client(args.env)
    if args.classes:
        questions = [q for q in questions if q["class"] in args.classes.split(",")]
    jobs = [(c, q, r) for r in range(args.reps) for q in questions for c in conditions]
    label = args.regime
    if args.wording != "caveat":
        label += "+" + args.wording
    if args.max_tool_calls != MAX_TOOL_CALLS:
        label += f"+budget{args.max_tool_calls}"
    if args.tag:
        label += "+" + args.tag
    spent = [0.0]

    def work_one(job):
        condition, question, rep = job
        path = out_dir / f"{label}__{condition}__{question['id']}__{rep}.json"
        if path.exists():
            return 0.0
        if spent[0] > args.max_usd:
            return 0.0
        try:
            record = answer_question(client, work / "sandbox" / condition, question["question"],
                                     args.regime, args.wording, args.max_tool_calls)
        except Exception as error:  # noqa: BLE001 - one failed run must not stop the batch
            print(f"failed {path.name}: {type(error).__name__}: {str(error)[:200]}", flush=True)
            return 0.0
        record.update({"regime": label, "condition": condition,
                       "question_id": question["id"], "rep": rep})
        path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        spent[0] += record["cost_usd"]
        return record["cost_usd"]

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        costs = list(pool.map(work_one, jobs))
    print(f"jobs {len(jobs)}, new spend USD {sum(costs):.4f}, files {len(list(out_dir.glob('*.json')))}")


# ---------------------------------------------------------------- judging

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["facts_present", "contradicts_key", "states_old_answer", "says_could_not_find"],
    "properties": {
        "facts_present": {"type": "array", "items": {"type": "boolean"}},
        "contradicts_key": {"type": "boolean"},
        "states_old_answer": {"type": "boolean"},
        "says_could_not_find": {"type": "boolean"},
    },
}
JUDGE_SYSTEM = (
    "You grade an answer against a key. Return JSON. `facts_present`: one boolean per required "
    "fact, in order, true only if the answer clearly states that fact (same meaning; wording may "
    "differ). `contradicts_key`: true if the answer asserts something that conflicts with the "
    "reference answer. `states_old_answer`: true if an outdated answer is given and the answer "
    "asserts it as the current behaviour (false when no outdated answer is given). "
    "`says_could_not_find`: true if the answer says it could not determine the result. Judge only "
    "what is written."
)


def judge(args):
    work = Path(args.work)
    questions = {q["id"]: q for q in json.loads(Path(args.questions).read_text(encoding="utf-8"))}
    client = api_client(args.env)
    out_dir = work / "judged"
    out_dir.mkdir(exist_ok=True)

    def judge_one(path):
        target = out_dir / path.name
        if target.exists():
            return 0.0
        record = json.loads(path.read_text(encoding="utf-8"))
        question = questions[record["question_id"]]
        prompt = json.dumps({
            "question": question["question"],
            "reference_answer": question["answer"],
            "required_facts": question["must_include"],
            "outdated_answer": question.get("old_answer"),
            "answer_to_grade": record["answer"],
        }, ensure_ascii=False, indent=1)
        key = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        response = client.messages.create(
            model=MODEL, max_tokens=2000, system=JUDGE_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": "low",
                           "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
        )
        text = next((b.text for b in response.content if b.type == "text"), "{}")
        try:
            verdict = json.loads(text)
        except json.JSONDecodeError:
            verdict = {"facts_present": [], "contradicts_key": False, "states_old_answer": False,
                       "says_could_not_find": False, "unparsed": True}
        facts = verdict.get("facts_present") or []
        verdict["correct"] = (len(facts) == len(question["must_include"]) and all(facts)
                              and not verdict.get("contradicts_key"))
        verdict["prompt_key"] = key
        target.write_text(json.dumps(verdict), encoding="utf-8")
        return (response.usage.input_tokens * PRICE["input"]
                + response.usage.output_tokens * PRICE["output"]) / 1e6

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        costs = list(pool.map(judge_one, sorted((work / "runs").glob("*.json"))))
    print(f"judged {len(costs)}, new spend USD {sum(costs):.4f}")


STANCE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["stance"],
    "properties": {"stance": {"type": "string", "enum": [
        "current", "outdated_asserted", "outdated_with_doubt", "abstained", "other"]}},
}
STANCE_SYSTEM = (
    "A question about a code base has a current answer and an outdated answer. Classify the given "
    "reply. `current`: it gives the current answer. `outdated_asserted`: it presents the outdated "
    "answer as how the code behaves, without saying it is unverified. `outdated_with_doubt`: it "
    "reports the outdated answer but says it could not verify it, or that the documentation it "
    "comes from may be stale. `abstained`: it says it could not find out and gives neither answer. "
    "`other`: anything else. Return JSON."
)


def stance(args):
    work = Path(args.work)
    questions = {q["id"]: q for q in json.loads(Path(args.questions).read_text(encoding="utf-8"))}
    client = api_client(args.env)
    out_dir = work / "stance"
    out_dir.mkdir(exist_ok=True)

    def one(path):
        target = out_dir / path.name
        record = json.loads(path.read_text(encoding="utf-8"))
        question = questions[record["question_id"]]
        if target.exists() or not question.get("old_answer"):
            return
        prompt = json.dumps({"question": question["question"],
                             "current_answer": question["answer"],
                             "outdated_answer": question["old_answer"],
                             "reply": record["answer"]}, ensure_ascii=False, indent=1)
        response = client.messages.create(
            model=MODEL, max_tokens=1000, system=STANCE_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": "low",
                           "format": {"type": "json_schema", "schema": STANCE_SCHEMA}})
        text = next((b.text for b in response.content if b.type == "text"), "{}")
        try:
            target.write_text(json.dumps(json.loads(text)), encoding="utf-8")
        except json.JSONDecodeError:
            target.write_text(json.dumps({"stance": "other", "unparsed": True}), encoding="utf-8")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(one, sorted((work / "runs").glob("*.json"))))
    print(f"stance files {len(list(out_dir.glob('*.json')))}")


# ---------------------------------------------------------------- reporting


def report(args):
    work = Path(args.work)
    questions = {q["id"]: q for q in json.loads(Path(args.questions).read_text(encoding="utf-8"))}
    cells = defaultdict(list)
    for path in sorted((work / "runs").glob("*.json")):
        judged = work / "judged" / path.name
        if not judged.exists():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        verdict = json.loads(judged.read_text(encoding="utf-8"))
        doc_reads = [c for c in record["tool_calls"]
                     if str(c["input"].get("path", "")).startswith("docs")]
        total_in = sum(record["usage"][k] for k in ("input", "cache_write", "cache_read"))
        cells[(f"{record['regime']}:{record['condition']}",
               questions[record["question_id"]]["class"])].append({
            "question_id": record["question_id"],
            "correct": verdict["correct"],
            "outdated": bool(verdict.get("states_old_answer")),
            "gave_up": bool(verdict.get("says_could_not_find")),
            "tool_calls": len(record["tool_calls"]),
            "doc_calls": len(doc_reads),
            "prompt_tokens": total_in,
            "output_tokens": record["usage"]["output"],
            "cost_usd": record["cost_usd"],
        })
    table = {}
    for (condition, klass), rows in sorted(cells.items()):
        by_question = defaultdict(list)
        for row in rows:
            by_question[row["question_id"]].append(row["correct"])
        table.setdefault(condition, {})[klass] = {
            "runs": len(rows),
            "questions": len(by_question),
            "correct": sum(r["correct"] for r in rows),
            "accuracy": round(statistics.mean(r["correct"] for r in rows), 4),
            "accuracy_mean_over_questions": round(
                statistics.mean(statistics.mean(v) for v in by_question.values()), 4),
            "gave_the_outdated_answer": sum(r["outdated"] for r in rows),
            "said_could_not_find": sum(r["gave_up"] for r in rows),
            "tool_calls_mean": round(statistics.mean(r["tool_calls"] for r in rows), 2),
            "doc_calls_mean": round(statistics.mean(r["doc_calls"] for r in rows), 2),
            "prompt_tokens_mean": round(statistics.mean(r["prompt_tokens"] for r in rows)),
            "output_tokens_mean": round(statistics.mean(r["output_tokens"] for r in rows)),
            "cost_usd_mean": round(statistics.mean(r["cost_usd"] for r in rows), 5),
        }
    result = {"model": MODEL, "effort": "low", "default_max_tool_calls": MAX_TOOL_CALLS, "table": table,
              "per_question": {
                  f"{c}|{k}": {r["question_id"]: None for r in rows}
                  for (c, k), rows in cells.items()}}
    per_question = defaultdict(lambda: defaultdict(list))
    for (condition, _), rows in cells.items():
        for row in rows:
            per_question[row["question_id"]][condition].append(int(row["correct"]))
    result["per_question"] = {q: {c: v for c, v in sorted(by.items())}
                              for q, by in sorted(per_question.items())}
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"{'condition':30s} {'class':9s} {'runs':>4s} {'acc':>6s} {'old':>4s} {'gaveup':>6s} "
          f"{'calls':>6s} {'docs':>5s} {'prompt':>8s} {'usd':>8s}")
    labels = sorted({key.split(":")[0] for key in table})
    for condition in [f"{label}:{c}" for label in labels for c in CONDITIONS]:
        for klass, row in table.get(condition, {}).items():
            print(f"{condition:30s} {klass:9s} {row['runs']:4d} {row['accuracy']:6.3f} "
                  f"{row['gave_the_outdated_answer']:4d} {row['said_could_not_find']:6d} "
                  f"{row['tool_calls_mean']:6.2f} {row['doc_calls_mean']:5.2f} "
                  f"{row['prompt_tokens_mean']:8d} {row['cost_usd_mean']:8.5f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    for name in ("earlier", "current", "doc-earlier", "doc-current", "decisions", "work"):
        b.add_argument(f"--{name}", required=True)
    b.add_argument("--rooted-paths", action="store_true",
                   help="cite code slices as src/app/... so they can be opened as written")
    r = sub.add_parser("run")
    r.add_argument("--work", required=True)
    r.add_argument("--questions", required=True)
    r.add_argument("--env", required=True)
    r.add_argument("--reps", type=int, default=2)
    r.add_argument("--regime", choices=["pull", "push"], required=True)
    r.add_argument("--wording", choices=sorted(CAVEAT), default="caveat")
    r.add_argument("--max-tool-calls", type=int, default=MAX_TOOL_CALLS)
    r.add_argument("--classes", help="comma-separated question classes to run")
    r.add_argument("--tag", help="suffix for the arm label, e.g. the docs variant in the sandbox")
    r.add_argument("--conditions")
    r.add_argument("--limit", type=int)
    r.add_argument("--workers", type=int, default=8)
    r.add_argument("--max-usd", type=float, default=3.0)
    j = sub.add_parser("judge")
    j.add_argument("--work", required=True)
    j.add_argument("--questions", required=True)
    j.add_argument("--env", required=True)
    j.add_argument("--workers", type=int, default=8)
    s = sub.add_parser("stance")
    s.add_argument("--work", required=True)
    s.add_argument("--questions", required=True)
    s.add_argument("--env", required=True)
    s.add_argument("--workers", type=int, default=8)
    p = sub.add_parser("report")
    p.add_argument("--work", required=True)
    p.add_argument("--questions", required=True)
    p.add_argument("--out", required=True)
    args = parser.parse_args()
    {"build": build, "run": run, "judge": judge, "stance": stance,
     "report": report}[args.command](args)


if __name__ == "__main__":
    main()
