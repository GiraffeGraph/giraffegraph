"""Turn filled labelling sheets into scorer input and measure annotator agreement.

One sheet:   writes the scorer's reference JSONL.
Two sheets:  prints inter-annotator agreement as mutual F1 under M1 and M2
             (one annotator scored against the other; F1 is the same either
             way round) and each annotator's mean seconds_spent per hadith.

In the `narrators` column mentions are separated by " | " and parallel chains
by " || "; chains are concatenated in order.

Usage:
  python evaluation/annotation/to_reference.py <filled.tsv> --out reference.jsonl
  python evaluation/annotation/to_reference.py <annotator_a.tsv> <annotator_b.tsv>
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scorer  # noqa: E402

REQUIRED = ("hadith_id", "narrators", "seconds_spent")


def parse_narrators(cell: str):
    return [m.strip() for chain in cell.split("||") for m in chain.split("|") if m.strip()]


def read_sheet(path):
    """Returns {hadith_id: {"mentions": [...], "seconds": float | None}} in sheet order."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing column(s): {', '.join(missing)}")
        out = {}
        for row in reader:
            hid = (row["hadith_id"] or "").strip()
            if not hid:
                continue
            if hid in out:
                raise ValueError(f"{path}: duplicate hadith_id {hid}")
            seconds = (row["seconds_spent"] or "").strip().replace(",", ".")
            try:
                seconds = float(seconds) if seconds else None
            except ValueError:
                raise ValueError(f"{path}: {hid}: seconds_spent is not a number: {seconds!r}") from None
            out[hid] = {"mentions": parse_narrators(row["narrators"] or ""), "seconds": seconds}
    if not out:
        raise ValueError(f"{path}: no labelled rows")
    return out


def mentions_of(sheet):
    return {hid: row["mentions"] for hid, row in sheet.items()}


def mean_seconds(sheet):
    """(mean seconds_spent, number of rows that recorded a time)"""
    timed = [row["seconds"] for row in sheet.values() if row["seconds"] is not None]
    return (sum(timed) / len(timed) if timed else None), len(timed)


def agreement(sheet_a, sheet_b):
    only_a, only_b = sorted(set(sheet_a) - set(sheet_b)), sorted(set(sheet_b) - set(sheet_a))
    if only_a or only_b:
        raise ValueError(
            "sheets cover different hadiths; "
            f"only in first: {', '.join(only_a) or '-'}; only in second: {', '.join(only_b) or '-'}"
        )
    return scorer.score(mentions_of(sheet_a), mentions_of(sheet_b), n_boot=0)


def describe_seconds(name, sheet):
    mean, timed = mean_seconds(sheet)
    value = f"{mean:.1f}" if mean is not None else "n/a"
    return f"mean seconds_spent per hadith, {name}: {value} ({timed} of {len(sheet)} rows timed)"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Convert filled labelling sheets; report annotator agreement.")
    ap.add_argument("sheets", nargs="+", help="one filled TSV, or two for inter-annotator agreement")
    ap.add_argument("--out", help="write the first sheet as reference JSONL (required with a single sheet)")
    args = ap.parse_args(argv)
    if len(args.sheets) > 2:
        ap.error("expected one or two sheets")
    if len(args.sheets) == 1 and not args.out:
        ap.error("--out is required with a single sheet")
    try:
        sheets = [read_sheet(p) for p in args.sheets]
        result = agreement(*sheets) if len(sheets) == 2 else None
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for hid, mentions in mentions_of(sheets[0]).items():
                fh.write(json.dumps({"hadith_id": hid, "mentions": mentions}, ensure_ascii=False) + "\n")
        print(f"wrote {len(sheets[0])} hadiths to {args.out}")
    for path, sheet in zip(args.sheets, sheets):
        empty = [hid for hid, row in sheet.items() if not row["mentions"]]
        if empty:
            print(f"warning: {path}: {len(empty)} row(s) without narrators: {', '.join(empty)}", file=sys.stderr)

    if result:
        print(f"hadiths: {result['n_hadiths']}")
        for criterion in scorer.CRITERIA:
            r = result[criterion]
            print(
                f"{criterion} mutual F1: {r['f1']:.4f} "
                f"(matched {r['tp']}, only in first {r['fn']}, only in second {r['fp']}; "
                f"identical chains {r['exact_chain_rate']:.4f})"
            )
    for name, sheet in zip(args.sheets, sheets):
        print(describe_seconds(name, sheet))
    return 0


if __name__ == "__main__":
    sys.exit(main())
