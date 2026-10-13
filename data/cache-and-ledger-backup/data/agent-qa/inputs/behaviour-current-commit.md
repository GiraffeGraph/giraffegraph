# Backend behaviour

## 1. Source ingestion and segmentation

- `create_source_unit` requires an existing project and a non-`draft` schema version of it (`_require_usable_schema`); `_persist_source_unit` stores status `ready` and turns a blank `external_ref` into `None`.
- `bulk_create_source_units` defaults to the project's active schema and marks an item `duplicate` when its `external_ref` exists in the project or earlier in the request; single create has no duplicate check.
- `generate_segments` resolves the strategy by casefolded name (`paragraphs`, `isnad`; unknown: `RuleViolationError`), numbers segments from 1, stamps `metadata_json["strategy"]` and replaces the unit's existing segments.
- `ParagraphSegmentation.split` cuts on blank lines, falls back to non-empty lines, then to the whole stripped text.
- `IsnadSegmentation.split` emits one segment per chain from `segment_isnad` (metadata `chain_no`, `start_offset`, `end_offset`), skips chains starting at or after the matn boundary, and falls back to the whole text (`fallback: whole_text`).
- `_ensure_segments` reuses segments already cut with the requested strategy; the strategy comes from the request, else the project template, else `paragraphs`.

Sources: application/use_cases/ingestion_management.py:96-167; application/use_cases/ingestion_management.py:225-258; application/use_cases/ingestion_management.py:368-393; application/use_cases/pipeline_management.py:82-103; domain/extraction/segmentation.py:22-37; domain/hadith/segmentation.py:7-33

## 2. Extraction: providers, prompts, what is sent to the model

- The container always registers `NoOpLLMProvider` (`noop`) and `RuleBasedIsnadProvider` (`rule_based_isnad`); `OpenAILLMProvider` and `AnthropicLLMProvider` only with a non-blank API key. `CachedLLMProvider` is not registered.
- Provider and model come from the run, else `default_llm_provider` / `default_llm_model`; an unregistered provider or prompt version raises `RuleViolationError`.
- The prompt is `candidate_graph_extraction` (default version `candidate_graph_extraction_v2`): v1 demands exact case-sensitive type names, v2 accepts names or aliases case-insensitively.
- `_build_prompt_payload` sends run ids, source-unit metadata (`title`, `external_ref`, …), the whole schema (merge keys, thresholds, aliases, `extraction_hints`, property definitions) and each segment's `segment_id`, `segment_order`, `text`; `raw_content` is not sent.
- `_plan_calls` issues one call per segment when the segmentation strategy sets `one_call_per_segment` (`isnad`), else chunks of `max_segments_per_call`, else one call.
- OpenAI receives `/chat/completions` with `temperature` 0 and `response_format` `json_object`; Anthropic receives `messages.create` with JSON schema `EXTRACTION_WIRE_SCHEMA`, properties as name/value lists and no `merge_key_payload`.
- `RuleBasedIsnadProvider` ignores the prompt: it runs `segment_isnad` and returns `Narrator` nodes and `NARRATED_FROM` relations at confidence 0.95.

Sources: bootstrap/container.py:141-161; application/use_cases/extraction_management.py:120-136; application/use_cases/extraction_management.py:322-401; application/use_cases/extraction_management.py:775-812; infrastructure/llm/prompt_catalog.py:6-63; infrastructure/llm/openai_provider.py:74-122; infrastructure/llm/anthropic_provider.py:92-168; infrastructure/llm/rule_based_isnad_provider.py:9-64

## 3. What happens to the model's output (parsing, undefined types and properties, failures)

- `_normalize_output` validates against `StructuredExtractionContract` (extra fields ignored, `confidence` 0–1); a `ValidationError` becomes `RuleViolationError`.
- A node or relation whose type is unknown by casefolded name or alias is dropped and recorded as a `SchemaProposal` (`schema_type_proposal`); relations with a dropped endpoint are dropped too.
- `_keep_declared_properties` strips properties not declared on the type and records `schema_property_proposal` with a sample value; the candidate is kept.
- A call fails (`RuleViolationError`) on a duplicate node `ref`, a relation with an unknown `ref`, or endpoint types differing from the relation type's `from_type`/`to_type`.
- A `RuleViolationError` or `ExternalServiceError` (Anthropic kinds `refusal`, `max_tokens`, `invalid_output`, …) fails only that call (`FailedExtractionCall`); the execution still ends `succeeded` with `error_message` set, unless every call failed.
- Any exception leaving `extract_candidates` marks the `ExtractionExecution` `failed` and, once started, the run and source unit `failed`.
- Non-dry runs persist candidates and upsert one `schema_proposal` review item per proposal (a closed one is not reopened); `dry_run` persists only the execution row; existing candidates raise `ConflictError`.

