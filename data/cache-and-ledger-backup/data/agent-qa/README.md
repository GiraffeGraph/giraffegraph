# Agent question answering: when does stored documentation help, do nothing, or mislead?

Run on 2026-10-13. A Claude Haiku 5.5 agent (effort `low`) answers 36 questions about the backend of
`giraffegraph-core` (141 Python files, 16,923 lines at commit `bfb0f9c`) with three read-only tools
(`list_dir`, `read_file`, `grep`). Conditions differ only in the files placed in the sandbox's `docs/`
folder. 2,880 runs, 2 repetitions per cell, judged by the same model against a written key, blind to
the condition.

## Questions (`questions.json`)

12 per class, written and verified against the code by a separate agent that never saw the
documentation pages under test.

- `stable`: a behavioural fact with the same answer at commit `4279c98` (2026-04-05) and at `bfb0f9c`.
- `changed`: a behavioural fact whose answer differs between those two commits.
- `decision`: a "why" whose answer is in the ADRs and rule sections, not in the code.

## Documentation variants

- `decisions.md`: 30 decisions with rationale, no derivable facts (2,196 words).
- `inputs/behaviour-current-commit.md` ("fresh", 1,754 words) and
  `inputs/behaviour-earlier-commit.md` ("stale", 1,981 words): two pages written by two agents with
  the same prompt and outline, one from each commit's source tree, each section ending with the code
  slices it rests on. The stale page is a faithful description of code that has since changed.
- Witness note: under each section heading, the result of comparing the cited slices with the current
  tree (a slice is unchanged when its text still occurs verbatim in the same file). 9 of the 10
  sections of the stale page have at least one changed slice; all slices of the fresh page are
  unchanged (`build.json`).
- Generic note: the same sentence under every heading ("this section may be outdated, verify").
- Symbol map: file → classes, methods, functions, generated with `ast` from either commit.
- Pointers: the page's headings and cited slices only, no statements (216 words).

## Arms

`pull`: the agent has to open `docs/` itself. `push`: the docs are also in the system prompt.
`plain`: the system prompt does not say that documentation may be outdated. `budgetN`: at most N tool
calls (default 14). `rooted`: cited slices are written as sandbox paths (`src/app/...`), so they can
be opened as given; in the other arms they are relative to `src/app/`.

## Results

Share of correct answers; mean over questions of the per-question mean over repetitions; 95%
percentile bootstrap over questions in brackets (`analysis.json`).

Full tool budget (14 calls):

| docs/ contains | structural, pull | structural, push | decision, pull | decision, push | prompt tokens per structural question, push |
|---|---|---|---|---|---|
| nothing | 0.979 [0.94, 1.00] | 0.938 [0.85, 1.00] | 0.042 | 0.000 | 21,843 |
| decisions | 0.938 | 0.979 | 1.000 | 0.958 | 45,343 |
| decisions + fresh page | 0.979 | 0.958 | 1.000 | 0.917 | 57,825 |
| decisions + stale page | 0.896 | 1.000 | 0.875 | 0.958 | 75,443 |
| + witness notes on the stale page | 0.938 | 0.938 | 0.958 | 0.958 | 90,303 |
| + generic note on the stale page | 0.979 | 0.979 | 0.958 | 0.958 | 76,700 |

In `pull` the agent made no call into `docs/` in any of the 432 structural runs; for decision
questions it made 2.0 to 2.5 such calls per question. Without the "may be outdated" sentence (`push+plain`) the
structural results are the same (0.94 to 0.98).

Restricted tool budget, `push`, structural questions, rooted paths:

| docs/ contains | 2 calls: all | stable | changed | 4 calls: all | stable | changed |
|---|---|---|---|---|---|---|
| nothing | 0.312 [0.15, 0.48] | 0.375 | 0.250 | 0.750 [0.60, 0.88] | 0.708 | 0.792 |
| fresh page | 0.875 [0.75, 0.98] | 0.792 | 0.958 | 0.979 [0.94, 1.00] | 0.958 | 1.000 |
| fresh pointers only | 0.604 [0.44, 0.75] | 0.542 | 0.667 | 0.833 | 0.833 | 0.833 |
| stale page | 0.688 [0.50, 0.85] | 0.875 | 0.500 | 0.812 | 0.917 | 0.708 |
| stale page + witness notes | 0.708 [0.58, 0.83] | 0.833 | 0.583 | 0.792 | 0.875 | 0.708 |
| stale page + generic note | 0.667 [0.48, 0.83] | 0.917 | 0.417 | 0.833 | 0.917 | 0.750 |
| stale pointers only | 0.500 [0.33, 0.67] | 0.500 | 0.500 | 0.792 | 0.750 | 0.833 |

