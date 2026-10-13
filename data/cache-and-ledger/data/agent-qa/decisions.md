# Decision ledger: GiraffeGraph Core

Intent, rationale, rejected alternatives and constraints that the backend source does not state.
Compiled 2026-10-13 from the five ADRs, the rule sections of the wiki pages on the isnad pipeline,
engine experiments and correctness measurement, the workspace map, and the `.gitignore` comments of
`giraffegraph-core`. Turkish sources are translated. Paths are relative to the workspace root.

## D-01 Modular monolith first
Decision: The backend is one application in which each bounded context (project, schema, ingestion, extraction, validation, graph commit, review) is a module.
Why: The bounded contexts are clear, but the domain language and data model will change quickly in the early phase, and a microservice deployment would add operational complexity at that stage. One application gives faster iteration and lower operating cost and lets the domain boundaries be fixed in code first.
Rejected: Microservices. The ADR notes that high-traffic contexts may want to split off in the long run.
Source: giraffegraph-core/docs/adr/ADR-001-modular-monolith.md (Context, Decision, Consequences)

## D-02 Postgres for metadata, Neo4j for the canonical graph
Decision: Two stores are used: Postgres for project, schema, configuration, run, review and candidate metadata; Neo4j for the canonical graph.
Why: The platform has two different data needs, structured metadata and a highly relational graph, and each is kept in the store that suits it; the graph store also supports traversal and future GraphRAG scenarios. Accepted cost: two stores have to be operated, and synchronisation and transaction boundaries must be designed explicitly.
Source: giraffegraph-core/docs/adr/ADR-002-postgres-and-neo4j.md (Context, Decision, Consequences)

## D-03 Schema is data, not code
Decision: Node types, relation types, properties, merge keys and extraction hints are held as a versioned data model instead of being fixed in code.
Why: The product must not be locked to one domain, and these definitions must be manageable from the dashboard. This keeps the core generic, supports domain templates, and lets AI suggestions and manual overrides work together. Accepted cost: more modelling at the start, and a schema migration and versioning strategy becomes mandatory.
Rejected: Fixing the schema in code.
Source: giraffegraph-core/docs/adr/ADR-003-schema-as-data.md (Context, Decision, Consequences)

## D-04 GraphRAG stays an optional adapter
Decision: GraphRAG is not a hard dependency of the core; when needed it is attached as an adapter or plugin.
Why: It can be valuable for retrieval and some extraction scenarios, but it must not be the central technology the core depends on. Keeping it outside keeps the core stable and replaceable, allows other retrieval or extraction engines, and reduces dependence on experimental APIs. Accepted cost: somewhat more integration code, and the shortcuts of the official package are not used directly.
Rejected: Binding GraphRAG into the core as a hard dependency.
Source: giraffegraph-core/docs/adr/ADR-004-optional-graphrag-adapter.md (Context, Decision, Consequences)

## D-05 Candidate, then validation, then canonical graph
Decision: Extraction output first becomes candidates, then passes resolution and validation, and only then is committed to the canonical graph.
Why: If LLM-assisted extraction output is written straight into the canonical graph, data quality degrades quickly. The staged pipeline gives a safer graph write, an auditable run history and a natural intermediate layer for human review. Accepted cost: extra data model and operational steps, and a longer first implementation.
Rejected: Writing extraction output directly to the canonical graph.
Source: giraffegraph-core/docs/adr/ADR-005-candidate-validation-canonical.md (Context, Decision, Consequences)

## D-06 A new gate routes to review and never rejects
Decision: Any newly added validation gate must send a failing candidate to review under its own reason code instead of rejecting it.
Why: Rejection silently deletes information; a candidate that sits in review can still be counted.
Source: wiki/domains/hadith/isnad-pipeline.md, Rules

## D-07 No hadith-specific names in engine code
Decision: Engine code must stay free of hadith-specific names; domain behaviour is added as a segmentation strategy, a template or a provider.
Why: Core is a general engine and hadith is only its first case.
Source: wiki/domains/hadith/isnad-pipeline.md, Rules

## D-08 Three couplings to the hadith domain are acknowledged violations of D-07
Decision: Three places are recorded as breaking D-07 rather than as intended design: the generic validation step takes its text-grounding comparison from the hadith package, so every project's gates run with Arabic-folding normalisation; the chain-reading code carries the narrator node type and the narrated-from relation type as fixed names; the isnad strategy and the rule-based provider are registered directly at bootstrap because no plugin registration point exists.
Why: Same as D-07. The page keeps the list so that each item is deleted from it when the coupling is removed.
Source: wiki/domains/hadith/isnad-pipeline.md, Rules and Verification checklist

