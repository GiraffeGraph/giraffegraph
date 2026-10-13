# 8 Supporting studies: what must be stored

Chapter 7 measured the engine's checks. This chapter reports two smaller studies on the other half of the design: the decision record. Section 2.6 stated the claim the project rests on. A fact that can be derived from a source should be derived again, and a decision made by a person cannot be derived and has to be stored once. The first study asks what storing an identity decision buys on labelled isnad chains. The second asks the same question in a different domain, a coding agent that reads the engine's own source code.

Both studies are exploratory and were run on 13 October 2026. The first is a simulation in which the dataset's labels stand in for the reviewer. The second uses a language model as the reader. No person took part in either, and Section 8.3 states what follows from that.

## 8.1 Reusing an identity decision on labelled isnad chains

Section 7.10 showed that a written name is not a narrator's identity. The decision that settles it, "this name, here, is this person", is the kind of decision the engine records. We asked how often such a decision can be reused and what the reuse costs.

**Simulation.** A ledger reads labelled chains one mention at a time. When it meets a key it has not seen, it asks the reviewer, and the answer is the dataset's label. Afterwards it reuses the answer for the same key. A *question* is anything that goes to the reviewer. A *silent error* is a reused answer that disagrees with the label and that no reviewer saw. Both are reported per mention. The module is `evaluation/identity_ledger.py`; the order of the chains is random and the values are means over five orders.

**Data.** The test chains of AR-Sanad 280K [@mahmoud2022arsanad]: 27,056 chains, 150,904 mentions, 6,378 people and 15,301 distinct written names, of which 815 stand for more than one person. The replication uses the hadiths of the six Ifta collections that carry narrator identifiers: 34,681 hadiths, 205,514 mentions and 6,891 people. The two label sets come from different sources [@internal-data-manifest]. In a chain we call the narrator named before a mention its *student* and the one named after it its *teacher*.

**Scope of a decision.** The ledger stores every answer with its full context (student, name, teacher). Which part of that context a later mention must share before the answer is reused is the decision's scope. A scope of the name alone gives the most reuse and the most errors. Table 8.1 gives the two fixed scopes and three ways of narrowing.

In the narrowing policies the scope is not chosen in advance. Every name starts with the name alone and is tied to its student only after a contradiction has been seen for that name. The contradiction detector is a deterministic rule on the narrator catalogue: the reviewer is asked when the person the ledger proposes and the neighbouring narrator are more than five generations apart, or less than minus one, or when their death years differ by more than 85 years or by less than minus 20. The bounds were chosen on the AR-Sanad chains, where they flag 0.8% of the labelled neighbouring pairs, and were applied to the Ifta data unchanged, where they flag 3.4%.

**Table 8.1** Questions and silent errors per mention for five policies on two label sets (means over five random orders). "Hindsight" starts the names known to be ambiguous in the narrower scope; it needs the labels in advance and is an upper bound.

| Policy | AR-Sanad: questions | AR-Sanad: silent errors | Ifta: questions | Ifta: silent errors |
|---|---|---|---|---|
| Fixed scope: name | 0.101 | 0.100 | 0.077 | 0.102 |
| Fixed scope: name; the rule asks about the flagged mention only | 0.204 | 0.054 | 0.229 | 0.049 |
| Scope narrowed by the rule | 0.178 | 0.014 | 0.199 | 0.010 |
| Fixed scope: student and name | 0.340 | 0.006 | 0.292 | 0.007 |
| Hindsight | 0.187 | 0.006 | 0.157 | 0.007 |

A decision keyed by the name alone is reused wrongly for one mention in ten. Keying it by student and name removes almost all of those errors and costs about three times the questions. Narrowing the scope only where the rule sees a contradiction comes close to the error of the narrow key (0.014 against 0.006 on AR-Sanad, 0.010 against 0.007 on Ifta) with about half to two thirds of its questions.

The same rule was used in two ways. When it only sends the flagged mention to the reviewer, the error stays near 0.05. When the flag also narrows the scope of that name, one contradiction protects every later occurrence of the name, and the error falls to 0.014 and 0.010.

**A collection the ledger has not seen.** We filled the ledger from five of the six Ifta collections and counted on the sixth, for each collection in turn. With the scope narrowed by the rule the silent error was between 0.004 and 0.016 per mention and the questions between 0.138 and 0.249. With the fixed scope of student and name the error was between 0.007 and 0.023 and the questions between 0.151 and 0.307; the narrowing policy asked fewer questions in every collection. With the name alone the error was between 0.091 and 0.151: an answer carried over from another collection may belong to a namesake.

**A reviewer who errs.** When the simulated reviewer gives a wrong answer for 5% of the ambiguous names (AR-Sanad), the narrowing policy gives 0.219 questions and 0.018 silent errors per mention, and the fixed scope of student and name 0.340 and 0.019. Wrong answers produce false contradictions and therefore more questions; the order of the policies does not change.

**Does a decision survive re-extraction?** A stored decision is useful only if it can be found again when the text is extracted a second time. The engine attaches a decision to a candidate. We compared the narrator candidates of the four runs of Chapter 7 and asked which share of the candidates of one run has a counterpart in another run when the target is the pair of hadith and normalised name (`evaluation/decision_reapplication.py`). Between two prompts of the same model the share is between 0.857 and 0.977 in the six directions. Between the rule-based parser and a model run it is between 0.561 and 0.634, because the parser's spans run long. Attached to the candidate identifier the share is zero by construction. This measures overlap of targets, not decisions, since no decision was made.

## 8.2 A second domain: what a coding agent needs stored

