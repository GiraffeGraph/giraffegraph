"""Set A: 50 hadiths per canonical collection from the Ifta corpus, with platform narrator labels.

Eligibility (all must hold):
  - the record has at least 2 labelled narrator mentions (`names`),
  - the cleaned text is 100..3000 characters long,
  - the record is in the graph release with at least one chain (needed for
    narrator ids per chain position),
  - the text does not match any of the 50 pilot hadiths. The exclusion is
    deliberately wider than the 0.9 used for linking corpora: character-overlap
    ratio >= 0.8, or >= 0.8 of the shorter text covered by common blocks of at
    least 20 characters, so repeats and fragments of a pilot hadith go too.
Sampling: per collection, `random.Random(f"{SEED}:{coll}").sample` over the
eligible records sorted by mainId.

Reference conventions:
  - `reference.jsonl` lists every labelled mention once, in text order. Parallel
    chains written one after another therefore come out chain by chain, and a
    narrator shared by several chains but written once appears once. This is
    the order in which the system export lists mentions.
  - `reference_chains.jsonl` keeps one list per chain, compiler side first (the
    order an isnad is written in), with the narrator id of every mention.

Usage:
  python3 -I data/scripts/build_sixbooks_fresh.py data/work/ifta_sixbooks.jsonl \
      <pilot_sample.json> data/raw/ifta-kaggle data/eval/sixbooks-fresh
"""
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    COLLECTIONS, SEED, TextIndex, normalise_for_matching, sha256_of, write_json, write_jsonl,
)

PER_COLLECTION = 50
MIN_CHARS, MAX_CHARS = 100, 3000
MIN_MENTIONS = 2
PILOT_EXCLUSION_THRESHOLD = 0.8
PILOT_CANDIDATES = 25
# Catalogue ids 0, 1, 2 are not people: unidentified narrator, narrator without a biography, anonymous narrator.
PLACEHOLDER_IDS = {0, 1, 2}
SOURCE_DIRS = {
    "original": "corpus-original",
    "graph": "ifta-hadith-isnad-linked-graph-data",
    "nlp": "ifta-hadith-with-narrators-entities-and-relations",
}


def hadith_id(record):
    return f"{record['coll']}:{record['num']}"


def monotone_assignment(step_occurrences):
    """Pick one occurrence per step so that as many steps as possible follow text order.

    step_occurrences: per chain step, the sorted positions of its narrator id in
    `names`. Returns one position (or None) per step: the longest strictly
    increasing selection, preferring earlier positions on ties.
    """
    memo = {}

    def best(step, after):
        if step == len(step_occurrences):
            return ()
        key = (step, after)
        if key not in memo:
            options = [(None,) + best(step + 1, after)]
            options += [(p,) + best(step + 1, p) for p in step_occurrences[step] if p > after]
            memo[key] = max(
                options,
                key=lambda path: (sum(p is not None for p in path), [-p if p is not None else -10**9 for p in path]),
            )
        return memo[key]

    return list(best(0, -1))


def chains_from_compiler(record):
    """Map each chain step of the graph release to a mention occurrence in `names`.

    The graph release orders a chain from the earliest narrator to the compiler;
    the output is reversed, compiler side first, which is the order an isnad is
    written in. Occurrences are chosen so that as many steps as possible follow
    text order; a step that cannot (a name restated after the chain, say) takes
    its first occurrence not used by the chain and is counted. Steps whose
    narrator id has no mention in the text (the compiler, or narrators implied
    by "with this isnad") are left out and counted.
    Returns (chains, stats): chains = [[(name_index, narrator_id), ...], ...].
    """
    positions = {}
    for index, (_, _, narrator_id) in enumerate(record["names"]):
        positions.setdefault(narrator_id, []).append(index)
    chains, stats = [], Counter()
    for chain in record["graph_chains"]:
        ordered = [narrator_id for narrator_id, _ in reversed(chain)]
        stats["chains"] += 1
        stats["chain_steps"] += len(ordered)
        stats["compiler_steps_without_mention"] += ordered[0] not in positions
        stats["other_steps_without_mention"] += sum(1 for i in ordered[1:] if i not in positions)
        mentioned = [i for i in ordered if i in positions]
        picked = monotone_assignment([positions[i] for i in mentioned])
        used = {p for p in picked if p is not None}
        steps = []
        for narrator_id, position in zip(mentioned, picked):
            if position is None:
                stats["steps_out_of_text_order"] += 1
                free = [p for p in positions[narrator_id] if p not in used]
                position = free[0] if free else positions[narrator_id][0]
                used.add(position)
            steps.append((position, narrator_id))
        chains.append(steps)
    return chains, stats


