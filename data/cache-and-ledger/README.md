# The Cache and the Ledger

*Why LLM-maintained knowledge bases keep failing, and the one shape that doesn't.*

---

I set out to build a thing a lot of people are building right now: a knowledge base an LLM both writes and reads. Typed docs, a compiler that keeps them honest against the code, a CLI that hands an agent exactly the context it needs so it stops flailing through `glob`/`grep`/`read` on every task. The pitch writes itself. Context bloat is real, agents waste turns rediscovering the same files, and a well-kept knowledge layer sounds like the fix.

I spent about a million tokens of research trying to break the idea before building it. It broke. But it broke in a specific, useful way — it split cleanly into one half that is a forty-year graveyard and one half that five unrelated systems independently reinvented. This is the writeup.

The one-sentence version:

> **If a fact can be derived from a source of truth, it is a cache — don't store it, regenerate it. If it cannot be derived, it is a decision — store it, once, forever. Almost every failed knowledge system failed by confusing the two.**

---

## The thing everyone actually wants

State it plainly, because the wanting is legitimate. You want a knowledge layer that:

- an LLM maintains, so humans don't rot it;
- never bloats the context window with noise;
- is as deterministic as possible, with the irreducibly fuzzy part — and *only* that part — left to the model;
- answers questions *and* gets written as a byproduct of work.

Nothing about that is unreasonable. The trouble starts the moment you try to make one artifact do all of it, because the artifact contains two kinds of sentence that have opposite physics.

---

## Two kinds of sentence

Take one real doc from a real codebase — a page describing an FAQ feature. It contains sentences like these:

**Derivable:**
- "Storage is `B2C_Faq` plus a localization table, with items in `B2C_FaqItem`."
- "The controller lives at `Controllers/Cms/B2C/FaqController.cs`."
- "It reuses the shared rich-text sanitizer."

**Not derivable:**
- "FAQ is a dedicated entity that *owns its items* — it is deliberately **not** a content block with a convention on top."

The first three are re-derivable from the code. If the doc and the code disagree, the code wins, trivially, and a machine can regenerate the sentence from scratch. They are a **cache** of the code.

The last one cannot be recovered from the code, because the code does not contain the road not taken. "We considered making this a content block and rejected it" is *intent*. It lives nowhere in the artifact it describes. It is a **decision**.

Once you see the split, you can't unsee it, and it explains every failure below.

| Symptom | What actually happened |
|---|---|
| Kubernetes KEP `replaces:` — of 50 forward values, **3 resolve**, 47 are junk (URLs, dead paths) | a typed field that gates nothing decays into freetext |
| Python PEP back-links **64% reciprocal** (27/42) | `Superseded-By` was derivable, stored anyway |
| Doc `updated:` dates silently lie | git already knows; copied anyway |
| Literate programming died | narrative "how it works" was derivable, hand-written anyway |
| ADRs write-once ~47–57% (67 repos, 765 ADRs) | **not a bug — correct.** Decisions don't change; they get superseded |

That last row is the tell. When people first measure ADR repos and find half the records are never edited after creation, they read it as neglect. It isn't. A decision *should* be write-once. The things that rot are the things that were derivable and got frozen into storage anyway.

---

## Why the cache half is a graveyard

I went looking for anyone who made "LLM keeps the derivable half in sync" actually work. Here is the tour.

**Literate programming (1984–).** Knuth's own 1984 paper pre-conceded the adoption problem, and the failure repeats for forty years with suspicious regularity: pbrt ships plain C++ and writes the literate book separately; lcc's living version diverged from its literate one; Axiom ripped out its literate tooling in 2014; TeX is literate *and deliberately frozen*. The pattern is unmistakable — **literate coupling survives exactly where change stops.** Eve, the strongest literate system ever built, removed every tooling excuse (no tangle step, live, treated prose/code mismatch as a compile error) and still failed on the only thing that mattered: *"people didn't actually like writing a bunch of prose."* Coupling docs to code doesn't fail because the coupling breaks. It fails because the coupling holds — it taxes the one thing you most want to stay cheap, refactoring.

**Swimm ($33M, patented auto-sync).** The closest commercial attempt. Its anchoring is fuzzy diff-matching with git-blame as a tiebreaker; above a change threshold it gives up and flags the doc "Outdated" for a human. It did not solve the rename problem — it built a triage queue around it. Five years, no Series B, and its homepage now sells *"agentic modernization"* consulting with "senior engineers to catch what tools miss." The strongest evidence against the model is Swimm's own current homepage: they re-inserted the human as the product.