Paired difference to "nothing" at 2 calls: fresh page +0.56 [0.38, 0.75]; stale page +0.38
[0.13, 0.63]; at 4 calls: fresh +0.23 [0.10, 0.38]; stale +0.06 [-0.10, 0.23].

Same budget of 2 calls with cited paths that cannot be opened as written (`push+budget2`): the stale
page gives 0.083 on changed questions (nothing: 0.292), with or without witness notes.

How the stale page fails: of the changed-question answers at 2 calls (rooted), 0 to 4% assert the
outdated behaviour as fact, 21 to 33% report it and say it could not be verified.

## Late-bound frames and a list of added symbols

A second round on the same day tests whether a description written at the earlier commit can be
refreshed by a script, without a model reading the current code.

- Frames (`cloze.py`, `inputs/frames-earlier-commit.json`): 58 sentences with 95 blanks, written by
  an agent that saw only the tree at `4279c98` and the ten section headings, not the questions. A
  sentence may not contain an identifier, number or literal; each blank is a selector
  (`path.py::Class.method`) with a reducer that `ast` evaluates. Filled against `4279c98` the page
  has 2,086 words (`frozen`); filled against `bfb0f9c` 92 of the 95 blanks resolve, one of them in
  another file, 3 sentences are withdrawn, and the page has 2,010 words (`live`).
- Added symbols (`added_symbols.py`): the 201 classes, functions and methods that exist at
  `bfb0f9c` and not at `4279c98` (800 against 995 symbols), as name:line per file, 320 words,
  appended to a page.

`push`, rooted paths, structural questions, 2 repetitions (384 runs):

| docs/ contains | 2 calls: all | stable | changed | 4 calls: all | stable | changed |
|---|---|---|---|---|---|---|
| stale page (from above) | 0.688 | 0.875 | 0.500 | 0.812 | 0.917 | 0.708 |
| stale page + added symbols | 0.771 [0.58, 0.92] | 0.958 | 0.583 | 0.875 | 0.875 | 0.875 |
| frames, frozen | 0.708 [0.54, 0.85] | 0.750 | 0.667 | 0.854 | 0.875 | 0.833 |
| frames, live | 0.792 [0.65, 0.92] | 0.958 | 0.625 | 0.896 | 0.958 | 0.833 |
| frames, live + added symbols | 0.750 [0.60, 0.88] | 0.917 | 0.583 | 0.917 | 0.917 | 0.917 |
| fresh page (from above) | 0.875 | 0.792 | 0.958 | 0.979 | 0.958 | 1.000 |

Paired differences on the 12 changed questions at 2 calls: live frames against the stale page
+0.13 [-0.13, 0.42]; live against frozen frames -0.04 [-0.25, 0.17]; fresh page against live frames
+0.33 [0.08, 0.63]; stale page with added symbols against the stale page +0.08 [0.00, 0.25]. On the
12 stable questions live against frozen frames is +0.21 [0.00, 0.42].

The kill criteria were written before the runs: live frames at or below 0.667 on changed questions
at 2 calls (the level of a pointers-only page), or a paired interval against the stale page that
includes 0. Both happened. Filling the blanks from the current tree did not help on the facts that
changed. The changed questions the live page misses (C01, C09, C12, and partly C03, C07, C10) ask
about checks and branches that were added after the frames were written; no blank points at them.
Naming the added symbols did not close the gap at 2 calls either. Prompt tokens per question at 2
calls: 43,491 for live frames, 34,420 for the fresh page.

Cost of this round: about USD 0.75 (agent runs 0.68).

## Notes inside the tree the agent searches

A third round tests where the stored statements are put. Both behaviour pages were rewritten by an
agent that saw only the page into one-line notes of at most 130 characters, each with the symbols
it is about (`inputs/notes-current-commit.json`, 234 notes; `inputs/notes-earlier-commit.json`, 214
notes). `scholia.py` places them in a sandbox whose `docs/` says there is no documentation:

- `file`: all notes as comment lines in `src/app/_scholia.py`, each ending with a rooted path and
  line; 142 of the 234 current notes resolve to a symbol.
- `woven`: the 142 resolved notes as comments directly above their symbol, the other 92 in the file.
- `earlier`: the 214 notes written from the earlier page, as a file.
- `earlier, valid only`: of those, the 69 whose symbols have the same source text at both commits.

`pull` (nothing in the prompt), structural questions, 2 repetitions, 720 runs with the controls:

