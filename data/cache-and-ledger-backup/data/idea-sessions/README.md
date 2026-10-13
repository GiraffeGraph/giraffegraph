# Fifteen idea sessions: five agents, three orderings of one brief

Run on 2026-10-13. Five coding agents were given the same brief (`brief.md`): propose a storage
form for LLM-maintained project knowledge that is neither a knowledge graph nor a markdown wiki,
consistent with ten measured facts, with a list of excluded ideas. Each agent then got the brief
twice more in separate sessions with the ten facts and the excluded list reordered by a seeded
shuffle (`shuffle_brief.py`, seeds 1 and 2; `brief-seed1.md`, `brief-seed2.md`). Every session
started without memory of the others. Full answers are in `outputs/`.

Agents: Claude Sonnet and Claude Opus (subagents of Claude Code), Codex (`gpt-6.1-sol`), Pi
(`gpt-5.6-sol`), Antigravity (`gemini-3.8-flash-high`). Three model families, not five independent
minds.

## What each session proposed

"Executable" means: the main idea stores a program, query or test that is run against the current
source at read time, and the agent reads its output. The criterion was fixed before the shuffled
sessions were read.

| Agent | Order | Main idea | Executable |
|---|---|---|---|
| Sonnet | original | Live probes: store the query that derives a fact, run it on every read | yes |
| Sonnet | seed 1 | Compiled trajectories: recipes compiled from the agent's own tool calls | yes |
| Sonnet | seed 2 | Probe shelf: parameterised question plus the script that answers it | yes |
| Codex | original | Contrast bench: fixture, intervention, observation; human-ranked consequences | yes |
| Codex | seed 1 | Counterfactual bench: minimal set of discriminating experiments | yes |
| Codex | seed 2 | Discriminator cartridges: experiments that separate competing interpretations | yes |
| Pi | original | Counterfactual capsules: accepted and rejected patch, reason, discriminating test | partly (the test decides whether the capsule is used; the text is stored) |
| Pi | seed 1 | Question virtual machine: capsules that recompute a typed observation | yes |
| Pi | seed 2 | Counterfactual assay cabinet: experiments, including one for the rejected alternative | yes |
| Antigravity | original | Precedent docket: append-only claims with symbol hashes and exception links | no |
| Antigravity | seed 1 | Ripple-down justification register: the same with multi-hop "bridges" | no |
| Antigravity | seed 2 | Epistemic precedent deck: the same with affirms/denies fields | no |
| Opus | original | Cloze ledger: sentences with blanks that a script fills from the code | yes |
| Opus | seed 1 | Closed-world ledger: store only "only/never/exactly N" claims as queries with a baseline set, deliver the difference | yes |
| Opus | seed 2 | Scholia: one-line notes placed inside the tree the agent already greps | no |

## Reading

- Reordering the brief changed almost nothing; the model decided the idea. Sonnet, Codex and
  Antigravity each returned their own idea three times under three names. Only Opus returned three
  different ideas.
- Of the 10 shuffled sessions 7 are in the executable family (predicted before reading: at least
  7). With the original order it is 11 of 15, plus one partial.
- The shuffle varies order only. The content of the facts and of the excluded list also steers the
  answer; that was not varied.
- Antigravity's three answers are combinations of items on the excluded list (decision log, hash
  witness, pointer, scope narrowing).

## What was tested afterwards

The executable family was tested in the form Opus gave it (the cloze ledger), with a frozen control
arm: `../agent-qa/README.md`, section "Late-bound frames and a list of added symbols". It did not
pass its own kill criteria. Scholia (delivery through the agent's own grep) was tested next and
passed its four: `../agent-qa/README.md`, section "Notes inside the tree the agent searches". Not
tested: the closed-world ledger (differences of standing queries), executable experiments that run
the code.
