# Brief: a storage form for LLM-maintained project knowledge that is neither a knowledge graph nor a markdown wiki

You are one of five independent agents (different models) given this same brief. Think on your own;
do not try to guess what the others will say. An unusual idea that survives the facts below is worth
more than a safe one.

## The question

An LLM agent works on a body of raw material over many sessions (a code base, a corpus of texts, a
data set). Between sessions it keeps some persistent context so that the next session starts ahead.
Today that context is almost always one of two things: a markdown wiki written by the agent, or a
knowledge graph of extracted entities and relations.

Propose a different form: a data model, a database kind, a file format, a protocol, or a mechanism
for what gets written, how it is read, and how it is invalidated. It does not have to be about
hadith, isnad chains or graphs. The aim is an invention, not a survey.

## What has been measured (an idea must be consistent with these)

Workspace: `/Users/efe/projects/GiraffeGraph`. Read these first:

- `cache-and-ledger/README.md` (the essay "The Cache and the Ledger")
- `cache-and-ledger/MEASUREMENTS.md` (one-page scorecard)
- `cache-and-ledger/data/agent-qa/README.md` (agent experiment, 2,880 runs)
- `cache-and-ledger/data/witness-survival/REPORT.md` (git-history measurement, 8 repositories)
- optional: `wiki/evaluation/wiki-for-agents-experiments.md`, `wiki/evaluation/decision-ledger-experiments.md` (Turkish)

Summary of the facts:

1. An agent with 14 tool calls answers structural questions about a 17k-line code base 94–98%
   correctly with no documentation at all. No kind of documentation changed that. Putting
   documentation in the prompt cost 2–4x the prompt tokens. When the agent had to open the docs
   itself, it never did for structural questions (0 of 432 runs).
2. "Why" questions (decisions that are not in the code): 0–4% without a decision log, 88–100% with it.
3. With only 2 tool calls: 31% with nothing, 88% with a fresh description page, 69% with a stale one
   (50% on the facts that changed). With 4 calls the gap shrinks; with 14 it is gone. So a stored
   derivation is worth as much as derivation is expensive at the moment of use.
4. A stale page rarely makes the agent assert the outdated fact (0–4%); it relays it with doubt
   (21–33%).
5. A per-section note "the code this section was written from has changed" changed nothing
   measurable, and did not beat a generic "may be outdated" sentence.
6. A page of pointers only ("look here") gives about half the gain of the full page.
7. Anchors to code: a file-level content hash is invalid after one month for 46% of documented
   files; a symbol-level one (function or class body) still matches for 78% after 12 months.
8. Decisions keyed too broadly are reused wrongly (10% of reuses by name alone in 150,904 mentions);
   keyed narrowly they cost three times the human questions. Starting broad and narrowing the key
   only after a contradiction is detected gets close to the narrow key's error at about half the
   questions. Mechanism known as Ripple-Down Rules.
9. Decisions keyed by content survive re-extraction with a changed prompt (86–98% of new candidates
   map to an existing target); keyed by candidate id, 0%.
10. "A verbatim copy from the source is safe, a transformation is risky" held on Arabic isnad
    extraction and failed on a human-labelled biomedical corpus (82% of wrong extractions were
    verbatim copies).

## Already on the table: do not return these

- knowledge graph / property graph / triple store
- markdown wiki, AGENTS.md / CLAUDE.md style rule files, ADR decision log
- vector store, embeddings, RAG over chunks
- memoizing the agent's answers together with the exact lines it read (verifying traces)
- staleness notes or hash witnesses per section
- a pointers-only index page, a symbol map generated from the AST

Combinations of the above with a new name also do not count.

## Rules

- Read-only. Do not create, edit or delete any file. Do not run anything that spends API money.
- Do not open any `.env` file. Do not read `giraffle/` or `giraffe-code/`.
- You may search the web if you can. Mark anything about prior work that you state from memory
  without checking as "unverified". Do not invent citations.

## What to return (plain text, under 900 words)

1. **Name** of the idea and one sentence that states it.
2. **What is stored**: the unit, its fields, and a concrete example of 10–20 lines in the proposed
   format (invent the format if needed).
3. **Operations**: when a unit is written, how the agent reads it under a tight tool budget, when it
   is invalidated or narrowed, who does each step (agent, deterministic script, human).
4. **Why it should beat a markdown page and a graph**, argued from the numbered facts above. Name
   the facts you rely on.
5. **Closest prior work** and the exact difference.
6. **One falsifiable experiment** that fits the existing harness (`cache-and-ledger/data/agent-qa/run_agent_qa.py`:
   same 36 questions, conditions differ in what the sandbox contains, tool budgets 2/4/14) and costs
   under USD 5. State the arm, the comparison arm, the metric, and the result that would kill the idea.
7. **Two runner-up ideas**, two sentences each.
8. **The weakest point** of your main idea, stated honestly.