| the sandbox contains | 2 calls: all | stable | changed | 4 calls: all | 14 calls: all | prompt tokens at 2 / 14 calls |
|---|---|---|---|---|---|---|
| nothing | 0.312 [0.17, 0.48] | 0.333 | 0.292 | 0.708 | 0.979 | 6,911 / 20,435 |
| fresh page in `docs/` | 0.333 [0.17, 0.52] | 0.417 | 0.250 | 0.708 | 0.979 | 6,854 / 22,718 |
| notes, file | 0.646 [0.46, 0.81] | 0.667 | 0.625 | 0.875 | 0.938 | 7,472 / 16,611 |
| notes, woven | 0.521 [0.35, 0.69] | 0.500 | 0.542 | 0.812 | 0.958 | 7,154 / 17,938 |
| earlier notes, file | 0.625 [0.46, 0.77] | 0.833 | 0.417 | 0.792 | | 7,595 |
| earlier notes, valid only | 0.229 [0.08, 0.40] | 0.250 | 0.208 | 0.625 | | 6,767 |
| fresh page in the prompt (`push`, from above) | 0.875 | 0.792 | 0.958 | 0.979 | | 34,420 |
| the 234 notes in the prompt (`push`) | 0.792 [0.65, 0.92] | 0.708 | 0.875 | | | 45,482 |

Paired differences at 2 calls, 24 questions: notes file against nothing +0.33 [0.15, 0.52]; against
the same page in `docs/` +0.31 [0.13, 0.50]; woven against nothing +0.21 [0.06, 0.35]; file against
woven +0.13 [-0.04, 0.29]; page in the prompt against notes file +0.23 [0.04, 0.42]; notes in the
prompt against page in the prompt -0.08 [-0.17, 0.00]. Earlier notes against nothing: +0.50
[0.21, 0.79] on stable questions, +0.13 [0.00, 0.25] on changed ones. Valid-only earlier notes
against nothing -0.08 [-0.19, 0.00]. At 14 calls notes file against nothing -0.04 [-0.10, 0.00],
with 4.1 tool calls per question against 5.0.

A note appeared in a tool result in 47 of 48 runs at 2 calls (file and woven alike; 41 of 48 for the
valid-only notes), and the notes file was read directly in 0 of them: the notes arrive as hits of
the greps the agent runs anyway. With the earlier notes, 4% of the answers to changed questions
assert the outdated behaviour and 25% relay it with a caveat; with the valid-only notes 0% and 4%.

The four kill criteria were written before the runs: a gain over nothing below +0.28 or with an
interval that includes 0; a note shown in fewer than half the runs; more than 4% outdated assertions
with the valid-only notes; more than 1.2 times the prompt tokens of nothing at 14 calls. The file
form passes all four. The woven form is below +0.28.

What this shows: the same statements are worth nothing in `docs/` when the agent has to open them,
and +0.33 in the search path, for 8% more prompt tokens; putting the page in the prompt gives more
(+0.56) for five times the tokens. Withholding the notes whose code changed removes the gain.

What it does not show: the harness `grep` returns files in path order, so `_scholia.py` comes
before the code and its hits are never cut off by the 40-line limit; a tool with another order may
bury them. The woven form does not depend on that order for its 142 notes and gains less.

Cost of this round: about USD 0.8 (agent runs 0.68).

## Does the note result survive another file order, another model, and decisions?

A fourth round. `--grep-order shuffled` makes `grep` walk the files in an order seeded by the call,
so the notes file is not returned first. `--model claude-sonnet-5-5` runs the agent on a second
model (the judge stays the same). The decision ledger was rewritten into 139 one-line notes
(`inputs/notes-decisions.json`, no symbols, so all of them sit in `src/app/_scholia.py`). `pull`,
2 repetitions, 720 runs.

Structural questions (24), share correct:

| grep order, model | calls | nothing | notes, file | notes, woven | file against nothing | runs showing a note (file / woven) |
|---|---|---|---|---|---|---|
| path order, Haiku (from above) | 2 | 0.312 | 0.646 | 0.521 | +0.33 [0.15, 0.52] | 47 / 47 of 48 |
| shuffled, Haiku | 2 | 0.417 [0.25, 0.60] | 0.458 [0.29, 0.62] | 0.479 [0.31, 0.65] | +0.04 [-0.15, 0.23] | 22 / 43 of 48 |
| shuffled, Haiku | 4 | 0.604 [0.42, 0.79] | 0.771 [0.62, 0.90] | 0.708 [0.56, 0.85] | +0.17 [0.00, 0.35] | 28 / 44 of 48 |
| path order, Sonnet 5.5 | 2 | 0.521 [0.33, 0.71] | 0.771 [0.60, 0.92] | | +0.25 [0.08, 0.44] | 47 of 48 |

