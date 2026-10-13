# CSE 491 Project Proposal

> **Draft, not yet reviewed by the group or the supervisor.** Points that need a decision before
> submission are listed in "Open points" at the end. Delete this box and that section before upload.

## 1. Title and summary

**Title:** A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and
Schema Drift in LLMs: An Application on Hadith Isnad Chains

**Group:** Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya
**Supervisor:** Dr. Taha Yiğit Alkan
**Domain expert:** Prof. Dr. Rifat Atay (Faculty of Theology)

**Summary.** Large language models can turn free text into knowledge graph facts, but they add facts
the source does not contain and they drift away from the schema they were given. GiraffeGraph is an
engine in which the model only proposes. Each proposed fact carries a quotation from the source, is
checked by deterministic rules, and reaches the graph only through a recorded human decision or a
recorded acceptance policy. The design rests on one claim: what such a system has to store is the
decision of a person, and what can be derived from the source is derived again. Our case study is the
hadith isnad: the chain of narrators that precedes a hadith text. By the end of CSE 491 we will deliver a working prototype that processes a small set
of Arabic hadiths end to end and reports, against hand-labelled data, how many errors each check
catches. Two supporting studies test the claim itself: a simulation of reusing narrator-identity
decisions on labelled chains, and an experiment in a second domain. Entity resolution of narrators
inside the engine, the full experiment and the question-answering layer are planned for Senior Design
Project II.

## 2. Problem and motivation

When an LLM extracts a narrator chain from a hadith, four things go wrong:

1. **Unsupported facts.** The model outputs a narrator or a link that the text does not contain, or
   it silently rewrites a name it did find.
2. **Schema drift.** The same relation appears as `NARRATED_FROM` in one run and under another name
   in the next, and property names vary between runs.
3. **Identity confusion.** One narrator is written in several ways, and several narrators share one
   short name. Merging two different people changes how the chain is judged.
4. **No trace.** After the graph is built, nobody can tell which sentence a fact came from or who
   accepted it.

These matter in this domain because the reliability of a hadith is judged from its chain. A single
wrong narrator changes the verdict, so a graph that is mostly right is not usable by a scholar.

**Target users.** Researchers and students in hadith studies who need to browse and query narrator
chains, and engineers who build knowledge graphs from text in other domains where each fact has to be
traceable to its source.

**What we already observed.** A pilot run on 30 September 2026 on 50 hadiths (327 reference narrator
mentions, one model, scored against the rule-generated labels of the Sanadset corpus, loose matching)
gave three results that shape this proposal:

- A rule-based parser reached F1 0.879 and an LLM with a schema-only prompt reached 0.865. An LLM
  with an isnad-aware prompt reached 0.935. Raw extraction accuracy is therefore not where the
  project can contribute most.
- Checking that the model's quotation occurs in the source caught nothing (605 of 605 quotations
  were verbatim). Checking that the extracted name occurs inside the model's own quotation flagged
  32 of 318 candidates.
- The model's self-reported confidence separated right from wrong candidates poorly (AUC 0.626).

These numbers are comparisons between methods on rule-generated labels. They are not accuracy
figures, and one of the aims of the project is to replace them with measurements on hand-labelled
data.

**The claim behind the design.** A candidate that a parser or a model extracts from a text can be
extracted again, so it is treated as derived: it is checked, not trusted, and it does not have to be
kept. An acceptance, a correction or the identification of a narrator by a person cannot be derived
from any text and has to be stored once, with who decided and when. Two exploratory studies of
13 October 2026 looked at the second half. Both are simulations: no person took part.

- On the 27,056 test chains of AR-Sanad [4] (150,904 narrator mentions), a stored identity decision
  that is reused whenever the same written name appears is wrong for one mention in ten. When the
  decision is tied to its context only after a deterministic rule on generations and death years
  has seen a contradiction, the silent error falls to 0.014 per mention with about half the reviewer
  questions that a fixed context key needs. The reviewer is simulated from the labels of the data set.
- In a second domain, a coding agent that answers questions about the engine's own source code
  answered questions about why the code is the way it is 0% to 4% correctly from the code alone and
  88% to 100% correctly with a ledger of decisions (12 questions, two runs each). It answered
  structural questions 94% to 98% correctly with no documentation when it had enough tool calls.

