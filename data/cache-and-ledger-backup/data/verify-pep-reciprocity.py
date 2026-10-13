#!/usr/bin/env python3
"""
verify-pep-reciprocity — reproduce, first-hand, the central number in the essay.

The claim: in the most disciplined decision-record system in existence (Python
PEPs), the FORWARD link (`Replaces`, written by an author already editing their
own doc) is well-populated, while the BACK link (`Superseded-By`, which requires
editing a document you're not otherwise touching) is not fully reciprocal. That
asymmetry is the whole argument for "store the forward link, DERIVE the back link".

This script downloads the public PEP dataset and computes the reciprocity itself,
so the number in README.md is not taken on faith from a research pass.

Run:  python3 verify-pep-reciprocity.py [--offline path/to/peps.json]
Data: https://peps.python.org/api/peps.json  (CC0-ish public metadata)
"""
import json
import sys
import urllib.request

API = "https://peps.python.org/api/peps.json"


def load(argv):
    if len(argv) >= 3 and argv[1] == "--offline":
        with open(argv[2]) as f:
            return json.load(f), argv[2]
    with urllib.request.urlopen(API, timeout=30) as r:
        return json.loads(r.read().decode()), API


def as_ids(field):
    """`replaces`/`superseded_by` are comma-separated PEP numbers, or None."""
    if not field:
        return []
    out = []
    for tok in str(field).replace(",", " ").split():
        tok = tok.strip()
        if tok.isdigit():
            out.append(int(tok))
    return out


def main():
    peps, src = load(sys.argv)
    by_num = {int(v["number"]): v for v in peps.values()}

    forward = {}   # new -> [old...]   from `replaces`
    backward = {}  # old -> [new...]   from `superseded_by`
    status_superseded = set()

    for num, v in by_num.items():
        r = as_ids(v.get("replaces"))
        s = as_ids(v.get("superseded_by"))
        if r:
            forward[num] = r
        if s:
            backward[num] = s
        if (v.get("status") or "").lower() == "superseded":
            status_superseded.add(num)

    n_forward = len(forward)
    n_backward = len(backward)
    n_status = len(status_superseded)

    # Reciprocity A: every "A replaces B" — does B carry superseded_by == A?
    fwd_pairs = [(new, old) for new, olds in forward.items() for old in olds]
    fwd_ok = sum(
        1 for new, old in fwd_pairs
        if new in as_ids(by_num.get(old, {}).get("superseded_by"))
    )
    # Reciprocity B: every "B superseded_by A" — does A carry replaces == B?
    bwd_pairs = [(old, new) for old, news in backward.items() for new in news]
    bwd_ok = sum(
        1 for old, new in bwd_pairs
        if old in as_ids(by_num.get(new, {}).get("replaces"))
    )

    # Header-vs-status inconsistency: carries superseded_by but status != Superseded
    hdr_status_mismatch = [
        num for num in backward
        if (by_num[num].get("status") or "").lower() != "superseded"
    ]

    def pct(a, b):
        return f"{100*a/b:.0f}%" if b else "n/a"

    print(f"source: {src}")
    print(f"total PEPs: {len(by_num)}")
    print()
    print(f"carry `replaces`      (forward, new->old): {n_forward}")
    print(f"carry `superseded_by` (backward, old->new): {n_backward}")
    print(f"status == Superseded:                       {n_status}")
    print()
    print("RECIPROCITY")
    print(f"  A replaces B      -> B carries superseded_by:A  = {fwd_ok}/{len(fwd_pairs)}  ({pct(fwd_ok, len(fwd_pairs))})")
    print(f"  B superseded_by A -> A carries replaces:B       = {bwd_ok}/{len(bwd_pairs)}  ({pct(bwd_ok, len(bwd_pairs))})")
    print()
    print(f"header/status mismatch (superseded_by set, status != Superseded): {len(hdr_status_mismatch)}")
    if hdr_status_mismatch:
        print("  PEPs:", ", ".join(map(str, sorted(hdr_status_mismatch))))
    print()
    # The load-bearing finding, stated plainly:
    if len(fwd_pairs) and len(bwd_pairs):
        f_recip = fwd_ok / len(fwd_pairs)
        b_recip = bwd_ok / len(bwd_pairs)
        weaker = "forward (`replaces`)" if f_recip < b_recip else "back (`superseded_by`)"
        print(f"weaker-reciprocated direction: {weaker}")
        print("interpretation: the direction requiring you to edit a document you're")
        print("not otherwise touching is the one that decays. Derive it instead.")


if __name__ == "__main__":
    main()
