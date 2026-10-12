# 5 System design

This chapter describes the design as implemented on the `feat/hadith-prototype` branch. Paths are relative to `backend/src/app/`. Several decisions answer defects found in a review of the earlier code (design analysis, 30 September 2026); we name the defect where it explains the design.

## 5.1 Design principles

**The model proposes and cannot write to the graph.** A provider returns suggested nodes and relations, stored as `CandidateNode` and `CandidateRelation` rows with status `pending`. The only graph write, `CanonicalGraphRepository.commit_bundle`, is called only from `CommitManagementService.commit_run` and receives only `validated` candidates.

**Every fact carries a quotation.** A candidate holds `EvidenceRef` values: a segment id, a quotation and optional offsets. An extracted candidate without evidence is flagged `missing_evidence`. This is a check, not a storage constraint: a reviewer can still accept such a candidate, and candidates entered by hand are not checked.

**Checks flag for review instead of silently rejecting.** A failed grounding, value, threshold or duplicate check sets status `review` and creates a review item with a reason code. Structural errors that leave a candidate unusable set `rejected`, but each is stored as a validation result.

**Every acceptance is recorded as a human decision or a named policy.** A validated candidate is traced to a row in `review_decisions` or to the policy `auto_validated` with the rule that passed it.

**Domain behaviour is plugged in; engine code stays generic.** Segmentation is a `SegmentationStrategy`, a schema comes from a template, and extraction goes through an `LLMProvider`. The use cases for extraction, validation, review and commit contain no narrator or hadith names. There are three exceptions. Validation imports its text comparison from `domain/hadith/grounding.py`, so the Arabic folding applies to every project. The chain read model (`domain/exploration/chains.py`, `ChainExplorationService`, the `/chains` endpoints) names the `Narrator` and `NARRATED_FROM` types. The plug-ins are registered in code in `bootstrap/container.py`.

## 5.2 Architecture

The backend is one FastAPI application in four layers. The application and domain layers import nothing from the infrastructure or interface layers: use cases depend on the protocols in `application/ports/`, and the infrastructure layer implements them.

```text
  Dashboard (Next.js)             Worker CLI
        | HTTP                        |
        v                             v
+----------------------------------------------------------------------+
| interfaces     FastAPI routers and schemas                           |
+----------------------------------------------------------------------+
| application    use cases: schema, ingestion, extraction, validation, |
|                review, commit, jobs, exploration; ports (protocols)  |
+----------------------------------------------------------------------+
| domain         entities, segmentation strategies, identity keys,     |
|                Arabic normalisation and grounding helpers            |
+----------------------------------------------------------------------+
| infrastructure                                                       |
|   LLM providers        template catalog       persistence            |
|   noop, openai,        blank, story,          in-memory, or          |
|   anthropic,           isnad                  Postgres + Neo4j       |
|   rule_based_isnad                                                   |
+----------------------------------------------------------------------+
        |                                       |
        v                                       v
  Postgres: schemas, source text, runs,    Neo4j: committed nodes and
  candidates, validation results,          edges, links to source units
  review items, decisions, deltas          and segments, graph deltas
```

Postgres holds configuration, source text, everything not yet accepted, and the audit trail. Neo4j holds only what has been committed, with links back to source units and segments. The repository's ADR-002 gives the reason: metadata is structured records, while the committed graph is highly connected and read by traversal. With this split, a candidate never exists in the graph store. The cost is that the two stores are not updated in one transaction (Section 6.9).

An in-memory backend implements the same repository protocols with dictionaries. It is the default when `REPOSITORY_BACKEND` is not `postgres`, and the test suite uses it.

## 5.3 Data model

| Entity | Main fields | Stored in |
|---|---|---|
| Project | name, `template_id`, status | `projects` |
| Schema version | `version_no`, status (`draft`, `published`, `active`, `retired`) | `schema_versions` |
| Node type | name, `display_name`, `merge_keys`, `confidence_threshold` (default 0.5), `extraction_hints` | `node_types` |
| Relation type | name, `from_type`, `to_type`, `merge_keys`, `confidence_threshold` (default 0.7) | `relation_types` |
| Property | name, `data_type`, required, `enum_values` | `property_definitions` |
| Source unit | `raw_content`, `external_ref`, status | `source_units` |
| Segment | order, text, metadata (strategy, chain number, source offsets) | `segments` |
| Run | source unit, schema version, provider, model, status | `processing_runs` |
| Candidate node, candidate relation | type, properties, confidence, evidence refs, status; a node has a `merge_key_payload`, a relation two candidate node refs | `candidate_nodes`, `candidate_relations` |
| Validation result | `candidate_ref`, `rule_code`, severity, result, message | `validation_results` |
| Review item | `item_type`, `item_ref`, `reason_code`, payload, status | `review_items` |
| Review decision | see Section 5.7 | `review_decisions` |
| Graph delta | counts of created, merged and rejected items of one run | `graph_deltas`, `GraphDelta` node |
| Canonical node | labels `CanonicalNode` and the type name; key `project_id`, `node_type`, `merge_key` | Neo4j |
| Canonical edge | relationship named after the relation type; key `project_id`, `relation_type`, `relation_identity_key` | Neo4j |