**DeepWiki, Mintlify, Cursor docs (LLM-generated).** No vendor — first-party or independent — claims anyone treats these as ground truth without human review. Every one hedges to "draft, then review." One independent audit of DeepWiki found factual errors in every section examined and a setup instruction to install a **VS Code extension that does not exist**. Confident and wrong is worse than stale: a stale doc degrades gracefully because you half-trust it; a fluent hallucination you fully trust.

**GraphRAG (Microsoft).** Building the index costs ~375× a plain vector index [research figure — verify before publishing]. The global-summary architecture means one new document can force re-summarizing communities it never touched — an invalidation cascade. Microsoft closed the incremental-update issue in January 2026 with, essentially, *we're not building this; re-index and rely on the cache.* Their own fix, LazyGraphRAG, defers all the LLM work to query time — i.e. removes the cache.

**Agent memory (Mem0, Zep, Letta…).** A 32-day production audit of one system found **97.8% junk** — including a hallucinated "prefers Vim" fact that the pipeline re-ingested from its own memory into 808 duplicates. That feedback loop is exactly the shape of "an LLM that both writes and reads its own store."

And underneath all of it, the base rate: independent measurement puts even GPT-4 code comments at **~20% factually wrong** [research figure — verify], and automated detection of whether generated prose is hallucinated tops out around ROC-AUC 0.6 — barely above a coin flip. You cannot cheaply verify the cache you are generating.

---

## Three reasons the cache half is not just hard but wrong

The graveyard is empirical. Three independent results say it's structural.

**1. Lens theory.** The database "view-update problem" (1981) and Pierce's lens laws formalize when a derived view can be edited and pushed back to its source. The condition is strict, and prose documentation fails it structurally, not just in practice: docs are not a lossy-but-recoverable view of code — they *add* information (rationale, tradeoffs) that isn't in the code at all. A transform that isn't even a function of its source has no inverse to invert. The one place teams achieve real sync (Fern generating API docs from an OpenAPI schema) works by **eliminating the human edit surface** — the doc becomes a pure regenerable projection with no independent content. That is the cache/decision split, restated by the theory: derivable views can be kept in sync by *deleting them and regenerating*; anything with independent content cannot.

**2. Determinism.** Every incremental build system that avoids redundant work — Bazel, Salsa (rust-analyzer), Roslyn's incremental generators — relies on *early cutoff*: recompute a node, and if the new output equals the old, stop the invalidation there. The rustc docs state the precondition as a hard requirement: same inputs *must* yield the same output "or else the compiler is not deterministic." An LLM does not clear that bar. It does not emit byte-identical prose for identical input, so the equality check never fires, and cutoff silently degrades to *recompute everything, every time*. There is no published system doing principled early cutoff over non-deterministic outputs. "Semantically equal even if not byte-equal" exists only as best-effort LLM caching that knowingly serves wrong answers for latency — precisely what a correctness-bearing knowledge base cannot accept.

**3. Metacrap, automated.** Doctorow's 2001 "Metacrap" lists seven reasons self-asserted metadata is unreliable. An LLM asserting the metadata kills the shallow four (it isn't lazy, has no incentive to lie) — but leaves the deep three untouched (a schema still isn't neutral; there's still more than one way to describe a thing) and *invents an eighth*: confident fabrication with no epistemic state corresponding to "I don't actually know this." A lying human knows they lied. A lazy human knows they skipped it. The model's errors correlate with no legible signal — they're statistically indistinguishable in surface form from correct output — which makes them *harder* to catch than the human failure modes we built filters for.

---

## Why the decision half is solid

Now the other half — and the surprise. The "store only decisions, write-once, forward-links-only, derive the back-links, resolve supersession by rule not judgment" design is not something I invented. Five unrelated lineages converged on it under different pressure, which is about as strong as design evidence gets.

- **Datomic** implements "store the forward reference, derive the reverse on the fly" as a *language feature*, and documents it in almost those exact words.
- **Git** stores each commit's parent pointer and derives "children" by scanning — because storing the reverse "would undermine the immutability of past commits."
- **IETF RFCs**: the new document declares what it `Obsoletes`; the old document is *never touched*, and "obsoleted-by" lives only in a derived index.
- **ADRs** (Nygard): you don't edit an accepted record; *"the truth of the architecture is the full chain, not the latest one."*
- **Double-entry bookkeeping**, 13th century: entries are append-only, and **balances are never stored** — they're summed on demand, because storing them invites divergence. "Accountants don't use erasers."

The shared move every time: **never store a derived value next to its source.** Store the forward-written, non-derivable fact; compute everything else. It's the same instinct as computing an account balance instead of caching it.

