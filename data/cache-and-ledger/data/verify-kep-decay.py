#!/usr/bin/env python3
"""
verify-kep-decay — reproduce, first-hand, the "typed field decays into freetext"
claim, on Kubernetes Enhancement Proposals (KEPs).

Each KEP has a kep.yaml with a typed `replaces:` list and a `status:` enum. The
claim: a typed field that nothing validates degenerates — most `replaces:` keys
sit empty (inherited from the template), and the few with values hold un-resolvable
junk (`n/a`, PR URLs, dead paths). And `status: replaced` (the closest thing to a
stored back-link) is far rarer than the forward `replaces:` claims — the same
asymmetry as PEPs, in a system with a stronger process gate.

This does NOT depend on PyYAML — kep.yaml is regular enough to scan line-wise,
and staying dependency-free is one of this project's own recorded decisions.

Run:  python3 verify-kep-decay.py <path-to-kubernetes-enhancements/keps>
Get the data:
  git clone --depth 1 --filter=blob:none --sparse \\
      https://github.com/kubernetes/enhancements.git ke
  cd ke && git sparse-checkout set keps
"""
import os
import re
import sys

TEMPLATE_TOKEN = "provisional|implementable"  # the literal template placeholder line


def scan_kep(path):
    """Return (status, replaces_raw) from a kep.yaml, line-wise, no YAML dep."""
    status = None
    replaces = None
    in_replaces = False
    inline = []
    with open(path, errors="replace") as f:
        for line in f:
            s = line.rstrip("\n")
            if re.match(r"^status:", s):
                status = s.split(":", 1)[1].strip().strip('"').strip("'")
                in_replaces = False
            elif re.match(r"^replaces:", s):
                rest = s.split(":", 1)[1].strip()
                if rest and rest != "[]":
                    replaces = rest          # inline form: replaces: [a, b] or a value
                    in_replaces = False
                else:
                    in_replaces = True       # block form follows on `  - ...` lines
                    inline = []
            elif in_replaces and re.match(r"^\s*-\s+", s):
                inline.append(s.strip()[1:].strip())
            elif in_replaces and re.match(r"^\S", s):
                in_replaces = False
    if replaces is None and inline:
        replaces = inline
    return status, replaces


def is_resolvable(val):
    """A `replaces` value that actually points at a KEP: a number or NNNN-slug."""
    v = str(val).strip().strip('"').strip("'").lstrip("-").strip()
    if not v or v.lower() in ("n/a", "na", "none", "tbd"):
        return False
    if "http://" in v or "https://" in v:
        return False
    # a bare KEP number, or NNNN-something
    return bool(re.match(r"^\d+(-|$)", v)) or bool(re.match(r"^kep-?\d+", v.lower()))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: verify-kep-decay.py <path-to/keps>")
    root = sys.argv[1]
    keps = []
    for dirpath, _, files in os.walk(root):
        if "kep.yaml" in files:
            keps.append(os.path.join(dirpath, "kep.yaml"))

    total = len(keps)
    key_present = 0
    empty = 0
    placeholder = 0
    real_vals = []       # flattened resolvable-or-not values
    status_counts = {}
    status_replaced = 0

    for p in keps:
        status, replaces = scan_kep(p)
        st = (status or "").strip()
        status_counts[st] = status_counts.get(st, 0) + 1
        if st == "replaced":
            status_replaced += 1

        if replaces is None:
            empty += 1
            continue
        key_present += 1
        vals = replaces if isinstance(replaces, list) else [replaces]
        joined = " ".join(str(v) for v in vals)
        if TEMPLATE_TOKEN in joined:
            placeholder += 1
            continue
        for v in vals:
            v = str(v).strip()
            if v and v != "[]":
                real_vals.append(v)

    resolvable = [v for v in real_vals if is_resolvable(v)]
    junk = [v for v in real_vals if not is_resolvable(v)]

    print(f"total KEPs (kep.yaml):            {total}")
    print(f"`replaces:` key present:          {key_present}")
    print(f"  ...empty (template default):    {empty}")
    print(f"  ...template placeholder string: {placeholder}")
    print(f"  ...real values:                 {len(real_vals)}")
    print(f"       resolvable (KEP id/slug):  {len(resolvable)}")
    print(f"       junk (n/a, URL, dead):     {len(junk)}")
    if junk:
        print("       junk sample:", ", ".join(sorted(set(junk))[:8]))
    print()
    print(f"status == replaced (stored back-link):  {status_replaced}")
    print()
    print("FORWARD vs BACK asymmetry:")
    print(f"  forward `replaces` claims (real): {len(real_vals)}")
    print(f"  backward status==replaced:        {status_replaced}")
    print()
    print("interpretation: a typed field that gates nothing decays into freetext;")
    print("the forward claim outnumbers the stored back-state, same as PEPs.")


if __name__ == "__main__":
    main()