Evidence refs are stored as JSON in the candidate rows. Only a draft schema version can be edited, so the types of a run do not change.

## 5.4 The pipeline, step by step

We follow one hadith with the reference `Muslim:978`, whose text contains the chain-switch marker ح. The segmenter returns two chains for it. The reference labels give three: the third starts after the report text has begun, and the segmenter does not return it.

1. **Ingest.** The text becomes a source unit with `external_ref = "Muslim:978"`, bound to the project's active schema version.
2. **Start a run.** A `ProcessingRun` records the schema version, provider and model. The source unit is marked `processing`, and no second run can start in that state.
3. **Segment.** The `isnad` strategy returns one segment per chain it finds; it starts a new chain only at the marker ح, so most hadiths give one segment. Each segment text is the exact substring `raw_content[start:end]`, and the offsets are stored in the segment metadata. If no chain is found, the whole text becomes one segment marked `fallback: whole_text`.
4. **Extract.** With the `isnad` strategy the engine makes one provider call per segment; with `paragraphs` it sends the segments of a source unit in one call. The payload holds the source unit reference, the schema with its hints, and the segment. The answer is parsed with `StructuredExtractionContract`. A node or relation with an unknown type is dropped and recorded as a schema proposal; an undeclared property is removed the same way. An answer that cites a segment outside the call, uses an unknown node ref, or connects nodes of the wrong types fails that call. Nodes from different calls with the same type and merge-key value become one candidate that keeps all quotations. The run fails only if every call fails.
5. **Validate.** `validate_run` applies the checks of Section 5.5, sets each candidate to `validated`, `review` or `rejected`, and builds the review items.
6. **Review.** A reviewer decides the open items (Section 5.7). After each decision, relations that waited on a node are refreshed.
7. **Commit.** `commit_run` refuses a run that already has a graph delta, a pending candidate, an open review item, a validated relation whose endpoint is not validated, a validated relation without a merge-key value, or two validated relations that would become one edge with different properties. Otherwise the validated candidates are written in one graph transaction, the delta is stored, and the run becomes `completed`.
8. **Read.** The chain endpoints return the hadith with its chains in order, each link with its quotation and acceptance record.

Steps 2 to 5, and step 7 for runs without open items, can run in one request (`POST /api/projects/{project_id}/source-units/process`). Steps 4, 5 and 7 can also run as queued jobs.

## 5.5 Validation checks

| Reason code | Trigger | Effect | Rationale |
|---|---|---|---|
| `node_type_exists`, `relation_type_exists` | Type is not in the schema version | Rejected | Graph labels come only from the schema; reached only by manual entries |
| `required_node_property`, `required_relation_property`, `node_merge_key` | A required property or a node merge-key value is missing | Rejected | Incomplete by the schema; a node without identity cannot be merged |
| `relation_candidate_refs`, `relation_from_type`, `relation_to_type` | An endpoint is not in the run, or its node type differs from the relation type | Rejected | Schema conformance |
| `relation_dependency_rejected` | An endpoint node is rejected | Rejected | An edge needs both nodes |
| `missing_evidence` | Extracted candidate has no evidence ref | Review | A fact without a quotation cannot be checked |
| `quote_not_in_segment` | Quotation is empty or not found in the cited segment | Review | The quotation may be invented |
| `value_not_in_quote` | A string merge-key value of a node occurs in none of its quotations and differs from the source unit's `external_ref` | Review | The name may be altered or invented |
| `property_value_not_allowed` | A string value is outside the property's `enum_values` | Review | Value drift |
| `node_confidence_threshold`, `relation_confidence_threshold` | Confidence is below the type's threshold | Review | The model reports doubt |
| `missing_relation_merge_key` | A relation lacks a value for a declared merge key | Review | A reviewer can supply it |
| `relation_dependency_review` | An endpoint node is in review | Review | The edge waits for its node |
| `potential_duplicate_node`, `potential_duplicate_relation` | Another candidate of the run has the same identity | Review for all but one | They would become one graph element |
| `schema_type_proposal`, `schema_property_proposal` | Extraction met an unknown type or an undeclared property | Candidate dropped or property removed; review item of type `schema_proposal` | Drift is recorded, the call survives |
| `candidate_node_valid`, `candidate_relation_valid` | All checks passed | Validated | Basis of `auto_validated` |
| `canonical_node_match`, `canonical_relation_match` | The same identity is already in the graph | No status change | Context for the reviewer |
| `human_review_decision` | The candidate has a recorded decision | Status follows the decision | Section 5.7 |

Quotations and values are compared after `normalize_for_grounding`. It applies the engine's `normalize_text` (Unicode NFKC, collapsed whitespace, case folding) and then `normalize_arabic`, which removes short-vowel and Quranic marks and the elongation character, replaces punctuation with spaces, and folds the alef forms to ا, ى to ي, ة to ه, ؤ to و and ئ to ي. The comparison is substring containment, and an empty quotation never matches. Relation property values are not compared with the quotation.

