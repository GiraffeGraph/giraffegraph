"""Compact per-hadith view of the six canonical books in the three Ifta Kaggle releases.

For every record of the six book files in the original corpus it writes one
JSON line with the cleaned text (chapter title cut off where the hadith's print
number separates it), the platform's narrator mentions (`names`) and,
where the record exists there, the id-linked chains of the graph release and
the derived fields of the entities-and-relations release.

Usage:
  python3 -I data/scripts/extract_ifta_sixbooks.py data/raw/ifta-kaggle data/work/ifta_sixbooks.jsonl
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import COLLECTIONS, clean_ifta_mention, clean_ifta_text  # noqa: E402

ORIGINAL = "corpus-original"
GRAPH = "ifta-hadith-isnad-linked-graph-data"
NLP = "ifta-hadith-with-narrators-entities-and-relations"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_split_ids(nlp_dir):
    split_of = {}
    for split in ("train", "val", "test"):
        with open(os.path.join(nlp_dir, f"{split}_mainids.txt"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    split_of[int(line)] = split
    return split_of


def main(argv):
    raw_dir, out_path = argv[1], argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    split_of = read_split_ids(os.path.join(raw_dir, NLP))
    totals = {}
    with open(out_path, "w", encoding="utf-8") as out:
        for coll, spec in COLLECTIONS.items():
            file_name = spec["ifta_file"]
            graph = {r["mainId"]: r for r in load(os.path.join(raw_dir, GRAPH, file_name))}
            nlp = {r["mainId"]: r for r in load(os.path.join(raw_dir, NLP, file_name))}
            original = load(os.path.join(raw_dir, ORIGINAL, file_name))
            counts = Counter(original=len(original), graph=len(graph), nlp=len(nlp))
            seen = set()
            for record in original:
                main_id = record["mainId"]
                if main_id in seen:
                    counts["duplicate_main_id"] += 1
                    continue
                seen.add(main_id)
                names = []
                for surface, surface_diac, narrator_id in record["names"]:
                    mention = clean_ifta_mention(surface_diac)
                    if mention:
                        names.append([mention, clean_ifta_mention(surface), narrator_id])
                    else:
                        counts["empty_name_after_cleaning"] += 1
                first = names[0] if names else (None, None)
                raw, flags, heading = clean_ifta_text(record["hadith_text_diac"], first[0])
                counts["chapter_heading_removed"] += bool(heading)
                graph_record = graph.get(main_id)
                nlp_record = nlp.get(main_id)
                row = {
                    "coll": coll,
                    "main_id": main_id,
                    "book": record["book"],
                    "hadith_num": record["hadith_num"],
                    "raw": raw,
                    "raw_plain": clean_ifta_text(record["hadith_text"], first[1])[0],
                    "clean_flags": flags,
                    "removed_heading": heading,
                    "names": names,
                    "chains_as_display_strings": record["chain_of_narrators"],
                    "graph_chains": graph_record["chain_of_narrators"] if graph_record else None,
                    "nlp_chain_of_names": nlp_record["chain_of_names"] if nlp_record else None,
                    "nlp_split": split_of.get(main_id),
                }
                counts["in_graph"] += graph_record is not None
                counts["in_nlp_file"] += nlp_record is not None
                counts["in_nlp_split"] += main_id in split_of
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
            counts["graph_ids_not_in_original"] = len(set(graph) - seen)
            totals[coll] = dict(counts)
            print(coll, dict(counts), flush=True)
    with open(os.path.splitext(out_path)[0] + ".counts.json", "w", encoding="utf-8") as fh:
        json.dump(totals, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main(sys.argv)
