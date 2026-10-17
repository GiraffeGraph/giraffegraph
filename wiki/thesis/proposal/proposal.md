# CSE 491 Project Proposal

<!-- The headings, sub-labels and table columns follow the course template
(CSE491_Project_Proposal_Template.docx); build_proposal.py writes this text into that template. -->

| Field | Value |
|---|---|
| Project title | A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and Schema Drift in LLMs: An Application on Hadith Isnad Chains |
| Group no. | |
| Project supervisor | Res. Asst. Dr. Taha Yiğit Alkan |
| Submission date | 18 October 2026 |

| # | Name and surname | Student no. | Role / responsibility in the project |
|---|---|---|---|
| 1 | Yahya Efe Kuruçay | 20220808005 | Architecture, validation checks, decision record, scoring script |
| 2 | Deniz Büyükşahin | 20240808701 | Labelling guideline, annotation (annotator 1), review screen |
| 3 | Alperen Ulukaya | 20220808006 | Isnad segmenter, annotation (annotator 2), chain view |

## 1. Summary

Large language models (LLMs) can turn text into knowledge graph facts, but they add facts the source
does not contain and drift away from the schema they were given. GiraffeGraph is an engine in which
the model only proposes. Each proposed fact carries a quotation from the source, is checked by
deterministic rules, and reaches the graph only through a recorded human decision or a recorded
acceptance policy. The design rests on one claim: what such a system has to store is the decision of
a person, and what can be derived from the source is derived again.

Our case study is the hadith isnad, the chain of narrators that precedes a hadith text. In a first
measurement on 300 hadiths, a check of whether the extracted name occurs in the model's own quotation
flagged 122 of the 145 proposals that disagreed with existing platform labels. Those labels were not
checked by people. By the end of CSE 491 we will deliver a working prototype that processes Arabic
hadiths end to end and reports how many errors each check catches on 50 hadiths labelled by two group
members, with disagreements decided by three hadith scholars. Entity resolution of narrators, the
larger experiment and the question-answering layer are planned for Senior Design Project II.

## 2. Problem Definition and Motivation

When an LLM extracts a narrator chain from a hadith, four things go wrong. It outputs a narrator the
text does not contain, or silently rewrites a name it did find. The same relation appears under
different names in different runs (schema drift). One narrator is written in several ways and several
narrators share one short name. After the graph is built, nobody can tell which sentence a fact came
from or who accepted it.

This matters because the reliability of a hadith is judged from its chain. One wrong narrator changes
the verdict, so a graph that is mostly right is not usable by a scholar.

**Target users.** Researchers and students in hadith studies, and engineers who build knowledge graphs
whose facts must be traceable to their source.

**What we already observed.** On 12 October 2026 we ran one model (Claude Haiku 5.5) on 300 hadiths,
50 from each of the six canonical collections, and scored the output against the narrator labels of
the Ifta Sunnah platform (1,778 reference mentions, loose matching):

- F1 was 0.923 for a rule-based parser, 0.890 for the LLM given only the schema and 0.956 for the LLM
  given an isnad-aware prompt, so raw extraction accuracy is not where we can contribute most.
- Checking that the model's quotation occurs in the source flagged nothing. Checking that the
  extracted name occurs inside the model's own quotation flagged 155 of 1,688 proposals (9.2%),
  including 122 of the 145 that disagreed with the labels, with 33 false alarms. Most flagged
  proposals were correct names that the model had transliterated or changed in grammatical case, not
  invented narrators. Precision of the proposals accepted without review rose from 0.914 to 0.985.
- The model's self-reported confidence separated right from wrong proposals poorly (AUC 0.634). Sending
  every proposal below 0.85 to review would send 16.3% of them and catch 50 of the 145.
- In the same hadiths, 10.0% of the 2,150 chain positions use a name shared by several of the 740
  persons, and 25.8% of the persons appear under more than one name.

