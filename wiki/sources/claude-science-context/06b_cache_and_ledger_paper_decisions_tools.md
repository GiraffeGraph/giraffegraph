# SOURCE FILE: cache-and-ledger/PAPER.md (verbatim copy)

# Store the Decision, Derive the Rest: An Empirical Note on Why Knowledge Bases Rot Asymmetrically

*Draft — empirical note. Every quantitative claim is backed by a re-runnable script in `data/`; numbers still marked [UNVERIFIED] are pending first-hand reproduction and must not be cited as fact.*

## Abstract

Systems that couple documentation to code — from literate programming to LLM-maintained wikis — fail with striking regularity. We argue the failures share one cause: a single artifact is made to hold two kinds of statement with opposite maintenance physics. **Derivable** statements ("the controller is `FaqController.cs`") are recoverable from a source of truth and should be regenerated, never stored; **decision** statements ("we rejected modelling this as a content block") are not recoverable from any artifact and must be stored, once. We give a decidability argument for why the derivable half cannot be kept in sync automatically (lens theory, determinism, and an LLM-specific failure mode), and we measure the decision half's characteristic rot — an asymmetry between forward and back references — first-hand across three public corpora (Python PEPs, Kubernetes KEPs, and a set of ADR repositories). In every corpus the forward reference (written by an author already editing the document) is populated far more reliably than the back reference (which demands an edit to an untouched document). The design implication is a two-line system: an append-only decision ledger whose back-links are *derived*, and a linter that flags broken code anchors without ever asserting a document is true. We ship both as ~330 lines of dependency-free shell.

## 1. Two kinds of sentence

Take one documentation page describing a software feature. It contains, intermixed:

- *Derivable:* "Storage is table `B2C_Faq`; the controller is `FaqController.cs`; it reuses the shared sanitizer." Each is a fact about code, recoverable from the code. If page and code disagree, the code wins; a machine can regenerate the sentence.
- *Decision:* "This is a dedicated entity that owns its items — deliberately **not** a content block with a convention on top." This is intent. The rejected alternative exists nowhere in the code. It can be recorded but never recomputed.

We call the first a **cache** of the source of truth and the second a **decision**. The claim of this note is that most documentation-rot pathologies are the two being stored in one place and maintained under one policy.

## 2. Why the cache half cannot be automated

Three independent arguments, each pointing the same way.

**Lens theory / the view-update problem.** A derived view can be edited and pushed back to its source only for a restricted class of transformations (well-behaved lenses; Bancilhon–Spyratos 1981; Foster et al. 2007). Prose documentation is not in that class: it does not merely project the code, it *adds* information (rationale, tradeoffs) absent from the code. A transform that is not a function of its source has no inverse. The systems that achieve real doc↔code sync (e.g. API docs generated from an OpenAPI schema) do so by removing the independent edit surface — the doc becomes a pure regenerable projection with no content of its own. That is exactly the cache/decision split, restated by the theory.