**The asymmetry is real, and it's measured first-hand — but its magnitude depends on the regime.** The forward link (written by an author already in the file) survives; the back link (an edit to a document you're not otherwise touching) lags. How much it lags tracks how hard the process gates the field:

| Dataset | forward | back / reciprocity | regime |
|---|---|---|---|
| Python PEPs (733) | 42 `Replaces` | 27 reciprocated — **64%** | CI linter checks the header |
| Kubernetes KEPs (656) | 50 `replaces` (3 resolve) | 4 `status: replaced` | field gates nothing → near-total decay |
| ADR population (67 repos, 765) | 50 forward | 22 back — **2.3 : 1** | ordinary hand-kept records |

So the gap is not the order-of-magnitude one an earlier research pass reported ("back-links ~3.7%, forward far more common") — across a real 67-repo ADR population the forward reference is only ~2.3× the back, and back-references *are* genuinely maintained in 16 of 67 repos. **But in every regime the back-link is incompletely maintained** — 36% missing even under a linter, almost entirely gone where nothing checks it. That is the whole argument for *deriving* the back-link instead of storing it: derive it and it is 100% by construction, in every regime, for free.

And it explains the one number that looked like decay. In the most disciplined decision system in existence — Python PEPs — the forward link (`Replaces`, written by the author already editing their doc) reciprocates at **27/42 (64%)**, while the back-link direction (`Superseded-By`, requiring you to go edit a document you're not otherwise touching) sits at 84% — with 10 PEPs carrying a `Superseded-By` header while their status disagrees. The weaker-reciprocated direction is exactly the one that forces an edit to an untouched document. The fix isn't discipline. It's to **stop storing the back-link and derive it** — then the gap cannot exist by construction.

*(That 64% is not taken on faith. `data/verify-pep-reciprocity.py` downloads the public PEP dataset and computes it first-hand — 733 PEPs, 42 forward relations across 36 PEPs, 27 reciprocated. Re-run it and you get the same number, or a newer one.)*

---

## The taxes you actually sign up for

Convergence doesn't mean free. Append-only, decision-only systems have a well-documented bill, and honesty requires naming it:

- **Schema evolution is a permanent tax.** The moment you add a field non-authors must interpret, you owe an upcaster, forever. Every mature event-sourced system pays this.
- **Deletion collides with reality.** "Never delete" meets GDPR and "this was recorded in error." Datomic's excision triggers massive index rewrites and its own team says use it rarely. Design the redaction path *before* you need it, because every system that didn't, bolted it on later at real cost. `bin/ledger redact` is that path: it tombstones a record's content while preserving its id and supersession links, so every derived back-link survives — the one narrow write-once exception, designed in, not bolted on.
- **No free self-check.** Double-entry catches its own corruption only because the domain has an invariant (debits = credits). Decisions have no such checksum. If you want "the system catches its own rot," you build it deliberately — e.g. a validator that supersession chains stay acyclic and single-headed.

These are affordable at decision-log volume. They are not zero.

---

## What this leaves you building

Strip everything the research killed and here's the residue — deliberately tiny, and small *is the point*:

1. **A decision log.** Write-once records of the non-derivable "why." Forward links only. Supersession resolved by `max(serial)` in code, never by asking a model which fact is newer — because the one benchmark built to test that ("don't ask the LLM to track freshness") found deterministic resolution beats LLM judgment by 10+ points, widening under load.

2. **Do not store the derivable half at all.** Let the agent read the code. On code, agentic `grep`/`read` is competitive precisely because code has structure to exploit — unique identifiers, call graphs. (Caveat worth stating: that structure is exactly what docs *lack*, so retrieval over a prose corpus is a genuinely harder and more open question than "just grep it." But the corpus that survives here — decisions — is small.)

3. **An immune system, not a certifier.** The one automatable check is cheap and worth running in CI: does every `file:symbol` anchor still resolve? But resolving proves the file exists, not that the claim is true — and a *validated* anchor makes a stale claim sound **more** authoritative, not less. So it flags, it doesn't bless. Detecting drift is a solved research problem (~90%+); preventing it without a human is not. Budget drift as expected maintenance, not a bug to engineer away.

Everything else — typed frontmatter migrations, a `related:` graph, stored `updated:` fields, an LLM-regenerated cache, semantic-equality invalidation — is a thing someone already tried and buried. The residue is a ledger and a linter. That's the whole product, and its smallness is the finding.

---

## Run it

Two Bash scripts, no dependencies. `bin/anchor-check` is the immune system; `bin/ledger` is the decision log. Point them at a real repo.

```
$ bin/anchor-check path/to/wiki path/to/code-root
rooted anchors: 315 | resolve: 315 | broken: 0
unrooted mentions (not verifiable, discipline gap): 296
clean: every rooted anchor resolves.
```

That output is the whole thesis in three lines. On a real 120-doc wiki, **315 code references are fully-qualified addresses and every one resolves** — but **296 more are bare mentions** (`FaqDtos.cs`, `components/Foo.tsx`), which no machine can verify because they aren't addresses. Anchor discipline exists in theory and is half-kept in practice, and the tool tells you exactly which half. It flags a broken *address* as drift (exit 1); it stays silent on truth, because truth isn't machine-checkable.

```
$ bin/ledger new decisions/ "FAQ owns its items" --supersedes 2
$ bin/ledger show decisions/ --all
* 0001  Media stored as path hierarchy            [current]
  0002  FAQ modelled as content block             (superseded by 0004)
* 0004  FAQ owns its items                        [current]

$ grep -rl superseded_by decisions/     # nothing — back-links are derived, never stored
```

The `(superseded by 0004)` on record 2 was never written into any file. Record 2 is immutable; nobody edited it when 4 arrived. The back-link is *derived by scanning*, exactly like Git derives a commit's children — which is why the PEP-style 36% reciprocity gap cannot exist here by construction.

---

## Coda

I started wanting a clever compiler. I ended with an accountant's ledger and a `grep` loop in CI. The disappointment is the result: the interesting move wasn't a mechanism, it was a *cut* — the line between what a machine can re-derive and what only a human ever decided. Everything on the derivable side wants to be recomputed, not stored. Everything on the decision side wants to be stored once and never touched. The forty-year graveyard is full of systems that ran that line through the middle of a single artifact and then spent themselves trying to keep both halves in sync.

Don't keep them in sync. Keep them apart.

---

### On the numbers

Three tiers, honestly labelled:

- **Verified first-hand, reproducible.** Four scripts, all against live data or a real repo, all re-runnable:
  - `bin/anchor-check` — 315/315 rooted anchors resolve vs 296 unverifiable bare mentions (real 120-doc wiki); 8/8 ADR statuses at 1/1 reciprocity in that wiki.
  - `data/verify-pep-reciprocity.py` — 733 PEPs; forward reciprocity 27/42 (64%), back 27/32 (84%), 10 header/status mismatches.
  - `data/verify-kep-decay.py` — 656 KEPs; 50 forward `replaces` values, only 3 resolvable, vs 4 `status: replaced`.
  - `data/verify-adr-writeonce.py` + the 67-repo sweep in `data/adr-sweep-results.md` — 765 ADRs across 67 repos: write-once **46.5%** pooled / **56.6%** per-repo (the "~52%" claim sits between them, confirmed), 68% carry a status field, and **50 forward vs 22 back** supersede references (2.3:1) with every SHA recorded for replay.

  Three of these came out *different from* the research pass, each caught by re-measuring: the KEP decay was sharper (3/50 resolvable, not "44 real"); MADR's status count was 3/19 not 1/19 (the agent even claimed ADR-0008 "Add Status Field" carries no status — it carries `status: on hold`); and the ADR supersede asymmetry is 2.3:1, **not** the order-of-magnitude "3.7% back-links" the pass reported. That is three fabrication-shaped errors from an automated pass, all corrected only because the numbers live behind scripts.
- **Agent-reported, not yet re-verified** (marked "verify before publishing"): GraphRAG's ~375× index cost; the ~20% comment-error rate. These remain claims until a script reproduces them.
- **The discipline this enforces:** an LLM asserting a number is Metacrap obstacle #8 — confident fabrication with no epistemic state for "I didn't actually check." The only defense is to make the check cheap and reproducible, which is what the scripts are for. Everything not behind a script stays a claim, not a fact.

---

## What's in here

```
README.md   this essay
PAPER.md    the same argument as an empirical note (arXiv-shaped draft)
MEASUREMENTS.md   what held and what did not when the claims were tested on labelled data and a live agent
bin/
  anchor-check   the immune system — flags broken code anchors, never blesses truth
  ledger         the decision log — write-once, forward-links, derived back-links, redact
data/
  verify-pep-reciprocity.py   PEP forward/back reciprocity, live dataset
  verify-kep-decay.py         KEP typed-field decay
  verify-adr-writeonce.py     ADR write-once + supersede asymmetry
  README.md                   how to reproduce every number
decisions/  this project's own decisions, kept in its own ledger (dogfood)
test.sh     every tool control paired with its falsifier (15 checks)
```

Run the tools' self-test: `./test.sh` (15 passed, 0 failed — each control has a paired failure case, because a check that cannot fail only looks like it works).
