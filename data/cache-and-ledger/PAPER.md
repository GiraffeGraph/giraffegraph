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
