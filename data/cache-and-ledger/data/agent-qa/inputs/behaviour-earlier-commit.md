# Backend behaviour

## 1. Source ingestion and segmentation

- `IngestionManagementService.create_source_unit` stores a `SourceUnit` from the `raw_content` string of `SourceUnitCreateInput` (plus `source_type`, `title`, optional `sequence_no`, `external_ref`, `metadata_json`) with status `READY`.
- It requires an existing project and a non-`DRAFT` schema version of that project; otherwise `NotFoundError` or `RuleViolationError`.
- Segmentation is a separate call, `PipelineManagementService.generate_segments`; the only accepted `strategy` is `paragraphs`, anything else raises `RuleViolationError`.
- `_split_into_segments` splits on blank lines (`\n\s*\n`); with at most one chunk it falls back to non-empty lines, then to the whole stripped content.
- Each `Segment` gets a new UUID, a 1-based `segment_order` and `metadata_json={"strategy": "paragraphs"}`; it has no offsets into `raw_content`, and no size limit or overlap is applied.
- `replace_for_source_unit` deletes the source unit's existing segments first, so regenerating changes every `segment_id`.
- Extraction without segments raises "Segments must be generated before candidate extraction can run."

Sources: application/use_cases/ingestion_management.py:92-125; application/dto/contracts.py:62-72; application/use_cases/pipeline_management.py:61-79; application/use_cases/pipeline_management.py:870-880; domain/ingestion/entities.py:7-28; infrastructure/persistence/postgres/repositories.py:451-457; application/use_cases/extraction_management.py:125-132

## 2. Extraction: providers, prompts, what is sent to the model

- `get_container` always registers `NoOpLLMProvider` (`noop`) and adds `OpenAILLMProvider` (`openai`) only when `openai_api_key` is non-blank; the default provider `noop` always returns empty `nodes` and `relations`.
- `_require_llm_provider` uses the run's `llm_provider`, else the default; an unregistered name raises `RuleViolationError`. The model is the run's `llm_model`, else `default_llm_model`; OpenAI raises `RuleViolationError` without one.
- The prompt is fetched by key `candidate_graph_extraction` and version `default_extraction_prompt_version` (`candidate_graph_extraction_v1`); an unregistered version raises `RuleViolationError`.
- The prompt asks for `nodes` (`ref`, `node_type`, `properties`, `merge_key_payload`, `confidence`, `evidence_refs`) and `relations` (`relation_type`, `from_ref`, `to_ref`, `properties`, `confidence`, `evidence_refs`).
- `extract_candidates` makes one `generate_structured` call. `_build_prompt_payload` sends run ids, source-unit metadata (not `raw_content`), every node and relation type with merge keys, thresholds, aliases, hints and property definitions, and all segments.
- `OpenAILLMProvider` POSTs to `{base_url}/chat/completions` with `temperature: 0`, `response_format` `json_object`, the prompt as system message and `{"schema_name", "payload"}` JSON as user message.
- With `dry_run` no candidate is persisted; otherwise the run must have no candidates yet.
- Each call writes an `ExtractionExecution` record (`RUNNING`, then `SUCCEEDED` or `FAILED`).

Sources: bootstrap/container.py:137-146; infrastructure/llm/noop_provider.py:5-21; infrastructure/llm/openai_provider.py:73-121; infrastructure/llm/prompt_catalog.py:6-45; application/use_cases/extraction_management.py:104-167; application/use_cases/extraction_management.py:237-314; application/use_cases/extraction_management.py:437-474; infrastructure/config/settings.py:23-28

## 3. What happens to the model's output (parsing, undefined types and properties, failures)

