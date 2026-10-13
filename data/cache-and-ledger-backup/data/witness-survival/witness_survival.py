#!/usr/bin/env python3
"""Witness survival: how long does a content hash of the code a doc sentence refers to stay valid?

Usage
-----
    python3 witness_survival.py --repos-dir DIR --out results.json [--dump-anchors anchors.jsonl]

DIR holds (or receives) one blobless clone per repository in REPOS, named `<org>_<repo>`.
Missing clones are created with `git clone --filter=blob:none --no-checkout <url>`; the blobs
the measurement needs are fetched in batches from the promisor remote. Requirements: Python 3.8+
standard library and the `git` CLI (2.45+ recommended so the missing-blob check does not fetch).

Each REPOS entry pins the HEAD commit that was measured, so a re-run reproduces results.json
byte for byte. Pass `--unpin` to measure the clone's current HEAD instead. The run prints the pooled
survival table and the 20-anchor sample to judge by eye.

Method (per repository)
-----------------------
t0        last first-parent commit whose committer date is >= 24 months older than HEAD
          (12 months when the history is too short; recorded as `lookback_months`).
anchor    (doc file, line number, doc line text, target path) taken from every tracked
          *.md / *.markdown / *.mdx file at t0. A token ([A-Za-z0-9_.@+~/-]+, URLs blanked out)
          is a path mention when it resolves to a regular file at t0, tried as written from the
          repository root and then relative to the Markdown file's directory. A token that fills
          a whole backtick span needs a "/" or a "."; any other token needs a "/". Targets that
          are Markdown, images, or under a vendored directory are dropped, and so are Markdown
          files under vendored directories. Directories are never anchors. Every result is given
          for all anchors and for the subset whose token has a directory component
          (`anchors_with_directory`), which leaves out bare names such as `package.json`.
symbol    first backticked identifier on the same doc line (`name`, `name()`, `name(...)`;
          at least 3 characters, not in STOPWORDS) that occurs as a whole word in the target
          file at t0.
horizons  t0 + {1, 3, 6, 12, 24} calendar months; the commit used is the last first-parent
          commit at or before that date. Horizon 0 goes through the same code as a self-check.
G0        target path still exists.
G1        target blob hash unchanged.
G2        (symbol anchors) definition block unchanged: first line containing the symbol as a
          whole word plus the following lines up to, not including, the next non-blank line
          indented no deeper than it; at most 80 lines; trailing blank lines dropped. A missing
          file or a missing symbol counts as changed.
DOC       the doc line is "edited" unless the identical line (CR stripped) is present anywhere
          in the same doc file at the horizon.

Text is decoded as UTF-8 with replacement and CRLF is read as LF. The 20-anchor sample for the
by-eye check is drawn from the pooled anchor list with random.Random(SEED).
"""
import argparse
import calendar
import datetime as dt
import json
import os
import posixpath
import random
import re
import subprocess
import sys
from collections import Counter

SEED = 20261013
SAMPLE_SIZE = 20
HORIZONS = [0, 1, 3, 6, 12, 24]
REPORT_HORIZONS = [1, 3, 6, 12, 24]
BLOCK_CAP = 80

# (url, primary language, measured HEAD sha)
REPOS = [
    ("https://github.com/bevyengine/bevy", "Rust", "12a94e0cd6b18df7a0dc2e5a202a55156d80e9a6"),
    ("https://github.com/bytecodealliance/wasmtime", "Rust", "d6ad2b172449bb79e55d733de685b63d2e63fd71"),
    ("https://github.com/zulip/zulip", "Python", "ef6e64bd3cb4e2fe7ed993e68e3b05ff576ee816"),
    ("https://github.com/huggingface/transformers", "Python", "78633ef9ff2338284e0c9da2218381b7ed755bc4"),
    ("https://github.com/argoproj/argo-cd", "Go", "3cc4faa2cbf92dfa92990070908ea2d49d9d60b6"),
    ("https://github.com/tektoncd/pipeline", "Go", "90b2235c66fb02d98e51c148a66725c537c805d6"),
    ("https://github.com/desktop/desktop", "TypeScript", "64fb73a68c582b2fc370a100bb2d28fdc5eb6372"),
    ("https://github.com/microsoft/playwright", "TypeScript", "5d2cd726001a10eafbdfd02086f0414164057b07"),
]

