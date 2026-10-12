"""Analyse one isnad experiment run against reference labels.

Reads the directory written by backend/scripts/run_isnad_experiment.py
(system_proposed.jsonl, system_validated.jsonl, candidates.jsonl, calls.jsonl,
run_report.json) and writes analysis.json and analysis.md. Standard library
only; the matching criteria come from scorer.py in this directory.

Evaluated hadiths are the reference hadiths the run processed. A reference
hadith the run did not receive, or did not process because it was stopped, is
left out and counted in `evaluated_hadiths`.

Gate table: every proposed Narrator mention is labelled correct (matched to a
reference mention by the scorer's M2 alignment) or wrong (unmatched). A mention
is flagged by a reason code when that code fired on its candidate node.
  errors caught   flagged and wrong        gate precision  caught / flagged
  false alarms    flagged and correct      gate recall     caught / wrong
  errors missed   not flagged and wrong

Usage:
  python evaluation/analyze_experiment.py --run <out-dir> --reference reference.jsonl
      [--bootstrap 2000] [--seed 0] --out <dir>
"""
import argparse
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scorer  # noqa: E402

ANY_GATE = "any gate"
CONFIDENCE_BINS = 10
GATE_CRITERION = "M2"


# -------------------------------------------------------------------------- I/O
def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def load_run(run_dir):
    with open(os.path.join(run_dir, "run_report.json"), encoding="utf-8") as fh:
        report = json.load(fh)
    return {
        "dir": run_dir,
        "report": report,
        "proposed": scorer.load_jsonl(os.path.join(run_dir, "system_proposed.jsonl")),
        "validated": scorer.load_jsonl(os.path.join(run_dir, "system_validated.jsonl")),
        "candidates": read_jsonl(os.path.join(run_dir, "candidates.jsonl")),
        "calls": read_jsonl(os.path.join(run_dir, "calls.jsonl")),
    }


def evaluated_reference(reference, run):
    """Reference restricted to the hadiths the run processed."""
    unknown = sorted(set(run["proposed"]) - set(reference))
    if unknown:
        raise ValueError(f"system hadith_id not in reference: {', '.join(unknown)}")
    evaluated = {h: mentions for h, mentions in reference.items() if h in run["proposed"]}
    if not evaluated:
        raise ValueError("the run processed no reference hadith")
    return evaluated


# ---------------------------------------------------------------------- mentions
def label_mentions(ref_mentions, sys_mentions, criterion=GATE_CRITERION):
    """Per system mention: True if the scorer's alignment matches it, False if not,
    None if it normalises to nothing (the scorer does not count such a mention)."""
    ref = [m for m in map(scorer.normalise, ref_mentions) if m]
    kept = [(i, m) for i, m in enumerate(map(scorer.normalise, sys_mentions)) if m]
    matched = {j for _, j in scorer.match(ref, [m for _, m in kept], criterion)}
    labels = [None] * len(sys_mentions)
    for position, (index, _) in enumerate(kept):
        labels[index] = position in matched
    return labels


def mention_records(reference, run):
    """One record per proposed Narrator mention that the scorer counts."""
    by_mention = {}
    for row in run["candidates"]:
        for index in row.get("mention_indexes", []):
            by_mention[(row["hadith_id"], index)] = row
    records = []
    for hadith_id in sorted(reference):
        mentions = run["proposed"][hadith_id]
        for index, correct in enumerate(label_mentions(reference[hadith_id], mentions)):
            if correct is None:
                continue
            candidate = by_mention.get((hadith_id, index))
            if candidate is None:
                raise ValueError(f"no candidate for mention {index} of {hadith_id}")
            records.append({
                "hadith_id": hadith_id,
                "mention": mentions[index],
                "correct": correct,
                "confidence": candidate["confidence"],
                "reason_codes": candidate["reason_codes"],
            })
    return records


