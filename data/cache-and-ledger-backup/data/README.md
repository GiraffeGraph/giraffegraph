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

## Agent experiment and witness survival (2026-10-13)

`agent-qa/` holds the question-answering experiment (does stored documentation help, do nothing or
mislead an agent; 3,984 runs, including the frames whose facts are filled in from the code at read
time and the one-line notes placed inside the searched tree) and `witness-survival/` the measurement of how long the code that
documentation cites stays unchanged in eight public repositories. Each has its own README or REPORT.
`idea-sessions/` holds the brief given to five agents in three orderings and their fifteen answers.
`explore-number-check.py` checks whether the numbers in a wiki page occur in the files it cites. The
scorecard over all of it is `../MEASUREMENTS.md`.

## Exploratory replays on labelled data (2026-10-13)

Four scripts test two claims of the essay against labelled corpora: "store the decision once" and
"a machine can verify only what is a copy of the source". They are exploratory; the write-up with
every table, limit and prior-work note is `../../wiki/evaluation/decision-ledger-experiments.md`.
Paths below are relative to the workspace root.

```
python3 -I cache-and-ledger/data/explore-decision-growth.py data/eval/ar-sanad-identity/chains.jsonl
python3 -I cache-and-ledger/data/explore-scoped-ledger.py data/eval/ar-sanad-identity/chains.jsonl \
    data/eval/ar-sanad-identity/narrators.csv
python3 -I cache-and-ledger/data/explore-ledger-domains.py chains data/eval/ar-sanad-identity/chains.jsonl
python3 -I cache-and-ledger/data/explore-ledger-domains.py pubtator \
    data/raw/medmentions/corpus_pubtator.txt.gz --first-per-document
```

`explore-copy-check-bc5cdr.py` calls the Claude API (about USD 0.20 for 300 abstracts and two
prompts) and needs the `anthropic` package; responses are cached in `.cache-bc5cdr/`.

What held: in 27,056 labelled isnad chains a stored identity decision is reused many times, and
deriving the scope of a decision from contradictions (a name is tied to its context only after it has
been seen to conflict) reaches about the error of a context key with about half the questions. What
did not hold: outside hadith, unmatched extractions are mostly verbatim copies of spans the annotators
did not label, so the copy check does not locate the errors; and a neighbour-context key is reused
only where the context itself recurs.