# REPOS was picked from 49 screened candidates by SELECTION_RULE, before looking at outcomes.
SELECTION_RULE = (
    "per language group (Rust, Python, Go, JavaScript/TypeScript by GitHub primary language) the two "
    "candidates with the most distinct targets among anchors with a directory component, skipping any "
    "whose first-parent history leaves a horizon commit more than 31 days before its horizon date")
# Candidates screened on 2026-10-13 and not kept: repo -> (anchors, distinct targets among anchors
# with a directory, max days a horizon commit precedes its horizon date).
SCREENED_OUT = {
    "astral-sh/ruff": (124, 32, 0),
    "cli/cli": (19, 10, 3),
    "containerd/containerd": (18, 8, 1),
    "curl/curl": (33, 16, 0),
    "dbt-labs/dbt-core": (40, 24, 2),
    "denoland/deno": (43, 23, 3),
    "electron/electron": (47, 13, 1),
    "element-hq/synapse": (93, 35, 1),
    "eslint/eslint": (167, 7, 1),
    "go-delve/delve": (15, 14, 5),
    "golang/tools": (16, 7, 2),
    "golangci/golangci-lint": (29, 9, 2),
    "hashicorp/terraform": (23, 6, 2),
    "helix-editor/helix": (34, 4, 66),
    "huggingface/diffusers": (57, 4, 3),
    "jestjs/jest": (122, 3, 24),
    "kubernetes-sigs/cluster-api": (48, 17, 1),
    "kubevirt/kubevirt": (93, 31, 1),
    "mermaid-js/mermaid": (120, 15, 36),
    "mitmproxy/mitmproxy": (17, 10, 26),
    "moby/moby": (53, 8, 2),
    "netbox-community/netbox": (37, 9, 5),
    "nushell/nushell": (24, 2, 0),
    "open-telemetry/opentelemetry-collector": (36, 20, 1),
    "prettier/prettier": (155, 11, 91),
    "prometheus/prometheus": (39, 27, 2),
    "pydantic/pydantic": (22, 13, 3),
    "python-poetry/poetry": (126, 0, 17),
    "rust-lang/cargo": (424, 3, 1),
    "rust-lang/miri": (17, 7, 1),
    "rust-lang/rust-analyzer": (6, 3, 1),
    "rust-lang/rust-clippy": (51, 14, 0),
    "rust-lang/rustfmt": (22, 9, 17),
    "sveltejs/svelte": (20, 8, 1),
    "tauri-apps/tauri": (55, 5, 1),
    "temporalio/temporal": (13, 4, 3),
    "Textualize/textual": (826, 430, 89),
    "tokio-rs/tokio": (23, 8, 4),
    "typescript-eslint/typescript-eslint": (96, 11, 3),
    "vuejs/core": (20, 7, 23),
    "wagtail/wagtail": (32, 11, 3),
}

MD_EXT = (".md", ".markdown", ".mdx")
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp", ".tif", ".tiff", ".avif")
VENDOR_PARTS = {
    "node_modules", "vendor", "vendored", "_vendor", "third_party", "third-party", "thirdparty",
    "3rdparty", "bower_components", "external", "extern", "deps", ".yarn",
}
STOPWORDS = {
    "true", "false", "null", "none", "nil", "self", "this", "void", "int", "str", "string", "bool",
    "float", "char", "byte", "bytes", "list", "dict", "map", "set", "type", "object", "func",
    "function", "def", "class", "var", "let", "const", "return", "import", "from", "for", "and",
    "not", "the", "with", "use", "pub", "mod", "new", "any", "number", "boolean", "undefined",
    "struct", "enum", "impl", "trait", "main", "test", "tests", "name", "value", "key", "data",
    "error", "err", "yes", "all", "get", "run", "std", "todo",
}

