"""Set D: the 50 pilot hadiths in the same layout as the other sets.

Writes hadiths.json (coll, num, raw), reference_sanadset.jsonl (the pilot's
Sanadset <NAR> labels with residual tags removed) and, for pilot hadiths whose
text links to an Ifta record (character-overlap ratio >= 0.9 in the same
collection), reference_ifta.jsonl with that record's platform mentions.

Usage:
  python3 -I data/scripts/build_pilot50.py <pilot_sample.json> data/work/ifta_sixbooks.jsonl data/eval/pilot50
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import link_by_text, strip_tags, write_json, write_jsonl  # noqa: E402


def main(argv):
    pilot_path, ifta_path, out_dir = argv[1], argv[2], argv[3]
    os.makedirs(out_dir, exist_ok=True)
    with open(pilot_path, encoding="utf-8") as fh:
        pilot = json.load(fh)

    hadiths = [{"coll": x["coll"], "num": x["num"], "raw": x["raw"]} for x in pilot]
    sanadset_reference = [
        {"hadith_id": f"{x['coll']}:{x['num']}", "mentions": [m for m in map(strip_tags, x["ref_nars"]) if m]}
        for x in pilot
    ]
    write_json(os.path.join(out_dir, "hadiths.json"), hadiths)
    write_jsonl(os.path.join(out_dir, "reference_sanadset.jsonl"), sanadset_reference)

    pilot_colls = {x["coll"] for x in pilot}
    ifta = {}
    with open(ifta_path, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row["coll"] in pilot_colls:
                ifta[row["main_id"]] = {
                    "key": row["main_id"], "coll": row["coll"], "raw": row["raw"],
                    "mentions": [name[0] for name in row["names"]],
                }
    queries = [{"key": f"{x['coll']}:{x['num']}", "coll": x["coll"], "raw": x["raw"]} for x in pilot]
    links = link_by_text(queries, list(ifta.values()))
    ifta_reference = [
        {"hadith_id": link["key"], "mentions": ifta[link["best_candidate"]]["mentions"]}
        for link in links if link["matched"]
    ]
    write_jsonl(os.path.join(out_dir, "reference_ifta.jsonl"), ifta_reference)

    per_coll = Counter()
    for link in links:
        coll = link["key"].split(":", 1)[0]
        per_coll[coll + "_total"] += 1
        per_coll[coll + "_matched"] += link["matched"]
    report = {
        "rule": "best Ifta record of the same collection; kept when ratio >= 0.9",
        "hadiths": len(pilot),
        "sanadset_mentions": sum(len(r["mentions"]) for r in sanadset_reference),
        "sanadset_mentions_that_carried_a_tag": sum(1 for x in pilot for m in x["ref_nars"] if "<" in m or ">" in m),
        "matched_to_ifta": len(ifta_reference),
        "match_rate": round(len(ifta_reference) / len(pilot), 4),
        "ifta_mentions_in_matched": sum(len(r["mentions"]) for r in ifta_reference),
        "matched_with_fewer_than_2_ifta_mentions": sum(1 for r in ifta_reference if len(r["mentions"]) < 2),
        "per_collection": {
            coll: {"total": per_coll[coll + "_total"], "matched": per_coll[coll + "_matched"]}
            for coll in sorted({k.rsplit("_", 1)[0] for k in per_coll})
        },
        "links": [
            {
                "hadith_id": link["key"],
                "ifta_main_id": link["best_candidate"],
                "ratio": link["ratio"],
                "containment": link["containment"],
                "matched": link["matched"],
            }
            for link in links
        ],
    }
    write_json(os.path.join(out_dir, "ifta_matches.json"), report)
    print({k: v for k, v in report.items() if k != "links"})


if __name__ == "__main__":
    main(sys.argv)