The second study leaves hadith. It asks whether the distinction between derivable facts and decisions holds for another reader and another kind of source: a coding agent that answers questions about a code base. The code base is the backend of the engine itself (141 files, 16,923 lines); the design, the questions and the runs are documented with the experiment [@internal-agent-experiment].

**Set-up.** The agent is Claude Haiku 5.5 at low effort with three read-only tools: list a directory, read a file, search. It answers 36 questions, twelve in each of three classes. *Stable* questions ask for a structural fact that is the same in the code of 5 April 2026 and in the current code. *Changed* questions ask for a structural fact that the October rewrite changed. *Decision* questions ask why something is the way it is; their answers are in the project's decision records and not in the code. A separate agent that did not see the documentation under test wrote the questions and the answer key from the code.

The conditions differ only in the content of a `docs/` folder: nothing; a ledger of 30 decisions, each with its reason and the rejected alternative and no derivable fact; the ledger with a page that describes the code and was written from the current code (the fresh page); and the ledger with a page written under the same instructions from the code of 5 April (the stale page). In one regime the agent has to open `docs/` itself, in the other the documents are also placed in the prompt. The tool budget is 14, 4 or 2 calls. Each cell was run twice. Answers were graded by the same model against the written key without seeing the condition. The unit of analysis is the question, and intervals are bootstrap intervals over questions. The base design has 2,880 runs; with the later arms described below the experiment has 5,520.

**Table 8.2** Share of correct answers with a budget of 14 tool calls (24 structural and 12 decision questions, two runs each).

| Content of `docs/` | Structural, agent opens `docs/` | Structural, documents in the prompt | Decision, agent opens `docs/` | Decision, documents in the prompt |
|---|---|---|---|---|
| Nothing | 0.979 | 0.938 | 0.042 | 0.000 |
| Decision ledger | 0.938 | 0.979 | 1.000 | 0.958 |
| Ledger and fresh page | 0.979 | 0.958 | 1.000 | 0.917 |
| Ledger and stale page | 0.896 | 1.000 | 0.875 | 0.958 |

With enough tool calls the agent reads structure from the code. It answers 94% to 98% of the structural questions with no documentation, and no kind of documentation changes that. In the 432 structural runs in which it had to open `docs/` itself it did not open the folder once. Placing the documents in the prompt raised the prompt tokens per structural question from 21,843 to between 45,343 and 75,443. The decision questions are the opposite case. Without the ledger the agent answers almost none of them, and with it almost all.

**Table 8.3** Structural questions with the documents in the prompt and a small tool budget.

| Content of `docs/` | 2 calls: all | 2 calls: stable | 2 calls: changed | 4 calls: all |
|---|---|---|---|---|
| Nothing | 0.312 | 0.375 | 0.250 | 0.750 |
| Fresh page | 0.875 | 0.792 | 0.958 | 0.979 |
| Stale page | 0.688 | 0.875 | 0.500 | 0.812 |

A stored description of the code pays only when reading the code is expensive. With two tool calls the fresh page raises the share of correct answers by 0.56 (interval 0.38 to 0.75) over no documentation, with four calls by 0.23 (0.10 to 0.38), and with fourteen by nothing. The stale page is right about half as often as the fresh one on the facts that changed.

We tried three ways of keeping a stored description valid without writing it again: a machine-made note under each section saying whether the code it was written from has changed, sentences whose facts are filled in from the current code by stored selectors, and a list of the symbols added since the page was written. None came near a page written again from the current code. On the changed facts at two calls the filled-in sentences gave 0.625, the stale page 0.500 and the fresh page 0.958.

Where a statement is put decides whether it reaches the agent. The fresh page cut into one-line notes and placed inside the source tree helps only when the search tool returns matching notes before code: the gain on structural questions at two calls is then between 0.15 and 0.31 on two models, Claude Haiku 5.5 and Claude Sonnet 5.5, against 0.04 (interval −0.15 to 0.23) when the files are searched in a shuffled order. The lowest of these gains has an interval that reaches zero. In the Sonnet runs the arm without notes returned an empty answer in 5 of 48 runs, above the 10% we had fixed in advance as the limit for a reliable comparison, so those two gains are reported with that reservation.

## 8.3 What the two studies add and what they do not show

The two studies agree with Section 2.6 on the first half of the claim. The agent could not recover a decision from the code, and a narrator's identity could not be recovered from the written name. In both cases the answer has to come from a person once and be stored.

They qualify the second half. A derivable fact need not be stored when deriving it is cheap at the moment of use, and a stored copy pays when it is not: at two tool calls for the agent, and wherever extraction costs a model call and a review. A stored copy that is not regenerated misleads on exactly the facts that changed.

They add one variable. A stored decision has a scope, and the scope did not have to be stored: it was derived from contradictions, with a deterministic domain rule as the detector. We make no claim that the mechanism is new. Attaching a correction to the context in which an earlier answer failed is known in knowledge acquisition as ripple-down rules, which we cite from its bibliographic record without having read the source in full [@compton1990philosophical].

The limits are those of simulations. In the ledger study the reviewer is the dataset's label, so the first answer is free and, except in the 5% variant, always right; a question is counted as one unit whatever time it would take a person. How the AR-Sanad person labels were assigned is not documented, and the six collections share most of their narrators, so a distant collection is untested. In the agent study there is one code base of 17 thousand lines, twelve questions per class and two runs per cell; the grader is the same model as the agent; the pages were written by agents and not by people; and the second model ran in two comparisons only, from the same model family. Neither study measures the engine, and neither replaces the reviewer experiment planned in Section 10.1.
