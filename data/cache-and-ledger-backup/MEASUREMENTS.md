# What the measurements say

The essay in `README.md` argues from prior art and three public corpora. This file lists what happened
when its claims, and seven extensions of them, were tested on labelled data and with a live agent on
2026-10-13. Every number is behind a script in `data/`; details, limits and prior work are in the two
wiki pages named under each heading.

## Scorecard

| Claim | Status | Evidence |
|---|---|---|
| Decisions cannot be derived; they must be stored | Holds, strongly | An agent answers "why" questions 0–4% correctly from code alone and 88–100% with a decision ledger |
| The derivable half does not need to be stored: the agent can read the code | Holds when search is cheap | With 14 tool calls an agent answers structural questions 94–98% correctly with no documentation; no kind of documentation changes that, and documentation in the prompt costs 2–4× the prompt tokens |
| … and stored derivations are worth nothing | Too strong | With 2 tool calls: 31% without documentation, 88% with a fresh page. The value of a stored derivation is a function of how expensive derivation is |
| Stale documentation misleads | Holds, in a milder form than feared | On facts that changed, a stale page halves accuracy at 2 tool calls (50% against 96% fresh). The agent almost never asserts the outdated fact (0–4%); it relays it with a caveat (21–33%). With enough tool calls it verifies and is not misled |
| LLM output is not deterministic, so a derived cache cannot be kept valid | Overstated | Early cutoff needs equal outputs; validating a stored result against the hashes of its inputs does not (Build Systems à la Carte, §6.3). What breaks in practice is granularity: a file-level hash is invalid after one month for 46% of documented files |
| A resolving anchor proves the file exists, not that the claim is true | Holds, measured twice | Verbatim copies account for 82% of the extractions that disagree with human labels on a biomedical corpus; a "the cited code changed" note on a stale section changes no outcome measurably |
| Anchors must be repo-rooted | Holds, by accident | The same stale page gave 50% on changed facts when its code paths could be opened as written and 8% when they could not (no documentation: 29%). Unplanned comparison |
| Documentation in a folder of its own reaches the agent | Fails | In 432 structural runs the agent opened `docs/` in none; the same statements as comments in the searched tree were shown in 47 of 48 runs and raised accuracy from 31% to 65% at two tool calls |
| Store a decision once, forever | Needs one more variable: scope | In 150,904 narrator mentions a decision keyed by name alone is reused wrongly 10% of the time; keyed by name and context, 0.6%, at three times the questions |

## Seven extensions that were tried

1. **The scope of a decision is derived, not stored.** A name starts with the broadest scope and is
   tied to its context only after a contradiction is seen. With a deterministic domain rule as the
   contradiction detector this reaches about the error of the narrow key with about half the
   questions (0.179 questions and 0.013 silent errors per mention, against 0.340 and 0.006), on two
   independently labelled hadith corpora and on held-out collections. The mechanism is Ripple-Down
   Rules (1990); the application and the measurement appear to be open. **Kept.**
2. **Content-addressed decisions survive re-extraction.** When the prompt changes, 86–98% of the new
   candidates map to an existing content target; with candidate ids it is 0% by construction. **Kept.**
3. **The copy check locates the errors.** True on Arabic isnad extraction with one prompt; false on a
   human-labelled biomedical corpus, where model confidence routes as well. **Dropped as a general
   claim.**
4. **A witnessed wiki** (each derived section carries the result of re-hashing the code it was
   written from). The notes changed no measurable outcome in any arm, and did not beat a generic
   "may be outdated" sentence. File-level witnesses die within a month; symbol-level ones last
   (78% at 12 months) but were not what was tested. **Dropped at section granularity; untested at
   statement granularity.**
5. **Store the query, not the answer.** Five agents from three model families were asked for a
   storage form that is neither a graph nor a wiki, in fifteen sessions; eleven answers were some
   form of "keep a program that derives the fact from the current source at read time". Tested as
   sentences whose facts are blanks filled by `ast` selectors, written at the earlier commit: 92 of
   95 selectors still resolve six months later, and the page they produce scores 63% on the facts
   that changed at two tool calls, against 67% for the same sentences filled from the earlier code,
   50% for the stale page and 96% for a page written again. The facts it misses are checks and
   branches that did not exist when the selectors were written. **Dropped: a selector refreshes the
   value of a known fact and cannot find a fact nobody asked about.**
6. **Tell the reader what was added.** A script-made list of the 201 symbols added since the page
   was written, appended to the stale page or to the filled sentences: 58% on changed facts at two
   calls in both cases. **No effect at two calls; a hint at four (88% against 71%, interval touching
   zero).**
7. **Put the statements where the agent searches.** The fresh page cut into 234 one-line notes and
   placed as comments inside the source tree, with nothing in the prompt and no documentation
   folder. At two tool calls: 65% against 31% with nothing and 33% with the same page in `docs/`
   (+0.33 [0.15, 0.52]), for 8% more prompt tokens; the page in the prompt gives 88% for five times
   the tokens. A note showed up in a grep result in 47 of 48 runs and the notes file was opened in
   none. Notes written at the earlier commit behave like the stale page (83% on stable facts, 42% on
   changed ones), and keeping only those whose code is unchanged leaves 23%, below nothing. **Kept:
   the one extension of the day that passed the kill criteria written before the run. It moves the
   statements; it does not keep them fresh.**

## What the essay becomes

The cut still runs between what can be derived and what was decided. The measurements add a second
axis, the price of derivation at the moment of use:

- decided → store once, with the context that bounds its scope;
- derivable and cheap to derive at the moment of use → store nothing, not even a pointer;
- derivable and expensive at the moment of use → a stored derivation pays: at two tool calls a fresh
  page gives 88% against 31% with nothing, and a stale one 69%; keep its anchors openable. Nothing a
  script did to an earlier page (notes, pointers, late-bound values, a list of additions) came near
  a page written again by a reader of the current source, so the cache is regenerated, not patched.
  Where it is put matters as much as what it says: in the prompt it costs five times the tokens, in
  a documentation folder it is not opened, as one-line notes in the searched tree it arrives with
  the agent's own grep.

The second line is where the essay stood. The third is the regime of large code bases, of extraction
that costs a model call and a human review, and of any reader that cannot afford to look.

## Where each result lives

- Agent experiment, witness survival, number check: `data/agent-qa/README.md`,
  `data/witness-survival/REPORT.md`, `data/explore-number-check.py`; write-up in
  `../wiki/evaluation/wiki-for-agents-experiments.md`.
- The fifteen idea sessions and their brief: `data/idea-sessions/README.md`.
- Decision reuse, scope, copy check: `data/explore-*.py`,
  `../giraffegraph-core/evaluation/identity_ledger.py` (branch `feat/identity-ledger`); write-up in
  `../wiki/evaluation/decision-ledger-experiments.md`.

## Not yet tested

A code base large enough that search is expensive for real; a second model; statement-level witnesses
harvested from the agent's own tool calls; human-written documentation; a human reviewer in the
ledger experiments; a search tool that does not return the notes file first; decisions as notes in
the tree. From the idea sessions: standing queries for "only" and "never" claims that deliver the
difference to their baseline; stored experiments that run the code.
