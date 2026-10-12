"""Build the blind labelling sheet for human annotators.

Reads the pilot sample JSON and writes a TSV holding only the hadith text. All
Sanadset tags are removed and the silver labels are never read, so nothing in
the sheet reveals an existing label.

Usage:
  python evaluation/annotation/build_sheet.py <pilot_sample.json> [--out hadiths_to_label.tsv] [--seed 0]
"""
import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path

COLUMNS = ["hadith_id", "collection", "text", "narrators", "notes", "seconds_spent"]
DEFAULT_OUT = Path(__file__).with_name("hadiths_to_label.tsv")
TAG = re.compile(r"<[^<>]*>")


def strip_tags(text: str) -> str:
    """Remove every <...> tag and any stray angle bracket, then tidy whitespace."""
    text = TAG.sub(" ", text)
    text = text.replace("<", " ").replace(">", " ")
    return re.sub(r"\s+", " ", text).strip()


def build_rows(sample, seed):
    rows = [
        {"hadith_id": f"{x['coll']}:{x['num']}", "collection": x["coll"], "text": strip_tags(x["raw"])}
        for x in sample
    ]
    ids = [r["hadith_id"] for r in rows]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate hadith_id: {', '.join(duplicates)}")
    random.Random(seed).shuffle(rows)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write the blind labelling sheet (TSV).")
    ap.add_argument("sample", help="path to pilot_sample.json")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help=f"output TSV (default {DEFAULT_OUT.name} next to this script)")
    ap.add_argument("--seed", type=int, default=0, help="row shuffle seed (default 0)")
    args = ap.parse_args(argv)
    try:
        with open(args.sample, encoding="utf-8") as fh:
            rows = build_rows(json.load(fh), args.seed)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n", restval="")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} hadiths to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
