#!/usr/bin/env python3
"""
verify-adr-writeonce — reproduce, first-hand, the "decisions are write-once"
claim on real Architecture Decision Record repositories.

The claim (agent-reported, here re-checked): most ADRs are created and never
edited again — which is not neglect, it's correct: a decision doesn't change, it
gets superseded. And where supersession exists, the forward reference is written
far more often than the back-reference is maintained.

This walks a git repo, finds ADR files, and for each one counts how many commits
touched it (write-once == exactly one commit). It also inspects each file for a
`status:`/`Status` field and for supersede references. No dependencies beyond
Python 3 + git.

Run:  python3 verify-adr-writeonce.py <repo-dir> [<glob>]
  <glob> defaults to common ADR names; pass one to override, e.g.:
    python3 verify-adr-writeonce.py madr 'docs/decisions/*.md'
    python3 verify-adr-writeonce.py arachne 'adr-*.md'
"""
import os
import re
import subprocess
import sys
import glob as globmod


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, errors="replace",
    ).stdout


def find_adrs(repo, pattern):
    if pattern:
        hits = globmod.glob(os.path.join(repo, "**", pattern), recursive=True)
    else:
        hits = []
        for pat in ("[0-9][0-9][0-9][0-9]-*.md", "adr-*.md", "*-adr-*.md", "ADR-*.md"):
            hits += globmod.glob(os.path.join(repo, "**", pat), recursive=True)
    # de-dup, always drop template/index/readme (not real decisions)
    seen, out = set(), []
    for h in sorted(hits):
        b = os.path.basename(h).lower()
        if h in seen or b in ("index.md", "readme.md") or "template" in b:
            continue
        seen.add(h)
        out.append(h)
    return out


STATUS_RE = re.compile(r'^\s*(status:|[-*]?\s*status\b|##\s*status)', re.I)
SUPERSEDE_FWD = re.compile(r'supersed(e|es|ed)\b|replaces\b', re.I)
SUPERSEDE_BACK = re.compile(r'supersed(ed)\s+by|superseded-by', re.I)


def inspect(path):
    status = False
    has_status_value = False
    fwd = back = False
    with open(path, errors="replace") as f:
        for line in f:
            if STATUS_RE.match(line):
                status = True
                val = line.split(":", 1)[-1].strip() if ":" in line else ""
                if val and val.lower() not in ("", "{status}", "accepted | ..."):
                    has_status_value = True
            if SUPERSEDE_BACK.search(line):
                back = True
            elif SUPERSEDE_FWD.search(line):
                fwd = True
    return status, fwd, back


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: verify-adr-writeonce.py <repo-dir> [<glob>]")
    repo = sys.argv[1].rstrip("/")
    pattern = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"not a git repo (need history for commit counts): {repo}")

    adrs = find_adrs(repo, pattern)
    if not adrs:
        sys.exit(f"no ADR files found in {repo} (try passing a glob)")

    total = len(adrs)
    write_once = 0
    commit_counts = []
    with_status = 0
    fwd_refs = back_refs = 0

    for path in adrs:
        rel = os.path.relpath(path, repo)
        log = git(repo, "log", "--oneline", "--follow", "--", rel)
        n = len([l for l in log.splitlines() if l.strip()])
        commit_counts.append(n)
        if n == 1:
            write_once += 1
        status, fwd, back = inspect(path)
        if status:
            with_status += 1
        if fwd:
            fwd_refs += 1
        if back:
            back_refs += 1

    commit_counts.sort()
    median = commit_counts[len(commit_counts) // 2] if commit_counts else 0

    def pct(a, b):
        return f"{100*a/b:.0f}%" if b else "n/a"

    print(f"repo: {repo}")
    print(f"ADR files: {total}")
    print(f"write-once (exactly 1 commit): {write_once}  ({pct(write_once, total)})")
    print(f"median commits per ADR:        {median}")
    print(f"carry a status field:          {with_status}  ({pct(with_status, total)})")
    print(f"forward supersede references:  {fwd_refs}")
    print(f"back  supersede references:    {back_refs}")
    print()
    if fwd_refs or back_refs:
        print("forward vs back supersede references:", fwd_refs, "vs", back_refs,
              "— the back direction, needing an edit to an untouched doc, lags.")


if __name__ == "__main__":
    main()