# --------------------------------------------------------------------- gate table
def gate_row(gate, records, flagged):
    caught = sum(1 for r in records if flagged(r) and not r["correct"])
    false_alarms = sum(1 for r in records if flagged(r) and r["correct"])
    missed = sum(1 for r in records if not flagged(r) and not r["correct"])
    return {
        "gate": gate,
        "errors_caught": caught,
        "false_alarms": false_alarms,
        "errors_missed": missed,
        "precision": caught / (caught + false_alarms) if caught + false_alarms else None,
        "recall": caught / (caught + missed) if caught + missed else None,
    }


def gate_table(records):
    codes = sorted({code for r in records for code in r["reason_codes"]})
    rows = [gate_row(code, records, lambda r, code=code: code in r["reason_codes"]) for code in codes]
    rows.append(gate_row(ANY_GATE, records, lambda r: bool(r["reason_codes"])))
    return {
        "criterion": GATE_CRITERION,
        "mentions": len(records),
        "correct": sum(1 for r in records if r["correct"]),
        "wrong": sum(1 for r in records if not r["correct"]),
        "rows": rows,
    }


# --------------------------------------------------------------------- confidence
def auc(positive_scores, negative_scores):
    """Probability that a positive outranks a negative, ties counting one half."""
    if not positive_scores or not negative_scores:
        return None
    ordered = sorted([(s, 1) for s in positive_scores] + [(s, 0) for s in negative_scores])
    positive_rank_sum = 0.0
    start = 0
    while start < len(ordered):
        end = start
        while end < len(ordered) and ordered[end][0] == ordered[start][0]:
            end += 1
        midrank = (start + 1 + end) / 2  # mean of the 1-based ranks start+1 .. end
        positive_rank_sum += midrank * sum(label for _, label in ordered[start:end])
        start = end
    n_pos, n_neg = len(positive_scores), len(negative_scores)
    return (positive_rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def confidence_analysis(records):
    histogram = [
        {"from": b / CONFIDENCE_BINS, "to": (b + 1) / CONFIDENCE_BINS, "correct": 0, "wrong": 0}
        for b in range(CONFIDENCE_BINS)
    ]
    for r in records:
        b = min(int(r["confidence"] * CONFIDENCE_BINS), CONFIDENCE_BINS - 1)
        histogram[b]["correct" if r["correct"] else "wrong"] += 1
    return {
        "auc_correct_vs_wrong": auc(
            [r["confidence"] for r in records if r["correct"]],
            [r["confidence"] for r in records if not r["correct"]],
        ),
        "histogram": histogram,
    }


# ------------------------------------------------------------- workload and cost
def review_workload(run):
    hadith_ids = list(run["proposed"])
    in_review = {h: 0 for h in hadith_ids}
    for row in run["candidates"]:
        if row["status"] == "review":
            in_review[row["hadith_id"]] += 1
    open_items = {h["hadith_id"]: h["open_review_items"] for h in run["report"]["per_hadith"]}
    counts = [in_review[h] for h in hadith_ids]
    return {
        "hadiths": len(hadith_ids),
        "candidates_in_review": sum(counts),
        "candidates_in_review_per_hadith": {
            "mean": sum(counts) / len(counts),
            "median": statistics.median(counts),
            "max": max(counts),
        },
        "open_review_items": sum(open_items[h] for h in hadith_ids),
        "share_hadiths_without_review_items": (
            sum(1 for h in hadith_ids if open_items[h] == 0) / len(hadith_ids)
        ),
    }


def cost_summary(run):
    calls, n = run["calls"], len(run["proposed"])
    cost = sum(c["cost_usd"] for c in calls)
    tokens_in = sum(c["input_tokens"] for c in calls)
    tokens_out = sum(c["output_tokens"] for c in calls)
    return {
        "hadiths": n,
        "calls": len(calls),
        "cached_calls": sum(1 for c in calls if c["cached"]),
        "failed_calls": sum(1 for c in calls if c["error"] is not None),
        "refused_calls": sum(1 for c in calls if c["error_kind"] == "refusal"),
        "truncated_calls": sum(1 for c in calls if c["error_kind"] == "max_tokens"),
        # Priced from the tokens of every call, whether or not it was served from the cache.
        "cost_usd": cost,
        "cost_usd_per_hadith": cost / n,
        "cost_usd_per_1000_hadiths": 1000 * cost / n,
        "cost_usd_spent_by_this_run": run["report"]["cost_usd"],
        "input_tokens_per_hadith": tokens_in / n,
        "output_tokens_per_hadith": tokens_out / n,
        "calls_per_hadith": len(calls) / n,
    }


# ---------------------------------------------------------------------- analysis
def analyse(run, reference, n_boot=2000, seed=0):
    report = run["report"]
    evaluated = evaluated_reference(reference, run)
    records = mention_records(evaluated, run)
    return {
        "run": {
            "condition": report["condition"],
            "model": report["model"],
            "effort": report["effort"],
            "provider": report["provider"],
            "segmentation_strategy": report["segmentation_strategy"],
            "budget_stopped": report["budget_stopped"],
            "stop_reason": report["stop_reason"],
        },
        "evaluated_hadiths": {
            "reference": len(reference),
            "evaluated": len(evaluated),
            "processed_by_run": len(run["proposed"]),
            "not_processed_by_run": report["hadith_ids_not_processed"],
        },
        "scores": {
            "proposed": scorer.score(evaluated, run["proposed"], n_boot, seed),
            "validated": scorer.score(evaluated, run["validated"], n_boot, seed),
        },
        "gate_table": gate_table(records),
        "confidence": confidence_analysis(records),
        "review_workload": review_workload(run),
        "cost": cost_summary(run),
        "schema_proposals": report["schema_proposals"],
        "candidates_by_reason_code": report["candidates_by_reason_code"],
        "committed_fact_invariants": {
            "exact_quote": report["committed_fact_invariants"]["holds"],
            "quote_with_grounding_normalisation": report[
                "committed_fact_invariants_with_grounding_normalisation"
            ]["holds"],
        },
    }


# ---------------------------------------------------------------------- markdown
def fmt(value, digits=3):
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}f}"


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def with_ci(result, key):
    """A scorer metric with its bootstrap interval, when one was computed."""
    if result["ci95"] is None:
        return fmt(result[key])
    low, high = result["ci95"][key]
    return f"{fmt(result[key])} [{fmt(low)}, {fmt(high)}]"


