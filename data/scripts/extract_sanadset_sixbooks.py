"""Compact view of the six canonical books in Sanadset 650K.

Each output line: collection key, book, hadith number, the text with tags
removed, and the <NAR> spans in text order with tags removed. The <NAR> spans
are the corpus' own labels, which its authors produced with regular
expressions and text matching.

Usage:
  python3 -I data/scripts/extract_sanadset_sixbooks.py \
      data/raw/sanadset-hf/train/sanadset.csv data/work/sanadset_sixbooks.jsonl
"""
import csv
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import COLLECTIONS, strip_tags  # noqa: E402

NAR_SPAN = re.compile(r"<NAR>(.*?)</NAR>", re.S)


def nar_mentions(tagged_text):
    """<NAR> spans in text order, tags stripped, empty spans dropped."""
    return [m for m in (strip_tags(span) for span in NAR_SPAN.findall(tagged_text)) if m]


def main(argv):
    csv_path, out_path = argv[1], argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    coll_of = {spec["sanadset_book"]: coll for coll, spec in COLLECTIONS.items()}
    csv.field_size_limit(1 << 30)
    counts, total_rows, books = Counter(), 0, set()
    with open(csv_path, encoding="utf-8", newline="") as fh, open(out_path, "w", encoding="utf-8") as out:
        reader = csv.DictReader(fh)
        for row in reader:
            total_rows += 1
            books.add(row["Book"])
            coll = coll_of.get(row["Book"])
            if coll is None:
                continue
            counts[coll] += 1
            out.write(json.dumps({
                "coll": coll,
                "book": row["Book"],
                "num": row["Num_hadith"],
                "raw": strip_tags(row["Hadith"]),
                "mentions": nar_mentions(row["Hadith"]),
                "sanad_length": row["Sanad_Length"],
            }, ensure_ascii=False) + "\n")
    report = {"csv_rows": total_rows, "distinct_books": len(books), "six_book_rows": dict(counts)}
    with open(os.path.splitext(out_path)[0] + ".counts.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(report)


if __name__ == "__main__":
    main(sys.argv)