URL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://\S+")
TOKEN_RE = re.compile(r"[A-Za-z0-9_.@+~\-/]+")
SPAN_RE = re.compile(r"`([^`\n]+)`")
IDENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(\(.*\))?$")


def git(repo, *args, stdin=None, env_extra=None):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    env.update(env_extra or {})
    r = subprocess.run(["git", "-C", repo, *args], input=stdin, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env)
    if r.returncode:
        raise RuntimeError("git %s failed: %s" % (" ".join(args[:3]), r.stderr.decode("utf-8", "replace")[-500:]))
    return r.stdout


def add_months(d, months):
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    return d.replace(year=y, month=m, day=min(d.day, calendar.monthrange(y, m)[1]))


def commit_date(repo, sha):
    ts = int(git(repo, "show", "-s", "--format=%ct", sha).strip())
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc)


def last_commit_before(repo, head, when):
    out = git(repo, "rev-list", "-1", "--first-parent", "--before=" + when.isoformat(), head).strip()
    return out.decode() or None


def tree(repo, sha):
    """path -> blob oid for regular files in the commit's tree."""
    files = {}
    for entry in git(repo, "ls-tree", "-r", "-z", sha).split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, typ, oid = meta.split()
        if typ == b"blob" and mode in (b"100644", b"100755"):
            files[path.decode("utf-8", "surrogateescape")] = oid.decode()
    return files


def prefetch(repo, oids):
    oids = sorted(set(oids))
    if not oids:
        return
    out = git(repo, "cat-file", "--batch-check", stdin=("\n".join(oids) + "\n").encode(),
              env_extra={"GIT_NO_LAZY_FETCH": "1"})
    missing = [ln.split()[0] for ln in out.splitlines() if ln.endswith(b" missing")]
    for i in range(0, len(missing), 4000):
        git(repo, "-c", "fetch.negotiationAlgorithm=noop", "fetch", "origin", "--no-tags",
            "--no-write-fetch-head", "--recurse-submodules=no", "--filter=blob:none", "--stdin",
            stdin=b"\n".join(missing[i:i + 4000]) + b"\n")


class Blobs:
    def __init__(self, repo):
        self.proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     env=dict(os.environ, GIT_NO_LAZY_FETCH="1", LC_ALL="C"))
        self.cache = {}

    def text(self, oid):
        if oid not in self.cache:
            self.proc.stdin.write(oid.encode() + b"\n")
            self.proc.stdin.flush()
            header = self.proc.stdout.readline().split()
            if header[-1] == b"missing":
                raise RuntimeError("blob %s missing after prefetch" % oid)
            size = int(header[2])
            data = self.proc.stdout.read(size + 1)[:size]
            self.cache[oid] = data.decode("utf-8", "replace").replace("\r\n", "\n")
        return self.cache[oid]

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def is_vendored(path):
    return any(part.lower() in VENDOR_PARTS for part in path.split("/")[:-1])


def resolve(token, md_dir, files):
    cands = [token.lstrip("/")] if token.startswith("/") else [token, posixpath.join(md_dir, token)]
    for c in cands:
        if not c:
            continue
        n = posixpath.normpath(c)
        if n in files:
            return n
    return None


def path_mentions(line, md_path, files):
    """(target path, token has a directory component) for each path mentioned on one doc line."""
    clean = URL_RE.sub(lambda m: " " * len(m.group()), line)
    whole_spans = set()
    for m in SPAN_RE.finditer(clean):
        inner = m.group(1)
        lead = len(inner) - len(inner.lstrip())
        whole_spans.add((m.start(1) + lead, m.start(1) + len(inner.rstrip())))
    md_dir = posixpath.dirname(md_path)
    found = {}
    for m in TOKEN_RE.finditer(clean):
        backticked = (m.start(), m.end()) in whole_spans
        tok = m.group().rstrip(".")
        if tok.startswith("~") or not tok:
            continue
        bare = tok
        while bare.startswith("./"):
            bare = bare[2:]
        has_dir = "/" in bare.strip("/")
        if not has_dir and not (backticked and "." in tok):
            continue
        target = resolve(tok, md_dir, files)
        if target is None or target == md_path:
            continue
        low = target.lower()
        if low.endswith(MD_EXT) or low.endswith(IMG_EXT) or is_vendored(target):
            continue
        found[target] = found.get(target, False) or has_dir
    return list(found.items())


