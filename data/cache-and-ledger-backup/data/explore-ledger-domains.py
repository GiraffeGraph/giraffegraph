"""The same decision-ledger replay on labelled corpora from different domains.

A document is an ordered list of (surface string, gold identity). A human is asked once per unseen
key and the answer is reused. Keys: the string alone, or (previous string in the document, string).
Policies: both fixed keys; "hindsight" (strings known to be ambiguous use the pair key); and
"refine on audit" (a string switches to the pair key after a random audit contradicts a reuse).

Rates are given per decision opportunity and, for errors, also per reuse.

usage: explore-ledger-domains.py chains  <chains.jsonl>
       explore-ledger-domains.py pubtator <file.txt|file.txt.gz> [more files]
Options (after the paths): --first-per-document  count a string once per document
"""
import gzip
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict

SHUFFLES = 10


def read_chains(path):
    documents = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            documents.append(list(zip(row["mentions"], row["narrator_ids"])))
    return documents, 0


def read_pubtator(paths):
    documents, current, current_id, dropped = [], [], None, 0
    for path in paths:
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 6 or not parts[1].isdigit():
                    continue
                if parts[0] != current_id:
                    if current:
                        documents.append(current)
                    current, current_id = [], parts[0]
                identity = parts[5].strip()
                if identity in ("", "-1", "-"):
                    dropped += 1
                    continue
                current.append((parts[3], identity))
        if current:
            documents.append(current)
            current, current_id = [], None
    return documents, dropped


def first_per_document(documents):
    out = []
    for document in documents:
        seen, kept = set(), []
        for surface, identity in document:
            if surface not in seen:
                seen.add(surface)
                kept.append((surface, identity))
        out.append(kept)
    return out


def replay(documents, policy, rng):
    by_string, by_pair = {}, {}
    refined = set(policy.get("start", ()))
    fixed, eps = policy.get("key"), policy.get("eps", 0.0)
    total = sum(len(d) for d in documents)
    tail_from = int(total * 0.9)
    seen = questions = reuses = wrong = tail_questions = tail_wrong = 0
    curve_points = {int(total * f): None for f in (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0)}
    for document in documents:
        previous = None
        for surface, identity in document:
            pair = (previous, surface)
            previous = surface
            in_tail = seen >= tail_from
            seen += 1
            use_pair = fixed == "pair" or (fixed is None and surface in refined)
            stored = by_pair.get(pair) if use_pair else by_string.get(surface)
            audit = stored is not None and eps and rng.random() < eps
            if stored is None or audit:
                questions += 1
                tail_questions += in_tail
                if audit and stored != identity and fixed is None:
                    refined.add(surface)
                by_string.setdefault(surface, identity)
                by_pair.setdefault(pair, identity)
            else:
                reuses += 1
                if stored != identity:
                    wrong += 1
                    tail_wrong += in_tail
            if seen in curve_points:
                curve_points[seen] = questions
    tail = total - tail_from
    points = [(math.log(n), math.log(q)) for n, q in curve_points.items() if n and q]
    mean_x = statistics.mean(p[0] for p in points)
    mean_y = statistics.mean(p[1] for p in points)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sum(
        (x - mean_x) ** 2 for x, _ in points)
    return {
        "questions_per_opportunity": questions / total,
        "silent_wrong_per_opportunity": wrong / total,
        "silent_wrong_per_reuse": wrong / reuses if reuses else 0.0,
        "tail10_questions_per_opportunity": tail_questions / tail,
        "tail10_silent_wrong_per_opportunity": tail_wrong / tail,
        "growth_exponent": slope,
    }


def average(runs):
    return {key: round(statistics.mean(run[key] for run in runs), 4) for key in runs[0]}


def entropy(counter):
    total = sum(counter.values())
    return -sum(c / total * math.log2(c / total) for c in counter.values())


def describe(documents):
    identities, by_string = Counter(), defaultdict(Counter)
    for document in documents:
        for surface, identity in document:
            identities[identity] += 1
            by_string[surface][identity] += 1
    total = sum(identities.values())
    ambiguous = {s for s, c in by_string.items() if len(c) > 1}
    return {
        "documents": len(documents),
        "opportunities": total,
        "identities": len(identities),
        "strings": len(by_string),
        "ambiguous_strings": len(ambiguous),
        "share_of_strings_ambiguous": round(len(ambiguous) / len(by_string), 4),
        "share_of_opportunities_under_ambiguous_strings": round(
            sum(sum(by_string[s].values()) for s in ambiguous) / total, 4),
        "bits_to_name_an_identity": round(entropy(identities), 3),
        "bits_left_after_the_string_plug_in": round(
            sum(sum(c.values()) / total * entropy(c) for c in by_string.values()), 3),
    }, ambiguous


def run(documents):
    summary, ambiguous = describe(documents)
    policies = {
        "fixed: string": {"key": "string"},
        "fixed: previous+string": {"key": "pair"},
        "hindsight: ambiguous strings use previous+string": {"start": ambiguous},
        "refine on audit, eps=0.05": {"eps": 0.05},
        "refine on audit, eps=0.10": {"eps": 0.10},
    }
    out = {"corpus": summary, "random_order": {}, "file_order": {}}
    for name, policy in policies.items():
        runs = []
        for seed in range(SHUFFLES):
            order = documents[:]
            random.Random(seed).shuffle(order)
            runs.append(replay(order, policy, random.Random(1000 + seed)))
        out["random_order"][name] = average(runs)
        out["file_order"][name] = average(
            [replay(documents, policy, random.Random(1000 + seed)) for seed in range(SHUFFLES)])
    return out


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    kind, paths = args[0], args[1:]
    documents, dropped = read_chains(paths[0]) if kind == "chains" else read_pubtator(paths)
    report = {"source": paths, "mentions_without_identity_dropped": dropped}
    if "--first-per-document" in flags:
        documents = first_per_document(documents)
        report["counting"] = "each string once per document"
    else:
        report["counting"] = "every mention"
    report.update(run(documents))
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
