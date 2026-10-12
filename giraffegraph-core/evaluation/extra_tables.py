"""Supplementary tables for a set of experiment runs.

For each run: loose-matching scores by collection, by number of reference chains and by number of
reference mentions; scores of the committed output only (hadiths whose run was blocked count as
zero mentions); how many errors a confidence threshold would send to review at each possible
threshold; and how many provider calls each hadith needed.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_experiment
import scorer

CRITERION = "M2"


def read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def summarise(items):
    total = scorer.aggregate(items)
    return {key: total[key] for key in ("tp", "fp", "fn", "precision", "recall", "f1")}


def grouped(items_by_hadith, key_function):
    groups = defaultdict(list)
    for hadith_id, item in items_by_hadith.items():
        groups[key_function(hadith_id)].append(item)
    return {
        name: {"hadiths": len(items), **summarise(items)} for name, items in sorted(groups.items())
    }


def mention_bin(count):
    if count <= 4:
        return "2-4"
    return "5-6" if count <= 6 else "7-11"


def confidence_thresholds(run_dir, reference):
    run = analyze_experiment.load_run(str(run_dir))
    labelled = [
        (record["confidence"], record["correct"], "value_not_in_quote" in record["reason_codes"])
        for record in analyze_experiment.mention_records(reference, run)
    ]
    total = len(labelled)
    wrong = sum(1 for _, correct, _ in labelled if not correct)
    rows = []
    for threshold in sorted(
        {confidence for confidence, _, _ in labelled if confidence is not None}
    ):
        below = [item for item in labelled if item[0] is not None and item[0] < threshold]
        if not below:
            continue
        rows.append(
            {
                "review_if_confidence_below": threshold,
                "mentions_sent_to_review": len(below),
                "share_of_mentions": len(below) / total,
                "wrong_mentions_among_them": sum(1 for _, correct, _ in below if not correct),
            }
        )
    flagged = [item for item in labelled if item[2]]
    return {
        "mentions": total,
        "wrong_mentions": wrong,
        "distinct_confidence_values": len({confidence for confidence, _, _ in labelled}),
        "by_threshold": rows,
        "value_not_in_quote_check": {
            "mentions_sent_to_review": len(flagged),
            "share_of_mentions": len(flagged) / total if total else None,
            "wrong_mentions_among_them": sum(1 for _, correct, _ in flagged if not correct),
        },
    }


def analyse(run_dir, reference, chain_counts):
    report = json.loads((run_dir / "run_report.json").read_text(encoding="utf-8"))
    proposed = {
        row["hadith_id"]: row["mentions"] for row in read_jsonl(run_dir / "system_proposed.jsonl")
    }
    validated = {
        row["hadith_id"]: row["mentions"] for row in read_jsonl(run_dir / "system_validated.jsonl")
    }
    blocked = set(report["runs"].get("blocked_hadith_ids", []))
    items = {
        hadith_id: scorer.score_hadith(mentions, proposed.get(hadith_id, []), CRITERION)
        for hadith_id, mentions in reference.items()
    }
    committed_items = [
        scorer.score_hadith(
            mentions, [] if hadith_id in blocked else validated.get(hadith_id, []), CRITERION
        )
        for hadith_id, mentions in reference.items()
    ]
    calls = Counter(call["hadith_id"] for call in read_jsonl(run_dir / "calls.jsonl"))
    result = {
        "condition": report.get("condition"),
        "model": report.get("model"),
        "backend": "in-memory",
        "by_collection": grouped(items, lambda hadith_id: hadith_id.split(":")[0]),
        "by_reference_mentions": grouped(
            items, lambda hadith_id: mention_bin(len(reference[hadith_id]))
        ),
        "committed_output_only": {
            "hadiths_committed": len(reference) - len(blocked & set(reference)),
            "hadiths_blocked": len(blocked & set(reference)),
            **summarise(committed_items),
        },
        "provider_calls_per_hadith": dict(sorted(Counter(calls.values()).items())),
        "hadiths_with_more_than_one_call": sum(1 for count in calls.values() if count > 1),
        "confidence_as_review_signal": confidence_thresholds(run_dir, reference),
    }
    if chain_counts:
        result["by_reference_chain_count"] = grouped(
            items, lambda hadith_id: "1 chain" if chain_counts[hadith_id] == 1 else "2+ chains"
        )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--reference-chains")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    reference = {row["hadith_id"]: row["mentions"] for row in read_jsonl(args.reference)}
    chain_counts = None
    if args.reference_chains:
        chain_counts = {
            row["hadith_id"]: len(row["chains"]) for row in read_jsonl(args.reference_chains)
        }
    output = {
        "criterion": CRITERION,
        "reference": args.reference,
        "runs": {Path(run).name: analyse(Path(run), reference, chain_counts) for run in args.runs},
    }
    Path(args.out).write_text(
        json.dumps(output, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
