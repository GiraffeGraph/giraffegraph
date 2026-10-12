"""Set B: Sanadset <NAR> labels for the sixbooks-fresh hadiths that also exist in Sanadset.

A fresh (Ifta) hadith is linked to the Sanadset record of the same collection
with the highest character-overlap ratio of the normalised texts; the link is
kept when the ratio is >= 0.9 (equal normalised texts have ratio 1.0). The
<NAR> labels were produced by regular expressions and text matching.

Usage:
  python3 -I data/scripts/build_sanadset_reference.py data/eval/sixbooks-fresh/hadiths.json \
      data/work/sanadset_sixbooks.jsonl data/eval/sixbooks-fresh
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import link_by_text, normalise_for_matching, write_json, write_jsonl  # noqa: E402


def main(argv):
    hadiths_path, sanadset_path, out_dir = argv[1], argv[2], argv[3]
    with open(hadiths_path, encoding="utf-8") as fh:
        hadiths = json.load(fh)
    sanadset = {}
    with open(sanadset_path, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            row["key"] = f"{row['coll']}:{row['num']}"
            sanadset[row["key"]] = row
    queries = [{"key": f"{h['coll']}:{h['num']}", "coll": h["coll"], "raw": h["raw"]} for h in hadiths]
    links = link_by_text(queries, list(sanadset.values()))

    reference, per_coll, equal_text = [], Counter(), 0
    raw_of = {q["key"]: q["raw"] for q in queries}
    for link in links:
        coll = link["key"].split(":", 1)[0]
        per_coll[coll + "_total"] += 1
        if not link["matched"]:
            continue
        per_coll[coll + "_matched"] += 1
        target = sanadset[link["best_candidate"]]
        equal_text += normalise_for_matching(raw_of[link["key"]]) == normalise_for_matching(target["raw"])
        reference.append({"hadith_id": link["key"], "mentions": target["mentions"]})
    write_jsonl(os.path.join(out_dir, "reference_sanadset.jsonl"), reference)
    report = {
        "rule": "best Sanadset record of the same collection; kept when ratio >= 0.9",
        "hadiths": len(links),
        "matched": len(reference),
        "match_rate": round(len(reference) / len(links), 4),
        "matched_with_equal_normalised_text": equal_text,
        "matched_with_zero_sanadset_mentions": sum(1 for r in reference if not r["mentions"]),
        "per_collection": {
            coll: {"total": per_coll[coll + "_total"], "matched": per_coll[coll + "_matched"]}
            for coll in sorted({k.rsplit("_", 1)[0] for k in per_coll})
        },
        "links": [
            {
                "hadith_id": link["key"],
                "sanadset_id": link["best_candidate"],
                "ratio": link["ratio"],
                "containment": link["containment"],
                "matched": link["matched"],
                "candidates_at_or_above_threshold": link["candidates_at_or_above_threshold"],
            }
            for link in links
        ],
    }
    write_json(os.path.join(out_dir, "sanadset_matches.json"), report)
    print({k: v for k, v in report.items() if k != "links"})


if __name__ == "__main__":
    main(sys.argv)
