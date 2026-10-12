"""Build the scorer's reference JSONL from the silver labels of the pilot sample.

`ref_nars` holds the Sanadset <NAR> labels, which regular expressions produced.
They are a silver standard: a score against them compares systems with each
other and is not an accuracy figure. Residual <...> tags are removed from every
mention, as the scorer's normalisation does not remove markup.

Usage:
  python evaluation/build_silver_reference.py <pilot_sample.json> --out reference_silver.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "annotation"))
from build_sheet import strip_tags  # noqa: E402


def build_reference(sample):
    """Returns [{"hadith_id", "mentions"}] in sample order, mentions in chain order."""
    rows = [
        {
            "hadith_id": f"{x['coll']}:{x['num']}",
            "mentions": [m for m in map(strip_tags, x["ref_nars"]) if m],
        }
        for x in sample
    ]
    ids = [r["hadith_id"] for r in rows]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate hadith_id: {', '.join(duplicates)}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write the silver reference JSONL from ref_nars.")
    ap.add_argument("sample", help="path to pilot_sample.json")
    ap.add_argument("--out", required=True, help="output reference JSONL")
    args = ap.parse_args(argv)
    try:
        with open(args.sample, encoding="utf-8") as fh:
            rows = build_reference(json.load(fh))
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} hadiths, {sum(len(r['mentions']) for r in rows)} mentions to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