Decision questions (12), share correct:

| grep order | calls | nothing | `decisions.md` in `docs/` | decision notes in the tree | notes against `docs/` |
|---|---|---|---|---|---|
| path order | 2 | 0.000 | 0.333 [0.12, 0.58] | 0.667 [0.42, 0.92] | +0.33 [0.04, 0.62] |
| path order | 4 | 0.042 | 0.875 | 1.000 | +0.13 [0.00, 0.29] |
| path order | 14 | 0.042 | 1.000 | 1.000 | 0 |
| shuffled | 2 | 0.000 | 0.417 [0.17, 0.67] | 0.500 [0.29, 0.71] | +0.08 [-0.17, 0.33] |
| shuffled | 4 | 0.000 | 0.917 [0.79, 1.00] | 0.750 [0.50, 0.96] | -0.17 [-0.42, 0.04] |

`decisions.md` in the prompt (`push`) at 2 calls: 1.000, with 14,922 prompt tokens per question
(2,674 to 3,056 in the `pull` arms).

The criteria were written before the runs. Other file order: a gain below +0.10 or an interval
that includes 0 means the first result came from the order; that happened (+0.04 [-0.15, 0.23]).
Second model: the interval of the gain excludes 0; it does (+0.25 [0.08, 0.44]). Decisions: at
least 0.50 at 2 calls and not more than 0.15 below `docs/`; met in path order, and at 2 calls in
shuffled order, not at 4 calls in shuffled order.

What this shows: the gain of the note round came from the notes file being the first thing the
search returned, on two models. With a neutral order the notes are cut off by the 40-hit limit in
more than half the runs, and the woven notes, which still appear in 43 of 48 runs, do not raise
accuracy at 2 calls. Placing statements in the tree is not enough; what was measured is the effect
of a search that returns the notes first. For decisions the plain way wins: the ledger in the
prompt answers every "why" question at 2 calls.

Sonnet 5.5 returned a final message without text in 15 requests after the tool budget was used
up; the harness asks again up to twice (`empty_replies` in the run record), and 4 of the 96 answers
stayed empty.

Cost of this round: about USD 1.6 (agent runs 1.50, of which Sonnet 1.05).

## A search that returns the notes first

A fifth round builds the thing the fourth round pointed at. With `--grep-order notes-first`, `grep`
walks the files in the shuffled order and puts up to 20 matching note lines from anywhere under
`src/` before the code hits, whatever path was searched. Where the notes sit and how the files are
ordered no longer matter. Haiku, `pull`, 2 repetitions, 624 runs.

Structural questions (24), share correct:

| calls | nothing | notes, file | notes, woven | earlier notes, file | file against nothing | woven against nothing |
|---|---|---|---|---|---|---|
| 2 | 0.396 [0.23, 0.56] | 0.542 [0.35, 0.71] | 0.625 [0.48, 0.77] | 0.583 [0.40, 0.77] | +0.15 [-0.02, 0.31] | +0.23 [0.04, 0.42] |
| 4 | 0.625 [0.44, 0.79] | 0.875 [0.75, 0.98] | 0.833 [0.71, 0.96] | 0.812 [0.67, 0.94] | +0.25 [0.10, 0.42] | +0.21 [0.08, 0.35] |
| 14 | 0.979 | 0.979 | | | 0.00 | |

At 14 calls the notes arm uses 18,054 prompt tokens and 4.2 tool calls per question against 25,212
and 5.3 with nothing. A note was shown in 46 and 47 of 48 runs at 2 calls. With the earlier notes,
0% of the answers to changed questions assert the outdated behaviour and 13% relay it with a caveat
(2 calls); at 4 calls neither occurs.

Decision questions (12), share correct:

| calls | nothing | `decisions.md` in `docs/` | decision notes | notes against `docs/` | prompt tokens, notes |
|---|---|---|---|---|---|
| 2 | 0.000 | 0.292 [0.08, 0.50] | 0.833 [0.58, 1.00] | +0.54 [0.29, 0.79] | 3,105 |
| 4 | 0.042 | 0.958 | 1.000 | +0.04 [0.00, 0.12] | 5,741 |

For comparison, `decisions.md` in the prompt gives 1.000 at 2 calls with 14,922 prompt tokens.

