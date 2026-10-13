# 1 Introduction

## 1.1 Problem

A knowledge graph built from text is useful only if each fact in it can be trusted and traced. Large language models make extraction cheap: given a passage and a schema, a model returns nodes and relations in seconds. The same models make two kinds of mistake that are hard to see afterwards. They return facts that the passage does not support, and they depart from the schema, using a type or a property that nobody defined. Once such output is written to a graph, it looks the same as correct output.

The usual answer is to ask the model for a quotation and a confidence score. A quotation shows where a fact came from, and a score suggests which facts to check. We started from the same idea and found, in our own code, in a pilot and in the experiments of this report, that with the models we tried neither works as assumed. The model quotes the source accurately and then writes a value that is not in the quotation. Its confidence is nearly the same for output that matches the reference and output that does not.

## 1.2 Case study

We study the problem on the isnad, the chain of narrators that introduces a hadith: "A told us, from B, from C". The task suits the question for three reasons. A chain is a graph by nature. Errors matter, because scholars judge a hadith from the people in its chain, and one wrong name changes the judgement. Finally, labelled data exists, so output can be scored instead of inspected.

The task is not unsolved. Fine-tuned models extract narrators and their links accurately when large labelled training sets are available [@oumer2025relation], an ontology and a knowledge graph of the six canonical collections have been published [@kamran2023semantichadith; @kamran2026semantic], and narrator names have been linked to biographical databases [@wirahman2026linking]. Chapter 3 reviews this work. What we did not find is a study of the step between a general-purpose model and the graph: which checks belong there, what each of them catches, and how a fact's acceptance is recorded.

## 1.3 Objective and approach

The objective is an engine in which a language model proposes graph facts, deterministic checks and human review decide which of them are accepted, and every accepted fact keeps its source quotation and a record of how it was accepted. The second objective is to measure what the checks contribute.

Behind both objectives is one claim, which Section 2.6 states in full. A fact that a parser or a model extracts from a text can be extracted again, so it does not have to be kept; a person's acceptance, rejection or correction cannot be derived from anything and has to be stored once. The engine is built on that division, and the third objective is to test it: on the engine's own task, and outside it.

The engine, GiraffeGraph Core, treats the model as an untrusted proposer. A candidate that fails a check is not rejected silently; it goes to a review queue with a reason code. A reviewer's decision is stored with the reviewer's name, the time and the duration, and later processing cannot overturn it. Candidates accepted without a person are recorded as accepted by a named policy. Hadith-specific behaviour is added as plug-ins: a segmentation strategy, a schema template and a rule-based provider.

## 1.4 Contributions

1. **A working engine** with source-grounded candidates, ten reason codes that route a candidate to review and two that record unknown types and properties, relation identity that keeps separate transmissions between the same two narrators apart, an append-only decision record, a chain view, and a test suite that also runs against real PostgreSQL and Neo4j instances (Chapters 5 and 6).
2. **A measurement of the checks inside the engine.** On 300 unseen hadiths, the value-in-quotation check flags 122 of the 145 proposals of a schema-only model that do not match the reference, before any of them is accepted, while a quotation-in-source check flags none (Chapter 7).
3. **A comparison of extraction conditions through one pipeline**: rules, a schema-only model, a model with descriptions and domain hints, and the same model restricted to the chain span, with paired bootstrap intervals. Adding descriptions and hints to a schema-only prompt raises F1 by 0.066; restricting the input to the chain span does not help.
4. **An evaluation kit and data sets**: a scorer with a fixed matching protocol, an analysis of checks, confidence and cost, a 300-hadith test set built from an existing labelled corpus with its provenance, and an annotation sheet with a guideline for a future human-labelled set.
5. **A baseline for narrator identity** that quantifies how often a written name stands for more than one person in the reference labels.
6. **A simulation of a decision ledger for narrator identity** on two labelled corpora. A decision keyed by the name alone is reused wrongly for one mention in ten. Deriving the scope of a decision from contradictions that a deterministic rule detects comes close to the error of a fixed narrow key with about half to two thirds of its reviewer questions, also on collections the ledger has not seen (Section 8.1).
7. **An experiment in a second domain**, in which a coding agent answers questions about the engine's source code. It answers questions about decisions almost never from the code alone and almost always with a decision ledger, and it needs no stored description of the code when it can afford to read the code (Section 8.2).

## 1.5 Scope and limits

The report describes a prototype. Narrator identity resolution, rules that need biographical dates, question answering over the graph and authentication are out of the engine's scope (Chapter 4); identity decisions and a date rule appear only in the simulation of Section 8.1. The reference labels come from existing corpora and are not a gold standard produced by independent annotators. No person reviewed the evaluation runs, so the human part of the loop is implemented and tested but not measured. Results of the engine evaluation come from one model, on the in-memory backend. The two supporting studies are exploratory: one simulates the reviewer from labels and the other uses a model as the reader. Chapter 7 lists what was not measured, and Chapter 9 discusses how far the results can be trusted.

## 1.6 Structure

Chapter 2 gives the background on hadith chains and on extraction with language models. Chapter 3 reviews related work. Chapter 4 states requirements and scope. Chapters 5 and 6 describe the design and the implementation. Chapter 7 reports the evaluation of the engine. Chapter 8 reports two supporting studies on what has to be stored. Chapter 9 discusses the results, and Chapter 10 concludes with the plan for the second term.