Sources: application/use_cases/extraction_management.py:72-107; application/use_cases/extraction_management.py:143-222; application/use_cases/extraction_management.py:228-306; application/use_cases/extraction_management.py:403-442; application/use_cases/extraction_management.py:485-564; application/use_cases/extraction_management.py:609-660; application/use_cases/extraction_management.py:672-744; infrastructure/llm/anthropic_provider.py:198-243

## 4. Validation rules and how a candidate gets its status

- `validate_run` refuses `completed` runs and validates nodes, then relations, then applies duplicate resolution.
- The latest human `ReviewDecision` outranks the rules: `reject` gives `rejected`, anything else `validated`, recorded as `human_review_decision`.
- Nodes are `rejected` for `node_type_exists`, `required_node_property`, `node_merge_key`; `derive_merge_key_payload` re-derives the payload, property values overriding supplied ones.
- Nodes go to `review` on evidence, grounding or enum findings or `node_confidence_threshold` (below the type's `confidence_threshold`); otherwise `validated` (`candidate_node_valid`).
- Relations are `rejected` for `relation_type_exists`, `relation_candidate_refs`, `relation_from_type`, `relation_to_type`, `required_relation_property`, `relation_dependency_rejected` (rejected endpoint).
- Relations go to `review` for evidence or enum findings, `missing_relation_merge_key`, `relation_dependency_review`, `relation_confidence_threshold`; otherwise `validated` (`candidate_relation_valid`).
- `_enum_findings` raises `property_value_not_allowed` only for string values with `enum_values`; no rule checks values against `data_type`.

Sources: application/use_cases/pipeline_management.py:172-251; application/use_cases/pipeline_management.py:302-331; application/use_cases/pipeline_management.py:332-409; application/use_cases/pipeline_management.py:411-453; application/use_cases/pipeline_management.py:455-525; application/use_cases/pipeline_management.py:527-602; application/use_cases/pipeline_management.py:1105-1150

## 5. Evidence and grounding checks

- `EvidenceRef` holds `segment_id`, `quote`, `start_offset`, `end_offset`; extraction fails the call when a `segment_id` was not sent in it, and the candidate API rejects segments of another source unit.
- Grounding applies only when the run has a `succeeded` non-dry-run extraction execution (`_grounding_segments`); other runs get no evidence findings.
- `_evidence_findings`: `missing_evidence` without evidence refs; `quote_not_in_segment` per ref whose quote is empty, whose segment is unknown, or whose quote is not a substring of the segment text.
- `_merge_key_grounding_findings` (nodes only): `value_not_in_quote` for each string merge-key value absent from every quote, unless it equals the cited source unit's `external_ref`; other properties are unchecked.
- Matching uses `normalize_for_grounding`: `normalize_text` (NFKC, whitespace collapse, casefold) then `normalize_arabic` (diacritics removed, punctuation to spaces, alef/hamza forms, ى and ة folded).
- There is no check of `start_offset`/`end_offset`: `_evidence_findings` reads only `segment_id` and `quote`.

Sources: domain/extraction/entities.py:11-16; application/use_cases/extraction_management.py:758-773; application/use_cases/pipeline_management.py:642-657; application/use_cases/pipeline_management.py:1024-1103; domain/hadith/grounding.py:1-27; domain/hadith/normalization.py:6-65; domain/shared/resolution.py:125-140

## 6. Duplicate detection and identity keys for nodes and relations

- Node identity is `build_candidate_node_resolution_key`: normalised type + `::` + JSON of the normalised `merge_key_payload` (NFKC, whitespace collapse, casefold; exact match, no Arabic folding).
- `_absorb_call` folds a node into an earlier call's node with the same identity (all merge keys present): evidence appended, confidence maximised, relations re-pointed; nodes within one call are not merged.
- `_flag_duplicate_candidate_nodes` groups non-rejected nodes with a merge payload; the primary is human-decided, then highest confidence, then lowest id; other undecided members become `review` (`potential_duplicate_node`).
- Relation identity is `build_candidate_relation_resolution_key`: type, both endpoint keys and `build_relation_identity_key` (SHA-256 of the type's merge-key properties, constant when none are declared).
- `_flag_duplicate_candidate_relations` skips rejected relations and those missing a merge-key value; non-primary members become `review` (`potential_duplicate_relation`).
- The canonical node key is `build_canonical_merge_key` (SHA-256 of the normalised payload, or of the candidate id when empty); `_annotate_canonical_matches` adds only `info` results `canonical_node_match` / `canonical_relation_match`.

Sources: domain/shared/resolution.py:30-34; domain/shared/resolution.py:47-101; domain/shared/resolution.py:104-130; application/use_cases/extraction_management.py:456-467; application/use_cases/extraction_management.py:568-607; application/use_cases/pipeline_management.py:700-746; application/use_cases/pipeline_management.py:798-854; application/use_cases/pipeline_management.py:941-1020

## 7. Human review: what is recorded, what a reviewer can do

- Validation rebuilds review items: `schema_proposal` and human-decided items are kept; each candidate in `review` gets one `open` item whose `reason_code` is its first review rule (fallback `candidate_review`).
- `decide_review_item` takes `accept`, `reject` or `edit`, requires `reviewer_id`, and raises `ConflictError` once the run is `completed`.
- Each decision is appended as a `ReviewDecision` (`reviewer_id`, `reviewer_note`, `duration_ms`; `before_json`/`after_json` only for `edit`); the item becomes `accepted`, `rejected` or `edited`.
- Node `edit` may replace `node_type`, `properties`, `merge_key_payload`, `confidence`; accept and edit re-check type, required properties, merge keys, relation compatibility and uniqueness, else `RuleViolationError` and nothing is saved.
- Relation `edit` may change type, endpoints, `properties`, `confidence`; accept and edit require both endpoint nodes `validated`, matching types, required properties and all merge keys.
- A `schema_proposal` item can only be accepted or rejected; `decide_review_item` records the decision and does not change the schema.
- `_refresh_relation_reviews_for_run` then rejects undecided relations with a rejected endpoint and auto-accepts an open `relation_dependency_review` item once both endpoints are `validated`, unless `_pending_relation_review` finds another reason.
- `list_acceptance_records` returns, per `validated` candidate, its latest accepting decision or policy `auto_validated`.

Sources: application/use_cases/pipeline_management.py:262-289; application/use_cases/pipeline_management.py:856-921; application/use_cases/review_management.py:59-138; application/use_cases/review_management.py:142-196; application/use_cases/review_management.py:215-255; application/use_cases/review_management.py:269-334; application/use_cases/review_management.py:336-405; application/use_cases/review_management.py:484-563

## 8. Commit to the graph: transactions, MERGE keys, what is written to Neo4j and Postgres

- `commit_run` raises `ConflictError` if the run already has a graph delta, and `RuleViolationError` for a `pending` candidate, an `open` review item (schema proposals included) or a validated relation with a non-validated endpoint.
- Only `validated` candidates are written; `rejected_count` counts rejected ones, `review_count` is always 0, and `CandidateStatus.COMMITTED` is never assigned.
- `_build_relation_identity_keys` refuses a missing merge-key value and two validated relations sharing an identity with different properties.
- `Neo4jCanonicalGraphRepository.commit_bundle` writes the run in one `session.execute_write` transaction; lookup indexes are ensured beforehand.
- Nodes: `MERGE (n:CanonicalNode:<type> {project_id, node_type, merge_key})` then `SET n += properties`, `source_unit_id`, `last_run_id`, `updated_at` (`created_at` only on create), so a later commit overwrites same-named properties; relations: `MERGE (from)-[r:<type> {project_id, relation_type, relation_identity_key}]->(to)`.
- Provenance: `SourceUnit` (no `raw_content`) `HAS_SEGMENT` `Segment`; node edges `DERIVED_FROM` and `SUPPORTED_BY` carrying `run_id`, `candidate_ref`; `RelationEvidence {candidate_relation_id}` with `FROM_NODE`, `TO_NODE`, `DERIVED_FROM`, `SUPPORTED_BY`; `GraphDelta` with counters. Quotes are not written.
- Postgres follows the Neo4j transaction: a `graph_deltas` row (unique per run), run `completed`, unit `processed`; a Neo4j error marks both `failed`.

Sources: application/use_cases/commit_management.py:45-123; application/use_cases/commit_management.py:125-204; infrastructure/persistence/neo4j/repositories.py:27-55; infrastructure/persistence/neo4j/repositories.py:284-332; infrastructure/persistence/neo4j/repositories.py:334-413; infrastructure/persistence/neo4j/repositories.py:457-494; infrastructure/persistence/neo4j/repositories.py:507-586; infrastructure/persistence/postgres/models.py:571-583

## 9. Schema model: node types, relation types, properties, templates

- `create_schema_version` requires a unique `version_no` (`ConflictError`), starts `draft`, and adds pipeline definition `v1` chaining `extract_candidates` → `validate_run` → `commit_run`.
- Types can be added only to `draft` versions; `activate_schema_version` sets the target `active` and demotes the previous one to `published`. Nothing assigns `retired`.
- Node types: `name`, `display_name`, `merge_keys`, `confidence_threshold` (0.5), `aliases`, `extraction_hints`, properties; names are unique case-insensitively; node `merge_keys` are not checked against declared properties.
- Relation types: `from_type`/`to_type` (must exist in the version), `required_properties`, `merge_keys` (must be declared properties), `confidence_threshold` (0.7), `directional`.
- Properties: `name`, `data_type`, `required`, `default_value`, `enum_values`; type and property names must match `IDENTIFIER_PATTERN`.
- Templates are `blank`, `story`, `isnad`; `isnad` defines `Narrator` (key `name`), `Hadith` (key `hadith_ref`), `NARRATED_FROM` (keys `hadith_ref`, `chain_no`, `position`), `TRANSMITS`, strategy `isnad`.
- `ProjectSetupService.create_project` with `apply_template_schema` creates the next version from the template and activates it; a template without a schema adds none.

Sources: application/use_cases/schema_management.py:53-120; application/use_cases/schema_management.py:140-201; application/use_cases/schema_management.py:205-284; application/dto/contracts.py:28-73; domain/orchestration/pipeline_definitions.py:6-41; infrastructure/template/catalog.py:13-42; infrastructure/template/catalog.py:44-123; application/use_cases/project_management.py:47-86

## 10. Runs, jobs and the public API surface

- `start_processing_run` rejects a `draft` or `processing` unit, a schema version differing from the unit's, and a `pipeline_version` without definition; the run starts `pending`, the unit becomes `processing`.
- Runs move `pending` → `running` → `completed` (unit `processed`) or `failed` (unit `failed`).
- `process_source_units` runs start, segmentation, extraction and validation per unit synchronously and commits only if `commit` is set and nothing is open; unit `status`: `failed`, `needs_review`, `validated`, `committed`.
- `enqueue_job` refuses completed runs and a second active job of the same type (`ConflictError`); `chain_on_success` comes from the request or the pipeline definition.
- `process_next_job` executes a claimed job, then enqueues its chained jobs unconditionally (skipped only when one is active or succeeded) and marks it `succeeded`; any exception, such as `commit_run` on a run with open review items, marks it `failed`, and failed jobs are not retried.
- Postgres `claim_next` takes the oldest `pending` job whose run has no `running` job, using `pg_try_advisory_xact_lock` and `FOR UPDATE SKIP LOCKED`.
- `api_router` mounts chains, commit, extraction, exploration, health, ingestion, pipeline-definition, pipeline, processing-job, project, review, schema and template routers; errors map to 404 (`NotFoundError`), 409 (`ConflictError`), 422 (`RuleViolationError`), 502 (`ExternalServiceError`).
- There is no authentication: `api_router` only aggregates these routers, and `reviewer_id` is whatever the caller sends.

Sources: application/use_cases/ingestion_management.py:179-213; domain/ingestion/lifecycle.py:7-34; application/use_cases/ingestion_management.py:290-366; application/use_cases/processing_job_management.py:43-97; application/use_cases/processing_job_management.py:230-309; infrastructure/persistence/postgres/repositories.py:734-777; interfaces/api/routers/__init__.py:19-32; interfaces/api/error_handlers.py:14-30