## 3. Objectives, scope and success criteria

**Objective.** Build an engine that turns hadith text into a narrator-chain graph in which every
fact is tied to a source quotation and to a recorded decision, and measure how much each validation
step reduces extraction errors. Test the claim behind the design, that decisions have to be stored
and derivable facts do not, on the engine's own task and in one other domain.

**In scope for CSE 491 (prototype):**

- Loading Arabic hadiths, one hadith per source unit, from Sanadset 650K (CC0).
- Rule-based separation of isnad and text, and splitting of the isnad into narrator mentions.
- LLM extraction of narrators and `NARRATED_FROM` links, one call per chain, constrained to a fixed
  schema.
- Three deterministic checks: the type exists in the schema; the quotation occurs in the source; the
  extracted value occurs in the quotation.
- A review screen where a person accepts, rejects or edits a candidate, with who decided, when, and
  how long it took.
- A canonical graph in which the same two narrators can be linked in different hadiths without one
  link overwriting the other.
- A scoring script and a hand-labelled set of 50 hadiths.
- Two supporting studies, reported with their scripts and limits: the simulation of a ledger of
  narrator-identity decisions on labelled chains, and the coding-agent experiment. Neither changes
  the engine.

**Out of scope for CSE 491** (planned for Project II unless stated otherwise):

- Linking narrator mentions to an authority list of known narrators (entity resolution), and a
  ledger of identity decisions inside the engine. CSE 491 has the simulation only.
- Domain rules that need biographical dates (contemporaneity, meeting, generation).
- The comparison of graph-based and text-only retrieval for question answering.
- Multi-model experiments and a labelled set larger than the 50-hadith calibration set.
- Turkish hadith text. We found no copyright-free Turkish source with full chains.
- Judging the authenticity of hadiths. The system records chains; it does not grade them.

**Success criteria.** The prototype is tested against these in week 13.

| # | Criterion | How it is measured |
|---|---|---|
| S1 | A set of 100 hadiths passes from upload to canonical graph without manual intervention outside the review screen | End-to-end run, logged |
| S2 | 100% of facts in the canonical graph have a source quotation and a decision record (human or policy) | Automated test over the graph |
| S3 | Precision, recall and F1 are reported for four conditions (rule-based parser; LLM; LLM with checks; LLM with checks and human review) on the 50 hand-labelled hadiths, under strict and loose matching, with hadith-level bootstrap confidence intervals | Scoring script, results table |
| S4 | Inter-annotator agreement on the 50 hadiths and mean labelling time per hadith are reported | Two independent annotators, mutual F1 |
| S5 | For the claim "decisions are stored, derivable facts are derived again", the report states what was measured for it and against it, and every number of the two supporting studies is reproduced by a script in the repository | Re-run of the scripts from a clean clone |

## 4. Similar systems and background

