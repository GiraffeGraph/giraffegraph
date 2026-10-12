"""Set C: AR-Sanad real test chains and narrator table for identity (disambiguation) evaluation.

Reads `Large dataset/sanads.test` (one chain per line, mentions separated by
"[فاصل]"), `Large dataset/labels.test` (comma-separated narrator ids, same line)
and `Narrators data.csv`. Converts every test chain; nothing is sampled.

Usage:
  python3 -I data/scripts/build_ar_sanad_identity.py \
      data/raw/ar-sanad/extracted/Narrator-Disambiguation-main data/eval/ar-sanad-identity
"""
import csv
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import normalise, write_json, write_jsonl  # noqa: E402

SEPARATOR = "[فاصل]"
NARRATOR_COLUMNS = [
    "id", "name", "shuhra", "kunia", "death_year", "birth_year", "tabaqa", "Ibnhajar_rank", "zahabi_rank",
]


def read_lines(path):
    with open(path, encoding="utf-8", newline="") as fh:
        lines = fh.read().split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def ambiguity(name_to_ids):
    """Distribution of ids-per-name and the 20 names with most distinct ids."""
    sizes = Counter(len(ids) for ids in name_to_ids.values())
    top = sorted(name_to_ids.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:20]
    return {
        "distinct_names": len(name_to_ids),
        "names_with_one_id": sizes.get(1, 0),
        "names_with_more_than_one_id": sum(n for size, n in sizes.items() if size > 1),
        "ids_per_name_distribution": {str(size): n for size, n in sorted(sizes.items())},
        "top20": [{"name": name, "distinct_ids": len(ids)} for name, ids in top],
    }


def main(argv):
    source, out_dir = argv[1], argv[2]
    os.makedirs(out_dir, exist_ok=True)

    sanads = read_lines(os.path.join(source, "Large dataset", "sanads.test"))
    labels = read_lines(os.path.join(source, "Large dataset", "labels.test"))
    if len(sanads) != len(labels):
        raise SystemExit(f"line count differs: {len(sanads)} chains, {len(labels)} label lines")

    with open(os.path.join(source, "Narrators data.csv"), encoding="utf-8", newline="") as fh:
        narrators = list(csv.DictReader(fh))
    table_ids = [int(row["id"]) for row in narrators]

    chains, length_mismatch, empty_mentions = [], [], 0
    exact, normalised = defaultdict(set), defaultdict(set)
    ids_used, mention_total = set(), 0
    for line_no, (sanad, label) in enumerate(zip(sanads, labels), start=1):
        mentions = [m.strip() for m in sanad.split(SEPARATOR)]
        ids = [int(x) for x in label.split(",")] if label.strip() else []
        chain_id = f"test-{line_no:05d}"
        empty_mentions += sum(1 for m in mentions if not m)
        if len(mentions) != len(ids):
            length_mismatch.append(chain_id)
        else:
            for mention, narrator_id in zip(mentions, ids):
                exact[mention].add(narrator_id)
                normalised[normalise(mention)].add(narrator_id)
        ids_used.update(ids)
        mention_total += len(mentions)
        chains.append({"chain_id": chain_id, "mentions": mentions, "narrator_ids": ids})
    write_jsonl(os.path.join(out_dir, "chains.jsonl"), chains)

    with open(os.path.join(out_dir, "narrators.csv"), "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=NARRATOR_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(narrators)

    lengths = Counter(len(c["mentions"]) for c in chains)
    report = {
        "source_files": ["Large dataset/sanads.test", "Large dataset/labels.test", "Narrators data.csv"],
        "chains": len(chains),
        "mentions": mention_total,
        "empty_mentions": empty_mentions,
        "chains_where_mention_and_id_counts_differ": len(length_mismatch),
        "chain_ids_where_counts_differ": length_mismatch[:50],
        "chain_length_distribution": {str(k): v for k, v in sorted(lengths.items())},
        "distinct_narrator_ids_in_test_chains": len(ids_used),
        "test_ids_missing_from_narrator_table": sorted(ids_used - set(table_ids)),
        "narrator_table_rows": len(narrators),
        "narrator_table_distinct_ids": len(set(table_ids)),
        "narrator_table_columns_in_source": list(narrators[0].keys()),
        "narrator_table_columns_written": NARRATOR_COLUMNS,
        "narrator_table_non_missing": {
            col: sum(1 for row in narrators if row[col].strip() not in ("", "-")) for col in NARRATOR_COLUMNS
        },
        "ambiguity_exact_surface": ambiguity(exact),
        "ambiguity_normalised_surface": ambiguity(normalised),
    }
    write_json(os.path.join(out_dir, "stats.json"), report)
    summary = {k: v for k, v in report.items() if not k.startswith("ambiguity") and k != "chain_length_distribution"}
    print(summary)
    for key in ("ambiguity_exact_surface", "ambiguity_normalised_surface"):
        amb = report[key]
        print(key, {k: v for k, v in amb.items() if k != "top20"})
        for row in amb["top20"]:
            print("   ", row["distinct_ids"], row["name"])


if __name__ == "__main__":
    main(sys.argv)