A failed check always routes to review, whatever the confidence. Confidence is a number the model reports about itself, so a fabricated fact that fits the schema can carry a high value; the check result does not depend on it. The candidate is not rejected either, because a failure can be legitimate: a model that adds a definite article to a name fails `value_not_in_quote`, and a person should decide that case. The dependency refresh closes only items with a dependency reason, so it leaves these open.

The evidence and value checks run only when the run has a successful extraction execution; candidates entered through the API are treated as written by the operator.

## 5.6 Relation identity

In the earlier code an edge was merged on its two endpoints and its type, and its properties were then overwritten. Two transmissions between the same two narrators in two hadiths became one edge, and the second replaced the hadith reference and wording of the first. Duplicate detection among candidates used all properties as the key, so it saw two different candidates and raised no review item. The loss was silent.

A relation type now declares `merge_keys`, which must name properties declared on the type. `build_relation_identity_key` hashes the normalised merge-key values with SHA-256, and the Neo4j statement merges on that key:

```text
MERGE (from_node)-[r:`NARRATED_FROM` {project_id: $project_id,
       relation_type: $relation_type,
       relation_identity_key: $relation_identity_key}]->(to_node)
```

Candidate-level detection uses the same identity. `build_candidate_relation_resolution_key` joins the relation type, the identity keys of both endpoints and the relation identity key, and ignores properties outside the merge keys. Two candidates are therefore duplicates exactly when they would become the same edge.

A type without merge keys keeps one edge per node pair, but a second candidate for that pair now goes to review, and the commit refuses two validated relations that resolve to one edge with different properties.

## 5.7 The decision record

Decisions are stored in `review_decisions`. The repository protocol offers only `add_decision` and `list_decisions_by_run`. Re-validation replaces a run's review items but not its decisions.

A decision stores the review item, run, item type and item reference, the action (`accept`, `reject`, `edit`), `reviewer_id`, an optional note, an optional `duration_ms`, the time, and for an edit the candidate before and after. An edit is applied to a copy of the candidate and checked against the schema and against duplicates in the run; a refused decision stores nothing. A second decision on the same item is appended, and the latest one counts. A completed run accepts no decisions.

Human decisions are final for the automatic steps. `validate_run` reads the decisions first: a decided candidate takes its status from the latest decision, receives the result `human_review_decision`, skips the checks and keeps its review item. Duplicate handling never moves a decided candidate back to review, and the dependency refresh skips decided relations.

Acceptance records are computed on request by `list_acceptance_records` and are not stored. For each validated candidate the record holds the latest accepting decision, or the policy `auto_validated` with the rule code that passed the candidate.

Two limits apply: the reviewer name is not authenticated, and a decision refers to a candidate id of one run, so a new run over the same text does not reuse it.

## 5.8 Plug-ins of the isnad case study

**Segmentation strategy.** `IsnadSegmentation` wraps the rule-based `segment_isnad`. It normalises the text while keeping a map to source offsets, splits at the marker ح, finds transmission formulas from a lexicon of 26 entries, and ends the chain at the first cue of the report text. The strategy sets `one_call_per_segment`.

**Schema template.** The `isnad` template declares `Narrator` (merge key `name`), `Hadith` (merge key `hadith_ref`), `NARRATED_FROM` from narrator to narrator (merge keys `hadith_ref`, `chain_no`, `position`; property `sigha` for the wording) and `TRANSMITS` from narrator to hadith. It also names the segmentation strategy. Project creation applies it when `apply_template_schema` is set.

**Rule-based provider.** `rule_based_isnad` is the condition without a language model. It ignores the prompt, runs the same segmenter on each segment, and returns narrator nodes with the name as written and one `NARRATED_FROM` relation per consecutive pair. It creates no `Hadith` nodes. Its quotations are slices of the segment, so its output passes the grounding checks by construction.

**Extraction hints.** Each type carries a list of hint strings that travel to the model inside the schema part of the payload, for example "Copy the narrator name verbatim from the segment text."

## 5.9 Design decisions and alternatives

| Decision | Alternative considered | Reason |
|---|---|---|
| Edge identity from relation merge keys | A node for each transmission event | Smaller change to the generic model |
| A failed check routes to review | Reject it, or accept above a confidence threshold | Rejection hides legitimate variants; the threshold trusts a self-reported number |
| An unknown type drops one candidate and is recorded | Fail the whole answer, as before | Valid candidates are kept and drift can be counted |
| Append-only decisions with computed acceptance records | An event log from which the graph is rebuilt | Enough for an audit trail; rebuild and undo are not implemented |
| A rule-based segmenter available before the model, with one call per chain segment | One call per hadith, with the model finding the chains | Exact substrings and offsets, isolated failures, a baseline without a model. The evaluation found no gain in extraction quality from it (Section 7.5), so both strategies remain selectable |
| One graph transaction per run | One transaction per node, as before | A failed commit leaves no partial graph |

We accept three limits knowingly. A narrator node is identified by the exact written name, diacritics included, so the graph merges people who share a name and splits one person written in two ways. Chains that start after the boundary of the report text are not segmented, because transmission particles there mostly belong to the narrative. The grounding checks apply only to candidates that come from an extraction call.
