#!/usr/bin/env bash
#
# test.sh — the tools must pass their own falsifiers.
#
# One of this project's recorded decisions (0007) is "numbers are facts only when
# a script reproduces them." The same rule applies to the tools: every control
# here is paired with the case that proves it can FAIL. A check that cannot fail
# reports clean because it is blind, which only looks like working.
#
# Self-contained: builds its own fixtures in a temp dir; needs nothing external.
# Run:  ./test.sh   (exit 0 = all pass)

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ANCHOR="$HERE/bin/anchor-check"
LEDGER="$HERE/bin/ledger"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0 fail=0
ok()   { printf '  PASS  %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  FAIL  %s\n' "$1"; fail=$((fail+1)); }
# expect <exit-wanted> <label> -- <command...>
expect() { local want="$1" label="$2"; shift 3; "$@" >/dev/null 2>&1; local got=$?; [ "$got" -eq "$want" ] && ok "$label (exit $got)" || bad "$label (wanted $want, got $got)"; }

echo "anchor-check"
# fixture: a tiny code root + a doc with one good rooted anchor
mkdir -p "$TMP/code/pkg/sub" "$TMP/docs"
echo 'class Foo {}' > "$TMP/code/pkg/sub/Foo.cs"
printf '# d\nSee `pkg/sub/Foo.cs:Foo`.\n' > "$TMP/docs/a.md"
expect 0 "clean repo resolves" -- "$ANCHOR" "$TMP/docs" "$TMP/code"
# falsifier 1: dead file path must fail
printf '# d\nSee `pkg/sub/Gone.cs`.\n' > "$TMP/docs/b.md"
expect 1 "dead file path -> drift" -- "$ANCHOR" "$TMP/docs" "$TMP/code"
rm "$TMP/docs/b.md"
# falsifier 2: present file, absent symbol must fail
printf '# d\nSee `pkg/sub/Foo.cs:NoSuchSymbol`.\n' > "$TMP/docs/c.md"
expect 1 "missing symbol -> drift" -- "$ANCHOR" "$TMP/docs" "$TMP/code"
rm "$TMP/docs/c.md"
# control: a bare mention is NOT counted as drift (unrooted, skipped)
printf '# d\nWe touch `Foo.cs` somewhere.\n' > "$TMP/docs/d.md"
expect 0 "bare mention -> not drift" -- "$ANCHOR" "$TMP/docs" "$TMP/code"
rm "$TMP/docs/d.md"

echo "ledger"
D="$TMP/dec"
expect 0 "init" -- "$LEDGER" init "$D"
"$LEDGER" new "$D" "First decision" >/dev/null
"$LEDGER" new "$D" "Second decision" >/dev/null
"$LEDGER" new "$D" "Replaces the first" --supersedes 1 >/dev/null
# derived back-link: record 1 must show as superseded, and NOT be a current head
if "$LEDGER" show "$D" --all | grep -q '0001.*superseded by 0003'; then ok "back-link derived"; else bad "back-link derived"; fi
if "$LEDGER" show "$D" | grep -q '0001'; then bad "superseded hidden from heads"; else ok "superseded hidden from heads"; fi
# nothing stores its own back-link
if grep -rq 'superseded_by' "$D" 2>/dev/null; then bad "back-link not stored"; else ok "back-link not stored"; fi
expect 0 "check clean chain" -- "$LEDGER" check "$D"
# falsifier: supersede a missing target must fail
expect 1 "supersede missing target -> fail" -- "$LEDGER" new "$D" "bad" --supersedes 99
# falsifier: ambiguous chain (two heads supersede #2) must fail check
"$LEDGER" new "$D" "supersedes 2 A" --supersedes 2 >/dev/null
"$LEDGER" new "$D" "supersedes 2 B" --supersedes 2 >/dev/null
expect 1 "ambiguous chain -> check fails" -- "$LEDGER" check "$D"

echo "ledger redact"
R="$TMP/red"
"$LEDGER" init "$R" >/dev/null
"$LEDGER" new "$R" "Sensitive decision" >/dev/null
"$LEDGER" new "$R" "Supersedes it" --supersedes 1 >/dev/null
"$LEDGER" redact "$R" 1 "recorded in error" >/dev/null
# content gone, skeleton kept, chain intact
if grep -q 'REDACTED' "$R"/0001-*.md; then ok "content tombstoned"; else bad "content tombstoned"; fi
if grep -q '^id: 0001' "$R"/0001-*.md && grep -q '^supersedes' "$R"/0002-*.md; then ok "skeleton + links preserved"; else bad "skeleton + links preserved"; fi
if "$LEDGER" show "$R" --all | grep -q '0001.*superseded by 0002'; then ok "derived link survives redaction"; else bad "derived link survives redaction"; fi
# falsifier: double-redact refused
expect 1 "double-redact refused" -- "$LEDGER" redact "$R" 1 "again"

echo
echo "── $pass passed, $fail failed ──"
[ "$fail" -eq 0 ]