## D-09 The isnad pipeline behaviour is not an approved decision yet
Decision: The isnad pipeline behaviour counts as a prototype; when it is accepted by the team its status line is updated and the decision is written as an ADR.
Why: It has no team or advisor approval and no ADR; its design comes from a list of proposed code changes.
Source: wiki/domains/hadith/isnad-pipeline.md, Scope (status line) and Rules

## D-10 Narrator counts carry the identity caveat
Decision: Whenever a count of narrator nodes is reported, the report states that a narrator's identity is the spelling of the name.
Why: Identity is the full spelling including diacritics, so different people who share a short name merge into one node and one person written in different spellings becomes several nodes; narrator identity matching does not exist.
Source: wiki/domains/hadith/isnad-pipeline.md, Rules and "Bilinen sınırlar"

## D-11 Co-narrators attached with the conjunction "و" are not split
Decision: The rule-based segmenter leaves co-narrators as one mention when the conjunction و is written attached to the following name.
Why: Names such as وكيع and وهب begin with the same letter, so a split rule would cut real names. The recall loss is accepted.
Rejected: Adding a rule that splits on an attached و.
Source: wiki/domains/hadith/isnad-pipeline.md, "Bilinen sınırlar"

## D-12 The rule-based condition is not evidence about the gates
Decision: Results of the rule-based, LLM-free condition do not count as evidence of how well the grounding gates catch errors.
Why: The rule-based provider copies names and quotes verbatim from the text, so its output passes the gates by construction.
Source: wiki/domains/hadith/isnad-pipeline.md, "Bilinen sınırlar"; wiki/evaluation/correctness-measurement.md, "Uçtan uca temel koşu"

## D-13 Label-agreement numbers are never called accuracy
Decision: A value measured against Sanadset rule labels or Ifta platform labels is reported as agreement with that label set and as a difference between systems, with the reference name and the matching criterion stated; the word "accuracy" is not used.
Why: Neither reference is a human gold standard.
Source: wiki/evaluation/engine-experiments.md, Rules; wiki/evaluation/correctness-measurement.md, Rules

## D-14 Every number states its layer, reference and matching criterion
Decision: Each reported number carries its correctness layer, its reference (silver, gold or rule) and its matching criterion, and the matching criterion is fixed in the protocol independently of the measurement.
Why: "Is it correct?" is five separate questions, each measured against a different reference, and the same output scores very differently by criterion (pilot parser F1 0.628 under strict matching, 0.879 under lenient matching).
Source: wiki/evaluation/correctness-measurement.md, Rules, BLUF, "Eşleşme kriteri" and "Somut örnek"

## D-15 The rule-based score on the 50 pilot hadiths is not a test result
Decision: The rule-based score on the 50 pilot hadiths is never presented as a test result; the test set is the 300-hadith set that shares no hadith with the pilot.
Why: The rule-based segmenter was tuned on those 50 hadiths.
Source: wiki/evaluation/engine-experiments.md, Rules and "Veri kümeleri"

## D-16 The Sonnet runs are not a model comparison
Decision: The Claude Sonnet 5.5 runs on 36 hadiths must not be reported as a comparison between models.
Why: What they measure is a configuration error produced jointly by the provider's wire format (properties sent as a list of name and value entries) and the effort setting `low`. No Sonnet run exists with another effort level or another wire format.
Source: wiki/evaluation/engine-experiments.md, Rules and "Sonnet 5.5, effort low: yapılandırma hatası"

## D-17 Precision, recall and F1 are reported together
Decision: P, R and F1 are always given together; if F0.5 is used as a summary, raw P and R stand next to it.
Why: In the pilot the binding constraint is recall.
Source: wiki/evaluation/correctness-measurement.md, Rules

## D-18 Confidence intervals are computed at hadith level
Decision: The unit of analysis is the hadith, and confidence intervals are computed by resampling hadiths.
Why: Triples cluster inside a hadith, so the interval comes from a hadith-level cluster bootstrap.
Source: wiki/evaluation/correctness-measurement.md, Rules and "Kanıt türleri"

## D-19 No single hallucination rate
Decision: A "hallucination rate" is never given as one number; mentions absent from the source, values absent from their quote, and category errors are reported separately.
Why: The rule itself states no reason. The same page's findings show that these failures behave differently: in the pilot the "quote exists in the source" check caught nothing while the "value exists in the quote" check caught 10.1%, and a text-presence check catches fabrication but not a correct word taken from the wrong place.
Source: wiki/evaluation/correctness-measurement.md, Rules, "Somut örnek" and "Ölçülmüş olanlar"

