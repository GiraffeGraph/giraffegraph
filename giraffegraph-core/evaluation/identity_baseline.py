"""How well does a written name identify a narrator?

Reads a reference file with narrator ids per mention and reports what happens when mentions are
grouped by a string key instead of by the id: how many keys cover more than one person, how many
people are split over several keys, and pairwise and B-cubed precision and recall of the grouping.
"""

import argparse
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scorer import normalise

PLACEHOLDER_IDS = {0, 1, 2}


def exact_key(mention: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", mention).split()).casefold()


KEYS = {"exact_written_name": exact_key, "normalised_name": normalise}


def load_mentions(path):
    mentions = []
    skipped = 0
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            for chain, ids in zip(record["chains"], record["narrator_ids"]):
                for mention, narrator_id in zip(chain, ids):
                    if narrator_id is None or narrator_id in PLACEHOLDER_IDS:
                        skipped += 1
                        continue
                    mentions.append((record["hadith_id"], mention, narrator_id))
    return mentions, skipped


def pairs(count: int) -> int:
    return count * (count - 1) // 2


def ratio(numerator: int, denominator: int):
    return numerator / denominator if denominator else None


def f1(precision, recall):
    if not precision or not recall:
        return None
    return 2 * precision * recall / (precision + recall)


def evaluate(mentions, key_function):
    by_key = defaultdict(Counter)
    by_id = defaultdict(Counter)
    for _, mention, narrator_id in mentions:
        key = key_function(mention)
        by_key[key][narrator_id] += 1
        by_id[narrator_id][key] += 1

    same_key_pairs = sum(pairs(sum(ids.values())) for ids in by_key.values())
    same_id_pairs = sum(pairs(sum(keys.values())) for keys in by_id.values())
    both_pairs = sum(pairs(count) for ids in by_key.values() for count in ids.values())
    pair_precision = ratio(both_pairs, same_key_pairs)
    pair_recall = ratio(both_pairs, same_id_pairs)

    total = len(mentions)
    bcubed_precision = sum(
        count * count / sum(ids.values()) for ids in by_key.values() for count in ids.values()
    ) / total
    bcubed_recall = sum(
        count * count / sum(keys.values()) for keys in by_id.values() for count in keys.values()
    ) / total

    conflating = {key: ids for key, ids in by_key.items() if len(ids) > 1}
    split = {narrator_id: keys for narrator_id, keys in by_id.items() if len(keys) > 1}
    return {
        "mentions": total,
        "distinct_narrator_ids": len(by_id),
        "distinct_keys": len(by_key),
        "keys_covering_more_than_one_person": len(conflating),
        "share_of_keys_covering_more_than_one_person": ratio(len(conflating), len(by_key)),
        "mentions_under_such_keys": sum(sum(ids.values()) for ids in conflating.values()),
        "share_of_mentions_under_such_keys": ratio(
            sum(sum(ids.values()) for ids in conflating.values()), total
        ),
        "people_split_over_several_keys": len(split),
        "share_of_people_split_over_several_keys": ratio(len(split), len(by_id)),
        "pairwise": {
            "precision": pair_precision,
            "recall": pair_recall,
            "f1": f1(pair_precision, pair_recall),
            "same_key_pairs": same_key_pairs,
            "same_person_pairs": same_id_pairs,
            "pairs_in_both": both_pairs,
        },
        "bcubed": {
            "precision": bcubed_precision,
            "recall": bcubed_recall,
            "f1": f1(bcubed_precision, bcubed_recall),
        },
        "most_ambiguous_keys": [
            {"key": key, "people": len(ids), "mentions": sum(ids.values())}
            for key, ids in sorted(conflating.items(), key=lambda item: (-len(item[1]), item[0]))[
                :15
            ]
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-chains", required=True)
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    mentions, skipped = load_mentions(args.reference_chains)
    report = {
        "reference": args.reference_chains,
        "mentions_without_a_person_id_skipped": skipped,
        "keys": {name: evaluate(mentions, function) for name, function in KEYS.items()},
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
