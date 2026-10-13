"""Label sanity report for an evaluation set built by build_sixbooks_fresh.py.

Reads hadiths.json, reference.jsonl and reference_chains.jsonl from the set
directory and writes label_checks.json and spotcheck.md there. The
normalisation is the local reimplementation in common.py; nothing is imported
from the scorer.

Usage:
  python3 -I data/scripts/label_checks.py data/eval/sixbooks-fresh
"""
import json
import os
import random
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SEED, normalise, write_json  # noqa: E402

SPOTCHECK_SIZE = 10


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def distribution(values):
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "median": statistics.median(ordered),
        "mean": round(statistics.fmean(ordered), 3),
        "max": ordered[-1],
        "histogram": {str(k): v for k, v in sorted(Counter(ordered).items())},
    }


def main(argv):
    set_dir = argv[1]
    with open(os.path.join(set_dir, "hadiths.json"), encoding="utf-8") as fh:
        hadiths = json.load(fh)
    reference = {r["hadith_id"]: r["mentions"] for r in read_jsonl(os.path.join(set_dir, "reference.jsonl"))}
    chains = {r["hadith_id"]: r for r in read_jsonl(os.path.join(set_dir, "reference_chains.jsonl"))}

    ids = [f"{h['coll']}:{h['num']}" for h in hadiths]
    totals = Counter()
    per_coll = {}
    not_verbatim = []
    for hadith, hid in zip(hadiths, ids):
        text = normalise(hadith["raw"])
        mentions = reference[hid]
        coll = per_coll.setdefault(hadith["coll"], Counter())
        cursor, in_order = 0, True
        for mention in mentions:
            norm = normalise(mention)
            found = bool(norm) and norm in text
            totals["mentions"] += 1
            totals["verbatim"] += found
            coll["mentions"] += 1
            coll["verbatim"] += found
            if not found:
                not_verbatim.append({"hadith_id": hid, "mention": mention})
            position = text.find(norm, cursor) if norm else -1
            if position < 0:
                in_order = False
            else:
                cursor = position + len(norm)
        totals["hadiths_all_mentions_found_in_text_order"] += in_order
        coll["hadiths"] += 1
        coll["multi_chain"] += len(chains[hid]["chains"]) > 1
        totals["empty_mentions"] += sum(1 for m in mentions if not m.strip())
        totals["mentions_with_markup"] += sum(1 for m in mentions if "<" in m or ">" in m or "[" in m)

    chain_counts = [len(chains[hid]["chains"]) for hid in ids]
    multi = sum(1 for n in chain_counts if n > 1)
    report = {
        "set": os.path.basename(os.path.normpath(set_dir)),
        "hadiths": len(hadiths),
        "duplicate_hadith_ids": len(ids) - len(set(ids)),
        "reference_ids_equal_hadith_ids": sorted(reference) == sorted(ids),
        "mentions": totals["mentions"],
        "mentions_verbatim_in_text_after_normalisation": totals["verbatim"],
        "share_verbatim": round(totals["verbatim"] / totals["mentions"], 4),
        "mentions_not_verbatim": not_verbatim,
        "hadiths_all_mentions_found_in_text_order": totals["hadiths_all_mentions_found_in_text_order"],
        "empty_mentions": totals["empty_mentions"],
        "mentions_with_markup": totals["mentions_with_markup"],
        "mentions_per_hadith": distribution([len(reference[hid]) for hid in ids]),
        "text_chars": distribution([len(h["raw"]) for h in hadiths]) | {"histogram": None},
        "hadiths_with_more_than_one_chain": multi,
        "share_with_more_than_one_chain": round(multi / len(hadiths), 4),
        "chains_per_hadith": {str(k): v for k, v in sorted(Counter(chain_counts).items())},
        "chain_positions_with_a_mention": sum(len(c) for hid in ids for c in chains[hid]["chains"]),
        "mentions_outside_chains": sum(len(chains[hid]["mentions_outside_chains"]) for hid in ids),
        "hadiths_with_mentions_outside_chains": sum(1 for hid in ids if chains[hid]["mentions_outside_chains"]),
        "per_collection": {
            coll: {
                "hadiths": c["hadiths"],
                "mentions": c["mentions"],
                "share_verbatim": round(c["verbatim"] / c["mentions"], 4),
                "hadiths_with_more_than_one_chain": c["multi_chain"],
            }
            for coll, c in per_coll.items()
        },
    }
    del report["text_chars"]["histogram"]
    write_json(os.path.join(set_dir, "label_checks.json"), report)

    picked = random.Random(SEED).sample(range(len(hadiths)), min(SPOTCHECK_SIZE, len(hadiths)))
    lines = [
        "# Spot check",
        "",
        f"{len(picked)} hadiths drawn with seed {SEED} from `hadiths.json`, with their reference labels.",
        "",
    ]
    for n, index in enumerate(picked, start=1):
        hid = ids[index]
        entry = chains[hid]
        lines += [f"## {n}. {hid}", "", hadiths[index]["raw"], "", "Reference mentions (text order):", ""]
        lines += [f"{i}. {m}" for i, m in enumerate(reference[hid], start=1)]
        lines += ["", "Chains (compiler side first, narrator id in brackets):", ""]
        for c, (chain, chain_ids) in enumerate(zip(entry["chains"], entry["narrator_ids"]), start=1):
            lines.append(f"- chain {c}: " + " | ".join(f"{m} [{i}]" for m, i in zip(chain, chain_ids)))
        if entry["mentions_outside_chains"]:
            lines.append("- outside chains: " + " ؛ ".join(
                f"{m} [{i}]" for m, i in zip(entry["mentions_outside_chains"], entry["narrator_ids_outside_chains"])
            ))
        lines.append("")
    with open(os.path.join(set_dir, "spotcheck.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print({k: v for k, v in report.items() if k != "mentions_not_verbatim"})
    print("not verbatim:", not_verbatim[:10])


if __name__ == "__main__":
    main(sys.argv)