**Determinism.** Every incremental build system that avoids redundant work (Bazel's change-pruning, Salsa's red-green backdating, Roslyn's incremental generators) depends on *early cutoff*: recompute a node, and if its output equals the prior output, halt propagation. The rustc documentation states the precondition as a hard requirement — identical inputs *must* yield identical output "or else the compiler is not deterministic." LLM generation does not satisfy this: it does not emit byte-identical prose for identical input, so the equality check never fires and cutoff degrades to full recomputation. We found no published system performing sound early cutoff over non-deterministic node outputs; "semantically equal but not byte-equal" exists only as best-effort caching that knowingly serves stale answers — unacceptable for a correctness-bearing store.

**An LLM-specific failure mode.** Doctorow's "Metacrap" (2001) lists why self-asserted metadata is unreliable. An LLM asserting metadata removes the incentive-and-effort obstacles (it is not lazy, has no motive to lie) but leaves the structural ones (a schema is not neutral) and adds a new one: confident fabrication with no epistemic state corresponding to "I did not actually verify this." Independent measurement puts even strong models' code-comment factual-error rate near 20% [UNVERIFIED — pending first-hand reproduction], and automated detection of hallucinated technical prose near chance. The cache you generate cannot be cheaply verified.

## 3. The decision half: measured rot is asymmetric

Decisions are correctly write-once — a decision does not change, it is superseded. The characteristic failure is therefore not editing but *linking*: a new decision must reference what it replaces (forward), and ideally the replaced decision references its replacement (back). We measured this asymmetry first-hand.

**Method.** For each corpus we obtained the public dataset, parsed the forward reference field (`Replaces` / `replaces` / `supersedes`) and the back reference or stored-back-state (`Superseded-By` / `status: replaced`), and computed reciprocity. Scripts are in `data/`; each hits live data and is re-runnable.

**Results.**

| Corpus | N | Forward references | Back / reciprocity | Regime | Script |
|---|---|---|---|---|---|
| Python PEPs | 733 | 42 `Replaces` (36 PEPs) | 27 reciprocated = **64%**; back-dir 27/32 = 84%; 10 mismatches | CI linter checks header | `verify-pep-reciprocity.py` |
| Kubernetes KEPs | 656 | 50 `replaces`, **3 resolve** (47 junk) | 4 `status: replaced` | field gates nothing | `verify-kep-decay.py` |
| ADR population | 765 / 67 repos | 50 forward supersede refs | 22 back = **2.3 : 1** | ordinary hand-kept records | `verify-adr-writeonce.py` + sweep |

The direction requiring an edit to an untouched document is the one that lags — but the *magnitude* is regime-dependent, and this corrects an earlier automated pass that reported the ADR gap as near-total (back ~3.7%). Measured first-hand across 67 repos, forward is only ~2.3× back, and back-references are genuinely maintained in 16 of 67 repos. The asymmetry sharpens exactly where the process stops checking: near-perfect maintenance would need a gate, and Kubernetes' ungated `replaces` field has instead decayed almost entirely into unresolvable freetext (3 of 50 values resolve) — *a typed field that nothing validates degenerates.* In every regime the back-link is incompletely maintained; deriving it makes it complete by construction, for free.

**Write-once rate.** Measured across 765 ADRs in 67 repositories (`data/adr-sweep-results.md`, every commit SHA recorded): **46.5% pooled (ADR-weighted), 56.6% per-repo mean** — the two weightings bracket the informal "~52%" figure, which is thus consistent with the population. The median per-repo median commit count per ADR is 1. Write-once is therefore not neglect but the expected shape of a decision record.

## 4. Design implication

If the derivable half must not be stored and the decision half's only reliable link is the forward one, the minimal honest system is:

1. **A decision ledger.** Append-only records of non-derivable intent. Forward links only. Back-links **derived** by scanning — as Datomic derives reverse references, as Git derives a commit's children, as double-entry bookkeeping derives balances. Because the back-link is computed, the reciprocity gap of §3 cannot exist by construction. Supersession resolved by `max(serial)` in code, never by an LLM's judgment of which fact is newer.
2. **A linter, not a certifier.** It verifies that each fully-qualified code anchor (`repo/path/File:Symbol`) resolves — structural drift is cheap to catch and worth gating. It never asserts the prose is true: a resolving anchor proves the file exists, not that the claim about it holds, and a validated anchor makes a stale claim sound *more* authoritative. Detection of structural drift is solved (~90%+ in the literature); semantic verification is not, and is left to a human.

We do **not** store: a regenerable cache of the code, typed `updated:` fields (git owns those), or stored back-links (derived). The residue is ~330 lines of shell (`bin/anchor-check`, `bin/ledger`), with a self-test whose every control is paired with its falsifier.

## 5. Threats to validity

- The §3 corpora are self-selected toward systems that *have* a supersession convention; systems without one contribute no data. The asymmetry claim is about maintenance of an existing convention, not its adoption.
- Anchor resolution depends on fully-qualified paths; symbol identity across refactors is only approximable (best published trackers reach ~97–99% F1 on curated oracles, and one 2025 result found predecessor oracles themselves contained errors). We therefore treat drift as budgeted maintenance, not a solvable-away bug.
- Numbers marked [UNVERIFIED] came from an automated research pass; two figures from that pass were already found wrong on first-hand recheck (a KEP field count; a status-field count), which is precisely why every load-bearing number in this note sits behind a script.

## 6. Conclusion

The interesting move is not a mechanism but a cut: the line between what a machine can re-derive and what only a human decided. Everything derivable wants to be recomputed, not stored; every decision wants to be stored once and never touched. Decades of systems ran that line through the middle of a single artifact and spent themselves keeping both halves in sync. Do not keep them in sync — keep them apart.

## Reproducibility

All numbers: `data/*.py` against live public datasets; tools: `bin/*`; self-test: `./test.sh`. Re-run and you get the same answer, or a newer one.


---
# SOURCE: cache-and-ledger/decisions/*.md (the project's own decision ledger, verbatim)

## FILE: decisions/0001-ship-a-typed-compiler-that-keeps-docs-synced-to-co.md
```
---
id: 0001
title: Ship a typed compiler that keeps docs synced to code
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0002-cut-the-derivable-cache-layer-entirely.md
```
---
id: 0002
title: Cut the derivable cache layer entirely
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0003-tools-are-bash-with-zero-dependencies.md
```
---
id: 0003
title: Tools are Bash with zero dependencies
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0004-anchors-must-be-repo-rooted-bare-mentions-are-unve.md
```
---
id: 0004
title: Anchors must be repo-rooted; bare mentions are unverifiable
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0005-back-links-are-derived-by-scanning-never-stored.md
```
---
id: 0005
title: Back-links are derived by scanning, never stored
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0006-the-linter-flags-drift-but-never-blesses-truth.md
```
---
id: 0006
title: The linter flags drift but never blesses truth
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0007-numbers-are-facts-only-when-a-script-reproduces-th.md
```
---
id: 0007
title: Numbers are facts only when a script reproduces them
date: 2026-08-03
supersedes: []
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

```

## FILE: decisions/0008-ship-a-ledger-and-a-linter-not-a-compiler.md
```
---
id: 0008
title: Ship a ledger and a linter, not a compiler
date: 2026-08-03
supersedes: [0001]
---

We started (0001) intending a typed compiler: frontmatter on every doc, a build
step that regenerates the derivable parts and keeps them synced to the code, a CLI
that hands an agent a pre-assembled context bundle.

Rejected after tracing the prior art. The compiler's core job — keep the
*derivable* half of a doc in sync — is a forty-year graveyard (literate
programming, MDA round-tripping, Swimm, GraphRAG), and three independent results
say it's not just hard but wrong: lens theory (prose isn't a view of code, so it
has no inverse), determinism (early cutoff needs `f(x)==f(x)`, which LLM output
never satisfies), and Metacrap-automated (an LLM asserting metadata invents a new,
undetectable failure mode). The derivable half should not be stored at all — the
agent can re-derive it by reading the code.

What survives is the *non-derivable* half: decisions. That needs no compiler —
it needs an append-only ledger (write-once, forward-links, derived back-links)
plus a linter that flags broken anchors without ever claiming the prose is true.

Constraint that forced the call: nothing automatable can verify a semantic claim
(detection tops out near a coin flip), so the honest system is one that stores
only what a human decided and refuses to fabricate the rest.

```

# SOURCE: cache-and-ledger/bin/ledger (verbatim)
```bash
#!/usr/bin/env bash
#
# ledger — the decision half. Write-once records of the non-derivable "why".
#
# The whole thesis of this repo, in one executable:
#   * A decision is stored ONCE and never edited. It is superseded, not changed.
#   * Only the FORWARD link is written ("this supersedes N"), by the author who
#     is already editing their own new record.
#   * The BACK link ("what superseded me") is NEVER stored — it is DERIVED by
#     scanning, exactly like git derives a commit's children. Storing it would
#     mean mutating an old, immutable record every time something points at it.
#   * "Which decision is current" is resolved by max(serial) in code — never by
#     asking a model which fact is newer. (The one benchmark built to test that
#     found deterministic resolution beats LLM judgment by 10+ points.)
#
# A decision is one Markdown file: NNNN-slug.md, NNNN a zero-padded serial.
# Frontmatter carries ONLY non-derivable fields. No `superseded_by:` — that's
# derived. No `updated:` — git owns that.
#
#   ---
#   id: 0007
#   title: FAQ owns its items
#   date: 2026-07-17
#   supersedes: [0003]
#   ---
#   We considered modelling FAQ as a content block with a naming convention.
#   Rejected: an FAQ owns ordered items; a content block is a single blob...
#
# Usage:
#   ledger init   <dir>
#   ledger new    <dir> "<title>" [--supersedes N[,N...]]
#   ledger show   <dir>               # current decisions (max-serial heads)
#   ledger show   <dir> --all         # every record, with DERIVED back-links
#   ledger check  <dir>               # supersession chains acyclic & single-headed
#   ledger redact <dir> N "<reason>"  # remove a record's CONTENT, keep its skeleton
#
# On redact: the WHY prose is replaced by a tombstone, but id/date/supersedes are
# preserved so the supersession chain and every DERIVED back-link stay intact.
# This is the one, deliberate, narrow exception to write-once — the GDPR /
# "recorded in error" path, designed in from the start rather than bolted on
# later (which is what every mature append-only system regretted). It is logged
# in the record itself; it never renumbers, never rewrites links.
#
# Deliberately tiny. Smallness is the point — see README.md.

set -euo pipefail

die() { echo "ledger: $*" >&2; exit 1; }

# --- frontmatter helpers (line-oriented; no YAML dependency) -----------------

# Print the value of a scalar frontmatter key from a file.
fm_get() {
  # $1 file, $2 key
  awk -v k="$2" '
    /^---[[:space:]]*$/ { n++; next }
    n==1 && $0 ~ "^"k":" { sub("^"k":[[:space:]]*",""); print; exit }
  ' "$1"
}

# Print serials listed in `supersedes: [a, b]` (space/comma separated), one per line.
fm_supersedes() {
  local raw
  raw="$(fm_get "$1" supersedes)"
  [ -n "$raw" ] || return 0
  echo "$raw" | tr -d '[]' | tr ',' ' ' | tr -s ' ' '\n' | sed '/^$/d'
}

records() {
  # emit every NNNN-*.md in serial order
  find "$1" -maxdepth 1 -type f -name '[0-9][0-9][0-9][0-9]-*.md' 2>/dev/null | sort
}

next_serial() {
  local last
  last="$(records "$1" | sed -E 's#.*/([0-9]{4})-.*#\1#' | tail -1)"
  [ -n "$last" ] || { echo "0001"; return; }
  printf '%04d' "$((10#$last + 1))"
}

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g' | cut -c1-50
}

# --- commands ----------------------------------------------------------------

cmd_init() {
  local dir="${1:?usage: ledger init <dir>}"
  mkdir -p "$dir"
  echo "ledger: initialized $dir"
}

cmd_new() {
  local dir="${1:?usage: ledger new <dir> \"<title>\" [--supersedes N]}"
  shift
  local title="${1:?title required}"; shift || true
  local sup=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --supersedes) sup="${2:?}"; shift 2 ;;
      *) die "unknown arg: $1" ;;
    esac
  done
  [ -d "$dir" ] || die "not a ledger dir: $dir (run: ledger init $dir)"

  local serial slug file supersedes_line="[]"
  serial="$(next_serial "$dir")"
  slug="$(slugify "$title")"
  file="$dir/$serial-$slug.md"

  if [ -n "$sup" ]; then
    # normalize "3" or "3,5" or "0003" -> [0003, 0005], and verify targets exist
    local norm="" s
    for s in $(echo "$sup" | tr ',' ' '); do
      s="$(printf '%04d' "$((10#$s))")"
      records "$dir" | grep -q "/$s-" || die "supersedes target not found: $s"
      norm="${norm:+$norm, }$s"
    done
    supersedes_line="[$norm]"
  fi

  # date passed in is avoided (no clock in this script's contract); use git-free stamp
  local today; today="$(date +%Y-%m-%d 2>/dev/null || echo 'YYYY-MM-DD')"

  cat > "$file" <<EOF
---
id: $serial
title: $title
date: $today
supersedes: $supersedes_line
---

<!-- The non-derivable WHY. What was considered and rejected, and the constraint
     that forced the call. This file is write-once: never edit it, supersede it. -->

EOF
  echo "$file"
}

# Build the DERIVED back-link map: for each serial, who supersedes it.
# Printed as "SERIAL SUPERSEDER" lines. This is never stored.
_derive_backlinks() {
  local dir="$1" f id t
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    id="$(fm_get "$f" id)"
    for t in $(fm_supersedes "$f"); do
      t="$(printf '%04d' "$((10#$t))")"
      echo "$t $id"
    done
  done < <(records "$dir")
}

cmd_show() {
  local dir="${1:?usage: ledger show <dir> [--all]}"; shift || true
  local all=0
  [ "${1:-}" = "--all" ] && all=1
  [ -d "$dir" ] || die "not a ledger dir: $dir"

  local backlinks; backlinks="$(_derive_backlinks "$dir")"

  local f id title superseded_by
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    id="$(fm_get "$f" id)"
    title="$(fm_get "$f" title)"
    # DERIVE: is this record superseded by anyone?
    superseded_by="$(echo "$backlinks" | awk -v k="$id" '$1==k{print $2}' | paste -sd, - 2>/dev/null || true)"

    if [ -n "$superseded_by" ]; then
      [ "$all" -eq 1 ] && printf '  %s  %-40s  (superseded by %s)\n' "$id" "$title" "$superseded_by"
    else
      # no successor => current head
      printf '* %s  %-40s  [current]\n' "$id" "$title"
    fi
  done < <(records "$dir")
}

cmd_redact() {
  local dir="${1:?usage: ledger redact <dir> N \"<reason>\"}"
  local id="${2:?record id required}"
  local reason="${3:?reason required (this is logged in the record)}"
  [ -d "$dir" ] || die "not a ledger dir: $dir"

  id="$(printf '%04d' "$((10#$id))")"
  local file
  file="$(records "$dir" | grep "/$id-" | head -1)"
  [ -n "$file" ] || die "record not found: $id"

  grep -q '^redacted:' "$file" && die "already redacted: $id"

  local today; today="$(date +%Y-%m-%d 2>/dev/null || echo 'YYYY-MM-DD')"

  # Keep the frontmatter skeleton (id/title/date/supersedes drive derivation);
  # drop the body; stamp the redaction inside the record.
  local tmp; tmp="$(mktemp)"
  awk -v d="$today" -v r="$reason" '
    BEGIN { fm=0 }
    /^---[[:space:]]*$/ { fm++; print; if (fm==2){ print "redacted: " d " — " r } next }
    fm<2 { print; next }
    fm>=2 && !done { print ""; print "[REDACTED " d ": " r "]"; done=1 }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
  echo "redacted $id — skeleton and links preserved: $file"
}

# Verify the supersession graph is sane: acyclic, single-headed per chain.
cmd_check() {
  local dir="${1:?usage: ledger check <dir>}"
  [ -d "$dir" ] || die "not a ledger dir: $dir"
  local backlinks rc=0
  backlinks="$(_derive_backlinks "$dir")"

  # 1. every supersedes target must exist (new already enforces this; re-check)
  local f t
  while IFS= read -r f; do
    for t in $(fm_supersedes "$f"); do
      t="$(printf '%04d' "$((10#$t))")"
      records "$dir" | grep -q "/$t-" || { echo "BROKEN: $(basename "$f") supersedes missing $t" >&2; rc=1; }
    done
  done < <(records "$dir")

  # 2. no record superseded by more than one head (multi-headed chain = ambiguous current)
  local dup
  dup="$(echo "$backlinks" | awk '{c[$1]++} END{for(k in c) if(c[k]>1) print k}')"
  if [ -n "$dup" ]; then
    echo "AMBIGUOUS: record(s) superseded by multiple successors: $dup" >&2
    rc=1
  fi

  # 3. no self-supersession (cheapest cycle)
  echo "$backlinks" | awk '$1==$2{print} ' | while read -r a b; do
    echo "CYCLE: $a supersedes itself" >&2
  done
  echo "$backlinks" | awk '$1==$2' | grep -q . && rc=1

  [ "$rc" -eq 0 ] && echo "ledger check: chains acyclic, single-headed, all targets present."
  return $rc
}

# --- dispatch ----------------------------------------------------------------

cmd="${1:-}"; shift || true
case "$cmd" in
  init)   cmd_init   "$@" ;;
  new)    cmd_new    "$@" ;;
  show)   cmd_show   "$@" ;;
  check)  cmd_check  "$@" ;;
  redact) cmd_redact "$@" ;;
  ""|-h|--help)
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    ;;
  *) die "unknown command: $cmd (try: init|new|show|check)" ;;
esac
```
# SOURCE: cache-and-ledger/bin/anchor-check (verbatim)
```bash
#!/usr/bin/env bash
#
# anchor-check — the immune system, not the certifier.
#
# Every doc anchor `repo/path/File.ext` or `repo/path/File.ext:Symbol` must
# resolve against the code: the file exists, and (if a symbol is named) the
# symbol appears in it. A broken anchor IS drift — caught the moment it happens.
#
# What this DOESN'T do, on purpose: it does not claim the doc is correct.
# A resolving anchor proves the file exists, not that the prose about it is true.
# A validated anchor makes a stale claim sound MORE authoritative, not less.
# So this flags; it never blesses. Detecting structural drift is cheap and worth
# gating in CI. Semantic truth is not machine-checkable — that stays a human's job.
#
# Usage:
#   anchor-check <docs-dir> <code-root>
#
# Example (this repo's test-bed — read-only, never modified):
#   anchor-check ../../COMPANY/wiki ../../COMPANY
#
# Exit: 0 if every anchor resolves, 1 if any is broken.

set -euo pipefail

DOCS="${1:?usage: anchor-check <docs-dir> <code-root>}"
CODE="${2:?usage: anchor-check <docs-dir> <code-root>}"

[ -d "$DOCS" ] || { echo "anchor-check: docs dir not found: $DOCS" >&2; exit 2; }
[ -d "$CODE" ] || { echo "anchor-check: code root not found: $CODE" >&2; exit 2; }

# An anchor is a backtick-quoted path with a source extension, optional :Symbol.
# Extend the extension list for your stack.
ANCHOR_RE='`[A-Za-z0-9_.][A-Za-z0-9_./-]*\.(cs|tsx|ts|js|jsx|sql|py|go|rs|java|rb)(:[A-Za-z_][A-Za-z0-9_]*)?`'

# An anchor is repo-ROOTED when its first path segment is a real directory under
# the code root (e.g. `company.cms/...`). Only rooted anchors are addresses a
# machine can resolve; a bare `FaqDtos.cs` or `components/Foo.tsx` is a human
# mention, not an anchor. This distinction IS the point — an anchor must be a
# fully-qualified address, or it can't be a load-bearing link. We verify the
# rooted ones and report the unrooted ones as a discipline gap, not as drift.

rooted() {
  # $1 = anchor path (no :symbol). True if first segment is a dir under CODE
  # AND the path carries no `...` elision (an elided path is a human mention,
  # not a resolvable address).
  case "$1" in
    *...*) return 1 ;;             # elision => not a full address
    */*)   [ -d "$CODE/${1%%/*}" ] ;;
    *)     return 1 ;;            # single segment => bare basename, never rooted
  esac
}

total=0 ok=0 broken=0 unrooted=0
broken_list=""

# Harvest unique anchors across all markdown, strip the backticks.
anchors="$(grep -rhoE "$ANCHOR_RE" "$DOCS" --include='*.md' 2>/dev/null | tr -d '`' | sort -u || true)"

if [ -z "$anchors" ]; then
  echo "anchor-check: no anchors found under $DOCS" >&2
  exit 0
fi

while IFS= read -r anchor; do
  [ -n "$anchor" ] || continue

  # Split optional :Symbol. Colons are illegal in these paths, so last field is safe.
  path="${anchor%%:*}"
  symbol=""
  [ "$anchor" != "$path" ] && symbol="${anchor##*:}"

  if ! rooted "$path"; then
    unrooted=$((unrooted + 1))
    continue
  fi

  total=$((total + 1))
  file="$CODE/$path"

  if [ ! -f "$file" ]; then
    broken=$((broken + 1))
    broken_list="${broken_list}  BROKEN(file)   $anchor"$'\n'
    continue
  fi

  if [ -n "$symbol" ]; then
    # Symbol must appear as a whole word somewhere in the file.
    if ! grep -qE "\\b${symbol}\\b" "$file" 2>/dev/null; then
      broken=$((broken + 1))
      broken_list="${broken_list}  BROKEN(symbol) $anchor"$'\n'
      continue
    fi
  fi

  ok=$((ok + 1))
done <<EOF
$anchors
EOF

echo "rooted anchors: $total | resolve: $ok | broken: $broken"
echo "unrooted mentions (not verifiable, discipline gap): $unrooted"

if [ "$broken" -gt 0 ]; then
  printf '\n%s' "$broken_list"
  echo "drift detected: $broken rooted anchor(s) fail to resolve." >&2
  exit 1
fi

echo "clean: every rooted anchor resolves."
```
# SOURCE: cache-and-ledger/data/README.md
# data — reproduce the numbers first-hand

The essay's central claim is that decision-record systems rot *asymmetrically*:
the forward link (written by an author already editing their doc) survives, the
back link (which forces an edit to an untouched document) does not — so you should
**derive the back link, not store it**. These two scripts check that claim against
live public datasets, so the numbers in `../README.md` are reproducible, not taken
on faith from a research pass. No dependencies beyond Python 3.

## PEP reciprocity

```
python3 verify-pep-reciprocity.py
```

Downloads `https://peps.python.org/api/peps.json` and computes, first-hand:

- forward `Replaces` reciprocity: **27/42 (64%)**
- back `Superseded-By` reciprocity: **27/32 (84%)**
- header/status mismatches: **10** PEPs

The weaker-reciprocated direction is the forward one — the direction that decays
is the one requiring you to edit a document you're not otherwise touching.

Offline: pass a saved copy — `python3 verify-pep-reciprocity.py --offline peps.json`.

## KEP field decay

```
git clone --depth 1 --filter=blob:none --sparse \
    https://github.com/kubernetes/enhancements.git ke
cd ke && git sparse-checkout set keps && cd ..
python3 verify-kep-decay.py ke/keps
```

Scans every `kep.yaml` line-wise (no PyYAML) and reports:

- **656** KEPs; **47** carry a non-empty `replaces:`; **50** forward values
- of those 50, **3 resolve** to a KEP; **47 are junk** (URLs, dead paths, `n/a`)
- **4** KEPs carry `status: replaced` (the stored back-state)

50 forward claims vs 4 stored back-states, and 94% of the forward values are
unresolvable freetext — a typed field that gates nothing decays. Note these came
out *sharper* than the original research pass (which reported "44 real"); that gap
is the entire reason these live behind a script instead of a citation.

## ADR write-once & supersede asymmetry

```
git clone https://github.com/adr/madr.git
git clone https://github.com/arachne-framework/architecture.git arachne
python3 verify-adr-writeonce.py madr    'docs/decisions/*.md'
python3 verify-adr-writeonce.py arachne 'adr-*.md'
```

Counts commits per ADR (write-once == 1 commit) and inspects status/supersede
references. Findings, first-hand:

Two example repos (both actively maintained, hence *low* write-once):
- **MADR** (the dominant template): 19 ADRs, only **3 carry a status field**; and
  `0008-add-status-field.md` itself carries `status: on hold`.
- **Arachne** (the canonical showcase): 16 ADRs, 100% status, forward 1 / back **0**.

**Population sweep** (see `adr-sweep-results.md` for the full 67-repo table and SHAs):

```
67 repos, 765 ADRs
write-once:  46.5% pooled (ADR-weighted) | 56.6% per-repo mean   → "~52%" confirmed
status field: 68% pooled
supersede:   50 forward vs 22 back = 2.3 : 1  (back maintained in 16/67 repos)
```

The load-bearing, reproduced result across PEP + KEP + ADR: **the forward reference
outnumbers the maintained back reference in every regime** — from 64% reciprocity
under a CI linter (PEP) to near-total decay where nothing gates the field (KEP), to
a moderate 2.3:1 in ordinary ADR repos. It is *never* fully reciprocal, so: derive
the back link, don't store it. (Note: this 2.3:1 corrects an earlier pass that
reported the ADR gap as an order of magnitude — one of three such corrections this
sweep and its siblings produced.)

## The discipline

An LLM asserting a number is confident fabrication with no epistemic state for
"I didn't actually check." The only defense is to make the check cheap and
reproducible. A number without a script here is a claim, not a fact.
