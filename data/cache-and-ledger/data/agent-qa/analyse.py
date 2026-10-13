"""Summaries with uncertainty for the agent question-answering runs.

Unit of analysis: the question. Each cell (arm, condition, question group) is the mean over its
questions of the per-question mean over repetitions; intervals are percentile bootstrap over
questions (2,000 resamples). Differences are paired by question against a reference condition.

usage: analyse.py <work-dir> <questions.json> <out.json>
"""
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

GROUPS = {"structural": ("stable", "changed"), "stable": ("stable",), "changed": ("changed",),
          "decision": ("decision",)}
METRICS = ("correct", "outdated", "tool_calls", "prompt_tokens", "output_tokens", "cost_usd")


def load(work, questions):
    rows = defaultdict(lambda: defaultdict(list))  # (arm, condition) -> question -> [metrics]
    for path in sorted((work / "runs").glob("*.json")):
        judged = work / "judged" / path.name
        if not judged.exists():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        verdict = json.loads(judged.read_text(encoding="utf-8"))
        usage = record["usage"]
        stance_path = work / "stance" / path.name
        stance = (json.loads(stance_path.read_text(encoding="utf-8")).get("stance")
                  if stance_path.exists() else None)
        rows[(record["regime"], record["condition"])][record["question_id"]].append({
            "stance": stance,
            "correct": float(verdict["correct"]),
            "outdated": float(bool(verdict.get("states_old_answer"))),
            "tool_calls": float(len(record["tool_calls"])),
            "prompt_tokens": float(usage["input"] + usage["cache_write"] + usage["cache_read"]),
            "output_tokens": float(usage["output"]),
            "cost_usd": record["cost_usd"],
        })
    return rows


def per_question(cell, metric, ids):
    return {q: statistics.mean(r[metric] for r in cell[q]) for q in ids if q in cell}


def interval(values, rng, resamples=2000):
    if len(values) < 2:
        return None
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(resamples))
    return [round(means[int(0.025 * resamples)], 4), round(means[int(0.975 * resamples) - 1], 4)]


def main(argv):
    work, questions_path, out_path = Path(argv[0]), Path(argv[1]), Path(argv[2])
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    rows = load(work, questions)
    rng = random.Random(0)
    report = {}
    for (arm, condition), cell in sorted(rows.items()):
        reference = rows.get((arm, "none"), {})
        entry = {}
        for group, classes in GROUPS.items():
            ids = [q["id"] for q in questions if q["class"] in classes]
            present = [q for q in ids if q in cell]
            if not present:
                continue
            summary = {"questions": len(present),
                       "runs": sum(len(cell[q]) for q in present)}
            for metric in METRICS:
                values = list(per_question(cell, metric, present).values())
                summary[metric] = round(statistics.mean(values), 5)
                if metric in ("correct", "tool_calls", "prompt_tokens", "cost_usd"):
                    summary[metric + "_ci"] = interval(values, rng)
            stances = [r["stance"] for q in present for r in cell[q] if r["stance"]]
            if stances:
                summary["stance_share"] = {
                    name: round(stances.count(name) / len(stances), 4)
                    for name in ("current", "outdated_asserted", "outdated_with_doubt",
                                 "abstained", "other")}
            if condition != "none" and reference:
                paired = [q for q in present if q in reference]
                for metric in ("correct", "tool_calls", "cost_usd"):
                    mine = per_question(cell, metric, paired)
                    base = per_question(reference, metric, paired)
                    diffs = [mine[q] - base[q] for q in paired]
                    if diffs:
                        summary[f"{metric}_minus_none"] = round(statistics.mean(diffs), 5)
                        summary[f"{metric}_minus_none_ci"] = interval(diffs, rng)
            entry[group] = summary
        report.setdefault(arm, {})[condition] = entry
    out_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for arm, conditions in report.items():
        print(f"\n== {arm}")
        print(f"{'condition':15s} {'group':10s} {'n':>3s} {'correct':>8s} {'ci':>16s} {'outd':>5s} "
              f"{'calls':>6s} {'prompt':>8s} {'usd':>8s} {'Δcorrect vs none':>22s}")
        for condition, entry in conditions.items():
            for group in ("structural", "decision"):
                if group not in entry:
                    continue
                s = entry[group]
                delta = (f"{s['correct_minus_none']:+.3f} {s['correct_minus_none_ci']}"
                         if "correct_minus_none" in s else "")
                print(f"{condition:15s} {group:10s} {s['questions']:3d} {s['correct']:8.3f} "
                      f"{str(s['correct_ci']):>16s} {s['outdated']:5.3f} {s['tool_calls']:6.2f} "
                      f"{s['prompt_tokens']:8.0f} {s['cost_usd']:8.5f} {delta:>22s}")


if __name__ == "__main__":
    main(sys.argv[1:])