## D-20 Over-merge rate is the primary identity metric
Decision: For narrator identity (layer L2) the primary metric is the over-merge rate.
Why: Wrongly merging two narrators changes the ruling on the chain; a missed merge only produces duplicates.
Source: wiki/evaluation/correctness-measurement.md, Rules

## D-21 Deterministic risk flags, not LLM confidence, for routing to review
Decision: As the signal that routes candidates to a human, deterministic risk flags are preferred over the LLM's confidence score.
Why: The model's own confidence is a weak routing signal: it separated correct from wrong mentions with AUC 0.626 in the pilot and 0.634 in the 300-hadith schema-only run.
Source: wiki/evaluation/correctness-measurement.md, Rules and "Ölçülmüş olanlar"

## D-22 Correctness layers are ordered and source integrity comes first
Decision: The layers (source integrity, extraction, identity, graph consistency, consumption) are evaluated in that order.
Why: If the source layer is wrong, every number above it measures the wrong text. This happened in the Quran case: a translation attributed to the wrong translator and corrupted to ASCII was the input of 6236 embeddings.
Source: wiki/evaluation/correctness-measurement.md, "Katman modeli"

## D-23 The gold standard is produced under a blind protocol
Decision: The person who produces a gold label does not see system output, the person who makes a review decision on a hadith has not produced that hadith's gold label, and the gold standard is itself reported with inter-coder agreement.
Why: The reliability of the gold standard depends on it; the page calls the blind protocol mandatory.
Source: wiki/evaluation/correctness-measurement.md, "Kanıt türleri" and "Önkoşullar"

## D-24 Review decisions are meant to target content, not candidate ids
Decision: A content-addressed decision target is a prerequisite for measurement; what exists is only the minimal decision record (who, when, how long).
Why: If a human decision stays bound to a candidate's UUID, the labelling effort is lost at every re-extraction.
Source: wiki/evaluation/correctness-measurement.md, "Önkoşullar"; wiki/architecture/workspace-map.md, "Bilinen durum notları"

## D-25 A relation's identity is scoped to the hadith
Decision: The identity of a transmission edge includes hadith-scoped keys.
Why: Otherwise the transmissions of the same narrator pair in different hadiths collapse into one edge and chain-level metrics cannot be measured.
Source: wiki/evaluation/correctness-measurement.md, "Önkoşullar"

## D-26 Evaluation outputs and the LLM response cache stay out of the Core repository
Decision: Only aggregate comparison tables from evaluation runs are tracked in Core; per-run output files and the local LLM response cache are ignored, and their copies live in the private evaluation-data repository.
Why: Evaluation outputs hold third-party hadith text and quotations.
Source: giraffegraph-core/.gitignore (comments); wiki/architecture/workspace-map.md, "Bilinen durum notları"

## D-27 Downloaded evaluation data is not redistributed and never executed
Decision: External labelled data is used for evaluation only, is not redistributed, and downloaded raw files are treated as untrusted and are not executed.
Why: The source states the constraint without a reason. It records the files as untrusted downloads and notes that the licence statements of the datasets conflict or are missing and that no written permission is on record.
Source: wiki/architecture/workspace-map.md, "Harita" and "Çalışma alanı dışındaki ilgili varlıklar"; wiki/evaluation/correctness-measurement.md, "Önkoşullar"

## D-28 Two sibling folders are out of scope
Decision: The folders `giraffle/` and `giraffe-code/` are not read or searched in project tasks.
Why: They only share a name with the project and have no code in common with the knowledge graph, hadith or RAG work; the rule keeps an agent from wandering into about 3.4 GB of unrelated code.
Source: wiki/architecture/workspace-map.md, Purpose and Rules

## D-29 The two dated source packages are frozen
Decision: The Claude Science context and results packages dated 2026-09-30 are never edited; new findings are written elsewhere, and a citation names the folder as well as the file.
Why: They are frozen references that the measurement and protocol proposals come from, and file numbers are independent in the two packages, so a number alone is ambiguous.
Source: wiki/architecture/workspace-map.md, "Harita" and Rules

## D-30 A path change in the source or literature folders is propagated in the same task
Decision: When a file under the source packages or the literature folder moves, everything that depends on its path (Core tests, the data README, the thesis build script) is updated in the same task.
Why: The pilot regression tests skip instead of failing when the file is missing, so the breakage would go unnoticed.
Source: wiki/architecture/workspace-map.md, Rules