The criteria were written before the runs. At 2 calls a gain of at least +0.20 with an interval
that excludes 0: the woven form meets it, the file form does not (+0.15, interval touching 0); the
two forms do not differ from each other (-0.08 [-0.23, 0.06]). A note shown in at least 80% of the
runs: met. At 14 calls no more than 1.2 times the tokens of nothing and no loss of accuracy: met
(0.72 times). Decision notes ahead of `docs/` with an interval that excludes 0: met at 2 calls.

What this shows: ranking the notes first restores a gain that does not depend on file order or on
where the notes are placed. For structural questions it is smaller at 2 calls than the +0.33 of the
third round and clear at 4 calls; with a full budget it saves about a quarter of the prompt tokens
at equal accuracy. For decisions it is large: 83% at 2 calls against 29% for the ledger in `docs/`,
at a fifth of the tokens of putting the ledger in the prompt.

Cost of this round: about USD 0.65 (agent runs 0.53).

## Reading

- Decisions are the only stored content with a large effect: 0 to 4% without them, 88 to 100% with.
- A stored statement in `docs/` is not opened for structural questions. As a note in the searched
  tree it helps only when the search returns the notes first; with a neutral file order the gain at
  2 calls is gone, and a search built to put matching notes first brings part of it back.
- Decisions are few and short: in the prompt they answer every "why" question at 2 calls; as notes
  behind a notes-first search they answer 83% at 2 calls and all at 4, for a fifth of the tokens.
- No script-made refresh of an earlier description (witness notes, pointers, late-bound values, a
  list of what was added) came close to a page written again from the current code.
- With enough tool calls the agent answers structural questions from the code; no kind of
  documentation changes accuracy, and documentation in the prompt costs 2 to 4 times the prompt tokens.
- A description of the code pays off only when exploration is scarce, and then a fresh one is worth
  much more than a stale one on the facts that changed.
- Section-level witness notes did not change any outcome measurably; neither did a generic warning.
- Pointers without statements give about half the gain of the full page.

## Limits

One repository of 17 thousand lines, one model, 12 questions per class, 2 repetitions. The judge is
the same model family; 26 of the 36 structural failures at full budget come from two questions whose
keys ask for a detail (HTTP status, "review item") that otherwise correct answers omit. The rooted
versus unrooted comparison was not planned: it comes from fixing the path form between two arms. The
witness notes are per section, not per statement.

## Reproduce

```
python3 -I run_agent_qa.py build --earlier <app at 4279c98> --current <app at bfb0f9c> \
    --doc-earlier inputs/behaviour-earlier-commit.md --doc-current inputs/behaviour-current-commit.md \
    --decisions decisions.md --work <dir> [--rooted-paths]
uv run --no-project --with anthropic python -I run_agent_qa.py run --work <dir> \
    --questions questions.json --env <.env> --regime push [--max-tool-calls 2] [--tag rooted]
uv run --no-project --with anthropic python -I run_agent_qa.py judge  --work <dir> --questions questions.json --env <.env>
uv run --no-project --with anthropic python -I run_agent_qa.py stance --work <dir> --questions questions.json --env <.env>
python3 -I analyse.py <dir> questions.json analysis.json
```

The frame arms are sandboxes made by hand: copy `<dir>/sandbox/stale` to `<dir>/sandbox/cloze_live`
and replace its `docs/behaviour.md` with the output of

```
python3 -I cloze.py render --tree <app at bfb0f9c> --frames inputs/frames-earlier-commit.json --out behaviour.md
python3 -I added_symbols.py <app at 4279c98> <app at bfb0f9c> >> behaviour.md   # for the "+ added symbols" arms
```

then run with `--conditions cloze_frozen,cloze_live,stale_added,cloze_live_added --max-tool-calls 2 --tag rooted`.

The note arms: `python3 -I scholia.py build --lines inputs/notes-current-commit.json --written-from
<app at bfb0f9c> --current <app at bfb0f9c> --base <dir>/sandbox/none --out <dir>/sandbox/scholia_file
--form file` (for the earlier notes `--written-from <app at 4279c98>`, optionally `--only-valid`),
then run with `--regime pull --conditions none,fresh,scholia_file,scholia_woven,scholia_stale,scholia_stale_valid`.
`python3 -I scholia.py surfaced --work <dir> --arm pull+budget2+rooted --condition scholia_file`
replays the stored tool calls and counts the runs in which a note was shown.

`runs.tar.gz` holds every run, verdict and stance label (5,328 runs). API cost of the whole
experiment: about USD 8.6 (first round 4.8, frame round 0.75, note round 0.8, robustness round 1.6,
notes-first round 0.65).