The labels are not a human gold standard, so these are comparisons between methods. One aim of the
project is to repeat them on hand-labelled data.

**The claim behind the design.** A candidate that a parser or a model extracts can be extracted again,
so it is checked, not trusted, and it does not have to be kept. An acceptance, a correction or the
identification of a narrator by a person cannot be derived from any text and has to be stored once,
with who decided and when. Two exploratory simulations of 13 October 2026, with no person taking part,
looked at this. On 27,056 labelled chains of AR-Sanad [5], an identity decision reused whenever the same
written name appears was wrong for one mention in ten; narrowing the decision only after a rule on
generations and death years found a contradiction lowered the silent error to 0.014 per mention. In a
second domain, a coding agent answered why-questions about the engine's code 0% to 4% correctly from
the code alone and 88% to 100% correctly with a ledger of decisions (12 questions, two runs each).

## 3. Objectives, Scope and Success Criteria

### Objectives

- Build an engine that turns Arabic hadith text into a narrator-chain graph in which every fact is
  tied to a source quotation and to a recorded decision. It covers loading hadiths from Sanadset 650K
  [1], rule-based separation of isnad and text, one LLM call per chain constrained to a fixed schema,
  three deterministic checks (the type is in the schema; the quotation occurs in the source; the
  value occurs in the quotation), one domain rule (the Prophet is not a narrator), a review screen and
  a canonical graph.
- Measure how many extraction errors each check catches on its own against hand-labelled data, and
  compare it with the model's own confidence when the same share of proposals is sent to review.
- Build a reference set of 50 hadiths labelled by two annotators, with disagreements decided by three
  hadith scholars, and report how often the annotators and the scholars agree.
- Report the two supporting studies of the claim with their scripts and limits.

### Out of scope

- Linking narrator mentions to an authority list (entity resolution) and an identity ledger inside
  the engine; domain rules that need biographical dates; question answering over the graph;
  multi-model experiments and a labelled set larger than 50 hadiths. These are planned for Project II.
- Turkish hadith text: we found no copyright-free Turkish source with full chains.
- Judging the authenticity of hadiths. The system records chains; it does not grade them.

### Success criteria

- **S1.** 100 hadiths pass from upload to canonical graph with no manual step outside the review
  screen (logged end-to-end run).
- **S2.** 100% of facts in the canonical graph have a source quotation and a decision record (automated
  test over the graph).
- **S3.** Precision, recall and F1 are reported for four conditions (rule-based parser; LLM; LLM with
  checks; LLM with checks and human review) on the 50 labelled hadiths, under strict and loose
  matching, with hadith-level bootstrap confidence intervals. For each check the table gives how many
  wrong proposals it flags on its own, next to what the model's confidence flags at the same review
  share.