def main(argv):
    compact_path, pilot_path, raw_dir, out_dir = argv[1], argv[2], argv[3], argv[4]
    os.makedirs(out_dir, exist_ok=True)

    by_coll = {coll: [] for coll in COLLECTIONS}
    with open(compact_path, encoding="utf-8") as fh:
        for line in fh:
            record = json.loads(line)
            by_coll[record["coll"]].append(record)
    with open(pilot_path, encoding="utf-8") as fh:
        pilot = json.load(fh)

    counts, sampled, pilot_exclusions = {}, [], []
    for coll, records in by_coll.items():
        stage = Counter(records=len(records))
        pool = []
        for record in records:
            ok_mentions = len(record["names"]) >= MIN_MENTIONS
            ok_length = MIN_CHARS <= len(record["raw"]) <= MAX_CHARS
            ok_graph = bool(record["graph_chains"])
            stage["with_at_least_2_mentions"] += ok_mentions
            stage["with_text_length_in_range"] += ok_length
            stage["in_graph_release_with_chain"] += ok_graph
            stage["mentions_and_length"] += ok_mentions and ok_length
            if ok_mentions and ok_length and ok_graph:
                pool.append(record)
        stage["eligible_before_pilot_exclusion"] = len(pool)

        index = TextIndex([(r["main_id"], normalise_for_matching(r["raw"])) for r in records])
        excluded = set()
        for item in pilot:
            if item["coll"] != coll:
                continue
            candidates = index.best(normalise_for_matching(item["raw"]), top_k=PILOT_CANDIDATES)
            for ratio, containment, main_id in candidates:
                if ratio >= PILOT_EXCLUSION_THRESHOLD or containment >= PILOT_EXCLUSION_THRESHOLD:
                    excluded.add(main_id)
                    pilot_exclusions.append({
                        "pilot_hadith_id": f"{item['coll']}:{item['num']}",
                        "ifta_main_id": main_id,
                        "ratio": round(ratio, 4),
                        "containment": round(containment, 4),
                    })
        stage["pilot_hadiths_in_collection"] = sum(1 for item in pilot if item["coll"] == coll)
        stage["records_matching_a_pilot_hadith"] = len(excluded)
        pool = sorted((r for r in pool if r["main_id"] not in excluded), key=lambda r: r["main_id"])
        stage["eligible"] = len(pool)
        drawn = random.Random(f"{SEED}:{coll}").sample(pool, min(PER_COLLECTION, len(pool)))
        stage["drawn"] = len(drawn)
        stage["eligible_in_nlp_benchmark_split"] = sum(1 for r in pool if r["nlp_split"])
        counts[coll] = dict(stage)
        sampled.extend(drawn)
        print(coll, dict(stage), flush=True)

    hadiths, reference, reference_chains, records_out = [], [], [], []
    chain_stats, flag_counts = Counter(), Counter()
    nlp_compared = nlp_equal = 0
    for record in sampled:
        record["num"] = f"ifta-{record['main_id']}"
        hid = hadith_id(record)
        mentions = [name[0] for name in record["names"]]
        ids = [name[2] for name in record["names"]]
        chains, stats = chains_from_compiler(record)
        chain_stats.update(stats)
        used = {index for chain in chains for index, _ in chain}
        outside = [i for i in range(len(mentions)) if i not in used]
        compilers = {chain[-1][0] for chain in record["graph_chains"]}
        compiler_mentions = sum(1 for narrator_id in ids if narrator_id in compilers)
        chain_stats["mentions"] += len(mentions)
        chain_stats["mentions_outside_chains"] += len(outside)
        chain_stats["mentions_of_the_compiler"] += compiler_mentions
        chain_stats["hadiths_with_a_mention_of_the_compiler"] += compiler_mentions > 0
        chain_stats["mentions_with_placeholder_id"] += sum(1 for i in ids if i in PLACEHOLDER_IDS)
        flag_counts.update(record["clean_flags"])

        if record["nlp_chain_of_names"] is not None:
            # The entities-and-relations release derives the same thing; compare surface forms.
            ours = [[record["names"][index][1] for index, _ in reversed(chain)] for chain in chains]
            nlp_compared += 1
            nlp_equal += ours == record["nlp_chain_of_names"]

        hadiths.append({"coll": record["coll"], "num": record["num"], "raw": record["raw"]})
        reference.append({"hadith_id": hid, "mentions": mentions})
        reference_chains.append({
            "hadith_id": hid,
            "chains": [[mentions[index] for index, _ in chain] for chain in chains],
            "narrator_ids": [[narrator_id for _, narrator_id in chain] for chain in chains],
            "mentions_outside_chains": [mentions[i] for i in outside],
            "narrator_ids_outside_chains": [ids[i] for i in outside],
        })
        records_out.append({
            "hadith_id": hid,
            "ifta_main_id": record["main_id"],
            "book": record["book"],
            "hadith_num_in_source": record["hadith_num"],
            "cleaning_applied": record["clean_flags"],
            "removed_chapter_heading": record["removed_heading"],
            "chains": len(chains),
            "mentions_of_the_compiler": compiler_mentions,
            "nlp_benchmark_split": record["nlp_split"],
        })

    write_json(os.path.join(out_dir, "hadiths.json"), hadiths)
    write_jsonl(os.path.join(out_dir, "reference.jsonl"), reference)
    write_jsonl(os.path.join(out_dir, "reference_chains.jsonl"), reference_chains)

    source_files = {}
    for release, directory in SOURCE_DIRS.items():
        for spec in COLLECTIONS.values():
            path = os.path.join(raw_dir, directory, spec["ifta_file"])
            source_files[f"{directory}/{spec['ifta_file']}"] = {
                "release": release, "bytes": os.path.getsize(path), "sha256": sha256_of(path),
            }
    write_json(os.path.join(out_dir, "provenance.json"), {
        "set": "sixbooks-fresh",
        "source": "Ifta Sunnah Hadith & Narrators data family (Kaggle, jehadoumer), six canonical books",
        "source_files": source_files,
        "fields_used": {
            "raw": "original corpus `hadith_text_diac`, cleaned (see cleaning)",
            "mentions": "original corpus `names[*][1]` (diacritised surface form), cleaned, in list order",
            "narrator ids": "original corpus `names[*][2]`",
            "chains": "graph release `chain_of_narrators` ([narrator_id, display string] per step)",
        },
        "cleaning": {
            "page_marker": "removed, e.g. [1/220]",
            "line_break": "line breaks and whitespace runs collapsed to one space",
            "print_number": "edition numbering removed, e.g. '15 - ', '99 (م) - ', '6 / 1 - ', '( 48 )'",
            "chapter_heading": "chapter title before the hadith's print number cut off; kept per record below",
            "leading_dash": "dash left at the start of an unnumbered record removed",
            "mention": "same rules, plus punctuation stripped from both ends",
            "sampled_hadiths_changed_by_rule": dict(flag_counts),
        },
        "id_scheme": "hadith_id = <coll>:ifta-<mainId>; mainId is the platform record id, not the print number",
        "seed": SEED,
        "sampling": "random.Random(f'{seed}:{coll}').sample(eligible sorted by mainId, 50)",
        "eligibility": {
            "min_mentions": MIN_MENTIONS,
            "text_chars": [MIN_CHARS, MAX_CHARS],
            "text_measured_on": "cleaned diacritised text as written to hadiths.json",
            "graph_release_with_chain": True,
            "pilot_exclusion": (
                f"ratio >= {PILOT_EXCLUSION_THRESHOLD} or containment >= {PILOT_EXCLUSION_THRESHOLD} "
                "against any pilot hadith of the same collection"
            ),
        },
        "counts_per_collection": counts,
        "pilot_exclusions": pilot_exclusions,
        "chain_mapping": {
            **dict(chain_stats),
            "sampled_hadiths_also_in_entities_release": nlp_compared,
            "of_those_chains_equal_to_its_chain_of_names": nlp_equal,
        },
        "records": records_out,
    })
    print("hadiths", len(hadiths), "mentions", sum(len(r["mentions"]) for r in reference))
    print("chain mapping", dict(chain_stats), "nlp compared", nlp_compared, "equal", nlp_equal)
    print("cleaning flags", dict(flag_counts), "pilot exclusions", len(pilot_exclusions))


if __name__ == "__main__":
    main(sys.argv)
