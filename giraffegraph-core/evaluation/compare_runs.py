"""Compare isnad experiment runs against the same reference labels.

Writes one Markdown file: a table with a row per run, and paired bootstrap
differences in M2 precision, recall and F1 between runs. A run is named by its
directory name. Standard library only.

Each row is computed by analyze_experiment.py on the hadiths that run processed.
A paired difference uses the hadiths both runs processed; every resample draws
the same hadiths for both runs.

Usage:
  python evaluation/compare_runs.py --runs <dir> <dir> ... --reference reference.jsonl
      --out comparison.md [--pair <name> <name>]... [--bootstrap 2000] [--seed 0]

Without --pair, every pair of runs is compared.
"""
import argparse
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_experiment as analysis  # noqa: E402
import scorer  # noqa: E402

PAIRED_CRITERION = "M2"
METRICS = ("precision", "recall", "f1")


def run_name(run_dir):
    return os.path.basename(os.path.normpath(run_dir))


def paired_bootstrap(counts_a, counts_b, n_boot, seed):
    """Difference a - b in micro-averaged P, R, F1 with 95% percentile intervals.

    `counts_a` and `counts_b` hold one (tp, fp, fn) tuple per hadith, in the same
    hadith order.
    """
    if len(counts_a) != len(counts_b) or not counts_a:
        raise ValueError("paired runs need the same, non-empty list of hadiths")

    def metrics(counts, indexes):
        tp, fp, fn = (sum(counts[i][k] for i in indexes) for k in range(3))
        return dict(zip(METRICS, scorer.prf(tp, fp, fn)))

    n = len(counts_a)
    everything = range(n)
    observed_a, observed_b = metrics(counts_a, everything), metrics(counts_b, everything)
    rng = random.Random(seed)
    samples = {metric: [] for metric in METRICS}
    for _ in range(n_boot):
        indexes = [rng.randrange(n) for _ in range(n)]
        a, b = metrics(counts_a, indexes), metrics(counts_b, indexes)
        for metric in METRICS:
            samples[metric].append(a[metric] - b[metric])
    return {
        metric: {
            "a": observed_a[metric],
            "b": observed_b[metric],
            "difference": observed_a[metric] - observed_b[metric],
            "ci95": (
                [scorer.percentile(samples[metric], 2.5), scorer.percentile(samples[metric], 97.5)]
                if n_boot > 0 else None
            ),
        }
        for metric in METRICS
    }


def compare_pair(run_a, run_b, reference, n_boot, seed):
    """Paired differences over the reference hadiths both runs processed."""
    hadith_ids = sorted(set(reference) & set(run_a["proposed"]) & set(run_b["proposed"]))

    def counts(run):
        items = [
            scorer.score_hadith(reference[h], run["proposed"][h], PAIRED_CRITERION)
            for h in hadith_ids
        ]
        return [(item["tp"], item["fp"], item["fn"]) for item in items]

    return {
        "hadiths": len(hadith_ids),
        "metrics": paired_bootstrap(counts(run_a), counts(run_b), n_boot, seed),
    }


def summary_row(name, result):
    proposed, validated = result["scores"]["proposed"], result["scores"]["validated"]
    any_gate = next(r for r in result["gate_table"]["rows"] if r["gate"] == analysis.ANY_GATE)
    workload, cost = result["review_workload"], result["cost"]
    fmt = analysis.fmt
    return [
        name,
        result["run"]["condition"],
        result["run"]["model"] or "n/a",
        result["run"]["effort"] or "n/a",
        result["evaluated_hadiths"]["evaluated"],
        fmt(proposed["M1"]["f1"]),
        analysis.with_ci(proposed["M2"], "precision"),
        analysis.with_ci(proposed["M2"], "recall"),
        analysis.with_ci(proposed["M2"], "f1"),
        fmt(proposed["M2"]["exact_chain_rate"]),
        fmt(validated["M2"]["precision"]),
        fmt(validated["M2"]["recall"]),
        fmt(validated["M2"]["f1"]),
        fmt(any_gate["precision"]),
        fmt(any_gate["recall"]),
        fmt(result["confidence"]["auc_correct_vs_wrong"]),
        fmt(workload["candidates_in_review_per_hadith"]["mean"]),
        fmt(workload["share_hadiths_without_review_items"]),
        fmt(cost["cost_usd_per_1000_hadiths"], 4),
        fmt(cost["input_tokens_per_hadith"] + cost["output_tokens_per_hadith"], 1),
        cost["failed_calls"],
    ]