| Work | What it provides | How quality was measured | What is missing for our purpose |
|---|---|---|---|
| Sanadset 650K [1] | 650,986 hadith records from 926 books with narrator tags | Not reported; tags were produced with regular expressions | No human check of the labels |
| SemanticHadith [2], [12] | Ontology and knowledge graph for the six canonical collections (34,458 hadiths); entities extracted with a custom NER model; narrator chain segments are modelled as classes | NER micro F1 97%; three experts checked a random sample of 100 instances per collection | No LLM extraction and no decision per fact; ambiguous names are excluded or left for manual review, and an expert validation framework is listed as future work |
| Çinici [13] | LLM with retrieval turns one volume of a classical biographical work into a structured dataset of 271 scholars | The author compared the first 100 records with the source; no figure reported | Biographies, not chains; one evaluator; no graph or review workflow |
| Muther and Smith [3] | Expert-annotated isnad boundaries in 50 classical texts | Strict F1 0.254, partial F1 0.835; experts agree exactly on the end point in 53% of cases | Finds isnad spans, not individual narrators |
| AR-Sanad 280K [4] | 27,056 real chains with narrator identities, 18,298 narrators | Micro F1 83.5, but 60.6% of chains contain at least one wrong narrator | Starts from already separated names, not from text |
| Oumer [5] | Fine-tuned models for narrator and relation extraction on 223,478 hadiths | Narrator F1 0.98, relation F1 0.95 (figures from the author's model repository) | Needs large labelled training data; no provenance or human review |
| Rezwan [6] | LLM-assisted corpus of 1.2M narrations | Six experts, 0–10 scores; no agreement statistic | Scores are not comparable across studies |
| Wirahman [7] | Links 185,216 narrator name variants to biographical databases | Not measured; the author states no labelled reference exists | Fully automatic, no human decision |
| Text2KGBench [8] | Benchmark for ontology-driven KG extraction with LLMs | Precision 0.38 with subject hallucination 0.17 on one dataset | General domain; shows that "appears in the text" does not imply "correct" |

A recent critical review of the field [9] lists weak benchmark comparability and sparse expert
validation as open problems. General frameworks for LLM-based graph construction exist as well
[10], [11].

**Position of this project.** A hadith knowledge graph, its ontology and narrator linking already
exist, and fine-tuned models already extract chains accurately. We build on that work for the schema. We did not find a study that measures the separate effect
of each validation step between an LLM and a graph, or one that reports a value-in-quotation check as
its own error class. We also did not find a measurement of how often a stored narrator-identity
decision can be reused and at what error; the mechanism we simulate, tying a correction to the context
in which an earlier answer failed, is known in knowledge acquisition as ripple-down rules and is not
our invention. Our search was not systematic, so this is a statement about what we found.

## 5. Preliminary requirements

**Functional**

| ID | The system shall |
|---|---|
| F1 | let a user define node types, relation types and their properties, and reject identifiers that the graph database cannot store |
| F2 | ingest a hadith as one source unit with a stable identifier and content hash |
| F3 | split a hadith into isnad and text and return narrator mentions with character offsets |
| F4 | request candidates from an LLM for one chain at a time, constrained to the schema |
| F5 | reject a candidate whose type is not in the schema without discarding the other candidates of the same call, and record the unknown type |
| F6 | mark a candidate for review when its quotation does not occur in the source |
| F7 | mark a candidate for review when its extracted value does not occur in its quotation |
| F8 | present candidates with their quotation and check results, and let a reviewer accept, reject or edit them |
| F9 | record for every decision the reviewer, the time and the duration |
| F10 | write accepted facts to the canonical graph so that links between the same two narrators in different hadiths stay distinct |
| F11 | display the chain of a hadith and the source quotation of each link |
| F12 | score system output against a reference file and produce precision, recall and F1 |

**Non-functional**

| ID | Requirement | Verification |
|---|---|---|
| N1 | No fact reaches the canonical graph without a decision record | Automated test (S2) |
| N2 | Re-running a commit does not create duplicate nodes or links | Integration test |
| N3 | The backend test suite runs without a database or network access in under one minute | CI |
| N4 | A new user can start the system from the README alone | Tested on a clean machine in week 14 |
| N5 | No API keys or passwords are stored in the repository | Repository scan in CI |

## 6. Method and technology plan

**Approach.** The engine is a pipeline with a gate at each stage:

```
hadith text → isnad segmenter → LLM proposal (per chain) → checks → review → canonical graph
                                                     schema / quotation / value      decision record
```

The model has no write access to the graph. A candidate becomes a fact only after it passes the
checks and receives a decision.

**Measurement.** We add the stages one at a time and score each configuration against the
hand-labelled set, so the contribution of each stage can be read from the table. The matching
criterion is fixed before measurement: strict (normalised strings equal) and loose (equal,
substring, or token F1 of at least 0.60), with maximum-weight matching between system and reference
mentions. The hadith is the unit of analysis.

**Labelled data.** Two group members label the same 50 hadiths independently, following a written
guideline, without seeing system output. The person who writes the checks does not label.

**Existing code.** GiraffeGraph Core already implements schema versioning, ingestion, LLM extraction
through an OpenAI-compatible provider, candidate validation, a review queue and commit to Neo4j. A
first version of the checks in F5–F7, the decision record in F9 and the link identity in F10 was
written in October with AI coding assistants and is covered by automated tests. It has not been
reviewed by the group and has not been used by a reviewer. Reviewing it, testing it with a person in
the loop and measuring it against hand-labelled data is the main work of this term.

**Technology**

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python 3.12, FastAPI | Existing code base; team experience |
| Operational store | PostgreSQL 16 | Runs, candidates, review items and decisions are relational |
| Canonical graph | Neo4j 5 | Path queries over chains |
| Internal dashboard | Next.js 15 | Existing review interface |
| LLM access | OpenAI-compatible HTTP API | Lets us switch between hosted and open models |
| Development | uv, pytest, ruff, Docker Compose, GitHub Actions | Reproducible setup and CI |
| Data | Sanadset 650K (CC0) | Arabic text with full chains and a confirmed licence |

A decision table with the alternatives considered for each choice will be part of the midterm report.

## 7. Work plan

| Week | Dates | Work | Output |
|---|---|---|---|
| 5 | 12–18 Oct | Proposal | This document |
| 6 | 19–25 Oct | Architecture, data model, three screen sketches | Diagrams; supervisor meeting 3 |
| 7 | 26 Oct – 1 Nov | Technology decision table; labelling guideline; start labelling 50 hadiths | Decision table; guideline v1 |
| 8 | 2–8 Nov | Midterm report and presentation | Report, slides, dated plan |
| 9 | 9–15 Nov | Repository clean-up, CI, one hadith end to end | Running skeleton; supervisor meeting 4 |
| 10 | 16–22 Nov | Segmenter, per-chain extraction, three checks, per-candidate rejection | Core components with tests |
| 11 | 23–29 Nov | Review screen, decision record, chain view | Clickable workflows; supervisor meeting 5 |
| 12 | 30 Nov – 6 Dec | Integration on 100 hadiths, scoring script, deployment | First tagged version |
| 13 | 7–13 Dec | Test against S1–S4, fixes, list of known limitations | Results table |
| 14 | 14–20 Dec | Final report, README, technical documentation | Report and repository |
| 15 | Final period | Prototype demo and plan for Project II | Presentation |

**Division of work (proposed)**

| Member | Main responsibility |
|---|---|
| Yahya Efe Kuruçay | Architecture, validation checks, decision record, scoring script |
| Deniz Büyükşahin | Labelling guideline, annotation (annotator 1), review screen |
| Alperen Ulukaya | Isnad segmenter, annotation (annotator 2), chain view |

All members commit their own work under their own accounts.

## 8. Expected outputs and risks

**Outputs at the end of the term**

- A working prototype and its repository with README, tests and CI. Engine, documentation and data
  are in one private repository; the engine is published under an open-source licence at the end of
  the project.
- A labelling guideline and 50 hadiths labelled by two annotators, with agreement figures.
- A results table for the four conditions in S3.
- The two supporting studies with their scripts, result files and stated limits.
- Final report, presentation and a plan for Project II.

**Risks**

| Risk | Early sign | Response |
|---|---|---|
| Labelling takes longer than planned | Time per hadith in week 7 | Reduce the set; label in a spreadsheet instead of building a tool |
| Annotators disagree | Low mutual F1 in the first round | Add boundary rules to the guideline and repeat the round |
| Development starts late | No running skeleton by mid-November | Simplify the interface; keep checks and scoring |
| Scope grows again | A new planning round with no working component | Return to the out-of-scope list in section 3 |
| LLM cost or access | Calls fail or the budget is used up | Use an open model through the same API; reduce the set |
| Licence of additional labelled data cannot be confirmed | No written confirmation | Use Sanadset and our own labels only |

## Use of AI assistants

AI assistants were used for the literature search, for the pilot analysis of 30 September 2026, for
code review of the existing engine, for the first version of the checks, for the two exploratory
studies of 13 October 2026 and for drafting this document. Bibliographic records were
retrieved from Crossref, arXiv and the ACL Anthology, not written from memory. The group is
responsible for every statement here.

## References

[1] M. Mghari, O. Bouras, and A. El Hibaoui, "Sanadset 650K: Data on Hadith narrators," *Data in
Brief*, vol. 44, 108540, 2022. doi:10.1016/j.dib.2022.108540

[2] A. B. Kamran, B. Abro, and A. Basharat, "SemanticHadith: An ontology-driven knowledge graph for
the hadith corpus," *Journal of Web Semantics*, vol. 78, 100797, 2023.
doi:10.1016/j.websem.2023.100797

[3] R. Muther and D. Smith, "Tracing Traditions: Automatic Extraction of Isnads from Classical Arabic
Texts," in *Proc. Fifth Arabic Natural Language Processing Workshop*, 2020, pp. 130–138.
https://aclanthology.org/2020.wanlp-1.12/

[4] S. Mahmoud, O. Saif, E. Nabil, M. Abdeen, M. ElNainay, and M. Torki, "AR-Sanad 280K: A Novel 280K
Artificial Sanads Dataset for Hadith Narrator Disambiguation," *Information*, vol. 13, no. 2, 55,
2022. doi:10.3390/info13020055

[5] J. M. Oumer, "Relation extraction for graph-based representation of Hadith Isnad," M.S. thesis,
University of Malta, 2025. https://www.um.edu.mt/library/oar/handle/123456789/137629

[6] M. Asgari-Bidhendi, M. A. Ghaseminia, A. Shahbazi, S. A. Hossayni, N. Torabian, and
B. Minaei-Bidgoli, "Rezwan: Leveraging Large Language Models for Comprehensive Hadith Text
Processing: A 1.2M Corpus Development," arXiv:2510.03781, 2025.

[7] T. Wirahman, "Linking Hadith Narrator Identities Across Heterogeneous Arabic Biographical
Databases: A Multi-Signal Entity Resolution Pipeline," arXiv:2607.05424, 2026.

[8] N. Mihindukulasooriya, S. Tiwari, C. F. Enguix, and K. Lata, "Text2KGBench: A Benchmark for
Ontology-Driven Knowledge Graph Generation from Text," arXiv:2308.02357, 2023.

[9] M. A. Haque and R. Islam, "Hadith computational science in the age of large language models: a
critical narrative review," arXiv:2608.20364, 2026.

[10] B. Zhang and H. Soh, "Extract, Define, Canonicalize: An LLM-based Framework for Knowledge Graph
Construction," in *Proc. EMNLP 2024*, pp. 9820–9836. doi:10.18653/v1/2024.emnlp-main.548

[11] D. Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization,"
arXiv:2404.16130, 2024.

[12] A. B. Kamran, N. A. Butt, and A. Basharat, "Semantic Enrichment of Hadith Corpus—Knowledge Graph
Generation From Islamic Text," *Semantic Web*, vol. 17, no. 2, pp. 1–27, 2026.
doi:10.1177/22104968261431425

[13] O. Çinici, "Hadis Araştırmalarında Büyük Dil Modelleri (LLM): Teorik Çerçeve, Sınırlar ve Yapay Zekâ
Destekli Yapılandırılmış Veri İnşası," *Mevzu: Sosyal Bilimler Dergisi*, no. 16, pp. 299–326, 2026.
doi:10.56720/msbd.2026.s16.326

## Open points (remove before submission)

1. **Language and data.** The proposal assumes Arabic text from Sanadset. Confirm with the supervisor.
2. **Additional labelled data.** Whether the Ifta and AR-Sanad labels may be used depends on their
   licences, which are unconfirmed. The success criteria do not rely on them. The ledger simulation
   in section 2 does use them, for measurement only and without redistributing any data; decide
   whether it stays in the proposal.
3. **Division of work.** Section 7 is a suggestion. Replace it with what the group agreed.
4. **Sizes.** 100 hadiths (S1) and 50 labelled hadiths (S3, S4) are proposed values.
5. **Week dates.** Computed from "week 5 ends on 18 October". Check against the course calendar.
6. **Meeting 2.** Add anything the supervisor asked for on 9 October.
7. **Format.** Check on Teams whether the upload must be PDF or DOCX.
8. **Frame.** The claim "decisions are stored, derivable facts are derived again" and the two
   supporting studies were added on 13 October by the project owner. The supervisor has not seen
   this frame; confirm it in meeting 2 or remove the paragraphs that carry it (summary, section 2
   "The claim behind the design", the objective, the last in-scope item, S5, the second output).
9. **Work plan against existing code.** Weeks 10 and 11 list the checks, the decision record and the
   chain view as development. A first version of them exists. Decide whether those weeks become
   review, testing with a reviewer and labelling.
10. **Repository access.** The repository is private. Add the supervisor and the course staff as
    collaborators before the repository link is submitted in week 10.
11. **Reference for ripple-down rules.** Section 4 names the mechanism without a numbered reference.
    The record is verified (Compton and Jansen, *Knowledge Acquisition* 2(3), 1990,
    doi:10.1016/S1042-8143(05)80017-2) but the source was not read; cite it only after reading.