def identifier_candidates(line):
    out = []
    for m in SPAN_RE.finditer(line):
        im = IDENT_RE.match(m.group(1).strip())
        if im and len(im.group(1)) >= 3 and im.group(1).lower() not in STOPWORDS and im.group(1) not in out:
            out.append(im.group(1))
    return out


def word_re(sym):
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(sym) + r"(?![A-Za-z0-9_])")


def indent(line):
    expanded = line.expandtabs(8)
    return len(expanded) - len(expanded.lstrip())


def definition_block(text, sym):
    rx = word_re(sym)
    lines = text.split("\n")
    for i, first in enumerate(lines):
        if rx.search(first):
            base = indent(first)
            block = [first]
            for nxt in lines[i + 1:i + BLOCK_CAP]:
                if nxt.strip() and indent(nxt) <= base:
                    break
                block.append(nxt)
            while not block[-1].strip() and len(block) > 1:
                block.pop()
            return "\n".join(block)
    return None


def share(num, den):
    return round(num / den, 4) if den else None


def table(cells, n):
    # cells: [changed&edited, changed&verbatim, unchanged&edited, unchanged&verbatim]
    ce, cv, ue, uv = cells
    return {
        "changed_edited": ce, "changed_verbatim": cv, "unchanged_edited": ue, "unchanged_verbatim": uv,
        "n": n,
        "share_changed_and_verbatim": share(cv, n),
        "share_verbatim_given_changed": share(cv, ce + cv),
        "share_edited_given_changed": share(ce, ce + cv),
        "share_edited_given_unchanged": share(ue, ue + uv),
    }


def block(anchors, horizons=REPORT_HORIZONS):
    """Survival shares and witness-changed x doc-edited tables for a set of measured anchors."""
    sym = [a for a in anchors if a["symbol"]]
    out = {"n_anchors": len(anchors), "n_symbol_anchors": len(sym),
           "n_doc_files": len({(a["repo"], a["doc"]) for a in anchors}),
           "n_unique_targets": len({(a["repo"], a["target"]) for a in anchors}),
           "survival": {}, "tables": {}}
    for h in map(str, horizons):
        res = [a["by_horizon"][h] for a in anchors]
        res_sym = [a["by_horizon"][h] for a in sym]
        out["survival"][h] = {
            "G0_exists": share(sum(r["G0"] for r in res), len(res)),
            "G1_file": share(sum(r["G1"] for r in res), len(res)),
            "G2_symbol": share(sum(r["G2"] for r in res_sym), len(res_sym)),
            "G1_file_symbol_anchors_only": share(sum(r["G1"] for r in res_sym), len(res_sym)),
            "doc_line_verbatim": share(sum(not r["doc_edited"] for r in res), len(res)),
        }
        cells = {"G1": [0, 0, 0, 0], "G2": [0, 0, 0, 0]}
        for g, rows in (("G1", res), ("G2", res_sym)):
            for r in rows:
                cells[g][(2 if r[g] else 0) + (0 if r["doc_edited"] else 1)] += 1
        out["tables"][h] = {"G1": table(cells["G1"], len(res)), "G2": table(cells["G2"], len(res_sym))}
    return out