SUMMARY_HEADER = [
    "run", "condition", "model", "effort", "hadiths", "M1 F1",
    "M2 precision [95% CI]", "M2 recall [95% CI]", "M2 F1 [95% CI]", "exact-chain rate",
    "validated M2 precision", "validated M2 recall", "validated M2 F1",
    "any-gate precision", "any-gate recall", "confidence AUC",
    "review candidates per hadith", "share of hadiths without review items",
    "USD per 1,000 hadiths", "tokens per hadith", "failed calls",
]


def render(results, pairs, n_boot, seed):
    fmt = analysis.fmt
    parts = [
        "# Run comparison",
        "Scores are agreement with the supplied reference. Against rule-generated (silver) labels "
        "they compare systems with each other and are not accuracy.",
        analysis.table(SUMMARY_HEADER, [summary_row(name, r) for name, r in results.items()]),
    ]
    evaluated = {r["evaluated_hadiths"]["evaluated"] for r in results.values()}
    if len(evaluated) > 1:
        parts.append(
            "The runs were evaluated on different numbers of hadiths, so their rows are not "
            "directly comparable; the paired differences below use the shared hadiths only."
        )
    parts += [
        f"## Paired differences ({PAIRED_CRITERION}, proposed output)",
        f"Difference = first run minus second run. Intervals: paired percentile bootstrap over "
        f"hadiths, {n_boot} resamples, seed {seed}.",
        analysis.table(
            ["first run", "second run", "hadiths", "metric", "first value", "second value",
             "difference", "95% CI"],
            [
                [name_a, name_b, pair["hadiths"], metric, fmt(m["a"]), fmt(m["b"]),
                 fmt(m["difference"]),
                 "n/a" if m["ci95"] is None else f"[{fmt(m['ci95'][0])}, {fmt(m['ci95'][1])}]"]
                for (name_a, name_b), pair in pairs.items()
                for metric, m in pair["metrics"].items()
            ],
        ),
    ]
    return "\n\n".join(parts) + "\n"


def compare(run_dirs, reference, pair_names=None, n_boot=2000, seed=0):
    names = [run_name(run_dir) for run_dir in run_dirs]
    if len(set(names)) != len(names):
        raise ValueError("run directories need distinct names")
    runs = {name: analysis.load_run(run_dir) for name, run_dir in zip(names, run_dirs)}
    for name_a, name_b in pair_names or []:
        for name in (name_a, name_b):
            if name not in runs:
                raise ValueError(f"--pair names an unknown run: {name}")
    results = {name: analysis.analyse(run, reference, n_boot, seed) for name, run in runs.items()}
    pairs = {
        (name_a, name_b): compare_pair(runs[name_a], runs[name_b], reference, n_boot, seed)
        for name_a, name_b in pair_names or itertools.combinations(names, 2)
    }
    return results, pairs


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compare isnad experiment runs.")
    ap.add_argument("--runs", required=True, nargs="+", help="run output directories")
    ap.add_argument("--reference", required=True, help="reference JSONL")
    ap.add_argument("--out", required=True, help="Markdown file to write")
    ap.add_argument("--pair", nargs=2, action="append", metavar=("FIRST", "SECOND"),
                    help="compare these two runs (repeatable; default: every pair)")
    ap.add_argument("--bootstrap", type=int, default=2000, help="bootstrap resamples (default 2000)")
    ap.add_argument("--seed", type=int, default=0, help="bootstrap seed (default 0)")
    args = ap.parse_args(argv)
    try:
        results, pairs = compare(
            args.runs, scorer.load_jsonl(args.reference), args.pair, args.bootstrap, args.seed
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    text = render(results, pairs, args.bootstrap, args.seed)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
