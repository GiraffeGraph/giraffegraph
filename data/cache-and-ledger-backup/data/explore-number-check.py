"""Number check: can every number in a wiki page be found in a file that the page cites?

For each Markdown page, the numbers in its prose and tables are compared with the numbers in the
files it anchors (backticked workspace-relative paths that exist). A page number counts as traced
when a cited file holds the same value at the page's precision, directly or as a percentage of a
stored fraction. Untraced numbers are not necessarily wrong: they may be arithmetic on traced
values, or come from a source the page does not cite. They are the numbers no machine can vouch for.

usage: explore-number-check.py <workspace-root> <wiki-dir> [--skip PREFIX ...]
"""
import json
import re
import sys
from pathlib import Path

NUMBER = re.compile(r"(?<![\w./:-])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w-]|[./:]\w)")
ANCHOR = re.compile(r"`([^`\s]+)`")
SOURCE_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
MAX_SOURCE_BYTES = 3_000_000
SUFFIXES = {".json", ".md", ".py", ".csv", ".txt", ".jsonl", ".bib", ".toml"}


def page_numbers(text):
    """(value, decimals, raw) for numbers written the Turkish way: 1.688 is an integer, 0,923 a float."""
    found = []
    text = re.sub(r"`[^`]*`", " ", text)  # code spans: paths, ids, commands
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", text)  # dates
    for match in NUMBER.finditer(text):
        whole, fraction = match.group(1), match.group(2)
        integer = int(whole.replace(".", ""))
        if fraction is None:
            if integer < 20:
                continue  # small counts are everywhere and prove nothing
            found.append((float(integer), 0, match.group(0)))
        else:
            found.append((float(f"{integer}.{fraction}"), len(fraction), match.group(0)))
    return found


def numbers_in_json(node, out):
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        out.add(float(node))
    elif isinstance(node, str):
        for token in SOURCE_NUMBER.findall(node):
            out.add(float(token))
    elif isinstance(node, dict):
        for key, value in node.items():
            numbers_in_json(key, out)
            numbers_in_json(value, out)
    elif isinstance(node, list):
        for value in node:
            numbers_in_json(value, out)


def source_numbers(path):
    out = set()
    files = [path] if path.is_file() else [
        p for p in path.rglob("*") if p.is_file() and p.suffix in SUFFIXES]
    for file in files[:400]:
        if file.suffix not in SUFFIXES or file.stat().st_size > MAX_SOURCE_BYTES:
            continue
        text = file.read_text(encoding="utf-8", errors="replace")
        if file.suffix == ".json":
            try:
                numbers_in_json(json.loads(text), out)
                continue
            except json.JSONDecodeError:
                pass
        text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)  # 150,904 -> 150904
        for token in SOURCE_NUMBER.findall(text):
            out.add(float(token))
    return out


def traced(value, decimals, pool_exact, pool_rounded):
    if decimals == 0:
        return value in pool_exact or value in pool_rounded[0]
    key = round(value, decimals)
    return key in pool_rounded[decimals] or key in pool_rounded[("pct", decimals)]


def check_page(root, page):
    text = page.read_text(encoding="utf-8")
    anchors = set()
    for token in ANCHOR.findall(text):
        candidate = token.split(":")[0].rstrip(",.;")
        if "/" in candidate and "*" not in candidate and (root / candidate).exists():
            anchors.add(candidate)
    pool = set()
    for anchor in sorted(anchors):
        if anchor.endswith(".md") and anchor.startswith("wiki/") and "/sources/" not in anchor:
            continue  # another living page is not a source of truth for a number
        pool |= source_numbers(root / anchor)
    rounded = {0: {float(round(v)) for v in pool if abs(v) < 1e12}}
    for decimals in (1, 2, 3, 4):
        rounded[decimals] = {round(v, decimals) for v in pool}
        rounded[("pct", decimals)] = {round(v * 100, decimals) for v in pool if abs(v) <= 1}
    numbers = page_numbers(text)
    missing = [raw for value, decimals, raw in numbers
               if not traced(value, min(decimals, 4), pool, rounded)]
    return {"numbers": len(numbers), "traced": len(numbers) - len(missing),
            "cited_sources": len(anchors), "untraced": missing}


def main(argv):
    root, wiki = Path(argv[0]), Path(argv[1])
    skip = [argv[i + 1] for i, a in enumerate(argv) if a == "--skip"]
    report, total, traced_total = {}, 0, 0
    for page in sorted(wiki.rglob("*.md")):
        relative = str(page.relative_to(root))
        if any(relative.startswith(prefix) for prefix in skip):
            continue
        result = check_page(root, page)
        if result["numbers"]:
            report[relative] = result
            total += result["numbers"]
            traced_total += result["traced"]
    summary = {"pages_with_numbers": len(report), "numbers": total, "traced": traced_total,
               "share_traced": round(traced_total / total, 4) if total else None}
    json.dump({"summary": summary, "pages": report}, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