- **S4.** Agreement between the two annotators (mutual F1), agreement among the three scholars
  (Fleiss' kappa), the number of contested items and the labelling time per hadith are reported.
- **S5.** Every number of the two supporting studies is reproduced by a script from a clean clone of
  the repository, and the report states what was measured for and against the claim.

## 4. Similar Systems and Background

| System / work | What it does | Limitation or gap your project addresses |
|---|---|---|
| Sanadset 650K [1] | 650,986 hadith records from 926 books with narrator tags produced by regular expressions | No human check of the tags |
| SemanticHadith [2], [3] | Ontology and knowledge graph of the six canonical collections; narrators extracted with a custom NER model (micro F1 97%); three experts checked samples | No LLM extraction and no decision per fact; ambiguous names are left for manual review; expert validation framework listed as future work |
| Muther and Smith [4] | Expert-annotated isnad boundaries in 50 classical texts | Finds isnad spans, not narrators; experts agree exactly on the end point in only 53% of cases |
| AR-Sanad 280K [5] | 27,056 real chains linked to 18,298 narrator identities | Starts from separated names, not text; 60.6% of chains contain at least one wrong narrator |
| Oumer [6] | Fine-tuned narrator and relation extraction on 223,478 hadiths (narrator F1 0.98) | Needs large labelled training data; no provenance or human review |
| Rezwan [7] | LLM-assisted corpus of 1.2M narrations scored by six experts | Scores without an agreement statistic; not comparable across studies |
| Text2KGBench [8] | Benchmark for ontology-driven graph extraction with LLMs | Shows that "appears in the text" does not imply "correct" (precision 0.38 on one dataset) |
| Tsaneva et al. [10] | Nine workflows combining LLM validators and people to validate a scientific graph, scored against three experts | Whole workflows compared; single modules are not evaluated in isolation |
| KARMA [11] | Multi-agent LLM enrichment of a biomedical graph with validation agents | Ablation scored by an LLM judge, not an external reference |
| ODKE+ [12] | Production extraction with a second LLM as grounding judge | No deterministic check of the extracted value; method of the reported effects not given |

**Position of this project.** A recent review of the field [9] names weak benchmark comparability and
sparse expert validation as open problems. A hadith knowledge graph, its ontology and accurate fine-tuned extractors
already exist; we build on them for the schema. Routing uncertain facts to people by confidence or by
disagreement is not new [10]–[12], and we do not claim it. We did not find a check that the extracted
value occurs in the model's own quotation reported as its own error class, nor a measurement of what
each deterministic check catches on the same candidates against an external reference, compared with
the model's confidence at the same review share. Our search was not systematic, so this is a
statement about what we found.

## 5. Preliminary Requirements

### Functional requirements

| ID | Requirement | Priority (must / should / could) |
|---|---|---|
| FR-1 | The system shall ingest a hadith as one source unit with a stable identifier and content hash. | must |
| FR-2 | The system shall split a hadith into isnad and text and return narrator mentions with character offsets. | must |
| FR-3 | The system shall request candidates from an LLM for one chain at a time, constrained to the schema. | must |
| FR-4 | The system shall reject a candidate whose type is not in the schema without discarding the other candidates of the same call, and record the unknown type. | must |
| FR-5 | The system shall mark a candidate for review when its quotation does not occur in the source. | must |
| FR-6 | The system shall mark a candidate for review when its extracted value does not occur in its quotation. | must |
| FR-7 | The system shall mark a candidate for review when it names the Prophet as a narrator. | should |
| FR-8 | The system shall show candidates with their quotation and check results and let a reviewer accept, reject or edit them. | must |
| FR-9 | The system shall record for every decision the reviewer, the time and the duration. | must |
| FR-10 | The system shall write accepted facts to the canonical graph so that links between the same two narrators in different hadiths stay distinct. | must |
| FR-11 | The system shall display the chain of a hadith with the source quotation of each link. | should |
| FR-12 | The system shall score output against a reference file and report precision, recall and F1. | must |
| FR-13 | The system shall let a user define node types, relation types and properties, and reject identifiers the graph database cannot store. | could |

### Non-functional requirements

| ID | Requirement | How it will be checked |
|---|---|---|
| NFR-1 | No fact reaches the canonical graph without a decision record. | Automated test (S2) |
| NFR-2 | Re-running a commit does not create duplicate nodes or links. | Integration test |
| NFR-3 | The backend test suite runs without a database or network access in under one minute. | CI |
| NFR-4 | A new user can start the system from the README alone. | Test on a clean machine in week 14 |
| NFR-5 | No API keys or passwords are stored in the repository. | Repository scan in CI |

## 6. Method and Technology Plan

**Approach.** The engine is a pipeline with a gate at each stage. The model has no write access to
the graph; a candidate becomes a fact only after it passes the checks and receives a decision.

```
hadith text → isnad segmenter → LLM proposal (per chain) → checks → review → canonical graph
```

**Measurement.** We add the stages one at a time and score each configuration against the
hand-labelled set, so the contribution of each stage can be read from the table. The matching rule is
fixed before measurement: strict (normalised strings equal) and loose (equal, substring, or token F1
of at least 0.60), with maximum-weight matching between system and reference mentions. The hadith is
the unit of analysis.

**Labelled data and the hadith scholars.** Two group members label the same 50 hadiths
independently, following a written guideline and without seeing system output; the member who writes
the checks does not label. Our supervisor advised working with more than one scholar, because hadith
scholars can disagree among themselves. Three scholars take part: Prof. Dr. Rifat Atay (Faculty of
Theology) and two scholars we will identify by week 6. All three review the guideline before
labelling starts. Every item on which the two annotators disagree goes to the three scholars, who
decide it independently of each other, and the majority answer enters the reference. When all three
answers differ, the item is marked contested, left out of the main score and reported separately. Ten
randomly chosen hadiths on which the annotators agreed also go to the scholars, to catch errors both
annotators share. The scholars do not judge system output, so the people who set the reference do not
also judge the system.

**Existing code.** GiraffeGraph Core already implements ingestion, LLM extraction, candidate
validation, a review queue and commit to Neo4j. The checks and the decision record were written in
October with AI coding assistants and have automated tests, but the group has not reviewed them and
no reviewer has used them. Reviewing, testing and measuring them is the main work of this term.

| Layer / component | Technology or tool | Reason for the choice |
|---|---|---|
| Backend | Python 3.12, FastAPI | Existing code base; team experience |
| Operational store | PostgreSQL 16 | Runs, candidates, review items and decisions are relational |
| Canonical graph | Neo4j 5 | Path queries over chains |
| Review dashboard | Next.js 15 | Existing review interface |
| LLM access | OpenAI-compatible HTTP API | Switch between hosted and open models without code changes |
| Development | uv, pytest, ruff, Docker Compose, GitHub Actions | Reproducible setup and CI |
| Data | Sanadset 650K (text); Ifta Sunnah labels for measurement only | Arabic text with full chains under an open licence; platform labels are not redistributed |

**Use of AI assistants.** AI assistants were used for the literature search, the measurements, the
code and the drafting of this document. References were retrieved from Crossref, arXiv and the ACL
Anthology. The group is responsible for every statement here.

## 7. Work Plan

| WP | Work package and its output | Responsible member(s) | Weeks |
|---|---|---|---|
| WP1 | Architecture, data model, three screen sketches and technology decision table | Yahya Efe Kuruçay; all for review | 5–7 |
| WP2 | Labelling guideline reviewed by the three scholars; 50 hadiths labelled by two annotators; scholar decisions; agreement figures and reference set | Deniz Büyükşahin, Alperen Ulukaya | 6–8 |
| WP3 | Midterm report and presentation | All | 8 |
| WP4 | Group review of the existing engine; segmenter, per-chain extraction, three checks and the Prophet rule tested | Alperen Ulukaya (segmenter), Yahya Efe Kuruçay (checks) | 9–10 |
| WP5 | Review screen used by a group member on the labelled set; decision record and chain view tested | Deniz Büyükşahin (review screen), Alperen Ulukaya (chain view), Yahya Efe Kuruçay (decision record) | 10–11 |
| WP6 | Integration on 100 hadiths, scoring script, test against S1–S5, final report, README and demo | All; Yahya Efe Kuruçay (scoring) | 12–15 |

Supervisor meetings follow the course plan (weeks 6–7, 9–10 and 12–13). Every member commits their
own work under their own account.

## 8. Expected Outputs and Risks

### Expected outputs

- A working prototype in one private repository with README, tests and CI; the engine is published
  under an open-source licence at the end of the project.
- A labelling guideline and 50 labelled hadiths with annotator and scholar agreement figures.
- A results table for the four conditions in S3.
- The two supporting studies with their scripts, result files and stated limits.
- Final report, presentation and a plan for Project II.

### Risks

| Risk | Likelihood | Impact | Mitigation plan |
|---|---|---|---|
| Labelling takes longer than planned | Medium | Medium | Measure time per hadith on the first ten; label in a spreadsheet instead of building a tool |
| Annotators disagree often | Medium | High | Add boundary rules to the guideline and repeat the round |
| A scholar cannot take part or is late | Medium | Medium | Work with two scholars; when they disagree the item is contested |
| Scholars disagree on many items | Medium | Medium | Report the contested share as a result; clarify the guideline with the scholars |
| Development starts late | Medium | High | Simplify the interface; keep the checks and the scoring |
| Licence of the platform labels cannot be confirmed | Medium | Low | Use them for measurement only; rely on Sanadset and our own labels |

## 9. References

[1] M. Mghari, O. Bouras, and A. El Hibaoui, "Sanadset 650K: Data on Hadith narrators," *Data in
Brief*, vol. 44, 108540, 2022. doi:10.1016/j.dib.2022.108540

[2] A. B. Kamran, B. Abro, and A. Basharat, "SemanticHadith: An ontology-driven knowledge graph for
the hadith corpus," *Journal of Web Semantics*, vol. 78, 100797, 2023.
doi:10.1016/j.websem.2023.100797

[3] A. B. Kamran, N. A. Butt, and A. Basharat, "Semantic Enrichment of Hadith Corpus—Knowledge Graph
Generation From Islamic Text," *Semantic Web*, vol. 17, no. 2, pp. 1–27, 2026.
doi:10.1177/22104968261431425

[4] R. Muther and D. Smith, "Tracing Traditions: Automatic Extraction of Isnads from Classical Arabic
Texts," in *Proc. Fifth Arabic Natural Language Processing Workshop*, 2020, pp. 130–138.
https://aclanthology.org/2020.wanlp-1.12/

[5] S. Mahmoud, O. Saif, E. Nabil, M. Abdeen, M. ElNainay, and M. Torki, "AR-Sanad 280K: A Novel 280K
Artificial Sanads Dataset for Hadith Narrator Disambiguation," *Information*, vol. 13, no. 2, 55,
2022. doi:10.3390/info13020055

[6] J. M. Oumer, "Relation extraction for graph-based representation of Hadith Isnad," M.S. thesis,
University of Malta, 2025. https://www.um.edu.mt/library/oar/handle/123456789/137629

[7] M. Asgari-Bidhendi, M. A. Ghaseminia, A. Shahbazi, S. A. Hossayni, N. Torabian, and
B. Minaei-Bidgoli, "Rezwan: Leveraging Large Language Models for Comprehensive Hadith Text
Processing: A 1.2M Corpus Development," arXiv:2510.03781, 2025.

[8] N. Mihindukulasooriya, S. Tiwari, C. F. Enguix, and K. Lata, "Text2KGBench: A Benchmark for
Ontology-Driven Knowledge Graph Generation from Text," arXiv:2308.02357, 2023.

[9] M. A. Haque and R. Islam, "Hadith computational science in the age of large language models: a
critical narrative review," arXiv:2608.20364, 2026.

[10] S. Tsaneva, D. Dessì, F. Osborne, and M. Sabou, "Knowledge graph validation by integrating LLMs and
human-in-the-loop," *Information Processing & Management*, vol. 62, no. 5, p. 104145, 2025.
doi:10.1016/j.ipm.2025.104145

[11] Y. Lu, W. Wu, X. Zhao, R. Peng, and J. Wang, "KARMA: Leveraging Multi-Agent LLMs for Automated
Knowledge Graph Enrichment," in *Proc. NeurIPS 2025*. arXiv:2502.06472

[12] S. Khorshidi et al., "ODKE+: Ontology-Guided Open-Domain Knowledge Extraction with LLMs,"
arXiv:2509.04696, 2025.
