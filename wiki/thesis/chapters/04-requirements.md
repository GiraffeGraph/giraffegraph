# 4 Requirements and scope

This chapter states what the system must do, where each requirement is implemented and which test checks it. Implementation paths are relative to `backend/src/app/` unless they start with another directory. Test files are in `backend/tests/unit/` or `backend/tests/integration/`. We list a requirement only if its code is on the `main` branch.

## 4.1 Users and use cases

The system has no user accounts, so the roles below are not enforced by the software.

- **Schema owner.** Creates a project, defines node and relation types or applies a template schema, and activates a schema version.
- **Operator.** Loads source text, starts processing and commits a run to the graph.
- **Reviewer.** A person with domain knowledge who accepts, rejects or edits the candidates in the review queue. The reviewer types a name, which is stored with every decision.
- **Reader.** Browses the committed graph and, in the case study, reads a hadith with its narrator chains, quotations and acceptance records.

The use cases are: set up a project with a schema, load texts, process a text into validated candidates, decide the open review items, commit a run, and trace a committed fact back to its source text and its acceptance.

## 4.2 Functional requirements

| ID | Requirement | Implemented in | Verified by |
|---|---|---|---|
| FR1 | A project has versioned schemas with node types, relation types, properties and merge keys. Names are ASCII identifiers. Only a draft version can be edited. | `application/use_cases/schema_management.py`, `domain/schema/identifiers.py` | `test_project_schema_api.py` |
| FR2 | Creating a project can apply a template schema and activate it in the same request. | `ProjectSetupService`, `infrastructure/template/catalog.py` | `test_template_project_api.py` |
| FR3 | Source text is loaded one unit at a time or in bulk. A repeated external reference is reported per item. | `IngestionManagementService` | `test_ingestion_api.py`, `test_bulk_ingest_api.py` |
| FR4 | A source unit is cut into segments by a named strategy: `paragraphs`, or `isnad` with one segment per narrator chain and source offsets. | `domain/extraction/segmentation.py`, `domain/hadith/segmentation.py` | `test_hadith_segmenter.py`, `test_isnad_segmentation.py` |
| FR5 | A provider proposes candidates per segment. A failed call does not discard the other calls. An unknown type or undeclared property is dropped alone and recorded as a schema proposal. | `ExtractionManagementService.extract_candidates` | `test_isnad_pipeline_api.py`, `test_grounding_extraction_api.py` |
| FR6 | Candidates are validated against the schema: type, required properties, merge keys, endpoint types, allowed values, confidence thresholds and duplicates. | `PipelineManagementService.validate_run` | `test_pipeline_api.py` |
| FR7 | The quotation of an extracted candidate must occur in its segment, and a node's merge-key value must occur in the quotation. A failed check sends the candidate to review. | `_evidence_findings`, `_merge_key_grounding_findings`, `domain/hadith/grounding.py` | `test_hadith_grounding.py`, `test_grounding_extraction_api.py` |
| FR8 | Two relations between the same two nodes with different merge-key values are stored as two edges. | `domain/shared/resolution.py`, `infrastructure/persistence/neo4j/repositories.py` | `test_resolution.py`, `test_commit_api.py` |
| FR9 | A reviewer accepts, rejects or edits a review item. Each decision is stored with reviewer, time and optional duration; decisions are only appended. Automatic steps do not change a decided candidate. | `ReviewManagementService.decide_review_item`, `validate_run`, table `review_decisions` | `test_review_decisions_api.py`, `test_review_api.py` |
| FR10 | For every validated candidate of a run, the system reports the human decision or the automatic policy that accepted it. | `ReviewManagementService.list_acceptance_records` | `test_review_decisions_api.py` |
| FR11 | A run is committed once, and only when no candidate is pending and no review item is open. | `CommitManagementService.commit_run` | `test_commit_api.py` |
| FR12 | Extraction, validation and commit run as queued jobs consumed by a worker, or in one synchronous request for a list of source units. | `processing_job_management.py`, `interfaces/cli/processing_jobs_worker.py`, `SourceUnitProcessingService` | `test_processing_jobs_api.py`, `test_bulk_ingest_api.py` |
| FR13 | The committed graph can be read, and a committed hadith can be read as ordered chains with quotations and acceptance records. | `application/use_cases/exploration_management.py` | `test_exploration_api.py`, `test_chains_api.py` |
| FR14 | A browser dashboard drives the steps above. | `frontend/src/modules/projects/` | No automated test; CI builds it |

## 4.3 Non-functional requirements

| ID | Requirement | Implemented in | Verified by |
|---|---|---|---|
| NFR1 | Traceability: a committed node or edge links to its source unit and supporting segments. | `DERIVED_FROM`, `SUPPORTED_BY` and `RelationEvidence` written by `Neo4jCanonicalGraphRepository` | `test_exploration_api.py` (in-memory), `test_realdb_isnad_flow.py` (`real_db`) |
| NFR2 | Atomic graph write: a failed commit leaves no part of the run in the graph. | `commit_bundle` runs `_write_bundle` in one `execute_write` transaction | `test_realdb_isnad_flow.py` (`real_db`) |
| NFR3 | The engine runs and is tested without a database, a network or an API key. | `infrastructure/persistence/memory/`, `infrastructure/llm/rule_based_isnad_provider.py` | The default test run, `test_isnad_baseline_script.py` |
| NFR4 | Domain behaviour is added as a segmentation strategy, a template or a provider. | `SegmentationStrategy`, `StaticDomainTemplateCatalog`, `StaticLLMProviderRegistry`, `bootstrap/container.py` | `test_isnad_pipeline_api.py`, `test_rule_based_isnad_provider.py` |
| NFR5 | Repeated model calls are served from a cache, and token usage is reported per call. | `infrastructure/llm/cached_provider.py`, `infrastructure/llm/anthropic_provider.py` | `test_llm_cache_provider.py`, `test_anthropic_provider.py` |
| NFR6 | The database schema is created only through migrations and matches the ORM models. | `backend/migrations/versions/` `0001` to `0006` | `test_review_decisions_migration.py`, `test_realdb_migrations.py` (`real_db`) |
| NFR7 | Backend code passes lint and strict type checking on every push. | `backend/pyproject.toml`, `.github/workflows/ci.yml` | The CI workflow |

Tests marked `real_db` need running databases and are skipped otherwise (Section 6.7). NFR4 holds with the exceptions listed in Section 5.1.

## 4.4 Out of scope

We checked each item against the code.

- **Narrator identity resolution.** The `Narrator` type has the single merge key `name`, compared after Unicode NFKC normalisation, whitespace collapsing and case folding only (`normalize_text`). People with the same written name share a node, and one person written in two ways becomes two nodes.
- **Domain rules that need biographical dates.** The isnad schema has no date properties, and validation has no hook for rules such as checking that two narrators were contemporaries.
- **Authenticity grading.** No type or property holds a grade for a hadith or a narrator.
- **Authentication and users.** No router has an authentication dependency. The reviewer name is free text.
- **Undo of a committed run.** The API has 33 `GET` and 20 `POST` endpoints and no `PUT`, `PATCH` or `DELETE`. A completed run cannot be changed.
- **Turkish hadith text.** The normalisation and the lexicon of transmission formulas cover Arabic script only. Only the dashboard interface is in Turkish.
- **Question answering over the graph.** The read endpoints list and show nodes, relations and chains. An `EmbeddingProvider` protocol is declared in `application/ports/llm_provider.py` without an implementation, and there is no retrieval endpoint.

Two schema fields are stored but not enforced. The `data_type` of a property is sent to the model and is not checked during validation. The `directional` flag of a relation type is not used after it is stored.