def score_rows(scores):
    rows = []
    for output in ("proposed", "validated"):
        for criterion in scorer.CRITERIA:
            s = scores[output][criterion]
            rows.append([
                output, criterion, with_ci(s, "precision"), with_ci(s, "recall"), with_ci(s, "f1"),
                s["tp"], s["fp"], s["fn"], fmt(s["exact_chain_rate"]),
            ])
    return rows


def render_markdown(analysis):
    run, evaluated = analysis["run"], analysis["evaluated_hadiths"]
    gates, workload, cost = analysis["gate_table"], analysis["review_workload"], analysis["cost"]
    per_hadith = workload["candidates_in_review_per_hadith"]
    bootstrap = analysis["scores"]["proposed"]["bootstrap"]
    parts = [
        f"# Experiment analysis: {run['condition']}",
        table(
            ["condition", "model", "effort", "provider", "segmentation", "stopped"],
            [[run["condition"], run["model"] or "n/a", run["effort"] or "n/a", run["provider"],
              run["segmentation_strategy"], run["stop_reason"] or "no"]],
        ),
        f"Evaluated hadiths: {evaluated['evaluated']} of {evaluated['reference']} in the reference "
        f"(the run processed {evaluated['processed_by_run']}; "
        f"{len(evaluated['not_processed_by_run'])} were not processed because the run stopped).",
        "Scores are agreement with the supplied reference. Against rule-generated (silver) labels "
        "they compare systems with each other and are not accuracy.",
        "## 1. Scores",
        table(
            ["output", "criterion", "precision [95% CI]", "recall [95% CI]", "F1 [95% CI]",
             "TP", "FP", "FN", "exact-chain rate"],
            score_rows(analysis["scores"]),
        ),
        f"Intervals: percentile bootstrap over hadiths, {bootstrap['resamples']} resamples, "
        f"seed {bootstrap['seed']}.",
        "## 2. Gates as error detectors",
        f"{gates['mentions']} proposed Narrator mentions under {gates['criterion']}: "
        f"{gates['correct']} correct, {gates['wrong']} wrong.",
        table(
            ["gate", "errors caught", "false alarms", "errors missed", "precision", "recall"],
            [[r["gate"], r["errors_caught"], r["false_alarms"], r["errors_missed"],
              fmt(r["precision"]), fmt(r["recall"])] for r in gates["rows"]],
        ),
        "## 3. Model confidence and correctness",
        f"AUC (correct vs wrong mentions, ties count one half): "
        f"{fmt(analysis['confidence']['auc_correct_vs_wrong'])}",
        table(
            ["confidence", "correct", "wrong"],
            [[f"{b['from']:.1f}-{b['to']:.1f}", b["correct"], b["wrong"]]
             for b in analysis["confidence"]["histogram"]],
        ),
        "## 4. Review workload",
        table(
            ["hadiths", "candidates in review", "mean per hadith", "median per hadith",
             "max per hadith", "open review items", "share of hadiths without review items"],
            [[workload["hadiths"], workload["candidates_in_review"], fmt(per_hadith["mean"]),
              fmt(per_hadith["median"]), per_hadith["max"], workload["open_review_items"],
              fmt(workload["share_hadiths_without_review_items"])]],
        ),
        "## 5. Cost",
        table(
            ["calls", "cached", "failed", "refused", "truncated", "USD per hadith",
             "USD per 1,000 hadiths", "input tokens per hadith", "output tokens per hadith",
             "USD spent by this run"],
            [[cost["calls"], cost["cached_calls"], cost["failed_calls"], cost["refused_calls"],
              cost["truncated_calls"], fmt(cost["cost_usd_per_hadith"], 6),
              fmt(cost["cost_usd_per_1000_hadiths"], 4), fmt(cost["input_tokens_per_hadith"], 1),
              fmt(cost["output_tokens_per_hadith"], 1),
              fmt(cost["cost_usd_spent_by_this_run"], 6)]],
        ),
        "Cost is priced from the tokens of every call, including calls served from the response "
        "cache.",
        "## 6. Schema proposals and reason codes",
        table(
            ["reason code", "kind", "type", "property", "count"],
            [[p["reason_code"], p["kind"], p["type_name"], p["property_name"] or "", p["count"]]
             for p in analysis["schema_proposals"]] or [["none", "", "", "", 0]],
        ),
        table(
            ["candidate kind", "reason code", "candidates"],
            [[kind, code, count]
             for kind, counts in analysis["candidates_by_reason_code"].items()
             for code, count in counts.items()] or [["none", "", 0]],
        ),
        "Every committed fact has a quote found verbatim in its source segment and an acceptance "
        f"record: {fmt(analysis['committed_fact_invariants']['exact_quote'])}; with the "
        "grounding gate's text normalisation: "
        f"{fmt(analysis['committed_fact_invariants']['quote_with_grounding_normalisation'])}.",
    ]
    return "\n\n".join(parts) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Analyse one isnad experiment run.")
    ap.add_argument("--run", required=True, help="output directory of run_isnad_experiment.py")
    ap.add_argument("--reference", required=True, help="reference JSONL")
    ap.add_argument("--bootstrap", type=int, default=2000, help="bootstrap resamples (default 2000)")
    ap.add_argument("--seed", type=int, default=0, help="bootstrap seed (default 0)")
    ap.add_argument("--out", required=True, help="directory for analysis.json and analysis.md")
    args = ap.parse_args(argv)
    try:
        analysis = analyse(
            load_run(args.run), scorer.load_jsonl(args.reference), args.bootstrap, args.seed
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "analysis.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n")
    with open(os.path.join(args.out, "analysis.md"), "w", encoding="utf-8") as fh:
        fh.write(render_markdown(analysis))
    print(render_markdown(analysis))
    return 0


if __name__ == "__main__":
    sys.exit(main())
