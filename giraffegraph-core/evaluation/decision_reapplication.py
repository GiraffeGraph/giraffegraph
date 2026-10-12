"""If review decisions are keyed by content, how many survive a re-extraction?

A decision is taken on a candidate of run A. Run B extracts the same hadiths again with another
prompt, model or provider and produces new candidates with new ids. A decision can be re-applied
to a candidate of B only if both map to the same content-addressed target. This script reports, for
every ordered pair of runs, the share of B's narrator candidates whose target exists in A, under
three definitions of the target:

    name    (hadith, normalised name)
    quote   (hadith, normalised evidence quote)
    either  the name target or the quote target exists
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scorer import normalise


def narrator_targets(run_dir):
    """Per hadith: list of (name target, quote targets) for every proposed narrator candidate."""
    by_hadith = defaultdict(list)
    with open(Path(run_dir) / "candidates.jsonl", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["kind"] != "node" or row["type"] != "Narrator":
                continue
            quotes = frozenset(normalise(q) for q in row.get("evidence_quotes") or [] if q)
            by_hadith[row["hadith_id"]].append((normalise(row.get("name") or ""), quotes))
    return by_hadith


def reapplication(decided, extracted):
    """Share of the candidates in `extracted` whose target already exists in `decided`."""
    total = name_hits = quote_hits = either_hits = 0
    for hadith_id, candidates in extracted.items():
        known_names = {name for name, _ in decided.get(hadith_id, []) if name}
        known_quotes = set().union(*(quotes for _, quotes in decided.get(hadith_id, [])))
        for name, quotes in candidates:
            total += 1
            by_name = bool(name) and name in known_names
            by_quote = bool(quotes & known_quotes)
            name_hits += by_name
            quote_hits += by_quote
            either_hits += by_name or by_quote
    if not total:
        return {"candidates": 0}
    return {
        "candidates": total,
        "name": round(name_hits / total, 4),
        "quote": round(quote_hits / total, 4),
        "either": round(either_hits / total, 4),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    targets = {Path(run).name: narrator_targets(run) for run in args.runs}
    report = {
        "runs": {name: sum(len(v) for v in by_hadith.values())
                 for name, by_hadith in targets.items()},
        "decided_on -> re_extracted_with": {
            f"{a} -> {b}": reapplication(targets[a], targets[b])
            for a in targets for b in targets if a != b
        },
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