- `_extract_content` accepts string content or a list of text parts; `_parse_output` strips a surrounding ``` fence and runs `json.loads`. Missing choices, non-text content or non-JSON output raise `ExternalServiceError`.
- `_normalize_output` validates against `StructuredExtractionContract` (`extra="ignore"` drops unknown fields; `confidence` must be 0–1); a mismatch raises `RuleViolationError`.
- `_resolve_node_type` and `_resolve_relation_type` use a stripped, casefolded registry of names and aliases; an alias is replaced by the canonical name, and a lookup shared by two types raises "Schema contains ambiguous … lookup".
- An undefined node or relation type raises `RuleViolationError` ("Structured extraction returned undefined node type '…'"); the item is neither skipped nor sent to review.
- Also fatal: a duplicate node `ref`, a relation referencing an unknown `ref`, and a relation whose endpoint node types differ from `from_type` or `to_type`.
- `properties` are copied as returned: names the schema does not define are kept and values are not type-checked; `merge_key_payload` is rebuilt by `derive_merge_key_payload`.
- Any exception aborts the execution: no candidate is created, the execution is saved `FAILED` with `error_message`, run and source unit become `FAILED`, and the exception is re-raised without retry.
- On success each suggestion becomes a `CandidateNode` or `CandidateRelation` with status `PENDING`.

Sources: infrastructure/llm/openai_provider.py:123-174; application/use_cases/extraction_management.py:51-86; application/use_cases/extraction_management.py:316-370; application/use_cases/extraction_management.py:372-418; application/use_cases/extraction_management.py:522-569; application/use_cases/extraction_management.py:171-231; application/use_cases/extraction_management.py:579-626

## 4. Validation rules and how a candidate gets its status

- `validate_run` (also called by `resolve_duplicates`) rejects `COMPLETED` runs, re-evaluates every candidate, then replaces all `ValidationResult` rows and all review items of the run, decided ones included.
- A `ValidationResult` has `candidate_ref`, `rule_code`, `severity` (`error`, `warning`, `info`), `result` (`failed`, `review`, `passed`) and `message`.
- Node errors set `REJECTED`: `node_type_exists` (lookup by casefolded name, aliases not consulted), `required_node_property`, `node_merge_key`.
- Otherwise confidence strictly below the type's `confidence_threshold` gives `REVIEW` with `node_confidence_threshold`; else `VALIDATED` with `candidate_node_valid`.
- Relation errors set `REJECTED`: `relation_type_exists`, `relation_candidate_refs`, `relation_from_type`, `relation_to_type`, `required_relation_property` (union of `required_properties` and properties flagged `required`), `relation_dependency_rejected`.
- A relation becomes `REVIEW` when an endpoint node is in `REVIEW` (`relation_dependency_review`) or its confidence is below the type threshold (`relation_confidence_threshold`); else `VALIDATED` with `candidate_relation_valid`.
- `CandidateStatus` also defines `COMMITTED`, but no code assigns it.

Sources: application/use_cases/pipeline_management.py:148-221; application/use_cases/pipeline_management.py:234-300; application/use_cases/pipeline_management.py:302-330; application/use_cases/pipeline_management.py:332-403; application/use_cases/pipeline_management.py:405-445; application/use_cases/pipeline_management.py:447-494; domain/shared/enums.py:51-56; domain/validation/entities.py:4-12

## 5. Evidence and grounding checks

- An `EvidenceRef` holds `segment_id` plus optional `quote`, `start_offset`, `end_offset`.
- In extraction `_build_evidence_ref` requires each `segment_id` to belong to the run's source unit; otherwise `RuleViolationError` fails the whole extraction.
- For candidates added through the API, `_ensure_evidence_refs_belong_to_source_unit` applies the same rule.
- There is no check that `quote` occurs in the segment text or that offsets fit it; offsets only have to be non-negative.
- There is no rule requiring evidence: `evidence_refs` defaults to empty and `_validate_candidate_node` reaches `VALIDATED` without reading it.
- On commit each node evidence ref becomes `(n)-[:SUPPORTED_BY {run_id, candidate_ref, segment_id}]->(sg:Segment)`; refs to segments outside the bundle are skipped, and `quote` and offsets are not written to Neo4j.
- Relation evidence goes to a `RelationEvidence` node keyed by `candidate_relation_id`, linked by `FROM_NODE`, `TO_NODE`, `DERIVED_FROM` and `SUPPORTED_BY`.
- The review queue's `_build_evidence_snippets` returns the segment's order and text with the stored `quote`.

Sources: domain/extraction/entities.py:7-12; application/use_cases/extraction_management.py:420-435; application/use_cases/pipeline_management.py:534-557; application/use_cases/extraction_management.py:51-57; application/use_cases/pipeline_management.py:302-330; infrastructure/persistence/neo4j/repositories.py:336-412; infrastructure/persistence/neo4j/repositories.py:461-532; infrastructure/persistence/review_queue_builders.py:132-155

## 6. Duplicate detection and identity keys for nodes and relations

- `derive_merge_key_payload` keeps only the node type's `merge_keys`: each is read from `properties`, else from the supplied payload.
- `normalize_text` applies NFKC, strip, whitespace collapse and casefold; `normalized_payload_key` serialises the normalised payload as key-sorted compact JSON.
- The candidate node key (`build_candidate_node_resolution_key`) is `<normalised node_type>::<normalised merge_key_payload>`; matching is exact string equality, with no fuzzy or similarity comparison.
- `_flag_duplicate_candidate_nodes` groups non-rejected nodes with a non-empty payload by that key; the highest-confidence member (ties by `candidate_node_id`) keeps its status, the others become `REVIEW` with `potential_duplicate_node`.
- The candidate relation key joins the normalised `relation_type`, both endpoint identity keys (`candidate_node_identity_key`, or `candidate::<id>`) and the normalised `properties`; duplicates become `REVIEW` with `potential_duplicate_relation`.
- Canonical identity is `build_canonical_merge_key`: SHA-256 hex of the normalised merge-key payload, or of `{"candidate_node_id": …}` when the payload is empty, so a node without merge keys never merges with another.
- `_annotate_canonical_matches` looks up existing canonical nodes and relations and adds info results `canonical_node_match` or `canonical_relation_match`; statuses are unchanged.
- In review, `_ensure_candidate_node_unique_within_run` and `_ensure_candidate_relation_unique_within_run` raise `RuleViolationError` when a decision would leave two non-rejected candidates with the same key.

Sources: domain/shared/resolution.py:10-62; domain/shared/resolution.py:65-111; application/use_cases/pipeline_management.py:559-623; application/use_cases/pipeline_management.py:671-712; application/use_cases/pipeline_management.py:781-824; application/use_cases/pipeline_management.py:826-868; application/use_cases/review_management.py:265-314; infrastructure/persistence/neo4j/repositories.py:1102-1106

## 7. Human review: what is recorded, what a reviewer can do

- `_build_review_items` creates one `ReviewItem` per candidate in `REVIEW`: `item_type` (`candidate_node` or `candidate_relation`), `item_ref`, `reason_code` (first rule code with result `review`, else `candidate_review`) and `payload_json` (type, confidence, messages).
- A `ReviewItem` also holds `status` (`open`, `accepted`, `rejected`, `edited`), `reviewer_note` and `created_at`; it has no reviewer identity and no decision timestamp.
- `decide_review_item` accepts `accept`, `reject` or `edit`; a non-open item raises `ConflictError`, any other action `RuleViolationError`.
- `reject` sets the candidate `REJECTED`; `accept` and `edit` set it `VALIDATED`. `edit` can change a node's `node_type`, `properties`, `merge_key_payload`, `confidence`, or a relation's `relation_type`, endpoints, `properties`, `confidence`.
- For a non-rejected node, `_validate_candidate_node_state` requires a defined type, required properties and merge keys, and `_ensure_node_relations_remain_compatible` blocks a type change that breaks a non-rejected relation; the confidence threshold is not re-checked.
- A non-rejected relation requires a defined type, both endpoint nodes `VALIDATED` in the same run, matching endpoint types and required properties.
- After every decision `_refresh_relation_reviews_for_run` re-evaluates all relations of the run: open relation items are updated, created, or closed with the note "Auto-resolved after dependent review decision." or "Auto-closed after dependent review decision."
- That re-evaluation applies `relation_confidence_threshold` again, so a relation accepted while still below the threshold returns to `REVIEW` with a new open item.

Sources: domain/review/entities.py:9-19; application/use_cases/pipeline_management.py:714-779; application/use_cases/review_management.py:49-86; application/use_cases/review_management.py:88-128; application/use_cases/review_management.py:142-207; application/use_cases/review_management.py:209-263; application/use_cases/review_management.py:316-335; application/use_cases/review_management.py:421-488

## 8. Commit to the graph: transactions, MERGE keys, what is written to Neo4j and Postgres

- `commit_run` raises `ConflictError` if the run already has a graph delta, and `RuleViolationError` if any candidate is `PENDING`, any review item is `OPEN`, or a validated relation points to a non-validated node.
- Only `VALIDATED` candidates enter the `CanonicalCommitBundle`; rejected ones are counted in `GraphDelta.rejected_count`, and `review_count` is always 0.
- With `repository_backend == "postgres"` metadata uses Postgres repositories and the graph `Neo4jCanonicalGraphRepository`; any other value uses in-memory repositories for everything.
- `commit_bundle` issues a separate `session.execute_write` for the source context, each node merge, each node provenance link, each relation merge, each relation provenance link and the delta; the commit is not one transaction and nothing undoes completed writes when a later one fails.
- Source context: `MERGE (su:SourceUnit {source_unit_id})` and `MERGE (sg:Segment {segment_id})` with `(su)-[:HAS_SEGMENT]->(sg)`.
- Nodes: `MERGE (n:CanonicalNode:<node_type> {project_id, node_type, merge_key})`, then `SET n += $properties`, `source_unit_id`, `last_run_id`, `updated_at`. `None` values are dropped, nested lists and dicts are JSON-encoded, and a type name outside `^[A-Za-z_][A-Za-z0-9_]*$` raises `ValueError`.
- Relations: `MERGE (from)-[r:<relation_type> {project_id, relation_type}]->(to)`, then `SET r += $properties`; properties are not part of relationship identity.
- Afterwards `graph_delta_repository.add` stores the delta and the run becomes `COMPLETED` (source unit `PROCESSED`); on an exception both are saved `FAILED` and the error is re-raised. These are separate repository calls outside the Neo4j transactions.

Sources: application/use_cases/commit_management.py:36-93; application/use_cases/commit_management.py:95-134; bootstrap/container.py:149-208; infrastructure/persistence/neo4j/repositories.py:38-113; infrastructure/persistence/neo4j/repositories.py:246-300; infrastructure/persistence/neo4j/repositories.py:302-334; infrastructure/persistence/neo4j/repositories.py:414-459; infrastructure/persistence/neo4j/repositories.py:1102-1130

## 9. Schema model: node types, relation types, properties, templates

- A `SchemaVersion` belongs to a project, has a unique `version_no` (duplicate raises `ConflictError`) and starts `DRAFT`; creating it also creates pipeline definition `v1` from `build_default_pipeline_steps`.
- Types can only be added to a `DRAFT` version ("Only draft schema versions can be edited."); the service has no update or delete operation for types.
- `activate_schema_version` sets the target `ACTIVE` from any status and turns any other `ACTIVE` version of the project into `PUBLISHED`; no code assigns `RETIRED`.
- `NodeTypeDefinition`: `name` (unique per version, case-insensitive), `display_name`, `description`, `is_core`, `merge_keys`, `confidence_threshold` (default 0.5), `aliases`, `extraction_hints`, `properties`, `is_active`.
- `RelationTypeDefinition`: `name`, `from_type` and `to_type` (both must already exist in the version, else `RuleViolationError`), `description`, `directional`, `aliases`, `extraction_hints`, `required_properties`, `properties`, `confidence_threshold` (default 0.7), `is_active`.
- `PropertyDefinition`: `owner_kind` (`node` or `relation`), `owner_type_name`, `name`, `data_type`, `required`, `description`, `default_value`, `enum_values`.
- Validation enforces only `required` and merge keys; `data_type`, `enum_values` and `default_value` reach the model but are never checked or applied, and `is_core`, `directional`, `is_active` do not affect extraction, validation or commit.
- Templates are the two `SYSTEM_DOMAIN_TEMPLATES` (`blank`, `story`) with id, name, slug and description; `create_project` stores the resolved `template_id` (default `blank`; unknown raises `RuleViolationError`) and creates no schema content from it.

Sources: domain/schema/entities.py:7-61; application/use_cases/schema_management.py:45-74; application/use_cases/schema_management.py:94-155; application/use_cases/schema_management.py:157-208; application/use_cases/schema_management.py:210-247; infrastructure/template/catalog.py:6-25; application/use_cases/project_management.py:17-48; application/use_cases/pipeline_management.py:262-272

## 10. Runs, jobs and the public API surface

- `start_processing_run` creates a `ProcessingRun` with status `PENDING` and sets the source unit to `PROCESSING`; it rejects a `DRAFT` or already `PROCESSING` source unit, a schema version different from the source unit's, and a `pipeline_version` without a pipeline definition.
- Run status changes through `mark_run_started` (`RUNNING`), `mark_run_failed` (`FAILED`, source unit `FAILED`) and `mark_run_completed` (`COMPLETED`, source unit `PROCESSED`).
- `enqueue_job` creates a `ProcessingJob` (`pending`) of type `extract_candidates`, `validate_run` or `commit_run`; it rejects completed runs and raises `ConflictError` when the run already has a pending or running job of that type.
- Postgres `claim_next` takes the oldest `PENDING` job whose run has no `RUNNING` job, guarded by `pg_try_advisory_xact_lock(hashtext(run_id))` and `FOR UPDATE SKIP LOCKED`, and marks it running.
- `process_next_job` executes the job, then enqueues the `chain_on_success` types from its payload (request value, else the pipeline definition step), skipping a type that is already active or has succeeded.
- Any exception marks the job `FAILED` with `error_message`; only pending jobs are claimed, so failed ones are not retried. Chaining ignores review items, so a chained `commit_run` fails while any are open.
- `processing_jobs_worker.main` loops over `process_next_job`, sleeping the poll interval when idle; flags: `--once`, `--job-type`, `--run-id`, `--poll-interval-seconds`, `--max-jobs`.
- HTTP job routes: `POST` and `GET /api/runs/{run_id}/processing-jobs`, `GET /api/projects/{project_id}/processing-jobs`, `POST /api/processing-jobs/process-next`. Errors map to 404 (`NotFoundError`), 409 (`ConflictError`), 422 (`RuleViolationError`), 502 (`ExternalServiceError`).

Sources: application/use_cases/ingestion_management.py:46-80; domain/ingestion/lifecycle.py:7-34; application/use_cases/processing_job_management.py:43-97; application/use_cases/processing_job_management.py:223-302; infrastructure/persistence/postgres/repositories.py:691-734; interfaces/cli/processing_jobs_worker.py:16-63; interfaces/api/routers/processing_jobs.py:42-112; interfaces/api/error_handlers.py:14-30