def mean_block(blocks, horizons=REPORT_HORIZONS):
    """Unweighted mean of per-repository shares; a repository without the measure is skipped."""
    def mean(values):
        vals = [v for v in values if v is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    out = {"n_repositories": len(blocks),
           "n_repositories_with_symbol_anchors": sum(1 for b in blocks if b["n_symbol_anchors"]),
           "survival": {}, "tables": {}}
    for h in map(str, horizons):
        out["survival"][h] = {m: mean(b["survival"][h][m] for b in blocks)
                              for m in blocks[0]["survival"][h]}
        out["tables"][h] = {g: {m: mean(b["tables"][h][g][m] for b in blocks)
                                for m in blocks[0]["tables"][h][g] if m.startswith("share_")}
                            for g in ("G1", "G2")}
    return out


def measure_repo(repos_dir, url, language, pinned=None, unpin=False):
    name = "_".join(url.rstrip("/").split("/")[-2:])
    repo = os.path.join(repos_dir, name)
    if not os.path.isdir(repo):
        subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", url + ".git", repo],
                       check=True)
    head = git(repo, "rev-parse", "HEAD" if (unpin or not pinned) else pinned).strip().decode()
    head_date = commit_date(repo, head)
    roots = git(repo, "rev-list", "--max-parents=0", "--first-parent", head).split()
    first_date = min(commit_date(repo, r.decode()) for r in roots)

    lookback = 24
    t0 = last_commit_before(repo, head, add_months(head_date, -24))
    if t0 is None:
        lookback = 12
        t0 = last_commit_before(repo, head, add_months(head_date, -12))
    t0_date = commit_date(repo, t0)

    horizon_commits, lag_days = {}, {}
    for h in HORIZONS:
        due = add_months(t0_date, h)
        horizon_commits[h] = last_commit_before(repo, head, due)
        lag_days[h] = (due - commit_date(repo, horizon_commits[h])).days
    trees = {h: tree(repo, sha) for h, sha in horizon_commits.items()}
    files0 = tree(repo, t0)

    md_files = sorted(p for p in files0 if p.lower().endswith(MD_EXT) and not is_vendored(p))
    prefetch(repo, [files0[p] for p in md_files])
    blobs = Blobs(repo)

    anchors = []
    for md in md_files:
        for lineno, line in enumerate(blobs.text(files0[md]).split("\n"), 1):
            if "/" not in line and "`" not in line:
                continue
            for target, has_dir in path_mentions(line, md, files0):
                anchors.append({"repo": name, "doc": md, "line": lineno, "text": line, "target": target,
                                "has_dir": has_dir, "symbol": None, "idents": identifier_candidates(line)})

    prefetch(repo, [files0[a["target"]] for a in anchors if a["idents"]])
    for a in anchors:
        for ident in a.pop("idents"):
            if word_re(ident).search(blobs.text(files0[a["target"]])):
                a["symbol"] = ident
                break

    need = []
    for files in trees.values():
        for a in anchors:
            if a["doc"] in files and files[a["doc"]] != files0[a["doc"]]:
                need.append(files[a["doc"]])
            if a["symbol"] and a["target"] in files and files[a["target"]] != files0[a["target"]]:
                need.append(files[a["target"]])
    prefetch(repo, need)

    doc_lines = {}
    for a in anchors:
        a["by_horizon"] = {}
        block0 = definition_block(blobs.text(files0[a["target"]]), a["symbol"]) if a["symbol"] else None
        for h, files in trees.items():
            oid = files.get(a["target"])
            g0 = oid is not None
            g1 = oid == files0[a["target"]]
            g2 = None
            if a["symbol"]:
                g2 = g1 or (g0 and definition_block(blobs.text(oid), a["symbol"]) == block0)
            doc_oid = files.get(a["doc"])
            if doc_oid is None:
                edited = True
            elif doc_oid == files0[a["doc"]]:
                edited = False
            else:
                if doc_oid not in doc_lines:
                    doc_lines[doc_oid] = set(blobs.text(doc_oid).split("\n"))
                edited = a["text"] not in doc_lines[doc_oid]
            a["by_horizon"][str(h)] = {"G0": g0, "G1": g1, "G2": g2, "doc_edited": edited}
    blobs.close()

    ext = Counter(posixpath.splitext(a["target"])[1].lower() or "(none)" for a in anchors)
    info = {
        "url": url, "name": name, "language": language,
        "head_sha": head, "head_date": head_date.isoformat(),
        "first_commit_date": first_date.isoformat(),
        "history_years": round((head_date - first_date).days / 365.25, 1),
        "lookback_months": lookback,
        "t0_sha": t0, "t0_date": t0_date.isoformat(),
        "horizon_commits": {str(h): {"sha": sha, "date": commit_date(repo, sha).isoformat(),
                                     "days_before_horizon_date": lag_days[h]}
                            for h, sha in horizon_commits.items()},
        "n_markdown_files_at_t0": len(md_files),
        "target_extensions_top10": dict(ext.most_common(10)),
        "all_anchors": block(anchors),
        "anchors_with_directory": block([a for a in anchors if a["has_dir"]]),
    }
    return info, anchors


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repos-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump-anchors", help="write every anchor with per-horizon outcomes as JSON lines")
    ap.add_argument("--unpin", action="store_true", help="measure each clone's current HEAD")
    args = ap.parse_args()

    repos, all_anchors = [], []
    for url, language, pinned in REPOS:
        print("measuring", url, file=sys.stderr)
        info, anchors = measure_repo(args.repos_dir, url, language, pinned, args.unpin)
        repos.append(info)
        all_anchors.extend(anchors)
    with_dir = [a for a in all_anchors if a["has_dir"]]

    zero = block(all_anchors, horizons=[0])
    horizon0_ok = (all(v == 1.0 for v in zero["survival"]["0"].values())
                   and all(r["horizon_commits"]["0"]["sha"] == r["t0_sha"] for r in repos))
    sample = random.Random(SEED).sample(all_anchors, min(SAMPLE_SIZE, len(all_anchors)))

    result = {
        "method": {
            "horizons_months": REPORT_HORIZONS, "block_cap_lines": BLOCK_CAP, "seed": SEED,
            "git_version": subprocess.run(["git", "--version"], stdout=subprocess.PIPE).stdout.decode().strip(),
            "table_cells": "witness changed x doc sentence edited; changed includes a deleted target",
            "anchors_with_directory": "sensitivity subset: the path token has a directory component",
            "selection_rule": SELECTION_RULE,
            "screened_out_columns": ["anchors", "distinct_targets_with_directory", "max_horizon_lag_days"],
            "screened_out": SCREENED_OUT,
        },
        "pooled": {"all_anchors": block(all_anchors), "anchors_with_directory": block(with_dir)},
        "per_repository_mean": {
            "all_anchors": mean_block([r["all_anchors"] for r in repos]),
            "anchors_with_directory": mean_block([r["anchors_with_directory"] for r in repos])},
        "repositories": repos,
        "sanity": {
            "horizon_0_all_unchanged": horizon0_ok,
            "horizon_0_pooled": zero["survival"]["0"],
            "sample": [{k: a[k] for k in ("repo", "doc", "line", "text", "target", "symbol")} for a in sample],
        },
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
        f.write("\n")
    if args.dump_anchors:
        with open(args.dump_anchors, "w", encoding="utf-8") as f:
            for a in all_anchors:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")

    print("horizon 0 all unchanged:", horizon0_ok)
    for label in ("all_anchors", "anchors_with_directory"):
        b = result["pooled"][label]
        print("\n%s: %d anchors, %d with symbol" % (label, b["n_anchors"], b["n_symbol_anchors"]))
        print("%-8s %8s %8s %8s %12s" % ("months", "G0", "G1", "G2", "G1(sym set)"))
        for h in map(str, REPORT_HORIZONS):
            v = b["survival"][h]
            print("%-8s %8s %8s %8s %12s" % (h, v["G0_exists"], v["G1_file"], v["G2_symbol"],
                                             v["G1_file_symbol_anchors_only"]))
    print("\nSample for the by-eye check (seed %d):" % SEED)
    for i, a in enumerate(sample, 1):
        print("%2d. [%s] %s:%d -> %s (symbol: %s)\n    %s" % (
            i, a["repo"], a["doc"], a["line"], a["target"], a["symbol"], a["text"].strip()[:220]))


if __name__ == "__main__":
    main()
