# GiraffeGraph Core — source code bundle (verbatim excerpts)

Repo: https://github.com/GiraffeGraph/giraffegraph-core (public). Snapshot taken 2026-09-30 from local checkout (git: 2 commits, last 2026-04-05; working tree may contain later uncommitted work).
Stack: Python 3.12+/FastAPI/Pydantic v2/SQLAlchemy+Alembic (Postgres 16), neo4j driver 6 (Neo4j 5 + APOC), Next.js 15 dashboard. Tests: 48 collected, 47 pass, 1 fail (stale assertion on prompt text) — run 2026-09-30 with memory backend.
Bundle excludes: .env, migrations, tests, frontend (except API client list), persistence repositories other than the Neo4j commit path.


## FILE: backend/src/app/domain/shared/enums.py
```python
 1 │ from enum import StrEnum
 2 │ 
 3 │ 
 4 │ class ProjectStatus(StrEnum):
 5 │     DRAFT = "draft"
 6 │     ACTIVE = "active"
 7 │     ARCHIVED = "archived"
 8 │ 
 9 │ 
10 │ class SchemaStatus(StrEnum):
11 │     DRAFT = "draft"
12 │     PUBLISHED = "published"
13 │     ACTIVE = "active"
14 │     RETIRED = "retired"
15 │ 
16 │ 
17 │ class SourceUnitStatus(StrEnum):
18 │     DRAFT = "draft"
19 │     READY = "ready"
20 │     PROCESSING = "processing"
21 │     PROCESSED = "processed"
22 │     FAILED = "failed"
23 │ 
24 │ 
25 │ class RunStatus(StrEnum):
26 │     PENDING = "pending"
27 │     RUNNING = "running"
28 │     COMPLETED = "completed"
29 │     FAILED = "failed"
30 │ 
31 │ 
32 │ class ExtractionExecutionStatus(StrEnum):
33 │     RUNNING = "running"
34 │     SUCCEEDED = "succeeded"
35 │     FAILED = "failed"
36 │ 
37 │ 
38 │ class ProcessingJobType(StrEnum):
39 │     EXTRACT_CANDIDATES = "extract_candidates"
40 │     VALIDATE_RUN = "validate_run"
41 │     COMMIT_RUN = "commit_run"
42 │ 
43 │ 
44 │ class ProcessingJobStatus(StrEnum):
45 │     PENDING = "pending"
46 │     RUNNING = "running"
47 │     SUCCEEDED = "succeeded"
48 │     FAILED = "failed"
49 │ 
50 │ 
51 │ class CandidateStatus(StrEnum):
52 │     PENDING = "pending"
53 │     VALIDATED = "validated"
54 │     REJECTED = "rejected"
55 │     REVIEW = "review"
56 │     COMMITTED = "committed"
57 │ 
58 │ 
59 │ class ReviewStatus(StrEnum):
60 │     OPEN = "open"
61 │     ACCEPTED = "accepted"
62 │     REJECTED = "rejected"
63 │     EDITED = "edited"
```

## FILE: backend/src/app/domain/shared/resolution.py
```python
  1 │ import hashlib
  2 │ import json
  3 │ from re import sub
  4 │ from unicodedata import normalize
  5 │ 
  6 │ from app.domain.extraction.entities import CandidateNode, CandidateRelation
  7 │ from app.domain.schema.entities import NodeTypeDefinition
  8 │ 
  9 │ 
 10 │ def derive_merge_key_payload(
 11 │     *,
 12 │     node_type: NodeTypeDefinition,
 13 │     properties: dict[str, object],
 14 │     provided_merge_key_payload: dict[str, object],
 15 │ ) -> dict[str, object]:
 16 │     merge_key_payload: dict[str, object] = {}
 17 │     for merge_key in node_type.merge_keys:
 18 │         property_value = properties.get(merge_key)
 19 │         if not is_missing_value(property_value):
 20 │             merge_key_payload[merge_key] = property_value
 21 │             continue
 22 │ 
 23 │         provided_value = provided_merge_key_payload.get(merge_key)
 24 │         if not is_missing_value(provided_value):
 25 │             merge_key_payload[merge_key] = provided_value
 26 │     return merge_key_payload
 27 │ 
 28 │ 
 29 │ def build_candidate_node_resolution_key(candidate_node: CandidateNode) -> str:
 30 │     return (
 31 │         f"{normalize_text(candidate_node.node_type)}::"
 32 │         f"{normalized_payload_key(candidate_node.merge_key_payload)}"
 33 │     )
 34 │ 
 35 │ 
 36 │ def build_candidate_relation_resolution_key(
 37 │     candidate_relation: CandidateRelation,
 38 │     *,
 39 │     node_resolution_keys_by_candidate_id: dict[str, str],
 40 │ ) -> str:
 41 │     from_key = node_resolution_keys_by_candidate_id.get(
 42 │         candidate_relation.from_candidate_ref,
 43 │         f"candidate::{candidate_relation.from_candidate_ref}",
 44 │     )
 45 │     to_key = node_resolution_keys_by_candidate_id.get(
 46 │         candidate_relation.to_candidate_ref,
 47 │         f"candidate::{candidate_relation.to_candidate_ref}",
 48 │     )
 49 │     return "::".join(
 50 │         [
 51 │             normalize_text(candidate_relation.relation_type),
 52 │             from_key,
 53 │             to_key,
 54 │             normalized_payload_key(candidate_relation.properties),
 55 │         ]
 56 │     )
 57 │ 
 58 │ 
 59 │ def candidate_node_identity_key(candidate_node: CandidateNode) -> str:
 60 │     if candidate_node.merge_key_payload:
 61 │         return build_candidate_node_resolution_key(candidate_node)
 62 │     return f"candidate::{candidate_node.candidate_node_id}"
 63 │ 
 64 │ 
 65 │ def build_canonical_merge_key(
 66 │     *,
 67 │     merge_key_payload: dict[str, object],
 68 │     fallback_payload: dict[str, object],
 69 │ ) -> str:
 70 │     payload = merge_key_payload if merge_key_payload else fallback_payload
 71 │     encoded = normalized_payload_key(payload)
 72 │     return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
 73 │ 
 74 │ 
 75 │ def normalized_payload_key(payload: dict[str, object]) -> str:
 76 │     return json.dumps(
 77 │         normalize_object(payload),
 78 │         sort_keys=True,
 79 │         separators=(",", ":"),
 80 │     )
 81 │ 
 82 │ 
 83 │ def normalize_object(value: object) -> object:
 84 │     if isinstance(value, str):
 85 │         return normalize_text(value)
 86 │     if isinstance(value, list):
 87 │         return [normalize_object(item) for item in value]
 88 │     if isinstance(value, dict):
 89 │         return {
 90 │             normalize_text(str(key)): normalize_object(item)
 91 │             for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
 92 │         }
 93 │     return value
 94 │ 
 95 │ 
 96 │ def normalize_text(value: str) -> str:
 97 │     normalized_value = normalize("NFKC", value).strip()
 98 │     if normalized_value == "":
 99 │         return ""
100 │     collapsed = sub(r"\s+", " ", normalized_value)
101 │     return collapsed.casefold()
102 │ 
103 │ 
104 │ def is_missing_value(value: object | None) -> bool:
105 │     if value is None:
106 │         return True
107 │     if isinstance(value, str):
108 │         return value.strip() == ""
109 │     if isinstance(value, (list, dict, set, tuple)):
110 │         return len(value) == 0
111 │     return False
```

## FILE: backend/src/app/domain/schema/entities.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ from datetime import UTC, datetime
 3 │ 
 4 │ from app.domain.shared.enums import SchemaStatus
 5 │ 
 6 │ 
 7 │ @dataclass(slots=True, kw_only=True)
 8 │ class PropertyDefinition:
 9 │     property_id: str
10 │     owner_kind: str
11 │     owner_type_name: str
12 │     name: str
13 │     data_type: str
14 │     required: bool = False
15 │     description: str | None = None
16 │     default_value: str | None = None
17 │     enum_values: list[str] = field(default_factory=list)
18 │ 
19 │ 
20 │ @dataclass(slots=True, kw_only=True)
21 │ class NodeTypeDefinition:
22 │     node_type_id: str
23 │     schema_version_id: str
24 │     name: str
25 │     display_name: str
26 │     description: str
27 │     is_core: bool = False
28 │     merge_keys: list[str] = field(default_factory=list)
29 │     confidence_threshold: float = 0.5
30 │     aliases: list[str] = field(default_factory=list)
31 │     extraction_hints: list[str] = field(default_factory=list)
32 │     properties: list[PropertyDefinition] = field(default_factory=list)
33 │     is_active: bool = True
34 │ 
35 │ 
36 │ @dataclass(slots=True, kw_only=True)
37 │ class RelationTypeDefinition:
38 │     relation_type_id: str
39 │     schema_version_id: str
40 │     name: str
41 │     from_type: str
42 │     to_type: str
43 │     description: str
44 │     directional: bool = True
45 │     aliases: list[str] = field(default_factory=list)
46 │     extraction_hints: list[str] = field(default_factory=list)
47 │     required_properties: list[str] = field(default_factory=list)
48 │     properties: list[PropertyDefinition] = field(default_factory=list)
49 │     confidence_threshold: float = 0.7
50 │     is_active: bool = True
51 │ 
52 │ 
53 │ @dataclass(slots=True, kw_only=True)
54 │ class SchemaVersion:
55 │     schema_version_id: str
56 │     project_id: str
57 │     version_no: int
58 │     status: SchemaStatus = SchemaStatus.DRAFT
59 │     notes: str | None = None
60 │     created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
61 │     activated_at: datetime | None = None
```

## FILE: backend/src/app/domain/extraction/entities.py
```python
  1 │ from dataclasses import dataclass, field
  2 │ from datetime import UTC, datetime
  3 │ 
  4 │ from app.domain.shared.enums import CandidateStatus, ExtractionExecutionStatus
  5 │ 
  6 │ 
  7 │ @dataclass(slots=True, kw_only=True)
  8 │ class EvidenceRef:
  9 │     segment_id: str
 10 │     quote: str | None = None
 11 │     start_offset: int | None = None
 12 │     end_offset: int | None = None
 13 │ 
 14 │ 
 15 │ @dataclass(slots=True, kw_only=True)
 16 │ class CandidateNode:
 17 │     candidate_node_id: str
 18 │     run_id: str
 19 │     node_type: str
 20 │     properties: dict[str, object] = field(default_factory=dict)
 21 │     merge_key_payload: dict[str, object] = field(default_factory=dict)
 22 │     confidence: float = 0.0
 23 │     evidence_refs: list[EvidenceRef] = field(default_factory=list)
 24 │     status: CandidateStatus = CandidateStatus.PENDING
 25 │ 
 26 │ 
 27 │ @dataclass(slots=True, kw_only=True)
 28 │ class CandidateRelation:
 29 │     candidate_relation_id: str
 30 │     run_id: str
 31 │     relation_type: str
 32 │     from_candidate_ref: str
 33 │     to_candidate_ref: str
 34 │     properties: dict[str, object] = field(default_factory=dict)
 35 │     confidence: float = 0.0
 36 │     evidence_refs: list[EvidenceRef] = field(default_factory=list)
 37 │     status: CandidateStatus = CandidateStatus.PENDING
 38 │ 
 39 │ 
 40 │ @dataclass(slots=True, kw_only=True)
 41 │ class SuggestedNode:
 42 │     ref: str
 43 │     node_type: str
 44 │     properties: dict[str, object] = field(default_factory=dict)
 45 │     merge_key_payload: dict[str, object] = field(default_factory=dict)
 46 │     confidence: float = 0.0
 47 │     evidence_refs: list[EvidenceRef] = field(default_factory=list)
 48 │ 
 49 │ 
 50 │ @dataclass(slots=True, kw_only=True)
 51 │ class SuggestedRelation:
 52 │     relation_type: str
 53 │     from_ref: str
 54 │     to_ref: str
 55 │     properties: dict[str, object] = field(default_factory=dict)
 56 │     confidence: float = 0.0
 57 │     evidence_refs: list[EvidenceRef] = field(default_factory=list)
 58 │ 
 59 │ 
 60 │ @dataclass(slots=True, kw_only=True)
 61 │ class ExtractionExecutionReport:
 62 │     execution_id: str
 63 │     run_id: str
 64 │     dry_run: bool
 65 │     prompt_version: str
 66 │     schema_name: str
 67 │     provider_name: str
 68 │     requested_llm_provider: str | None = None
 69 │     requested_llm_model: str | None = None
 70 │     resolved_llm_model: str | None = None
 71 │     segment_count: int = 0
 72 │     suggested_nodes: list[SuggestedNode] = field(default_factory=list)
 73 │     suggested_relations: list[SuggestedRelation] = field(default_factory=list)
 74 │     created_candidate_node_ids: list[str] = field(default_factory=list)
 75 │     created_candidate_relation_ids: list[str] = field(default_factory=list)
 76 │     started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
 77 │     completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
 78 │ 
 79 │ 
 80 │ @dataclass(slots=True, kw_only=True)
 81 │ class ExtractionExecution:
 82 │     execution_id: str
 83 │     run_id: str
 84 │     dry_run: bool
 85 │     status: ExtractionExecutionStatus
 86 │     prompt_key: str
 87 │     prompt_version: str | None = None
 88 │     schema_name: str | None = None
 89 │     provider_name: str | None = None
 90 │     requested_llm_provider: str | None = None
 91 │     requested_llm_model: str | None = None
 92 │     resolved_llm_model: str | None = None
 93 │     segment_count: int = 0
 94 │     suggested_node_count: int = 0
 95 │     suggested_relation_count: int = 0
 96 │     created_candidate_node_count: int = 0
 97 │     created_candidate_relation_count: int = 0
 98 │     error_message: str | None = None
 99 │     started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
100 │     completed_at: datetime | None = None
```

## FILE: backend/src/app/domain/review/entities.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ from datetime import UTC, datetime
 3 │ 
 4 │ from app.domain.extraction.entities import CandidateNode, CandidateRelation
 5 │ from app.domain.ingestion.entities import ProcessingRun, SourceUnit
 6 │ from app.domain.shared.enums import ReviewStatus
 7 │ 
 8 │ 
 9 │ @dataclass(slots=True, kw_only=True)
10 │ class ReviewItem:
11 │     review_item_id: str
12 │     run_id: str
13 │     item_type: str
14 │     item_ref: str
15 │     reason_code: str
16 │     payload_json: dict[str, object]
17 │     status: ReviewStatus = ReviewStatus.OPEN
18 │     reviewer_note: str | None = None
19 │     created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
20 │ 
21 │ 
22 │ @dataclass(slots=True, kw_only=True)
23 │ class ReviewEvidenceSnippet:
24 │     segment_id: str
25 │     segment_order: int | None = None
26 │     text: str | None = None
27 │     quote: str | None = None
28 │ 
29 │ 
30 │ @dataclass(slots=True, kw_only=True)
31 │ class ReviewQueueItem:
32 │     review_item: ReviewItem
33 │     candidate_node: CandidateNode | None = None
34 │     candidate_relation: CandidateRelation | None = None
35 │     headline: str = ""
36 │     confidence: float | None = None
37 │     messages: list[str] = field(default_factory=list)
38 │     evidence_snippets: list[ReviewEvidenceSnippet] = field(default_factory=list)
39 │ 
40 │ 
41 │ @dataclass(slots=True, kw_only=True)
42 │ class ReviewQueueRunEntry:
43 │     run: ProcessingRun
44 │     source_unit: SourceUnit
45 │     review_items: list[ReviewQueueItem] = field(default_factory=list)
46 │     open_review_count: int = 0
47 │     total_review_count: int = 0
48 │ 
49 │ 
50 │ @dataclass(slots=True, kw_only=True)
51 │ class ProjectReviewQueue:
52 │     project_id: str
53 │     run_entries: list[ReviewQueueRunEntry] = field(default_factory=list)
54 │     status_filter: str = "all"
55 │     run_limit: int = 0
56 │     open_review_count: int = 0
57 │     total_review_count: int = 0
58 │     filtered_run_count: int = 0
59 │     returned_run_count: int = 0
60 │     returned_review_count: int = 0
61 │     has_more_runs: bool = False
```

## FILE: backend/src/app/domain/graph_commit/entities.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ from datetime import UTC, datetime
 3 │ 
 4 │ from app.domain.extraction.entities import CandidateNode, CandidateRelation
 5 │ from app.domain.ingestion.entities import Segment, SourceUnit
 6 │ 
 7 │ 
 8 │ @dataclass(slots=True, kw_only=True)
 9 │ class GraphDelta:
10 │     delta_id: str
11 │     run_id: str
12 │     project_id: str
13 │     nodes_created: int = 0
14 │     nodes_merged: int = 0
15 │     relations_created: int = 0
16 │     relations_merged: int = 0
17 │     review_count: int = 0
18 │     rejected_count: int = 0
19 │     created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
20 │ 
21 │ 
22 │ @dataclass(slots=True, kw_only=True)
23 │ class CanonicalCommitBundle:
24 │     delta: GraphDelta
25 │     source_unit: SourceUnit
26 │     segments: list[Segment] = field(default_factory=list)
27 │     candidate_nodes: list[CandidateNode] = field(default_factory=list)
28 │     candidate_relations: list[CandidateRelation] = field(default_factory=list)
```

## FILE: backend/src/app/domain/ingestion/entities.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ from datetime import UTC, datetime
 3 │ 
 4 │ from app.domain.shared.enums import RunStatus, SourceUnitStatus
 5 │ 
 6 │ 
 7 │ @dataclass(slots=True, kw_only=True)
 8 │ class SourceUnit:
 9 │     source_unit_id: str
10 │     project_id: str
11 │     schema_version_id: str
12 │     source_type: str
13 │     title: str
14 │     raw_content: str
15 │     sequence_no: int | None = None
16 │     external_ref: str | None = None
17 │     metadata_json: dict[str, str] = field(default_factory=dict)
18 │     status: SourceUnitStatus = SourceUnitStatus.DRAFT
19 │     created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
20 │ 
21 │ 
22 │ @dataclass(slots=True, kw_only=True)
23 │ class Segment:
24 │     segment_id: str
25 │     source_unit_id: str
26 │     segment_order: int
27 │     text: str
28 │     metadata_json: dict[str, str] = field(default_factory=dict)
29 │ 
30 │ 
31 │ @dataclass(slots=True, kw_only=True)
32 │ class ProcessingRun:
33 │     run_id: str
34 │     project_id: str
35 │     schema_version_id: str
36 │     source_unit_id: str
37 │     pipeline_version: str
38 │     status: RunStatus = RunStatus.PENDING
39 │     llm_provider: str | None = None
40 │     llm_model: str | None = None
41 │     created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
42 │     started_at: datetime | None = None
43 │     ended_at: datetime | None = None
```

## FILE: backend/src/app/domain/orchestration/pipeline_definitions.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ from datetime import UTC, datetime
 3 │ 
 4 │ from app.domain.shared.enums import ProcessingJobType
 5 │ 
 6 │ DEFAULT_PIPELINE_VERSION = "v1"
 7 │ DEFAULT_PIPELINE_DESCRIPTION = "Default extraction, validation, and commit pipeline."
 8 │ 
 9 │ 
10 │ @dataclass(slots=True, kw_only=True)
11 │ class PipelineStepDefinition:
12 │     job_type: ProcessingJobType
13 │     chain_on_success: list[ProcessingJobType] = field(default_factory=list)
14 │ 
15 │ 
16 │ @dataclass(slots=True, kw_only=True)
17 │ class PipelineDefinition:
18 │     pipeline_definition_id: str
19 │     schema_version_id: str
20 │     version: str
21 │     description: str | None = None
22 │     steps: list[PipelineStepDefinition] = field(default_factory=list)
23 │     created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
24 │     updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
25 │ 
26 │ 
27 │ def build_default_pipeline_steps() -> list[PipelineStepDefinition]:
28 │     return [
29 │         PipelineStepDefinition(
30 │             job_type=ProcessingJobType.EXTRACT_CANDIDATES,
31 │             chain_on_success=[ProcessingJobType.VALIDATE_RUN],
32 │         ),
33 │         PipelineStepDefinition(
34 │             job_type=ProcessingJobType.VALIDATE_RUN,
35 │             chain_on_success=[ProcessingJobType.COMMIT_RUN],
36 │         ),
37 │         PipelineStepDefinition(
38 │             job_type=ProcessingJobType.COMMIT_RUN,
39 │             chain_on_success=[],
40 │         ),
41 │     ]
```

## FILE: backend/src/app/application/dto/contracts.py
```python
  1 │ from pydantic import BaseModel, ConfigDict, Field
  2 │ 
  3 │ from app.domain.shared.enums import ProcessingJobType
  4 │ 
  5 │ 
  6 │ class ProjectCreateInput(BaseModel):
  7 │     model_config = ConfigDict(extra="forbid")
  8 │ 
  9 │     name: str = Field(min_length=1, max_length=120)
 10 │     description: str | None = Field(default=None, max_length=1000)
 11 │     template_id: str | None = None
 12 │ 
 13 │ 
 14 │ class SchemaVersionCreateInput(BaseModel):
 15 │     model_config = ConfigDict(extra="forbid")
 16 │ 
 17 │     project_id: str
 18 │     version_no: int = Field(ge=1)
 19 │     notes: str | None = Field(default=None, max_length=1000)
 20 │ 
 21 │ 
 22 │ class PropertyDefinitionInput(BaseModel):
 23 │     model_config = ConfigDict(extra="forbid")
 24 │ 
 25 │     name: str = Field(min_length=1, max_length=120)
 26 │     data_type: str = Field(min_length=1, max_length=50)
 27 │     required: bool = False
 28 │     description: str | None = Field(default=None, max_length=500)
 29 │     default_value: str | None = None
 30 │     enum_values: list[str] = Field(default_factory=list)
 31 │ 
 32 │ 
 33 │ class NodeTypeDefinitionInput(BaseModel):
 34 │     model_config = ConfigDict(extra="forbid")
 35 │ 
 36 │     name: str = Field(min_length=1, max_length=80)
 37 │     display_name: str = Field(min_length=1, max_length=120)
 38 │     description: str = Field(min_length=1, max_length=500)
 39 │     is_core: bool = False
 40 │     merge_keys: list[str] = Field(default_factory=list)
 41 │     confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
 42 │     aliases: list[str] = Field(default_factory=list)
 43 │     extraction_hints: list[str] = Field(default_factory=list)
 44 │     properties: list[PropertyDefinitionInput] = Field(default_factory=list)
 45 │ 
 46 │ 
 47 │ class RelationTypeDefinitionInput(BaseModel):
 48 │     model_config = ConfigDict(extra="forbid")
 49 │ 
 50 │     name: str = Field(min_length=1, max_length=80)
 51 │     from_type: str = Field(min_length=1, max_length=80)
 52 │     to_type: str = Field(min_length=1, max_length=80)
 53 │     description: str = Field(min_length=1, max_length=500)
 54 │     directional: bool = True
 55 │     aliases: list[str] = Field(default_factory=list)
 56 │     extraction_hints: list[str] = Field(default_factory=list)
 57 │     required_properties: list[str] = Field(default_factory=list)
 58 │     confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
 59 │     properties: list[PropertyDefinitionInput] = Field(default_factory=list)
 60 │ 
 61 │ 
 62 │ class SourceUnitCreateInput(BaseModel):
 63 │     model_config = ConfigDict(extra="forbid")
 64 │ 
 65 │     project_id: str
 66 │     schema_version_id: str
 67 │     source_type: str = Field(min_length=1, max_length=80)
 68 │     title: str = Field(min_length=1, max_length=200)
 69 │     raw_content: str = Field(min_length=1)
 70 │     sequence_no: int | None = Field(default=None, ge=1)
 71 │     external_ref: str | None = Field(default=None, max_length=200)
 72 │     metadata_json: dict[str, str] = Field(default_factory=dict)
 73 │ 
 74 │ 
 75 │ class ProcessingRunStartInput(BaseModel):
 76 │     model_config = ConfigDict(extra="forbid")
 77 │ 
 78 │     schema_version_id: str
 79 │     source_unit_id: str
 80 │     pipeline_version: str = Field(min_length=1, max_length=50)
 81 │     llm_provider: str | None = Field(default=None, max_length=80)
 82 │     llm_model: str | None = Field(default=None, max_length=120)
 83 │ 
 84 │ 
 85 │ class PipelineStepDefinitionInput(BaseModel):
 86 │     model_config = ConfigDict(extra="forbid")
 87 │ 
 88 │     job_type: ProcessingJobType
 89 │     chain_on_success: list[ProcessingJobType] = Field(default_factory=list)
 90 │ 
 91 │ 
 92 │ class PipelineDefinitionCreateInput(BaseModel):
 93 │     model_config = ConfigDict(extra="forbid")
 94 │ 
 95 │     schema_version_id: str
 96 │     version: str = Field(min_length=1, max_length=50)
 97 │     description: str | None = Field(default=None, max_length=500)
 98 │     steps: list[PipelineStepDefinitionInput] = Field(min_length=1)
 99 │ 
100 │ 
101 │ class SegmentGenerationInput(BaseModel):
102 │     model_config = ConfigDict(extra="forbid")
103 │ 
104 │     source_unit_id: str
105 │     strategy: str = Field(default="paragraphs", min_length=1, max_length=50)
106 │ 
107 │ 
108 │ class ExtractionExecutionInput(BaseModel):
109 │     model_config = ConfigDict(extra="forbid")
110 │ 
111 │     dry_run: bool = False
112 │ 
113 │ 
114 │ class ProcessingJobCreateInput(BaseModel):
115 │     model_config = ConfigDict(extra="forbid")
116 │ 
117 │     run_id: str
118 │     job_type: ProcessingJobType
119 │     dry_run: bool = False
120 │     chain_on_success: list[ProcessingJobType] | None = None
121 │ 
122 │ 
123 │ class ProcessingJobProcessNextInput(BaseModel):
124 │     model_config = ConfigDict(extra="forbid")
125 │ 
126 │     job_type: ProcessingJobType | None = None
127 │     run_id: str | None = None
128 │ 
129 │ 
130 │ class EvidenceRefInput(BaseModel):
131 │     model_config = ConfigDict(extra="forbid")
132 │ 
133 │     segment_id: str
134 │     quote: str | None = None
135 │     start_offset: int | None = Field(default=None, ge=0)
136 │     end_offset: int | None = Field(default=None, ge=0)
137 │ 
138 │ 
139 │ class CandidateNodeInput(BaseModel):
140 │     model_config = ConfigDict(extra="forbid")
141 │ 
142 │     node_type: str = Field(min_length=1, max_length=80)
143 │     properties: dict[str, object] = Field(default_factory=dict)
144 │     merge_key_payload: dict[str, object] = Field(default_factory=dict)
145 │     confidence: float = Field(default=0.0, ge=0.0, le=1.0)
146 │     evidence_refs: list[EvidenceRefInput] = Field(default_factory=list)
147 │ 
148 │ 
149 │ class CandidateRelationInput(BaseModel):
150 │     model_config = ConfigDict(extra="forbid")
151 │ 
152 │     relation_type: str = Field(min_length=1, max_length=80)
153 │     from_candidate_ref: str
154 │     to_candidate_ref: str
155 │     properties: dict[str, object] = Field(default_factory=dict)
156 │     confidence: float = Field(default=0.0, ge=0.0, le=1.0)
157 │     evidence_refs: list[EvidenceRefInput] = Field(default_factory=list)
158 │ 
159 │ 
160 │ class ReviewDecisionInput(BaseModel):
161 │     model_config = ConfigDict(extra="forbid")
162 │ 
163 │     action: str = Field(min_length=1, max_length=20)
164 │     reviewer_note: str | None = Field(default=None, max_length=1000)
165 │     node_type: str | None = Field(default=None, max_length=80)
166 │     relation_type: str | None = Field(default=None, max_length=80)
167 │     from_candidate_ref: str | None = None
168 │     to_candidate_ref: str | None = None
169 │     properties: dict[str, object] = Field(default_factory=dict)
170 │     merge_key_payload: dict[str, object] = Field(default_factory=dict)
171 │     confidence: float | None = Field(default=None, ge=0.0, le=1.0)
```

## FILE: backend/src/app/infrastructure/llm/prompt_catalog.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ 
 3 │ from app.application.ports.prompt_catalog import StructuredPromptDefinition
 4 │ from app.application.ports.repositories import StructuredPromptRepository
 5 │ 
 6 │ CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY = "candidate_graph_extraction"
 7 │ CANDIDATE_GRAPH_EXTRACTION_V1 = StructuredPromptDefinition(
 8 │     prompt_key=CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY,
 9 │     version="candidate_graph_extraction_v1",
10 │     schema_name="candidate_graph_extraction_v1",
11 │     prompt_text=(
12 │         "You are extracting candidate graph suggestions from segmented source material.\n"
13 │         "Use only the provided schema node and relation types, including aliases.\n\n"
14 │         "Return a JSON object with exactly this structure:\n"
15 │         "{\n"
16 │         '  "nodes": [\n'
17 │         "    {\n"
18 │         '      "ref": "<stable unique string id for this node, e.g. node-1>",\n'
19 │         '      "node_type": "<must match a name from schema.node_types>",\n'
20 │         '      "properties": {"<merge_key_field>": "<value>", ...},\n'
21 │         '      "merge_key_payload": {},\n'
22 │         '      "confidence": 0.9,\n'
23 │         '      "evidence_refs": [{"segment_id": "<id from segments list>", "quote": "<exact quote>"}]\n'
24 │         "    }\n"
25 │         "  ],\n"
26 │         '  "relations": [\n'
27 │         "    {\n"
28 │         '      "relation_type": "<must match a name from schema.relation_types>",\n'
29 │         '      "from_ref": "<ref of the source node>",\n'
30 │         '      "to_ref": "<ref of the target node>",\n'
31 │         '      "properties": {},\n'
32 │         '      "confidence": 0.85,\n'
33 │         '      "evidence_refs": [{"segment_id": "<id from segments list>", "quote": "<exact quote>"}]\n'
34 │         "    }\n"
35 │         "  ]\n"
36 │         "}\n\n"
37 │         "Rules:\n"
38 │         "- 'ref' must be a unique string (e.g. node-1, node-2); never use 'id' or 'type' as field names.\n"
39 │         "- 'node_type' and 'relation_type' must exactly match schema names (case-sensitive).\n"
40 │         "- 'from_ref' and 'to_ref' must match a 'ref' defined in the nodes list.\n"
41 │         "- Put the merge key value inside 'properties' (e.g. {\"name\": \"Alice\"}).\n"
42 │         "- Only reference segment_ids that appear in the input payload.\n"
43 │         "- Do not add any fields outside this schema."
44 │     ),
45 │ )
46 │ DEFAULT_STRUCTURED_PROMPTS = [CANDIDATE_GRAPH_EXTRACTION_V1]
47 │ 
48 │ 
49 │ @dataclass(slots=True)
50 │ class StaticStructuredPromptCatalog:
51 │     prompts: dict[tuple[str, str], StructuredPromptDefinition] = field(default_factory=dict)
52 │ 
53 │     def __init__(self, prompts: list[StructuredPromptDefinition]) -> None:
54 │         registry: dict[tuple[str, str], StructuredPromptDefinition] = {}
55 │         for prompt in prompts:
56 │             key = (prompt.prompt_key.strip().casefold(), prompt.version.strip())
57 │             if key in registry:
58 │                 raise ValueError(
59 │                     f"Prompt '{prompt.prompt_key}' version '{prompt.version}' is duplicated."
60 │                 )
61 │             registry[key] = prompt
62 │         self.prompts = registry
63 │ 
64 │     def get(
65 │         self,
66 │         *,
67 │         prompt_key: str,
68 │         version: str,
69 │     ) -> StructuredPromptDefinition | None:
70 │         normalized_key = prompt_key.strip().casefold()
71 │         normalized_version = version.strip()
72 │         if normalized_key == "" or normalized_version == "":
73 │             return None
74 │         return self.prompts.get((normalized_key, normalized_version))
75 │ 
76 │ 
77 │ @dataclass(slots=True)
78 │ class RepositoryStructuredPromptCatalog:
79 │     repository: StructuredPromptRepository
80 │ 
81 │     def get(
82 │         self,
83 │         *,
84 │         prompt_key: str,
85 │         version: str,
86 │     ) -> StructuredPromptDefinition | None:
87 │         return self.repository.get(prompt_key=prompt_key, version=version)
88 │ 
89 │ 
90 │ def seed_default_structured_prompts(repository: StructuredPromptRepository) -> None:
91 │     for prompt in DEFAULT_STRUCTURED_PROMPTS:
92 │         repository.upsert(prompt)
```

## FILE: backend/src/app/infrastructure/llm/openai_provider.py
```python
  1 │ import json
  2 │ from dataclasses import dataclass, field
  3 │ from json import JSONDecodeError
  4 │ from typing import Any, Protocol
  5 │ from urllib import error, request
  6 │ 
  7 │ from app.application.errors import ExternalServiceError, RuleViolationError
  8 │ 
  9 │ 
 10 │ class OpenAITransport(Protocol):
 11 │     def __call__(
 12 │         self,
 13 │         *,
 14 │         url: str,
 15 │         headers: dict[str, str],
 16 │         payload: dict[str, object],
 17 │         timeout_seconds: float,
 18 │     ) -> dict[str, Any]: ...
 19 │ 
 20 │ 
 21 │ def _default_openai_transport(
 22 │     *,
 23 │     url: str,
 24 │     headers: dict[str, str],
 25 │     payload: dict[str, object],
 26 │     timeout_seconds: float,
 27 │ ) -> dict[str, Any]:
 28 │     body = json.dumps(payload).encode("utf-8")
 29 │     http_request = request.Request(
 30 │         url,
 31 │         data=body,
 32 │         headers=headers,
 33 │         method="POST",
 34 │     )
 35 │     try:
 36 │         with request.urlopen(http_request, timeout=timeout_seconds) as response:
 37 │             raw_response = response.read().decode("utf-8")
 38 │     except error.HTTPError as exc:
 39 │         detail = exc.read().decode("utf-8", errors="replace").strip()
 40 │         if detail:
 41 │             raise ExternalServiceError(
 42 │                 f"OpenAI provider request failed with status {exc.code}: {detail}"
 43 │             ) from exc
 44 │         raise ExternalServiceError(
 45 │             f"OpenAI provider request failed with status {exc.code}."
 46 │         ) from exc
 47 │     except error.URLError as exc:
 48 │         raise ExternalServiceError(
 49 │             f"OpenAI provider request failed: {exc.reason}."
 50 │         ) from exc
 51 │     except OSError as exc:
 52 │         raise ExternalServiceError(
 53 │             f"OpenAI provider request failed: {exc}."
 54 │         ) from exc
 55 │ 
 56 │     try:
 57 │         parsed = json.loads(raw_response)
 58 │     except JSONDecodeError as exc:
 59 │         raise ExternalServiceError("OpenAI provider returned invalid JSON.") from exc
 60 │     if not isinstance(parsed, dict):
 61 │         raise ExternalServiceError("OpenAI provider returned a non-object response.")
 62 │     return parsed
 63 │ 
 64 │ 
 65 │ @dataclass(slots=True)
 66 │ class OpenAILLMProvider:
 67 │     api_key: str
 68 │     base_url: str = "https://api.openai.com/v1"
 69 │     timeout_seconds: float = 30.0
 70 │     transport: OpenAITransport = field(default=_default_openai_transport)
 71 │     provider_name: str = "openai"
 72 │ 
 73 │     def generate_structured(
 74 │         self,
 75 │         *,
 76 │         prompt: str,
 77 │         schema_name: str,
 78 │         payload: dict[str, Any],
 79 │         model: str | None = None,
 80 │     ) -> dict[str, Any]:
 81 │         normalized_model = self._normalize_optional(model)
 82 │         if normalized_model is None:
 83 │             raise RuleViolationError(
 84 │                 "OpenAI extraction provider requires a configured model."
 85 │             )
 86 │ 
 87 │         response = self.transport(
 88 │             url=f"{self.base_url.rstrip('/')}/chat/completions",
 89 │             headers={
 90 │                 "Authorization": f"Bearer {self.api_key}",
 91 │                 "Content-Type": "application/json",
 92 │             },
 93 │             payload={
 94 │                 "model": normalized_model,
 95 │                 "temperature": 0,
 96 │                 "response_format": {"type": "json_object"},
 97 │                 "messages": [
 98 │                     {
 99 │                         "role": "system",
100 │                         "content": prompt,
101 │                     },
102 │                     {
103 │                         "role": "user",
104 │                         "content": json.dumps(
105 │                             {
106 │                                 "schema_name": schema_name,
107 │                                 "payload": payload,
108 │                             }
109 │                         ),
110 │                     },
111 │                 ],
112 │             },
113 │             timeout_seconds=self.timeout_seconds,
114 │         )
115 │         content = self._extract_content(response)
116 │         parsed_output = self._parse_output(content)
117 │         if not isinstance(parsed_output, dict):
118 │             raise ExternalServiceError(
119 │                 "OpenAI provider returned a non-object structured output."
120 │             )
121 │         return parsed_output
122 │ 
123 │     def _extract_content(self, response: dict[str, Any]) -> str:
124 │         choices = response.get("choices")
125 │         if not isinstance(choices, list) or len(choices) == 0:
126 │             raise ExternalServiceError("OpenAI provider response did not include choices.")
127 │ 
128 │         first_choice = choices[0]
129 │         if not isinstance(first_choice, dict):
130 │             raise ExternalServiceError("OpenAI provider returned an invalid choice payload.")
131 │ 
132 │         message = first_choice.get("message")
133 │         if not isinstance(message, dict):
134 │             raise ExternalServiceError("OpenAI provider response did not include a message.")
135 │ 
136 │         content = message.get("content")
137 │         if isinstance(content, str):
138 │             return content
139 │         if isinstance(content, list):
140 │             text_parts: list[str] = []
141 │             for item in content:
142 │                 if not isinstance(item, dict):
143 │                     continue
144 │                 text_value = item.get("text")
145 │                 if isinstance(text_value, str):
146 │                     text_parts.append(text_value)
147 │                     continue
148 │                 if isinstance(text_value, dict):
149 │                     nested_text = text_value.get("value")
150 │                     if isinstance(nested_text, str):
151 │                         text_parts.append(nested_text)
152 │             if text_parts:
153 │                 return "".join(text_parts)
154 │ 
155 │         raise ExternalServiceError(
156 │             "OpenAI provider response did not include textual message content."
157 │         )
158 │ 
159 │     def _parse_output(self, content: str) -> object:
160 │         normalized_content = content.strip()
161 │         if normalized_content.startswith("```"):
162 │             normalized_content = self._strip_code_fence(normalized_content)
163 │         try:
164 │             return json.loads(normalized_content)
165 │         except JSONDecodeError as exc:
166 │             raise ExternalServiceError(
167 │                 "OpenAI provider returned a non-JSON structured output."
168 │             ) from exc
169 │ 
170 │     def _strip_code_fence(self, content: str) -> str:
171 │         lines = content.splitlines()
172 │         if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
173 │             return "\n".join(lines[1:-1]).strip()
174 │         return content
175 │ 
176 │     def _normalize_optional(self, value: str | None) -> str | None:
177 │         if value is None:
178 │             return None
179 │         normalized_value = value.strip()
180 │         if normalized_value == "":
181 │             return None
182 │         return normalized_value
```

## FILE: backend/src/app/application/use_cases/extraction_management.py
```python
  1 │ from dataclasses import dataclass
  2 │ from datetime import UTC, datetime
  3 │ from typing import Any, TypeVar
  4 │ from uuid import uuid4
  5 │ 
  6 │ from pydantic import BaseModel, ConfigDict, Field, ValidationError
  7 │ 
  8 │ from app.application.dto.contracts import ExtractionExecutionInput
  9 │ from app.application.errors import ConflictError, NotFoundError, RuleViolationError
 10 │ from app.application.ports.llm_provider import LLMProvider, LLMProviderRegistry
 11 │ from app.application.ports.prompt_catalog import (
 12 │     StructuredPromptCatalog,
 13 │     StructuredPromptDefinition,
 14 │ )
 15 │ from app.application.ports.repositories import (
 16 │     CandidateNodeRepository,
 17 │     CandidateRelationRepository,
 18 │     ExtractionExecutionRepository,
 19 │     ProcessingRunRepository,
 20 │     SchemaRepository,
 21 │     SegmentRepository,
 22 │     SourceUnitRepository,
 23 │ )
 24 │ from app.domain.extraction.entities import (
 25 │     CandidateNode,
 26 │     CandidateRelation,
 27 │     EvidenceRef,
 28 │     ExtractionExecution,
 29 │     ExtractionExecutionReport,
 30 │     SuggestedNode,
 31 │     SuggestedRelation,
 32 │ )
 33 │ from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
 34 │ from app.domain.ingestion.lifecycle import (
 35 │     mark_run_failed,
 36 │     mark_run_started,
 37 │     reserve_source_for_run,
 38 │ )
 39 │ from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
 40 │ from app.domain.shared.enums import ExtractionExecutionStatus, RunStatus
 41 │ from app.domain.shared.resolution import derive_merge_key_payload
 42 │ 
 43 │ EXTRACTION_PROMPT_KEY = "candidate_graph_extraction"
 44 │ SchemaTypeDefinition = TypeVar(
 45 │     "SchemaTypeDefinition",
 46 │     NodeTypeDefinition,
 47 │     RelationTypeDefinition,
 48 │ )
 49 │ 
 50 │ 
 51 │ class ExtractionEvidenceContract(BaseModel):
 52 │     model_config = ConfigDict(extra="ignore")
 53 │ 
 54 │     segment_id: str
 55 │     quote: str | None = None
 56 │     start_offset: int | None = Field(default=None, ge=0)
 57 │     end_offset: int | None = Field(default=None, ge=0)
 58 │ 
 59 │ 
 60 │ class SuggestedNodeContract(BaseModel):
 61 │     model_config = ConfigDict(extra="ignore")
 62 │ 
 63 │     ref: str = Field(min_length=1, max_length=120)
 64 │     node_type: str = Field(min_length=1, max_length=80)
 65 │     properties: dict[str, object] = Field(default_factory=dict)
 66 │     merge_key_payload: dict[str, object] = Field(default_factory=dict)
 67 │     confidence: float = Field(default=0.0, ge=0.0, le=1.0)
 68 │     evidence_refs: list[ExtractionEvidenceContract] = Field(default_factory=list)
 69 │ 
 70 │ 
 71 │ class SuggestedRelationContract(BaseModel):
 72 │     model_config = ConfigDict(extra="ignore")
 73 │ 
 74 │     relation_type: str = Field(min_length=1, max_length=80)
 75 │     from_ref: str = Field(min_length=1, max_length=120)
 76 │     to_ref: str = Field(min_length=1, max_length=120)
 77 │     properties: dict[str, object] = Field(default_factory=dict)
 78 │     confidence: float = Field(default=0.0, ge=0.0, le=1.0)
 79 │     evidence_refs: list[ExtractionEvidenceContract] = Field(default_factory=list)
 80 │ 
 81 │ 
 82 │ class StructuredExtractionContract(BaseModel):
 83 │     model_config = ConfigDict(extra="ignore")
 84 │ 
 85 │     nodes: list[SuggestedNodeContract] = Field(default_factory=list)
 86 │     relations: list[SuggestedRelationContract] = Field(default_factory=list)
 87 │ 
 88 │ 
 89 │ @dataclass(slots=True)
 90 │ class ExtractionManagementService:
 91 │     processing_run_repository: ProcessingRunRepository
 92 │     source_unit_repository: SourceUnitRepository
 93 │     segment_repository: SegmentRepository
 94 │     schema_repository: SchemaRepository
 95 │     candidate_node_repository: CandidateNodeRepository
 96 │     candidate_relation_repository: CandidateRelationRepository
 97 │     extraction_execution_repository: ExtractionExecutionRepository
 98 │     provider_registry: LLMProviderRegistry
 99 │     prompt_catalog: StructuredPromptCatalog
100 │     default_llm_provider: str
101 │     default_llm_model: str | None = None
102 │     default_extraction_prompt_version: str = "candidate_graph_extraction_v1"
103 │ 
104 │     def extract_candidates(
105 │         self,
106 │         run_id: str,
107 │         payload: ExtractionExecutionInput,
108 │     ) -> ExtractionExecutionReport:
109 │         run = self._require_run(run_id)
110 │         self._ensure_run_is_mutable(run)
111 │         source_unit = self._require_source_unit(run.source_unit_id)
112 │         execution = ExtractionExecution(
113 │             execution_id=str(uuid4()),
114 │             run_id=run.run_id,
115 │             dry_run=payload.dry_run,
116 │             status=ExtractionExecutionStatus.RUNNING,
117 │             prompt_key=EXTRACTION_PROMPT_KEY,
118 │             requested_llm_provider=run.llm_provider,
119 │             requested_llm_model=run.llm_model,
120 │         )
121 │         self.extraction_execution_repository.add(execution)
122 │         run_marked_running = False
123 │ 
124 │         try:
125 │             segments = self.segment_repository.list_by_source_unit(source_unit.source_unit_id)
126 │             execution.segment_count = len(segments)
127 │             node_types = self.schema_repository.list_node_types(run.schema_version_id)
128 │             relation_types = self.schema_repository.list_relation_types(run.schema_version_id)
129 │             if not segments:
130 │                 raise RuleViolationError(
131 │                     "Segments must be generated before candidate extraction can run."
132 │                 )
133 │ 
134 │             if not payload.dry_run:
135 │                 self._ensure_run_has_no_existing_candidates(run_id)
136 │ 
137 │             self._mark_run_running(run=run, source_unit=source_unit)
138 │             run_marked_running = True
139 │ 
140 │             llm_provider = self._require_llm_provider(run.llm_provider)
141 │             execution.provider_name = llm_provider.provider_name
142 │             resolved_llm_model = self._resolve_llm_model(run.llm_model)
143 │             execution.resolved_llm_model = resolved_llm_model
144 │             prompt_definition = self._require_prompt_definition()
145 │             execution.prompt_version = prompt_definition.version
146 │             execution.schema_name = prompt_definition.schema_name
147 │             node_type_registry = self._build_node_type_registry(node_types)
148 │             relation_type_registry = self._build_relation_type_registry(relation_types)
149 │             prompt_payload = self._build_prompt_payload(
150 │                 run=run,
151 │                 source_unit=source_unit,
152 │                 segments=segments,
153 │                 node_types=node_types,
154 │                 relation_types=relation_types,
155 │             )
156 │             raw_output = llm_provider.generate_structured(
157 │                 prompt=prompt_definition.prompt_text,
158 │                 schema_name=prompt_definition.schema_name,
159 │                 payload=prompt_payload,
160 │                 model=resolved_llm_model,
161 │             )
162 │             suggested_nodes, suggested_relations = self._normalize_output(
163 │                 raw_output,
164 │                 source_unit_id=source_unit.source_unit_id,
165 │                 node_type_registry=node_type_registry,
166 │                 relation_type_registry=relation_type_registry,
167 │             )
168 │             execution.suggested_node_count = len(suggested_nodes)
169 │             execution.suggested_relation_count = len(suggested_relations)
170 │ 
171 │             created_candidate_node_ids: list[str] = []
172 │             created_candidate_relation_ids: list[str] = []
173 │             if not payload.dry_run:
174 │                 node_ref_map = {}
175 │                 for node_suggestion in suggested_nodes:
176 │                     candidate_node = CandidateNode(
177 │                         candidate_node_id=str(uuid4()),
178 │                         run_id=run.run_id,
179 │                         node_type=node_suggestion.node_type,
180 │                         properties=node_suggestion.properties,
181 │                         merge_key_payload=node_suggestion.merge_key_payload,
182 │                         confidence=node_suggestion.confidence,
183 │                         evidence_refs=node_suggestion.evidence_refs,
184 │                     )
185 │                     self.candidate_node_repository.add(candidate_node)
186 │                     node_ref_map[node_suggestion.ref] = candidate_node.candidate_node_id
187 │                     created_candidate_node_ids.append(candidate_node.candidate_node_id)
188 │ 
189 │                 for relation_suggestion in suggested_relations:
190 │                     candidate_relation = CandidateRelation(
191 │                         candidate_relation_id=str(uuid4()),
192 │                         run_id=run.run_id,
193 │                         relation_type=relation_suggestion.relation_type,
194 │                         from_candidate_ref=node_ref_map[relation_suggestion.from_ref],
195 │                         to_candidate_ref=node_ref_map[relation_suggestion.to_ref],
196 │                         properties=relation_suggestion.properties,
197 │                         confidence=relation_suggestion.confidence,
198 │                         evidence_refs=relation_suggestion.evidence_refs,
199 │                     )
200 │                     self.candidate_relation_repository.add(candidate_relation)
201 │                     created_candidate_relation_ids.append(
202 │                         candidate_relation.candidate_relation_id
203 │                     )
204 │ 
205 │             execution.created_candidate_node_count = len(created_candidate_node_ids)
206 │             execution.created_candidate_relation_count = len(created_candidate_relation_ids)
207 │             self._mark_execution_succeeded(execution)
208 │ 
209 │             return ExtractionExecutionReport(
210 │                 execution_id=execution.execution_id,
211 │                 run_id=run.run_id,
212 │                 dry_run=payload.dry_run,
213 │                 prompt_version=prompt_definition.version,
214 │                 schema_name=prompt_definition.schema_name,
215 │                 provider_name=llm_provider.provider_name,
216 │                 requested_llm_provider=run.llm_provider,
217 │                 requested_llm_model=run.llm_model,
218 │                 resolved_llm_model=resolved_llm_model,
219 │                 segment_count=len(segments),
220 │                 suggested_nodes=suggested_nodes,
221 │                 suggested_relations=suggested_relations,
222 │                 created_candidate_node_ids=created_candidate_node_ids,
223 │                 created_candidate_relation_ids=created_candidate_relation_ids,
224 │                 started_at=execution.started_at,
225 │                 completed_at=execution.completed_at or execution.started_at,
226 │             )
227 │         except Exception as exc:
228 │             self._mark_execution_failed(execution, error_message=str(exc))
229 │             if run_marked_running:
230 │                 self._mark_run_failed(run=run, source_unit=source_unit)
231 │             raise
232 │ 
233 │     def list_executions(self, run_id: str) -> list[ExtractionExecution]:
234 │         self._require_run(run_id)
235 │         return self.extraction_execution_repository.list_by_run(run_id)
236 │ 
237 │     def _build_prompt_payload(
238 │         self,
239 │         *,
240 │         run: ProcessingRun,
241 │         source_unit: SourceUnit,
242 │         segments: list[Segment],
243 │         node_types: list[NodeTypeDefinition],
244 │         relation_types: list[RelationTypeDefinition],
245 │     ) -> dict[str, Any]:
246 │         return {
247 │             "run": {
248 │                 "run_id": run.run_id,
249 │                 "schema_version_id": run.schema_version_id,
250 │                 "pipeline_version": run.pipeline_version,
251 │             },
252 │             "source_unit": {
253 │                 "source_unit_id": source_unit.source_unit_id,
254 │                 "source_type": source_unit.source_type,
255 │                 "title": source_unit.title,
256 │                 "sequence_no": source_unit.sequence_no,
257 │             },
258 │             "schema": {
259 │                 "node_types": [
260 │                     {
261 │                         "name": node_type.name,
262 │                         "description": node_type.description,
263 │                         "merge_keys": node_type.merge_keys,
264 │                         "confidence_threshold": node_type.confidence_threshold,
265 │                         "aliases": node_type.aliases,
266 │                         "extraction_hints": node_type.extraction_hints,
267 │                         "properties": [
268 │                             {
269 │                                 "name": property_definition.name,
270 │                                 "data_type": property_definition.data_type,
271 │                                 "required": property_definition.required,
272 │                                 "description": property_definition.description,
273 │                                 "default_value": property_definition.default_value,
274 │                                 "enum_values": property_definition.enum_values,
275 │                             }
276 │                             for property_definition in node_type.properties
277 │                         ],
278 │                     }
279 │                     for node_type in node_types
280 │                 ],
281 │                 "relation_types": [
282 │                     {
283 │                         "name": relation_type.name,
284 │                         "from_type": relation_type.from_type,
285 │                         "to_type": relation_type.to_type,
286 │                         "description": relation_type.description,
287 │                         "aliases": relation_type.aliases,
288 │                         "extraction_hints": relation_type.extraction_hints,
289 │                         "required_properties": relation_type.required_properties,
290 │                         "confidence_threshold": relation_type.confidence_threshold,
291 │                         "properties": [
292 │                             {
293 │                                 "name": property_definition.name,
294 │                                 "data_type": property_definition.data_type,
295 │                                 "required": property_definition.required,
296 │                                 "description": property_definition.description,
297 │                                 "default_value": property_definition.default_value,
298 │                                 "enum_values": property_definition.enum_values,
299 │                             }
300 │                             for property_definition in relation_type.properties
301 │                         ],
302 │                     }
303 │                     for relation_type in relation_types
304 │                 ],
305 │             },
306 │             "segments": [
307 │                 {
308 │                     "segment_id": segment.segment_id,
309 │                     "segment_order": segment.segment_order,
310 │                     "text": segment.text,
311 │                 }
312 │                 for segment in segments
313 │             ],
314 │         }
315 │ 
316 │     def _normalize_output(
317 │         self,
318 │         raw_output: dict[str, Any],
319 │         *,
320 │         source_unit_id: str,
321 │         node_type_registry: dict[str, NodeTypeDefinition],
322 │         relation_type_registry: dict[str, RelationTypeDefinition],
323 │     ) -> tuple[list[SuggestedNode], list[SuggestedRelation]]:
324 │         try:
325 │             parsed = StructuredExtractionContract.model_validate(raw_output)
326 │         except ValidationError as exc:
327 │             raise RuleViolationError(
328 │                 "Structured extraction output did not match the configured "
329 │                 "extraction prompt schema."
330 │             ) from exc
331 │ 
332 │         evidence_segment_ids = {
333 │             segment.segment_id
334 │             for segment in self.segment_repository.list_by_source_unit(source_unit_id)
335 │         }
336 │         node_ref_set: set[str] = set()
337 │         node_types_by_ref: dict[str, NodeTypeDefinition] = {}
338 │         suggested_nodes: list[SuggestedNode] = []
339 │         for node_contract in parsed.nodes:
340 │             if node_contract.ref in node_ref_set:
341 │                 raise RuleViolationError(
342 │                     f"Structured extraction returned duplicate node ref '{node_contract.ref}'."
343 │                 )
344 │             resolved_node_type = self._resolve_node_type(
345 │                 node_contract.node_type,
346 │                 node_type_registry=node_type_registry,
347 │             )
348 │             node_ref_set.add(node_contract.ref)
349 │             node_types_by_ref[node_contract.ref] = resolved_node_type
350 │             evidence_refs = [
351 │                 self._build_evidence_ref(
352 │                     evidence_ref,
353 │                     valid_segment_ids=evidence_segment_ids,
354 │                 )
355 │                 for evidence_ref in node_contract.evidence_refs
356 │             ]
357 │             suggested_nodes.append(
358 │                 SuggestedNode(
359 │                     ref=node_contract.ref,
360 │                     node_type=resolved_node_type.name,
361 │                     properties=node_contract.properties,
362 │                     merge_key_payload=derive_merge_key_payload(
363 │                         node_type=resolved_node_type,
364 │                         properties=node_contract.properties,
365 │                         provided_merge_key_payload=node_contract.merge_key_payload,
366 │                     ),
367 │                     confidence=node_contract.confidence,
368 │                     evidence_refs=evidence_refs,
369 │                 )
370 │             )
371 │ 
372 │         suggested_relations: list[SuggestedRelation] = []
373 │         for relation_contract in parsed.relations:
374 │             if (
375 │                 relation_contract.from_ref not in node_ref_set
376 │                 or relation_contract.to_ref not in node_ref_set
377 │             ):
378 │                 raise RuleViolationError(
379 │                     "Structured extraction returned a relation that references "
380 │                     "unknown node refs."
381 │                 )
382 │             resolved_relation_type = self._resolve_relation_type(
383 │                 relation_contract.relation_type,
384 │                 relation_type_registry=relation_type_registry,
385 │             )
386 │             from_node_type = node_types_by_ref[relation_contract.from_ref]
387 │             to_node_type = node_types_by_ref[relation_contract.to_ref]
388 │             if from_node_type.name.casefold() != resolved_relation_type.from_type.casefold():
389 │                 raise RuleViolationError(
390 │                     "Structured extraction returned a relation whose from_ref does not match "
391 │                     f"relation type '{resolved_relation_type.name}' from_type "
392 │                     f"'{resolved_relation_type.from_type}'."
393 │                 )
394 │             if to_node_type.name.casefold() != resolved_relation_type.to_type.casefold():
395 │                 raise RuleViolationError(
396 │                     "Structured extraction returned a relation whose to_ref does not match "
397 │                     f"relation type '{resolved_relation_type.name}' to_type "
398 │                     f"'{resolved_relation_type.to_type}'."
399 │                 )
400 │             evidence_refs = [
401 │                 self._build_evidence_ref(
402 │                     evidence_ref,
403 │                     valid_segment_ids=evidence_segment_ids,
404 │                 )
405 │                 for evidence_ref in relation_contract.evidence_refs
406 │             ]
407 │             suggested_relations.append(
408 │                 SuggestedRelation(
409 │                     relation_type=resolved_relation_type.name,
410 │                     from_ref=relation_contract.from_ref,
411 │                     to_ref=relation_contract.to_ref,
412 │                     properties=relation_contract.properties,
413 │                     confidence=relation_contract.confidence,
414 │                     evidence_refs=evidence_refs,
415 │                 )
416 │             )
417 │ 
418 │         return suggested_nodes, suggested_relations
419 │ 
420 │     def _build_evidence_ref(
421 │         self,
422 │         evidence_ref: ExtractionEvidenceContract,
423 │         *,
424 │         valid_segment_ids: set[str],
425 │     ) -> EvidenceRef:
426 │         if evidence_ref.segment_id not in valid_segment_ids:
427 │             raise RuleViolationError(
428 │                 f"Evidence segment '{evidence_ref.segment_id}' does not belong to the run source."
429 │             )
430 │         return EvidenceRef(
431 │             segment_id=evidence_ref.segment_id,
432 │             quote=evidence_ref.quote,
433 │             start_offset=evidence_ref.start_offset,
434 │             end_offset=evidence_ref.end_offset,
435 │         )
436 │ 
437 │     def _require_llm_provider(self, requested_provider_name: str | None) -> LLMProvider:
438 │         resolved_provider_name = self._normalize_optional(requested_provider_name)
439 │         if resolved_provider_name is None:
440 │             resolved_provider_name = self._normalize_optional(self.default_llm_provider)
441 │         if resolved_provider_name is None:
442 │             raise RuleViolationError(
443 │                 "No LLM provider is configured for candidate extraction."
444 │             )
445 │ 
446 │         provider = self.provider_registry.get(resolved_provider_name)
447 │         if provider is None:
448 │             raise RuleViolationError(
449 │                 f"LLM provider '{resolved_provider_name}' is not configured "
450 │                 "for candidate extraction."
451 │             )
452 │         return provider
453 │ 
454 │     def _resolve_llm_model(self, requested_model: str | None) -> str | None:
455 │         return self._normalize_optional(requested_model) or self._normalize_optional(
456 │             self.default_llm_model
457 │         )
458 │ 
459 │     def _require_prompt_definition(self) -> StructuredPromptDefinition:
460 │         configured_version = self._normalize_optional(self.default_extraction_prompt_version)
461 │         if configured_version is None:
462 │             raise RuleViolationError(
463 │                 "No extraction prompt version is configured for candidate extraction."
464 │             )
465 │ 
466 │         prompt_definition = self.prompt_catalog.get(
467 │             prompt_key=EXTRACTION_PROMPT_KEY,
468 │             version=configured_version,
469 │         )
470 │         if prompt_definition is None:
471 │             raise RuleViolationError(
472 │                 f"Extraction prompt version '{configured_version}' is not registered."
473 │             )
474 │         return prompt_definition
475 │ 
476 │     def _build_node_type_registry(
477 │         self,
478 │         node_types: list[NodeTypeDefinition],
479 │     ) -> dict[str, NodeTypeDefinition]:
480 │         registry: dict[str, NodeTypeDefinition] = {}
481 │         for node_type in node_types:
482 │             self._register_type_lookup(
483 │                 registry=registry,
484 │                 kind="node type",
485 │                 lookup_value=node_type.name,
486 │                 resolved_name=node_type.name,
487 │                 definition=node_type,
488 │             )
489 │             for alias in node_type.aliases:
490 │                 self._register_type_lookup(
491 │                     registry=registry,
492 │                     kind="node type",
493 │                     lookup_value=alias,
494 │                     resolved_name=node_type.name,
495 │                     definition=node_type,
496 │                 )
497 │         return registry
498 │ 
499 │     def _build_relation_type_registry(
500 │         self,
501 │         relation_types: list[RelationTypeDefinition],
502 │     ) -> dict[str, RelationTypeDefinition]:
503 │         registry: dict[str, RelationTypeDefinition] = {}
504 │         for relation_type in relation_types:
505 │             self._register_type_lookup(
506 │                 registry=registry,
507 │                 kind="relation type",
508 │                 lookup_value=relation_type.name,
509 │                 resolved_name=relation_type.name,
510 │                 definition=relation_type,
511 │             )
512 │             for alias in relation_type.aliases:
513 │                 self._register_type_lookup(
514 │                     registry=registry,
515 │                     kind="relation type",
516 │                     lookup_value=alias,
517 │                     resolved_name=relation_type.name,
518 │                     definition=relation_type,
519 │                 )
520 │         return registry
521 │ 
522 │     def _register_type_lookup(
523 │         self,
524 │         *,
525 │         registry: dict[str, SchemaTypeDefinition],
526 │         kind: str,
527 │         lookup_value: str,
528 │         resolved_name: str,
529 │         definition: SchemaTypeDefinition,
530 │     ) -> None:
531 │         normalized_lookup = lookup_value.strip().casefold()
532 │         if normalized_lookup == "":
533 │             return
534 │ 
535 │         existing = registry.get(normalized_lookup)
536 │         if existing is not None and existing.name != resolved_name:
537 │             raise RuleViolationError(
538 │                 f"Schema contains ambiguous {kind} lookup '{lookup_value.strip()}'."
539 │             )
540 │         registry[normalized_lookup] = definition
541 │ 
542 │     def _resolve_node_type(
543 │         self,
544 │         requested_type: str,
545 │         *,
546 │         node_type_registry: dict[str, NodeTypeDefinition],
547 │     ) -> NodeTypeDefinition:
548 │         normalized_requested_type = requested_type.strip().casefold()
549 │         node_type = node_type_registry.get(normalized_requested_type)
550 │         if node_type is None:
551 │             raise RuleViolationError(
552 │                 f"Structured extraction returned undefined node type '{requested_type.strip()}'."
553 │             )
554 │         return node_type
555 │ 
556 │     def _resolve_relation_type(
557 │         self,
558 │         requested_type: str,
559 │         *,
560 │         relation_type_registry: dict[str, RelationTypeDefinition],
561 │     ) -> RelationTypeDefinition:
562 │         normalized_requested_type = requested_type.strip().casefold()
563 │         relation_type = relation_type_registry.get(normalized_requested_type)
564 │         if relation_type is None:
565 │             raise RuleViolationError(
566 │                 "Structured extraction returned undefined relation type "
567 │                 f"'{requested_type.strip()}'."
568 │             )
569 │         return relation_type
570 │ 
571 │     def _normalize_optional(self, value: str | None) -> str | None:
572 │         if value is None:
573 │             return None
574 │         normalized_value = value.strip()
575 │         if normalized_value == "":
576 │             return None
577 │         return normalized_value
578 │ 
579 │     def _mark_execution_succeeded(self, execution: ExtractionExecution) -> None:
580 │         execution.status = ExtractionExecutionStatus.SUCCEEDED
581 │         execution.completed_at = datetime.now(UTC)
582 │         self.extraction_execution_repository.save(execution)
583 │ 
584 │     def _mark_execution_failed(
585 │         self,
586 │         execution: ExtractionExecution,
587 │         *,
588 │         error_message: str,
589 │     ) -> None:
590 │         execution.status = ExtractionExecutionStatus.FAILED
591 │         execution.error_message = error_message
592 │         execution.completed_at = datetime.now(UTC)
593 │         self.extraction_execution_repository.save(execution)
594 │ 
595 │     def _ensure_run_has_no_existing_candidates(self, run_id: str) -> None:
596 │         if self.candidate_node_repository.list_by_run(run_id):
597 │             raise ConflictError(
598 │                 f"Run '{run_id}' already has candidate nodes. Extraction cannot append yet."
599 │             )
600 │         if self.candidate_relation_repository.list_by_run(run_id):
601 │             raise ConflictError(
602 │                 f"Run '{run_id}' already has candidate relations. Extraction cannot append yet."
603 │             )
604 │ 
605 │     def _require_run(self, run_id: str) -> ProcessingRun:
606 │         run = self.processing_run_repository.get(run_id)
607 │         if run is None:
608 │             raise NotFoundError(f"Run '{run_id}' was not found.")
609 │         return run
610 │ 
611 │     def _ensure_run_is_mutable(self, run: ProcessingRun) -> None:
612 │         if run.status == RunStatus.COMPLETED:
613 │             raise RuleViolationError(
614 │                 f"Processing run '{run.run_id}' is already completed and cannot be changed."
615 │             )
616 │ 
617 │     def _mark_run_running(self, *, run: ProcessingRun, source_unit: SourceUnit) -> None:
618 │         reserve_source_for_run(source_unit)
619 │         mark_run_started(run)
620 │         self.source_unit_repository.save(source_unit)
621 │         self.processing_run_repository.save(run)
622 │ 
623 │     def _mark_run_failed(self, *, run: ProcessingRun, source_unit: SourceUnit) -> None:
624 │         mark_run_failed(run, source_unit)
625 │         self.processing_run_repository.save(run)
626 │         self.source_unit_repository.save(source_unit)
627 │ 
628 │     def _require_source_unit(self, source_unit_id: str) -> SourceUnit:
629 │         source_unit = self.source_unit_repository.get(source_unit_id)
630 │         if source_unit is None:
631 │             raise NotFoundError(f"Source unit '{source_unit_id}' was not found.")
632 │         return source_unit
```

## FILE: backend/src/app/application/use_cases/pipeline_management.py
```python
  1 │ from collections.abc import Sequence
  2 │ from dataclasses import dataclass
  3 │ from re import split
  4 │ from uuid import uuid4
  5 │ 
  6 │ from app.application.dto.contracts import (
  7 │     CandidateNodeInput,
  8 │     CandidateRelationInput,
  9 │     EvidenceRefInput,
 10 │     SegmentGenerationInput,
 11 │ )
 12 │ from app.application.errors import NotFoundError, RuleViolationError
 13 │ from app.application.ports.repositories import (
 14 │     CandidateNodeRepository,
 15 │     CandidateRelationRepository,
 16 │     CanonicalGraphRepository,
 17 │     ProcessingRunRepository,
 18 │     ReviewItemRepository,
 19 │     SchemaRepository,
 20 │     SegmentRepository,
 21 │     SourceUnitRepository,
 22 │     ValidationResultRepository,
 23 │ )
 24 │ from app.domain.extraction.entities import CandidateNode, CandidateRelation, EvidenceRef
 25 │ from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
 26 │ from app.domain.ingestion.lifecycle import mark_run_started, reserve_source_for_run
 27 │ from app.domain.review.entities import ReviewItem
 28 │ from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
 29 │ from app.domain.shared.enums import CandidateStatus, RunStatus
 30 │ from app.domain.shared.resolution import (
 31 │     build_candidate_node_resolution_key,
 32 │     build_candidate_relation_resolution_key,
 33 │     build_canonical_merge_key,
 34 │     candidate_node_identity_key,
 35 │     derive_merge_key_payload,
 36 │     is_missing_value,
 37 │ )
 38 │ from app.domain.validation.entities import ValidationResult
 39 │ 
 40 │ 
 41 │ @dataclass(slots=True)
 42 │ class RunValidationReport:
 43 │     run: ProcessingRun
 44 │     candidate_nodes: list[CandidateNode]
 45 │     candidate_relations: list[CandidateRelation]
 46 │     validation_results: list[ValidationResult]
 47 │ 
 48 │ 
 49 │ @dataclass(slots=True)
 50 │ class PipelineManagementService:
 51 │     source_unit_repository: SourceUnitRepository
 52 │     segment_repository: SegmentRepository
 53 │     processing_run_repository: ProcessingRunRepository
 54 │     schema_repository: SchemaRepository
 55 │     candidate_node_repository: CandidateNodeRepository
 56 │     candidate_relation_repository: CandidateRelationRepository
 57 │     validation_result_repository: ValidationResultRepository
 58 │     review_item_repository: ReviewItemRepository
 59 │     canonical_graph_repository: CanonicalGraphRepository
 60 │ 
 61 │     def generate_segments(self, payload: SegmentGenerationInput) -> list[Segment]:
 62 │         source_unit = self._require_source_unit(payload.source_unit_id)
 63 │         strategy = payload.strategy.strip().casefold()
 64 │         if strategy != "paragraphs":
 65 │             raise RuleViolationError("Only the 'paragraphs' segmentation strategy is supported.")
 66 │ 
 67 │         segment_texts = self._split_into_segments(source_unit.raw_content)
 68 │         segments = [
 69 │             Segment(
 70 │                 segment_id=str(uuid4()),
 71 │                 source_unit_id=source_unit.source_unit_id,
 72 │                 segment_order=index,
 73 │                 text=text,
 74 │                 metadata_json={"strategy": strategy},
 75 │             )
 76 │             for index, text in enumerate(segment_texts, start=1)
 77 │         ]
 78 │         self.segment_repository.replace_for_source_unit(source_unit.source_unit_id, segments)
 79 │         return self.segment_repository.list_by_source_unit(source_unit.source_unit_id)
 80 │ 
 81 │     def list_segments(self, source_unit_id: str) -> list[Segment]:
 82 │         self._require_source_unit(source_unit_id)
 83 │         return self.segment_repository.list_by_source_unit(source_unit_id)
 84 │ 
 85 │     def add_candidate_node(self, run_id: str, payload: CandidateNodeInput) -> CandidateNode:
 86 │         run = self._require_run(run_id)
 87 │         self._ensure_run_is_mutable(run)
 88 │         self._mark_run_running(run)
 89 │         self._ensure_evidence_refs_belong_to_source_unit(
 90 │             source_unit_id=run.source_unit_id,
 91 │             evidence_refs=payload.evidence_refs,
 92 │         )
 93 │ 
 94 │         candidate_node = CandidateNode(
 95 │             candidate_node_id=str(uuid4()),
 96 │             run_id=run_id,
 97 │             node_type=payload.node_type.strip(),
 98 │             properties=payload.properties,
 99 │             merge_key_payload=payload.merge_key_payload,
100 │             confidence=payload.confidence,
101 │             evidence_refs=[self._build_evidence_ref(item) for item in payload.evidence_refs],
102 │         )
103 │         self.candidate_node_repository.add(candidate_node)
104 │         return candidate_node
105 │ 
106 │     def list_candidate_nodes(self, run_id: str) -> list[CandidateNode]:
107 │         self._require_run(run_id)
108 │         return self.candidate_node_repository.list_by_run(run_id)
109 │ 
110 │     def add_candidate_relation(
111 │         self,
112 │         run_id: str,
113 │         payload: CandidateRelationInput,
114 │     ) -> CandidateRelation:
115 │         run = self._require_run(run_id)
116 │         self._ensure_run_is_mutable(run)
117 │         self._mark_run_running(run)
118 │         self._ensure_evidence_refs_belong_to_source_unit(
119 │             source_unit_id=run.source_unit_id,
120 │             evidence_refs=payload.evidence_refs,
121 │         )
122 │         self._require_candidate_node_in_run(
123 │             candidate_node_id=payload.from_candidate_ref,
124 │             run_id=run_id,
125 │         )
126 │         self._require_candidate_node_in_run(
127 │             candidate_node_id=payload.to_candidate_ref,
128 │             run_id=run_id,
129 │         )
130 │ 
131 │         candidate_relation = CandidateRelation(
132 │             candidate_relation_id=str(uuid4()),
133 │             run_id=run_id,
134 │             relation_type=payload.relation_type.strip(),
135 │             from_candidate_ref=payload.from_candidate_ref,
136 │             to_candidate_ref=payload.to_candidate_ref,
137 │             properties=payload.properties,
138 │             confidence=payload.confidence,
139 │             evidence_refs=[self._build_evidence_ref(item) for item in payload.evidence_refs],
140 │         )
141 │         self.candidate_relation_repository.add(candidate_relation)
142 │         return candidate_relation
143 │ 
144 │     def list_candidate_relations(self, run_id: str) -> list[CandidateRelation]:
145 │         self._require_run(run_id)
146 │         return self.candidate_relation_repository.list_by_run(run_id)
147 │ 
148 │     def validate_run(self, run_id: str) -> RunValidationReport:
149 │         run = self._require_run(run_id)
150 │         self._ensure_run_is_mutable(run)
151 │         self._mark_run_running(run)
152 │         node_type_map = {
153 │             node_type.name.casefold(): node_type
154 │             for node_type in self.schema_repository.list_node_types(run.schema_version_id)
155 │         }
156 │         relation_type_map = {
157 │             relation_type.name.casefold(): relation_type
158 │             for relation_type in self.schema_repository.list_relation_types(run.schema_version_id)
159 │         }
160 │ 
161 │         candidate_nodes = self.candidate_node_repository.list_by_run(run_id)
162 │         candidate_relations = self.candidate_relation_repository.list_by_run(run_id)
163 │         candidate_node_map = {
164 │             candidate_node.candidate_node_id: candidate_node
165 │             for candidate_node in candidate_nodes
166 │         }
167 │ 
168 │         validation_results: list[ValidationResult] = []
169 │         for candidate_node in candidate_nodes:
170 │             validation_results.extend(
171 │                 self._validate_candidate_node(
172 │                     candidate_node=candidate_node,
173 │                     node_type_map=node_type_map,
174 │                 )
175 │             )
176 │             self.candidate_node_repository.save(candidate_node)
177 │ 
178 │         for candidate_relation in candidate_relations:
179 │             validation_results.extend(
180 │                 self._validate_candidate_relation(
181 │                     candidate_relation=candidate_relation,
182 │                     relation_type_map=relation_type_map,
183 │                     candidate_node_map=candidate_node_map,
184 │                 )
185 │             )
186 │         validation_results.extend(
187 │             self._apply_duplicate_resolution(
188 │                 candidate_nodes=candidate_nodes,
189 │                 candidate_relations=candidate_relations,
190 │                 candidate_node_map=candidate_node_map,
191 │             )
192 │         )
193 │         validation_results.extend(
194 │             self._annotate_canonical_matches(
195 │                 project_id=run.project_id,
196 │                 candidate_nodes=candidate_nodes,
197 │                 candidate_relations=candidate_relations,
198 │                 candidate_node_map=candidate_node_map,
199 │             )
200 │         )
201 │ 
202 │         for candidate_node in candidate_nodes:
203 │             self.candidate_node_repository.save(candidate_node)
204 │         for candidate_relation in candidate_relations:
205 │             self.candidate_relation_repository.save(candidate_relation)
206 │ 
207 │         self.validation_result_repository.replace_for_run(run_id, validation_results)
208 │         self.review_item_repository.replace_for_run(
209 │             run_id,
210 │             self._build_review_items(
211 │                 candidate_nodes=candidate_nodes,
212 │                 candidate_relations=candidate_relations,
213 │                 validation_results=validation_results,
214 │             ),
215 │         )
216 │         return RunValidationReport(
217 │             run=run,
218 │             candidate_nodes=self.candidate_node_repository.list_by_run(run_id),
219 │             candidate_relations=self.candidate_relation_repository.list_by_run(run_id),
220 │             validation_results=self.validation_result_repository.list_by_run(run_id),
221 │         )
222 │ 
223 │     def list_validation_results(self, run_id: str) -> list[ValidationResult]:
224 │         self._require_run(run_id)
225 │         return self.validation_result_repository.list_by_run(run_id)
226 │ 
227 │     def list_review_items(self, run_id: str) -> list[ReviewItem]:
228 │         self._require_run(run_id)
229 │         return self.review_item_repository.list_by_run(run_id)
230 │ 
231 │     def resolve_duplicates(self, run_id: str) -> RunValidationReport:
232 │         return self.validate_run(run_id)
233 │ 
234 │     def _validate_candidate_node(
235 │         self,
236 │         *,
237 │         candidate_node: CandidateNode,
238 │         node_type_map: dict[str, NodeTypeDefinition],
239 │     ) -> list[ValidationResult]:
240 │         results: list[ValidationResult] = []
241 │         node_type = node_type_map.get(candidate_node.node_type.casefold())
242 │         if node_type is None:
243 │             candidate_node.status = CandidateStatus.REJECTED
244 │             results.append(
245 │                 self._build_validation_result(
246 │                     run_id=candidate_node.run_id,
247 │                     candidate_ref=candidate_node.candidate_node_id,
248 │                     rule_code="node_type_exists",
249 │                     severity="error",
250 │                     result="failed",
251 │                     message=f"Node type '{candidate_node.node_type}' is not defined in schema.",
252 │                 )
253 │             )
254 │             return results
255 │ 
256 │         candidate_node.node_type = node_type.name
257 │         candidate_node.merge_key_payload = derive_merge_key_payload(
258 │             node_type=node_type,
259 │             properties=candidate_node.properties,
260 │             provided_merge_key_payload=candidate_node.merge_key_payload,
261 │         )
262 │         missing_required = [
263 │             property_definition.name
264 │             for property_definition in node_type.properties
265 │             if property_definition.required
266 │             and is_missing_value(candidate_node.properties.get(property_definition.name))
267 │         ]
268 │         missing_merge_keys = [
269 │             merge_key
270 │             for merge_key in node_type.merge_keys
271 │             if is_missing_value(candidate_node.merge_key_payload.get(merge_key))
272 │         ]
273 │ 
274 │         for property_name in missing_required:
275 │             results.append(
276 │                 self._build_validation_result(
277 │                     run_id=candidate_node.run_id,
278 │                     candidate_ref=candidate_node.candidate_node_id,
279 │                     rule_code="required_node_property",
280 │                     severity="error",
281 │                     result="failed",
282 │                     message=f"Missing required node property '{property_name}'.",
283 │                 )
284 │             )
285 │ 
286 │         for merge_key in missing_merge_keys:
287 │             results.append(
288 │                 self._build_validation_result(
289 │                     run_id=candidate_node.run_id,
290 │                     candidate_ref=candidate_node.candidate_node_id,
291 │                     rule_code="node_merge_key",
292 │                     severity="error",
293 │                     result="failed",
294 │                     message=f"Missing merge key '{merge_key}' for candidate node.",
295 │                 )
296 │             )
297 │ 
298 │         if results:
299 │             candidate_node.status = CandidateStatus.REJECTED
300 │             return results
301 │ 
302 │         if candidate_node.confidence < node_type.confidence_threshold:
303 │             candidate_node.status = CandidateStatus.REVIEW
304 │             results.append(
305 │                 self._build_validation_result(
306 │                     run_id=candidate_node.run_id,
307 │                     candidate_ref=candidate_node.candidate_node_id,
308 │                     rule_code="node_confidence_threshold",
309 │                     severity="warning",
310 │                     result="review",
311 │                     message=(
312 │                         "Candidate node confidence is below the baseline review threshold "
313 │                         f"({node_type.confidence_threshold:.2f})."
314 │                     ),
315 │                 )
316 │             )
317 │             return results
318 │ 
319 │         candidate_node.status = CandidateStatus.VALIDATED
320 │         results.append(
321 │             self._build_validation_result(
322 │                 run_id=candidate_node.run_id,
323 │                 candidate_ref=candidate_node.candidate_node_id,
324 │                 rule_code="candidate_node_valid",
325 │                 severity="info",
326 │                 result="passed",
327 │                 message="Candidate node passed validation.",
328 │             )
329 │         )
330 │         return results
331 │ 
332 │     def _validate_candidate_relation(
333 │         self,
334 │         *,
335 │         candidate_relation: CandidateRelation,
336 │         relation_type_map: dict[str, RelationTypeDefinition],
337 │         candidate_node_map: dict[str, CandidateNode],
338 │     ) -> list[ValidationResult]:
339 │         results: list[ValidationResult] = []
340 │         relation_type = relation_type_map.get(candidate_relation.relation_type.casefold())
341 │         if relation_type is None:
342 │             candidate_relation.status = CandidateStatus.REJECTED
343 │             results.append(
344 │                 self._build_validation_result(
345 │                     run_id=candidate_relation.run_id,
346 │                     candidate_ref=candidate_relation.candidate_relation_id,
347 │                     rule_code="relation_type_exists",
348 │                     severity="error",
349 │                     result="failed",
350 │                     message=(
351 │                         f"Relation type '{candidate_relation.relation_type}' "
352 │                         "is not defined in schema."
353 │                     ),
354 │                 )
355 │             )
356 │             return results
357 │ 
358 │         candidate_relation.relation_type = relation_type.name
359 │         from_candidate = candidate_node_map.get(candidate_relation.from_candidate_ref)
360 │         to_candidate = candidate_node_map.get(candidate_relation.to_candidate_ref)
361 │         if from_candidate is None or to_candidate is None:
362 │             candidate_relation.status = CandidateStatus.REJECTED
363 │             results.append(
364 │                 self._build_validation_result(
365 │                     run_id=candidate_relation.run_id,
366 │                     candidate_ref=candidate_relation.candidate_relation_id,
367 │                     rule_code="relation_candidate_refs",
368 │                     severity="error",
369 │                     result="failed",
370 │                     message="Relation references candidate nodes that do not exist in the run.",
371 │                 )
372 │             )
373 │             return results
374 │ 
375 │         if from_candidate.node_type.casefold() != relation_type.from_type.casefold():
376 │             results.append(
377 │                 self._build_validation_result(
378 │                     run_id=candidate_relation.run_id,
379 │                     candidate_ref=candidate_relation.candidate_relation_id,
380 │                     rule_code="relation_from_type",
381 │                     severity="error",
382 │                     result="failed",
383 │                     message=(
384 │                         f"Relation expects from_type '{relation_type.from_type}' but received "
385 │                         f"'{from_candidate.node_type}'."
386 │                     ),
387 │                 )
388 │             )
389 │ 
390 │         if to_candidate.node_type.casefold() != relation_type.to_type.casefold():
391 │             results.append(
392 │                 self._build_validation_result(
393 │                     run_id=candidate_relation.run_id,
394 │                     candidate_ref=candidate_relation.candidate_relation_id,
395 │                     rule_code="relation_to_type",
396 │                     severity="error",
397 │                     result="failed",
398 │                     message=(
399 │                         f"Relation expects to_type '{relation_type.to_type}' but received "
400 │                         f"'{to_candidate.node_type}'."
401 │                     ),
402 │                 )
403 │             )
404 │ 
405 │         required_properties = {
406 │             *relation_type.required_properties,
407 │             *[
408 │                 property_definition.name
409 │                 for property_definition in relation_type.properties
410 │                 if property_definition.required
411 │             ],
412 │         }
413 │         for property_name in sorted(required_properties):
414 │             if is_missing_value(candidate_relation.properties.get(property_name)):
415 │                 results.append(
416 │                     self._build_validation_result(
417 │                         run_id=candidate_relation.run_id,
418 │                         candidate_ref=candidate_relation.candidate_relation_id,
419 │                         rule_code="required_relation_property",
420 │                         severity="error",
421 │                         result="failed",
422 │                         message=f"Missing required relation property '{property_name}'.",
423 │                     )
424 │                 )
425 │ 
426 │         if any(result.severity == "error" for result in results):
427 │             candidate_relation.status = CandidateStatus.REJECTED
428 │             return results
429 │ 
430 │         if (
431 │             from_candidate.status == CandidateStatus.REJECTED
432 │             or to_candidate.status == CandidateStatus.REJECTED
433 │         ):
434 │             candidate_relation.status = CandidateStatus.REJECTED
435 │             results.append(
436 │                 self._build_validation_result(
437 │                     run_id=candidate_relation.run_id,
438 │                     candidate_ref=candidate_relation.candidate_relation_id,
439 │                     rule_code="relation_dependency_rejected",
440 │                     severity="error",
441 │                     result="failed",
442 │                     message="Relation depends on candidate nodes that failed validation.",
443 │                 )
444 │             )
445 │             return results
446 │ 
447 │         if (
448 │             from_candidate.status == CandidateStatus.REVIEW
449 │             or to_candidate.status == CandidateStatus.REVIEW
450 │             or candidate_relation.confidence < relation_type.confidence_threshold
451 │         ):
452 │             candidate_relation.status = CandidateStatus.REVIEW
453 │             if (
454 │                 from_candidate.status == CandidateStatus.REVIEW
455 │                 or to_candidate.status == CandidateStatus.REVIEW
456 │             ):
457 │                 results.append(
458 │                     self._build_validation_result(
459 │                         run_id=candidate_relation.run_id,
460 │                         candidate_ref=candidate_relation.candidate_relation_id,
461 │                         rule_code="relation_dependency_review",
462 │                         severity="warning",
463 │                         result="review",
464 │                         message="Relation depends on candidate nodes that require review.",
465 │                     )
466 │                 )
467 │             if candidate_relation.confidence < relation_type.confidence_threshold:
468 │                 results.append(
469 │                     self._build_validation_result(
470 │                         run_id=candidate_relation.run_id,
471 │                         candidate_ref=candidate_relation.candidate_relation_id,
472 │                         rule_code="relation_confidence_threshold",
473 │                         severity="warning",
474 │                         result="review",
475 │                         message=(
476 │                             "Relation confidence is below the schema threshold "
477 │                             f"({relation_type.confidence_threshold:.2f})."
478 │                         ),
479 │                     )
480 │                 )
481 │             return results
482 │ 
483 │         candidate_relation.status = CandidateStatus.VALIDATED
484 │         results.append(
485 │             self._build_validation_result(
486 │                 run_id=candidate_relation.run_id,
487 │                 candidate_ref=candidate_relation.candidate_relation_id,
488 │                 rule_code="candidate_relation_valid",
489 │                 severity="info",
490 │                 result="passed",
491 │                 message="Candidate relation passed validation.",
492 │             )
493 │         )
494 │         return results
495 │ 
496 │     def _require_source_unit(self, source_unit_id: str) -> SourceUnit:
497 │         source_unit = self.source_unit_repository.get(source_unit_id)
498 │         if source_unit is None:
499 │             raise NotFoundError(f"Source unit '{source_unit_id}' was not found.")
500 │         return source_unit
501 │ 
502 │     def _require_run(self, run_id: str) -> ProcessingRun:
503 │         run = self.processing_run_repository.get(run_id)
504 │         if run is None:
505 │             raise NotFoundError(f"Processing run '{run_id}' was not found.")
506 │         return run
507 │ 
508 │     def _ensure_run_is_mutable(self, run: ProcessingRun) -> None:
509 │         if run.status == RunStatus.COMPLETED:
510 │             raise RuleViolationError(
511 │                 f"Processing run '{run.run_id}' is already completed and cannot be changed."
512 │             )
513 │ 
514 │     def _mark_run_running(self, run: ProcessingRun) -> None:
515 │         source_unit = self._require_source_unit(run.source_unit_id)
516 │         reserve_source_for_run(source_unit)
517 │         mark_run_started(run)
518 │         self.source_unit_repository.save(source_unit)
519 │         self.processing_run_repository.save(run)
520 │ 
521 │     def _require_candidate_node_in_run(
522 │         self,
523 │         *,
524 │         candidate_node_id: str,
525 │         run_id: str,
526 │     ) -> CandidateNode:
527 │         candidate_node = self.candidate_node_repository.get(candidate_node_id)
528 │         if candidate_node is None or candidate_node.run_id != run_id:
529 │             raise NotFoundError(
530 │                 f"Candidate node '{candidate_node_id}' was not found in run '{run_id}'."
531 │             )
532 │         return candidate_node
533 │ 
534 │     def _ensure_evidence_refs_belong_to_source_unit(
535 │         self,
536 │         *,
537 │         source_unit_id: str,
538 │         evidence_refs: Sequence[EvidenceRefInput],
539 │     ) -> None:
540 │         segment_ids = {
541 │             segment.segment_id
542 │             for segment in self.segment_repository.list_by_source_unit(source_unit_id)
543 │         }
544 │         for evidence_ref in evidence_refs:
545 │             if evidence_ref.segment_id not in segment_ids:
546 │                 raise RuleViolationError(
547 │                     f"Evidence ref segment '{evidence_ref.segment_id}' "
548 │                     f"does not belong to source unit '{source_unit_id}'."
549 │                 )
550 │ 
551 │     def _build_evidence_ref(self, item: EvidenceRefInput) -> EvidenceRef:
552 │         return EvidenceRef(
553 │             segment_id=item.segment_id,
554 │             quote=item.quote,
555 │             start_offset=item.start_offset,
556 │             end_offset=item.end_offset,
557 │         )
558 │ 
559 │     def _apply_duplicate_resolution(
560 │         self,
561 │         *,
562 │         candidate_nodes: list[CandidateNode],
563 │         candidate_relations: list[CandidateRelation],
564 │         candidate_node_map: dict[str, CandidateNode],
565 │     ) -> list[ValidationResult]:
566 │         results: list[ValidationResult] = []
567 │         results.extend(self._flag_duplicate_candidate_nodes(candidate_nodes))
568 │         node_resolution_keys = {
569 │             candidate_node.candidate_node_id: candidate_node_identity_key(candidate_node)
570 │             for candidate_node in candidate_nodes
571 │             if candidate_node.status != CandidateStatus.REJECTED
572 │         }
573 │         results.extend(
574 │             self._refresh_relation_dependency_statuses(candidate_relations, candidate_node_map)
575 │         )
576 │         results.extend(
577 │             self._flag_duplicate_candidate_relations(
578 │                 candidate_relations,
579 │                 node_resolution_keys=node_resolution_keys,
580 │             )
581 │         )
582 │         return results
583 │ 
584 │     def _flag_duplicate_candidate_nodes(
585 │         self,
586 │         candidate_nodes: list[CandidateNode],
587 │     ) -> list[ValidationResult]:
588 │         groups: dict[str, list[CandidateNode]] = {}
589 │         for candidate_node in candidate_nodes:
590 │             if candidate_node.status == CandidateStatus.REJECTED:
591 │                 continue
592 │             if not candidate_node.merge_key_payload:
593 │                 continue
594 │             groups.setdefault(
595 │                 build_candidate_node_resolution_key(candidate_node),
596 │                 [],
597 │             ).append(candidate_node)
598 │ 
599 │         results: list[ValidationResult] = []
600 │         for group in groups.values():
601 │             if len(group) < 2:
602 │                 continue
603 │             sorted_group = sorted(
604 │                 group,
605 │                 key=lambda item: (-item.confidence, item.candidate_node_id),
606 │             )
607 │             primary = sorted_group[0]
608 │             for duplicate in sorted_group[1:]:
609 │                 duplicate.status = CandidateStatus.REVIEW
610 │                 results.append(
611 │                     self._build_validation_result(
612 │                         run_id=duplicate.run_id,
613 │                         candidate_ref=duplicate.candidate_node_id,
614 │                         rule_code="potential_duplicate_node",
615 │                         severity="warning",
616 │                         result="review",
617 │                         message=(
618 │                             f"Candidate node may duplicate '{primary.candidate_node_id}' "
619 │                             "based on merge key payload."
620 │                         ),
621 │                     )
622 │                 )
623 │         return results
624 │ 
625 │     def _refresh_relation_dependency_statuses(
626 │         self,
627 │         candidate_relations: list[CandidateRelation],
628 │         candidate_node_map: dict[str, CandidateNode],
629 │     ) -> list[ValidationResult]:
630 │         results: list[ValidationResult] = []
631 │         for candidate_relation in candidate_relations:
632 │             if candidate_relation.status == CandidateStatus.REJECTED:
633 │                 continue
634 │             from_candidate = candidate_node_map.get(candidate_relation.from_candidate_ref)
635 │             to_candidate = candidate_node_map.get(candidate_relation.to_candidate_ref)
636 │             if from_candidate is None or to_candidate is None:
637 │                 continue
638 │             if (
639 │                 from_candidate.status == CandidateStatus.REJECTED
640 │                 or to_candidate.status == CandidateStatus.REJECTED
641 │             ):
642 │                 candidate_relation.status = CandidateStatus.REJECTED
643 │                 results.append(
644 │                     self._build_validation_result(
645 │                         run_id=candidate_relation.run_id,
646 │                         candidate_ref=candidate_relation.candidate_relation_id,
647 │                         rule_code="relation_dependency_rejected",
648 │                         severity="error",
649 │                         result="failed",
650 │                         message="Relation depends on candidate nodes that failed validation.",
651 │                     )
652 │                 )
653 │                 continue
654 │             if (
655 │                 from_candidate.status == CandidateStatus.REVIEW
656 │                 or to_candidate.status == CandidateStatus.REVIEW
657 │             ):
658 │                 candidate_relation.status = CandidateStatus.REVIEW
659 │                 results.append(
660 │                     self._build_validation_result(
661 │                         run_id=candidate_relation.run_id,
662 │                         candidate_ref=candidate_relation.candidate_relation_id,
663 │                         rule_code="relation_dependency_review",
664 │                         severity="warning",
665 │                         result="review",
666 │                         message="Relation depends on candidate nodes that require review.",
667 │                     )
668 │                 )
669 │         return results
670 │ 
671 │     def _flag_duplicate_candidate_relations(
672 │         self,
673 │         candidate_relations: list[CandidateRelation],
674 │         *,
675 │         node_resolution_keys: dict[str, str],
676 │     ) -> list[ValidationResult]:
677 │         groups: dict[str, list[CandidateRelation]] = {}
678 │         for candidate_relation in candidate_relations:
679 │             if candidate_relation.status == CandidateStatus.REJECTED:
680 │                 continue
681 │             groups.setdefault(
682 │                 build_candidate_relation_resolution_key(
683 │                     candidate_relation,
684 │                     node_resolution_keys_by_candidate_id=node_resolution_keys,
685 │                 ),
686 │                 [],
687 │             ).append(candidate_relation)
688 │ 
689 │         results: list[ValidationResult] = []
690 │         for group in groups.values():
691 │             if len(group) < 2:
692 │                 continue
693 │             sorted_group = sorted(
694 │                 group,
695 │                 key=lambda item: (-item.confidence, item.candidate_relation_id),
696 │             )
697 │             primary = sorted_group[0]
698 │             for duplicate in sorted_group[1:]:
699 │                 duplicate.status = CandidateStatus.REVIEW
700 │                 results.append(
701 │                     self._build_validation_result(
702 │                         run_id=duplicate.run_id,
703 │                         candidate_ref=duplicate.candidate_relation_id,
704 │                         rule_code="potential_duplicate_relation",
705 │                         severity="warning",
706 │                         result="review",
707 │                         message=(
708 │                             f"Candidate relation may duplicate '{primary.candidate_relation_id}'."
709 │                         ),
710 │                     )
711 │                 )
712 │         return results
713 │ 
714 │     def _build_review_items(
715 │         self,
716 │         *,
717 │         candidate_nodes: list[CandidateNode],
718 │         candidate_relations: list[CandidateRelation],
719 │         validation_results: list[ValidationResult],
720 │     ) -> list[ReviewItem]:
721 │         all_messages_by_candidate: dict[str, list[str]] = {}
722 │         review_messages_by_candidate: dict[str, list[str]] = {}
723 │         review_reasons_by_candidate: dict[str, str] = {}
724 │         for result in validation_results:
725 │             all_messages_by_candidate.setdefault(result.candidate_ref, []).append(result.message)
726 │             if result.result != "review":
727 │                 continue
728 │             review_messages_by_candidate.setdefault(result.candidate_ref, []).append(result.message)
729 │             review_reasons_by_candidate.setdefault(result.candidate_ref, result.rule_code)
730 │ 
731 │         review_items: list[ReviewItem] = []
732 │         for candidate_node in candidate_nodes:
733 │             if candidate_node.status != CandidateStatus.REVIEW:
734 │                 continue
735 │             review_items.append(
736 │                 ReviewItem(
737 │                     review_item_id=str(uuid4()),
738 │                     run_id=candidate_node.run_id,
739 │                     item_type="candidate_node",
740 │                     item_ref=candidate_node.candidate_node_id,
741 │                     reason_code=review_reasons_by_candidate.get(
742 │                         candidate_node.candidate_node_id,
743 │                         "candidate_review",
744 │                     ),
745 │                     payload_json={
746 │                         "node_type": candidate_node.node_type,
747 │                         "confidence": candidate_node.confidence,
748 │                         "messages": all_messages_by_candidate.get(
749 │                             candidate_node.candidate_node_id,
750 │                             [],
751 │                         ),
752 │                     },
753 │                 )
754 │             )
755 │ 
756 │         for candidate_relation in candidate_relations:
757 │             if candidate_relation.status != CandidateStatus.REVIEW:
758 │                 continue
759 │             review_items.append(
760 │                 ReviewItem(
761 │                     review_item_id=str(uuid4()),
762 │                     run_id=candidate_relation.run_id,
763 │                     item_type="candidate_relation",
764 │                     item_ref=candidate_relation.candidate_relation_id,
765 │                     reason_code=review_reasons_by_candidate.get(
766 │                         candidate_relation.candidate_relation_id,
767 │                         "candidate_review",
768 │                     ),
769 │                     payload_json={
770 │                         "relation_type": candidate_relation.relation_type,
771 │                         "confidence": candidate_relation.confidence,
772 │                         "messages": all_messages_by_candidate.get(
773 │                             candidate_relation.candidate_relation_id,
774 │                             [],
775 │                         ),
776 │                     },
777 │                 )
778 │             )
779 │         return review_items
780 │ 
781 │     def _annotate_canonical_matches(
782 │         self,
783 │         *,
784 │         project_id: str,
785 │         candidate_nodes: list[CandidateNode],
786 │         candidate_relations: list[CandidateRelation],
787 │         candidate_node_map: dict[str, CandidateNode],
788 │     ) -> list[ValidationResult]:
789 │         results: list[ValidationResult] = []
790 │         canonical_merge_keys_by_candidate_id: dict[str, str] = {}
791 │ 
792 │         for candidate_node in candidate_nodes:
793 │             if candidate_node.status == CandidateStatus.REJECTED:
794 │                 continue
795 │             if not candidate_node.merge_key_payload:
796 │                 continue
797 │ 
798 │             canonical_merge_key = build_canonical_merge_key(
799 │                 merge_key_payload=candidate_node.merge_key_payload,
800 │                 fallback_payload={"candidate_node_id": candidate_node.candidate_node_id},
801 │             )
802 │             canonical_merge_keys_by_candidate_id[candidate_node.candidate_node_id] = (
803 │                 canonical_merge_key
804 │             )
805 │             if (
806 │                 self.canonical_graph_repository.get_node_detail(
807 │                     project_id,
808 │                     node_type=candidate_node.node_type,
809 │                     merge_key=canonical_merge_key,
810 │                 )
811 │                 is None
812 │             ):
813 │                 continue
814 │ 
815 │             results.append(
816 │                 self._build_validation_result(
817 │                     run_id=candidate_node.run_id,
818 │                     candidate_ref=candidate_node.candidate_node_id,
819 │                     rule_code="canonical_node_match",
820 │                     severity="info",
821 │                     result="passed",
822 │                     message="Candidate node resolves to an existing canonical node.",
823 │                 )
824 │             )
825 │ 
826 │         for candidate_relation in candidate_relations:
827 │             if candidate_relation.status == CandidateStatus.REJECTED:
828 │                 continue
829 │ 
830 │             from_candidate = candidate_node_map.get(candidate_relation.from_candidate_ref)
831 │             to_candidate = candidate_node_map.get(candidate_relation.to_candidate_ref)
832 │             if from_candidate is None or to_candidate is None:
833 │                 continue
834 │ 
835 │             from_merge_key = canonical_merge_keys_by_candidate_id.get(
836 │                 from_candidate.candidate_node_id
837 │             )
838 │             to_merge_key = canonical_merge_keys_by_candidate_id.get(
839 │                 to_candidate.candidate_node_id
840 │             )
841 │             if from_merge_key is None or to_merge_key is None:
842 │                 continue
843 │ 
844 │             if (
845 │                 self.canonical_graph_repository.get_relation_detail(
846 │                     project_id,
847 │                     relation_type=candidate_relation.relation_type,
848 │                     from_node_type=from_candidate.node_type,
849 │                     from_merge_key=from_merge_key,
850 │                     to_node_type=to_candidate.node_type,
851 │                     to_merge_key=to_merge_key,
852 │                 )
853 │                 is None
854 │             ):
855 │                 continue
856 │ 
857 │             results.append(
858 │                 self._build_validation_result(
859 │                     run_id=candidate_relation.run_id,
860 │                     candidate_ref=candidate_relation.candidate_relation_id,
861 │                     rule_code="canonical_relation_match",
862 │                     severity="info",
863 │                     result="passed",
864 │                     message="Candidate relation resolves to an existing canonical relation.",
865 │                 )
866 │             )
867 │ 
868 │         return results
869 │ 
870 │     def _split_into_segments(self, raw_content: str) -> list[str]:
871 │         paragraph_chunks = [
872 │             item.strip() for item in split(r"\n\s*\n", raw_content) if item.strip()
873 │         ]
874 │         if len(paragraph_chunks) > 1:
875 │             return paragraph_chunks
876 │ 
877 │         line_chunks = [line.strip() for line in raw_content.splitlines() if line.strip()]
878 │         if line_chunks:
879 │             return line_chunks
880 │         return [raw_content.strip()]
881 │ 
882 │     def _build_validation_result(
883 │         self,
884 │         *,
885 │         run_id: str,
886 │         candidate_ref: str,
887 │         rule_code: str,
888 │         severity: str,
889 │         result: str,
890 │         message: str,
891 │     ) -> ValidationResult:
892 │         return ValidationResult(
893 │             validation_result_id=str(uuid4()),
894 │             run_id=run_id,
895 │             candidate_ref=candidate_ref,
896 │             rule_code=rule_code,
897 │             severity=severity,
898 │             result=result,
899 │             message=message,
900 │         )
```

## FILE: backend/src/app/application/use_cases/review_management.py
```python
  1 │ from copy import deepcopy
  2 │ from dataclasses import dataclass
  3 │ from uuid import uuid4
  4 │ 
  5 │ from app.application.dto.contracts import ReviewDecisionInput
  6 │ from app.application.errors import ConflictError, NotFoundError, RuleViolationError
  7 │ from app.application.ports.repositories import (
  8 │     CandidateNodeRepository,
  9 │     CandidateRelationRepository,
 10 │     ProcessingRunRepository,
 11 │     ReviewItemRepository,
 12 │     SchemaRepository,
 13 │ )
 14 │ from app.domain.extraction.entities import CandidateNode, CandidateRelation
 15 │ from app.domain.ingestion.entities import ProcessingRun
 16 │ from app.domain.review.entities import ReviewItem
 17 │ from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
 18 │ from app.domain.shared.enums import CandidateStatus, ReviewStatus
 19 │ from app.domain.shared.resolution import (
 20 │     build_candidate_node_resolution_key,
 21 │     build_candidate_relation_resolution_key,
 22 │     candidate_node_identity_key,
 23 │     derive_merge_key_payload,
 24 │     is_missing_value,
 25 │ )
 26 │ 
 27 │ 
 28 │ @dataclass(slots=True)
 29 │ class RelationEvaluation:
 30 │     status: CandidateStatus
 31 │     reason_code: str
 32 │     messages: list[str]
 33 │ 
 34 │ 
 35 │ @dataclass(slots=True)
 36 │ class ReviewManagementService:
 37 │     review_item_repository: ReviewItemRepository
 38 │     candidate_node_repository: CandidateNodeRepository
 39 │     candidate_relation_repository: CandidateRelationRepository
 40 │     processing_run_repository: ProcessingRunRepository
 41 │     schema_repository: SchemaRepository
 42 │ 
 43 │     def get_review_item(self, review_item_id: str) -> ReviewItem:
 44 │         review_item = self.review_item_repository.get(review_item_id)
 45 │         if review_item is None:
 46 │             raise NotFoundError(f"Review item '{review_item_id}' was not found.")
 47 │         return review_item
 48 │ 
 49 │     def decide_review_item(self, review_item_id: str, payload: ReviewDecisionInput) -> ReviewItem:
 50 │         review_item = self.get_review_item(review_item_id)
 51 │         if review_item.status != ReviewStatus.OPEN:
 52 │             raise ConflictError(f"Review item '{review_item_id}' is already closed.")
 53 │ 
 54 │         action = payload.action.strip().casefold()
 55 │         if action not in {"accept", "reject", "edit"}:
 56 │             raise RuleViolationError("Review action must be one of: accept, reject, edit.")
 57 │ 
 58 │         affected_run_id = review_item.run_id
 59 │         if review_item.item_type == "candidate_node":
 60 │             node_candidate = deepcopy(self._require_candidate_node(review_item.item_ref))
 61 │             self._apply_node_decision(node_candidate, payload)
 62 │             if node_candidate.status != CandidateStatus.REJECTED:
 63 │                 self._validate_candidate_node_state(node_candidate)
 64 │                 self._ensure_node_relations_remain_compatible(node_candidate)
 65 │                 self._ensure_candidate_node_unique_within_run(node_candidate)
 66 │             self.candidate_node_repository.save(node_candidate)
 67 │         elif review_item.item_type == "candidate_relation":
 68 │             relation_candidate = deepcopy(self._require_candidate_relation(review_item.item_ref))
 69 │             self._apply_relation_decision(relation_candidate, payload)
 70 │             if relation_candidate.status != CandidateStatus.REJECTED:
 71 │                 self._validate_candidate_relation_state(relation_candidate)
 72 │                 self._ensure_candidate_relation_unique_within_run(relation_candidate)
 73 │             self.candidate_relation_repository.save(relation_candidate)
 74 │         else:
 75 │             raise RuleViolationError(f"Unsupported review item type '{review_item.item_type}'.")
 76 │ 
 77 │         if action == "accept":
 78 │             review_item.status = ReviewStatus.ACCEPTED
 79 │         elif action == "reject":
 80 │             review_item.status = ReviewStatus.REJECTED
 81 │         else:
 82 │             review_item.status = ReviewStatus.EDITED
 83 │         review_item.reviewer_note = payload.reviewer_note
 84 │         self.review_item_repository.save(review_item)
 85 │         self._refresh_relation_reviews_for_run(affected_run_id)
 86 │         return review_item
 87 │ 
 88 │     def _apply_node_decision(self, candidate: CandidateNode, payload: ReviewDecisionInput) -> None:
 89 │         action = payload.action.strip().casefold()
 90 │         if action == "reject":
 91 │             candidate.status = CandidateStatus.REJECTED
 92 │             return
 93 │ 
 94 │         if action == "edit":
 95 │             if payload.node_type is not None:
 96 │                 candidate.node_type = payload.node_type.strip()
 97 │             if payload.properties:
 98 │                 candidate.properties = payload.properties
 99 │             if payload.merge_key_payload:
100 │                 candidate.merge_key_payload = payload.merge_key_payload
101 │             if payload.confidence is not None:
102 │                 candidate.confidence = payload.confidence
103 │ 
104 │         candidate.status = CandidateStatus.VALIDATED
105 │ 
106 │     def _apply_relation_decision(
107 │         self,
108 │         candidate: CandidateRelation,
109 │         payload: ReviewDecisionInput,
110 │     ) -> None:
111 │         action = payload.action.strip().casefold()
112 │         if action == "reject":
113 │             candidate.status = CandidateStatus.REJECTED
114 │             return
115 │ 
116 │         if action == "edit":
117 │             if payload.relation_type is not None:
118 │                 candidate.relation_type = payload.relation_type.strip()
119 │             if payload.from_candidate_ref is not None:
120 │                 candidate.from_candidate_ref = payload.from_candidate_ref
121 │             if payload.to_candidate_ref is not None:
122 │                 candidate.to_candidate_ref = payload.to_candidate_ref
123 │             if payload.properties:
124 │                 candidate.properties = payload.properties
125 │             if payload.confidence is not None:
126 │                 candidate.confidence = payload.confidence
127 │ 
128 │         candidate.status = CandidateStatus.VALIDATED
129 │ 
130 │     def _require_candidate_node(self, candidate_node_id: str) -> CandidateNode:
131 │         candidate = self.candidate_node_repository.get(candidate_node_id)
132 │         if candidate is None:
133 │             raise NotFoundError(f"Candidate node '{candidate_node_id}' was not found.")
134 │         return candidate
135 │ 
136 │     def _require_candidate_relation(self, candidate_relation_id: str) -> CandidateRelation:
137 │         candidate = self.candidate_relation_repository.get(candidate_relation_id)
138 │         if candidate is None:
139 │             raise NotFoundError(f"Candidate relation '{candidate_relation_id}' was not found.")
140 │         return candidate
141 │ 
142 │     def _validate_candidate_node_state(self, candidate: CandidateNode) -> None:
143 │         run = self._require_run(candidate.run_id)
144 │         node_type_map = self._node_type_map(run.schema_version_id)
145 │         node_type = node_type_map.get(candidate.node_type.casefold())
146 │         if node_type is None:
147 │             raise RuleViolationError(
148 │                 f"Node type '{candidate.node_type}' is not defined in the active schema."
149 │             )
150 │ 
151 │         missing_required = [
152 │             property_definition.name
153 │             for property_definition in node_type.properties
154 │             if property_definition.required
155 │             and is_missing_value(candidate.properties.get(property_definition.name))
156 │         ]
157 │         if missing_required:
158 │             raise RuleViolationError(
159 │                 "Candidate node is missing required properties: "
160 │                 + ", ".join(sorted(missing_required))
161 │                 + "."
162 │             )
163 │ 
164 │         candidate.merge_key_payload = derive_merge_key_payload(
165 │             node_type=node_type,
166 │             properties=candidate.properties,
167 │             provided_merge_key_payload=candidate.merge_key_payload,
168 │         )
169 │         missing_merge_keys = [
170 │             merge_key
171 │             for merge_key in node_type.merge_keys
172 │             if is_missing_value(candidate.merge_key_payload.get(merge_key))
173 │         ]
174 │         if missing_merge_keys:
175 │             raise RuleViolationError(
176 │                 "Candidate node is missing merge keys: "
177 │                 + ", ".join(sorted(missing_merge_keys))
178 │                 + "."
179 │             )
180 │ 
181 │         candidate.node_type = node_type.name
182 │ 
183 │     def _ensure_node_relations_remain_compatible(self, candidate: CandidateNode) -> None:
184 │         run = self._require_run(candidate.run_id)
185 │         relation_type_map = self._relation_type_map(run.schema_version_id)
186 │         for relation in self.candidate_relation_repository.list_by_run(candidate.run_id):
187 │             if relation.status == CandidateStatus.REJECTED:
188 │                 continue
189 │             relation_type = relation_type_map.get(relation.relation_type.casefold())
190 │             if relation_type is None:
191 │                 continue
192 │             if (
193 │                 relation.from_candidate_ref == candidate.candidate_node_id
194 │                 and candidate.node_type.casefold() != relation_type.from_type.casefold()
195 │             ):
196 │                 raise RuleViolationError(
197 │                     "Review edit would invalidate an existing relation because the edited node "
198 │                     f"no longer matches from_type '{relation_type.from_type}'."
199 │                 )
200 │             if (
201 │                 relation.to_candidate_ref == candidate.candidate_node_id
202 │                 and candidate.node_type.casefold() != relation_type.to_type.casefold()
203 │             ):
204 │                 raise RuleViolationError(
205 │                     "Review edit would invalidate an existing relation because the edited node "
206 │                     f"no longer matches to_type '{relation_type.to_type}'."
207 │                 )
208 │ 
209 │     def _validate_candidate_relation_state(self, candidate: CandidateRelation) -> None:
210 │         run = self._require_run(candidate.run_id)
211 │         relation_type_map = self._relation_type_map(run.schema_version_id)
212 │         relation_type = relation_type_map.get(candidate.relation_type.casefold())
213 │         if relation_type is None:
214 │             raise RuleViolationError(
215 │                 f"Relation type '{candidate.relation_type}' is not defined in the active schema."
216 │             )
217 │ 
218 │         from_candidate = self._require_candidate_node(candidate.from_candidate_ref)
219 │         to_candidate = self._require_candidate_node(candidate.to_candidate_ref)
220 │         if from_candidate.run_id != candidate.run_id or to_candidate.run_id != candidate.run_id:
221 │             raise RuleViolationError(
222 │                 "Candidate relation references candidate nodes outside of its run."
223 │             )
224 │         if (
225 │             from_candidate.status != CandidateStatus.VALIDATED
226 │             or to_candidate.status != CandidateStatus.VALIDATED
227 │         ):
228 │             raise RuleViolationError(
229 │                 "Candidate relation can only be accepted or edited when both node candidates "
230 │                 "are validated."
231 │             )
232 │         if from_candidate.node_type.casefold() != relation_type.from_type.casefold():
233 │             raise RuleViolationError(
234 │                 f"Relation expects from_type '{relation_type.from_type}' but received "
235 │                 f"'{from_candidate.node_type}'."
236 │             )
237 │         if to_candidate.node_type.casefold() != relation_type.to_type.casefold():
238 │             raise RuleViolationError(
239 │                 f"Relation expects to_type '{relation_type.to_type}' but received "
240 │                 f"'{to_candidate.node_type}'."
241 │             )
242 │ 
243 │         required_properties = {
244 │             *relation_type.required_properties,
245 │             *[
246 │                 property_definition.name
247 │             for property_definition in relation_type.properties
248 │             if property_definition.required
249 │             ],
250 │         }
251 │         missing_required = [
252 │             property_name
253 │             for property_name in sorted(required_properties)
254 │             if is_missing_value(candidate.properties.get(property_name))
255 │         ]
256 │         if missing_required:
257 │             raise RuleViolationError(
258 │                 "Candidate relation is missing required properties: "
259 │                 + ", ".join(missing_required)
260 │                 + "."
261 │             )
262 │ 
263 │         candidate.relation_type = relation_type.name
264 │ 
265 │     def _ensure_candidate_node_unique_within_run(self, candidate: CandidateNode) -> None:
266 │         duplicate = next(
267 │             (
268 │                 other
269 │                 for other in self.candidate_node_repository.list_by_run(candidate.run_id)
270 │                 if other.candidate_node_id != candidate.candidate_node_id
271 │                 and other.status != CandidateStatus.REJECTED
272 │                 and build_candidate_node_resolution_key(other)
273 │                 == build_candidate_node_resolution_key(candidate)
274 │             ),
275 │             None,
276 │         )
277 │         if duplicate is not None:
278 │             raise RuleViolationError(
279 │                 "Review decision would create a duplicate candidate node merge key with "
280 │                 f"'{duplicate.candidate_node_id}'."
281 │             )
282 │ 
283 │     def _ensure_candidate_relation_unique_within_run(
284 │         self,
285 │         candidate: CandidateRelation,
286 │     ) -> None:
287 │         node_resolution_keys = {
288 │             candidate_node.candidate_node_id: candidate_node_identity_key(candidate_node)
289 │             for candidate_node in self.candidate_node_repository.list_by_run(candidate.run_id)
290 │             if candidate_node.status != CandidateStatus.REJECTED
291 │         }
292 │         candidate_relation_key = build_candidate_relation_resolution_key(
293 │             candidate,
294 │             node_resolution_keys_by_candidate_id=node_resolution_keys,
295 │         )
296 │         duplicate = next(
297 │             (
298 │                 other
299 │                 for other in self.candidate_relation_repository.list_by_run(candidate.run_id)
300 │                 if other.candidate_relation_id != candidate.candidate_relation_id
301 │                 and other.status != CandidateStatus.REJECTED
302 │                 and build_candidate_relation_resolution_key(
303 │                     other,
304 │                     node_resolution_keys_by_candidate_id=node_resolution_keys,
305 │                 )
306 │                 == candidate_relation_key
307 │             ),
308 │             None,
309 │         )
310 │         if duplicate is not None:
311 │             raise RuleViolationError(
312 │                 "Review decision would create a duplicate candidate relation with "
313 │                 f"'{duplicate.candidate_relation_id}'."
314 │             )
315 │ 
316 │     def _refresh_relation_reviews_for_run(self, run_id: str) -> None:
317 │         run = self._require_run(run_id)
318 │         relation_type_map = self._relation_type_map(run.schema_version_id)
319 │         review_items = self.review_item_repository.list_by_run(run_id)
320 │         review_items_by_ref: dict[str, list[ReviewItem]] = {}
321 │         for item in review_items:
322 │             review_items_by_ref.setdefault(item.item_ref, []).append(item)
323 │ 
324 │         for relation in self.candidate_relation_repository.list_by_run(run_id):
325 │             evaluation = self._evaluate_relation_candidate_state(
326 │                 relation=relation,
327 │                 relation_type_map=relation_type_map,
328 │             )
329 │             relation.status = evaluation.status
330 │             self.candidate_relation_repository.save(relation)
331 │             self._sync_relation_review_items(
332 │                 relation=relation,
333 │                 evaluation=evaluation,
334 │                 review_items=review_items_by_ref.get(relation.candidate_relation_id, []),
335 │             )
336 │ 
337 │     def _evaluate_relation_candidate_state(
338 │         self,
339 │         *,
340 │         relation: CandidateRelation,
341 │         relation_type_map: dict[str, RelationTypeDefinition],
342 │     ) -> "RelationEvaluation":
343 │         relation_type = relation_type_map.get(relation.relation_type.casefold())
344 │         if relation_type is None:
345 │             return RelationEvaluation(
346 │                 status=CandidateStatus.REJECTED,
347 │                 reason_code="relation_type_exists",
348 │                 messages=[
349 │                     f"Relation type '{relation.relation_type}' is not defined in schema."
350 │                 ],
351 │             )
352 │ 
353 │         from_candidate = self._require_candidate_node(relation.from_candidate_ref)
354 │         to_candidate = self._require_candidate_node(relation.to_candidate_ref)
355 │         if from_candidate.run_id != relation.run_id or to_candidate.run_id != relation.run_id:
356 │             return RelationEvaluation(
357 │                 status=CandidateStatus.REJECTED,
358 │                 reason_code="relation_candidate_refs",
359 │                 messages=[
360 │                     "Relation references candidate nodes that do not exist in the run."
361 │                 ],
362 │             )
363 │         if (
364 │             from_candidate.node_type.casefold() != relation_type.from_type.casefold()
365 │             or to_candidate.node_type.casefold() != relation_type.to_type.casefold()
366 │         ):
367 │             return RelationEvaluation(
368 │                 status=CandidateStatus.REJECTED,
369 │                 reason_code="relation_type_mismatch",
370 │                 messages=[
371 │                     "Relation references candidate nodes with incompatible node types."
372 │                 ],
373 │             )
374 │         if (
375 │             from_candidate.status == CandidateStatus.REJECTED
376 │             or to_candidate.status == CandidateStatus.REJECTED
377 │         ):
378 │             return RelationEvaluation(
379 │                 status=CandidateStatus.REJECTED,
380 │                 reason_code="relation_dependency_rejected",
381 │                 messages=[
382 │                     "Relation depends on candidate nodes that failed validation."
383 │                 ],
384 │             )
385 │         if (
386 │             from_candidate.status != CandidateStatus.VALIDATED
387 │             or to_candidate.status != CandidateStatus.VALIDATED
388 │         ):
389 │             return RelationEvaluation(
390 │                 status=CandidateStatus.REVIEW,
391 │                 reason_code="relation_dependency_review",
392 │                 messages=[
393 │                     "Relation depends on candidate nodes that require review."
394 │                 ],
395 │             )
396 │ 
397 │         required_properties = {
398 │             *relation_type.required_properties,
399 │             *[
400 │                 property_definition.name
401 │                 for property_definition in relation_type.properties
402 │                 if property_definition.required
403 │             ],
404 │         }
405 │         missing_required = [
406 │             property_name
407 │             for property_name in sorted(required_properties)
408 │             if is_missing_value(relation.properties.get(property_name))
409 │         ]
410 │         if missing_required:
411 │             return RelationEvaluation(
412 │                 status=CandidateStatus.REJECTED,
413 │                 reason_code="required_relation_property",
414 │                 messages=[
415 │                     "Relation is missing required properties: "
416 │                     + ", ".join(missing_required)
417 │                     + "."
418 │                 ],
419 │             )
420 │ 
421 │         if relation.confidence < relation_type.confidence_threshold:
422 │             return RelationEvaluation(
423 │                 status=CandidateStatus.REVIEW,
424 │                 reason_code="relation_confidence_threshold",
425 │                 messages=[
426 │                     "Relation confidence is below the schema threshold "
427 │                     f"({relation_type.confidence_threshold:.2f})."
428 │                 ],
429 │             )
430 │ 
431 │         relation.relation_type = relation_type.name
432 │         return RelationEvaluation(
433 │             status=CandidateStatus.VALIDATED,
434 │             reason_code="candidate_relation_valid",
435 │             messages=["Candidate relation passed validation."],
436 │         )
437 │ 
438 │     def _sync_relation_review_items(
439 │         self,
440 │         *,
441 │         relation: CandidateRelation,
442 │         evaluation: "RelationEvaluation",
443 │         review_items: list[ReviewItem],
444 │     ) -> None:
445 │         open_items = [
446 │             item
447 │             for item in review_items
448 │             if item.status == ReviewStatus.OPEN
449 │         ]
450 │         messages = list(evaluation.messages)
451 │         payload_json = {
452 │             "relation_type": relation.relation_type,
453 │             "confidence": relation.confidence,
454 │             "messages": messages,
455 │         }
456 │ 
457 │         if relation.status == CandidateStatus.REVIEW:
458 │             if open_items:
459 │                 for item in open_items:
460 │                     item.reason_code = evaluation.reason_code
461 │                     item.payload_json = payload_json
462 │                     self.review_item_repository.save(item)
463 │                 return
464 │ 
465 │             self.review_item_repository.save(
466 │                 ReviewItem(
467 │                     review_item_id=str(uuid4()),
468 │                     run_id=relation.run_id,
469 │                     item_type="candidate_relation",
470 │                     item_ref=relation.candidate_relation_id,
471 │                     reason_code=evaluation.reason_code,
472 │                     payload_json=payload_json,
473 │                 )
474 │             )
475 │             return
476 │ 
477 │         if relation.status == CandidateStatus.VALIDATED:
478 │             auto_status = ReviewStatus.ACCEPTED
479 │             note = "Auto-resolved after dependent review decision."
480 │         else:
481 │             auto_status = ReviewStatus.REJECTED
482 │             note = "Auto-closed after dependent review decision."
483 │ 
484 │         for item in open_items:
485 │             item.status = auto_status
486 │             item.reviewer_note = note
487 │             item.payload_json = payload_json
488 │             self.review_item_repository.save(item)
489 │ 
490 │     def _require_run(self, run_id: str) -> ProcessingRun:
491 │         run = self.processing_run_repository.get(run_id)
492 │         if run is None:
493 │             raise NotFoundError(f"Processing run '{run_id}' was not found.")
494 │         return run
495 │ 
496 │     def _node_type_map(self, schema_version_id: str) -> dict[str, NodeTypeDefinition]:
497 │         return {
498 │             node_type.name.casefold(): node_type
499 │             for node_type in self.schema_repository.list_node_types(schema_version_id)
500 │         }
501 │ 
502 │     def _relation_type_map(self, schema_version_id: str) -> dict[str, RelationTypeDefinition]:
503 │         return {
504 │             relation_type.name.casefold(): relation_type
505 │             for relation_type in self.schema_repository.list_relation_types(schema_version_id)
506 │         }
```

## FILE: backend/src/app/application/use_cases/commit_management.py
```python
  1 │ from dataclasses import dataclass
  2 │ from uuid import uuid4
  3 │ 
  4 │ from app.application.errors import ConflictError, NotFoundError, RuleViolationError
  5 │ from app.application.ports.repositories import (
  6 │     CandidateNodeRepository,
  7 │     CandidateRelationRepository,
  8 │     CanonicalGraphRepository,
  9 │     GraphDeltaRepository,
 10 │     ProcessingRunRepository,
 11 │     ReviewItemRepository,
 12 │     SegmentRepository,
 13 │     SourceUnitRepository,
 14 │ )
 15 │ from app.domain.graph_commit.entities import CanonicalCommitBundle, GraphDelta
 16 │ from app.domain.ingestion.lifecycle import (
 17 │     mark_run_completed,
 18 │     mark_run_failed,
 19 │     mark_run_started,
 20 │     reserve_source_for_run,
 21 │ )
 22 │ from app.domain.shared.enums import CandidateStatus, ReviewStatus
 23 │ 
 24 │ 
 25 │ @dataclass(slots=True)
 26 │ class CommitManagementService:
 27 │     processing_run_repository: ProcessingRunRepository
 28 │     source_unit_repository: SourceUnitRepository
 29 │     segment_repository: SegmentRepository
 30 │     candidate_node_repository: CandidateNodeRepository
 31 │     candidate_relation_repository: CandidateRelationRepository
 32 │     review_item_repository: ReviewItemRepository
 33 │     graph_delta_repository: GraphDeltaRepository
 34 │     canonical_graph_repository: CanonicalGraphRepository
 35 │ 
 36 │     def commit_run(self, run_id: str) -> GraphDelta:
 37 │         if self.graph_delta_repository.get_by_run(run_id) is not None:
 38 │             raise ConflictError(f"Run '{run_id}' already has a graph delta.")
 39 │ 
 40 │         run = self.processing_run_repository.get(run_id)
 41 │         if run is None:
 42 │             raise NotFoundError(f"Processing run '{run_id}' was not found.")
 43 │ 
 44 │         candidate_nodes = self.candidate_node_repository.list_by_run(run_id)
 45 │         candidate_relations = self.candidate_relation_repository.list_by_run(run_id)
 46 │         if any(candidate.status == CandidateStatus.PENDING for candidate in candidate_nodes):
 47 │             raise RuleViolationError("All candidate nodes must be validated before commit.")
 48 │         if any(candidate.status == CandidateStatus.PENDING for candidate in candidate_relations):
 49 │             raise RuleViolationError("All candidate relations must be validated before commit.")
 50 │ 
 51 │         open_review_items = [
 52 │             item
 53 │             for item in self.review_item_repository.list_by_run(run_id)
 54 │             if item.status == ReviewStatus.OPEN
 55 │         ]
 56 │         if open_review_items:
 57 │             raise RuleViolationError("Run has open review items and cannot be committed.")
 58 │ 
 59 │         validated_nodes = [
 60 │             candidate
 61 │             for candidate in candidate_nodes
 62 │             if candidate.status == CandidateStatus.VALIDATED
 63 │         ]
 64 │         validated_relations = [
 65 │             candidate
 66 │             for candidate in candidate_relations
 67 │             if candidate.status == CandidateStatus.VALIDATED
 68 │         ]
 69 │         validated_node_ids = {
 70 │             candidate.candidate_node_id
 71 │             for candidate in validated_nodes
 72 │         }
 73 │         invalid_relation_dependencies = [
 74 │             candidate.candidate_relation_id
 75 │             for candidate in validated_relations
 76 │             if candidate.from_candidate_ref not in validated_node_ids
 77 │             or candidate.to_candidate_ref not in validated_node_ids
 78 │         ]
 79 │         if invalid_relation_dependencies:
 80 │             raise RuleViolationError(
 81 │                 "Validated relations depend on candidate nodes that are not validated: "
 82 │                 + ", ".join(sorted(invalid_relation_dependencies))
 83 │                 + ". Re-run validation or resolve dependent review items first."
 84 │             )
 85 │         rejected_count = sum(
 86 │             candidate.status == CandidateStatus.REJECTED for candidate in candidate_nodes
 87 │         ) + sum(
 88 │             candidate.status == CandidateStatus.REJECTED for candidate in candidate_relations
 89 │         )
 90 │ 
 91 │         source_unit = self.source_unit_repository.get(run.source_unit_id)
 92 │         if source_unit is None:
 93 │             raise NotFoundError(f"Source unit '{run.source_unit_id}' was not found.")
 94 │ 
 95 │         delta = GraphDelta(
 96 │             delta_id=str(uuid4()),
 97 │             run_id=run_id,
 98 │             project_id=run.project_id,
 99 │             nodes_created=0,
100 │             nodes_merged=0,
101 │             relations_created=0,
102 │             relations_merged=0,
103 │             review_count=0,
104 │             rejected_count=rejected_count,
105 │         )
106 │         reserve_source_for_run(source_unit)
107 │         mark_run_started(run)
108 │         self.processing_run_repository.save(run)
109 │         self.source_unit_repository.save(source_unit)
110 │ 
111 │         try:
112 │             committed_delta = self.canonical_graph_repository.commit_bundle(
113 │                 CanonicalCommitBundle(
114 │                     delta=delta,
115 │                     source_unit=source_unit,
116 │                     segments=self.segment_repository.list_by_source_unit(
117 │                         source_unit.source_unit_id
118 │                     ),
119 │                     candidate_nodes=validated_nodes,
120 │                     candidate_relations=validated_relations,
121 │                 )
122 │             )
123 │         except Exception:
124 │             mark_run_failed(run, source_unit)
125 │             self.processing_run_repository.save(run)
126 │             self.source_unit_repository.save(source_unit)
127 │             raise
128 │         self.graph_delta_repository.add(committed_delta)
129 │ 
130 │         mark_run_completed(run, source_unit)
131 │         self.processing_run_repository.save(run)
132 │         self.source_unit_repository.save(source_unit)
133 │ 
134 │         return committed_delta
135 │ 
136 │     def get_graph_delta(self, run_id: str) -> GraphDelta:
137 │         delta = self.graph_delta_repository.get_by_run(run_id)
138 │         if delta is None:
139 │             raise NotFoundError(f"Run '{run_id}' does not have a graph delta yet.")
140 │         return delta
```

## FILE: backend/src/app/infrastructure/template/catalog.py
```python
 1 │ from dataclasses import dataclass, field
 2 │ 
 3 │ from app.application.ports.template_catalog import DomainTemplateCatalog
 4 │ from app.domain.template.entities import DomainTemplate
 5 │ 
 6 │ BLANK_TEMPLATE_ID = "blank"
 7 │ STORY_TEMPLATE_ID = "story"
 8 │ 
 9 │ SYSTEM_DOMAIN_TEMPLATES = [
10 │     DomainTemplate(
11 │         template_id=BLANK_TEMPLATE_ID,
12 │         name="Blank",
13 │         slug=BLANK_TEMPLATE_ID,
14 │         description="Start from an empty generic graph schema and configure everything manually.",
15 │     ),
16 │     DomainTemplate(
17 │         template_id=STORY_TEMPLATE_ID,
18 │         name="Story / Series / Film",
19 │         slug=STORY_TEMPLATE_ID,
20 │         description=(
21 │             "Story-oriented starter template for transcripts, scripts, episodes, scenes, "
22 │             "characters, events, and related narrative structures."
23 │         ),
24 │     ),
25 │ ]
26 │ 
27 │ 
28 │ @dataclass(slots=True)
29 │ class StaticDomainTemplateCatalog(DomainTemplateCatalog):
30 │     templates: dict[str, DomainTemplate] = field(default_factory=dict)
31 │     default_template_id: str = BLANK_TEMPLATE_ID
32 │ 
33 │     def __init__(
34 │         self,
35 │         *,
36 │         templates: list[DomainTemplate],
37 │         default_template_id: str = BLANK_TEMPLATE_ID,
38 │     ) -> None:
39 │         normalized_templates: dict[str, DomainTemplate] = {}
40 │         for template in templates:
41 │             normalized_templates[self._normalize(template.template_id)] = template
42 │         normalized_default_template_id = self._normalize(default_template_id)
43 │         if normalized_default_template_id not in normalized_templates:
44 │             raise ValueError(
45 │                 f"Default template '{default_template_id}' is not registered in the catalog."
46 │             )
47 │         self.templates = normalized_templates
48 │         self.default_template_id = normalized_default_template_id
49 │ 
50 │     def get(self, template_id: str) -> DomainTemplate | None:
51 │         normalized_template_id = self._normalize(template_id)
52 │         if normalized_template_id == "":
53 │             return None
54 │         return self.templates.get(normalized_template_id)
55 │ 
56 │     def list(self) -> list[DomainTemplate]:
57 │         return sorted(
58 │             self.templates.values(),
59 │             key=lambda template: (template.is_system is False, template.name.casefold()),
60 │         )
61 │ 
62 │     def get_default(self) -> DomainTemplate:
63 │         return self.templates[self.default_template_id]
64 │ 
65 │     def _normalize(self, value: str) -> str:
66 │         return value.strip().casefold()
```

## FILE: backend/src/app/infrastructure/persistence/neo4j/repositories.py (lines 1-470 + 1095-1145: commit path, MERGE Cypher, identifier regex)
```python
     1	import json
     2	import re
     3	from dataclasses import dataclass
     4	from typing import Any
     5	
     6	from neo4j import Driver, ManagedTransaction
     7	
     8	from app.application.ports.repositories import CanonicalGraphRepository
     9	from app.domain.exploration.entities import (
    10	    CanonicalNodeDetail,
    11	    CanonicalNodeView,
    12	    CanonicalRelationDetail,
    13	    CanonicalRelationEndpointView,
    14	    CanonicalRelationView,
    15	    CanonicalSegmentSupport,
    16	    CanonicalSourceUnitRef,
    17	    ConnectedRelationView,
    18	    GraphOverview,
    19	    NodeTypeCount,
    20	)
    21	from app.domain.extraction.entities import CandidateNode, CandidateRelation
    22	from app.domain.graph_commit.entities import CanonicalCommitBundle, GraphDelta
    23	from app.domain.ingestion.entities import Segment, SourceUnit
    24	from app.domain.shared.resolution import build_canonical_merge_key
    25	
    26	IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    27	
    28	
    29	@dataclass(slots=True)
    30	class Neo4jCanonicalGraphRepository(CanonicalGraphRepository):
    31	    driver: Driver
    32	
    33	    def commit_bundle(self, bundle: CanonicalCommitBundle) -> GraphDelta:
    34	        delta = bundle.delta
    35	        segment_map = {segment.segment_id: segment for segment in bundle.segments}
    36	        node_refs_by_candidate: dict[str, tuple[str, str]] = {}
    37	
    38	        with self.driver.session() as session:
    39	            session.execute_write(
    40	                self._upsert_source_context,
    41	                bundle.source_unit,
    42	                bundle.segments,
    43	            )
    44	
    45	            nodes_created = 0
    46	            nodes_merged = 0
    47	            for candidate_node in bundle.candidate_nodes:
    48	                merge_key = self._build_merge_key(candidate_node)
    49	                created = session.execute_write(
    50	                    self._merge_candidate_node,
    51	                    delta,
    52	                    bundle.source_unit,
    53	                    candidate_node,
    54	                    merge_key,
    55	                )
    56	                node_refs_by_candidate[candidate_node.candidate_node_id] = (
    57	                    candidate_node.node_type,
    58	                    merge_key,
    59	                )
    60	                if created:
    61	                    nodes_created += 1
    62	                else:
    63	                    nodes_merged += 1
    64	
    65	                session.execute_write(
    66	                    self._link_node_provenance,
    67	                    delta,
    68	                    bundle.source_unit,
    69	                    candidate_node,
    70	                    merge_key,
    71	                    segment_map,
    72	                )
    73	
    74	            relations_created = 0
    75	            relations_merged = 0
    76	            for candidate_relation in bundle.candidate_relations:
    77	                from_ref = node_refs_by_candidate.get(candidate_relation.from_candidate_ref)
    78	                to_ref = node_refs_by_candidate.get(candidate_relation.to_candidate_ref)
    79	                if from_ref is None or to_ref is None:
    80	                    raise ValueError(
    81	                        "Canonical commit received relation candidates without canonical node refs."
    82	                    )
    83	
    84	                created = session.execute_write(
    85	                    self._merge_candidate_relation,
    86	                    delta,
    87	                    bundle.source_unit,
    88	                    candidate_relation,
    89	                    from_ref,
    90	                    to_ref,
    91	                )
    92	                if created:
    93	                    relations_created += 1
    94	                else:
    95	                    relations_merged += 1
    96	
    97	                session.execute_write(
    98	                    self._link_relation_provenance,
    99	                    delta,
   100	                    bundle.source_unit,
   101	                    candidate_relation,
   102	                    from_ref,
   103	                    to_ref,
   104	                    segment_map,
   105	                )
   106	
   107	            delta.nodes_created = nodes_created
   108	            delta.nodes_merged = nodes_merged
   109	            delta.relations_created = relations_created
   110	            delta.relations_merged = relations_merged
   111	            session.execute_write(self._upsert_graph_delta, delta)
   112	
   113	        return delta
   114	
   115	    def get_project_overview(self, project_id: str) -> GraphOverview:
   116	        with self.driver.session() as session:
   117	            counts = session.execute_read(self._fetch_project_overview_counts, project_id)
   118	            node_type_counts = session.execute_read(
   119	                self._fetch_project_node_type_counts,
   120	                project_id,
   121	            )
   122	        return GraphOverview(
   123	            project_id=project_id,
   124	            node_count=counts["node_count"],
   125	            relation_count=counts["relation_count"],
   126	            node_type_counts=node_type_counts,
   127	        )
   128	
   129	    def list_nodes(
   130	        self,
   131	        project_id: str,
   132	        *,
   133	        node_type: str | None = None,
   134	        limit: int = 50,
   135	    ) -> list[CanonicalNodeView]:
   136	        with self.driver.session() as session:
   137	            return session.execute_read(
   138	                self._fetch_project_nodes,
   139	                project_id,
   140	                node_type,
   141	                limit,
   142	            )
   143	
   144	    def list_relations(
   145	        self,
   146	        project_id: str,
   147	        *,
   148	        relation_type: str | None = None,
   149	        limit: int = 50,
   150	    ) -> list[CanonicalRelationView]:
   151	        with self.driver.session() as session:
   152	            return session.execute_read(
   153	                self._fetch_project_relations,
   154	                project_id,
   155	                relation_type,
   156	                limit,
   157	            )
   158	
   159	    def get_node_detail(
   160	        self,
   161	        project_id: str,
   162	        *,
   163	        node_type: str,
   164	        merge_key: str,
   165	    ) -> CanonicalNodeDetail | None:
   166	        with self.driver.session() as session:
   167	            node = session.execute_read(
   168	                self._fetch_canonical_node,
   169	                project_id,
   170	                node_type,
   171	                merge_key,
   172	            )
   173	            if node is None:
   174	                return None
   175	
   176	            return CanonicalNodeDetail(
   177	                node=node,
   178	                source_units=session.execute_read(
   179	                    self._fetch_node_source_units,
   180	                    project_id,
   181	                    node_type,
   182	                    merge_key,
   183	                ),
   184	                supporting_segments=session.execute_read(
   185	                    self._fetch_node_supporting_segments,
   186	                    project_id,
   187	                    node_type,
   188	                    merge_key,
   189	                ),
   190	                connected_relations=session.execute_read(
   191	                    self._fetch_node_connected_relations,
   192	                    project_id,
   193	                    node_type,
   194	                    merge_key,
   195	                ),
   196	            )
   197	
   198	    def get_relation_detail(
   199	        self,
   200	        project_id: str,
   201	        *,
   202	        relation_type: str,
   203	        from_node_type: str,
   204	        from_merge_key: str,
   205	        to_node_type: str,
   206	        to_merge_key: str,
   207	    ) -> CanonicalRelationDetail | None:
   208	        with self.driver.session() as session:
   209	            relation_payload = session.execute_read(
   210	                self._fetch_canonical_relation_detail_payload,
   211	                project_id,
   212	                relation_type,
   213	                from_node_type,
   214	                from_merge_key,
   215	                to_node_type,
   216	                to_merge_key,
   217	            )
   218	            if relation_payload is None:
   219	                return None
   220	
   221	            relation, from_node, to_node = relation_payload
   222	            return CanonicalRelationDetail(
   223	                relation=relation,
   224	                from_node=from_node,
   225	                to_node=to_node,
   226	                source_units=session.execute_read(
   227	                    self._fetch_relation_source_units,
   228	                    project_id,
   229	                    relation_type,
   230	                    from_node_type,
   231	                    from_merge_key,
   232	                    to_node_type,
   233	                    to_merge_key,
   234	                ),
   235	                supporting_segments=session.execute_read(
   236	                    self._fetch_relation_supporting_segments,
   237	                    project_id,
   238	                    relation_type,
   239	                    from_node_type,
   240	                    from_merge_key,
   241	                    to_node_type,
   242	                    to_merge_key,
   243	                ),
   244	            )
   245	
   246	    def _upsert_source_context(
   247	        self,
   248	        tx: ManagedTransaction,
   249	        source_unit: SourceUnit,
   250	        segments: list[Segment],
   251	    ) -> None:
   252	        source_query = """
   253	        MERGE (su:SourceUnit {source_unit_id: $source_unit_id})
   254	        SET su.project_id = $project_id,
   255	            su.schema_version_id = $schema_version_id,
   256	            su.source_type = $source_type,
   257	            su.title = $title,
   258	            su.status = $status,
   259	            su.sequence_no = $sequence_no,
   260	            su.external_ref = $external_ref,
   261	            su.metadata_json = $metadata_json,
   262	            su.created_at = datetime($created_at)
   263	        """
   264	        tx.run(
   265	            source_query,
   266	            source_unit_id=source_unit.source_unit_id,
   267	            project_id=source_unit.project_id,
   268	            schema_version_id=source_unit.schema_version_id,
   269	            source_type=source_unit.source_type,
   270	            title=source_unit.title,
   271	            status=source_unit.status.value,
   272	            sequence_no=source_unit.sequence_no,
   273	            external_ref=source_unit.external_ref,
   274	            metadata_json=json.dumps(source_unit.metadata_json, sort_keys=True),
   275	            created_at=source_unit.created_at.isoformat(),
   276	        ).consume()
   277	
   278	        segment_query = """
   279	        MATCH (su:SourceUnit {source_unit_id: $source_unit_id})
   280	        UNWIND $segments AS segment
   281	        MERGE (sg:Segment {segment_id: segment.segment_id})
   282	        SET sg.source_unit_id = $source_unit_id,
   283	            sg.segment_order = segment.segment_order,
   284	            sg.text = segment.text,
   285	            sg.metadata_json = segment.metadata_json
   286	        MERGE (su)-[:HAS_SEGMENT]->(sg)
   287	        """
   288	        tx.run(
   289	            segment_query,
   290	            source_unit_id=source_unit.source_unit_id,
   291	            segments=[
   292	                {
   293	                    "segment_id": segment.segment_id,
   294	                    "segment_order": segment.segment_order,
   295	                    "text": segment.text,
   296	                    "metadata_json": json.dumps(segment.metadata_json, sort_keys=True),
   297	                }
   298	                for segment in segments
   299	            ],
   300	        ).consume()
   301	
   302	    def _merge_candidate_node(
   303	        self,
   304	        tx: ManagedTransaction,
   305	        delta: GraphDelta,
   306	        source_unit: SourceUnit,
   307	        candidate_node: CandidateNode,
   308	        merge_key: str,
   309	    ) -> bool:
   310	        label = self._quoted_identifier(candidate_node.node_type)
   311	        query = f"""
   312	        MERGE (n:CanonicalNode:{label} {{
   313	            project_id: $project_id,
   314	            node_type: $node_type,
   315	            merge_key: $merge_key
   316	        }})
   317	        ON CREATE SET n.created_at = datetime($created_at)
   318	        SET n += $properties,
   319	            n.source_unit_id = $source_unit_id,
   320	            n.last_run_id = $run_id,
   321	            n.updated_at = datetime($created_at)
   322	        """
   323	        result = tx.run(
   324	            query,
   325	            project_id=delta.project_id,
   326	            node_type=candidate_node.node_type,
   327	            merge_key=merge_key,
   328	            properties=self._sanitize_property_map(candidate_node.properties),
   329	            source_unit_id=source_unit.source_unit_id,
   330	            run_id=delta.run_id,
   331	            created_at=delta.created_at.isoformat(),
   332	        )
   333	        summary = result.consume()
   334	        return summary.counters.nodes_created > 0
   335	
   336	    def _link_node_provenance(
   337	        self,
   338	        tx: ManagedTransaction,
   339	        delta: GraphDelta,
   340	        source_unit: SourceUnit,
   341	        candidate_node: CandidateNode,
   342	        merge_key: str,
   343	        segment_map: dict[str, Segment],
   344	    ) -> None:
   345	        label = self._quoted_identifier(candidate_node.node_type)
   346	        source_query = f"""
   347	        MATCH (n:CanonicalNode:{label} {{
   348	            project_id: $project_id,
   349	            node_type: $node_type,
   350	            merge_key: $merge_key
   351	        }})
   352	        MATCH (su:SourceUnit {{source_unit_id: $source_unit_id}})
   353	        MERGE (n)-[:DERIVED_FROM {{
   354	            run_id: $run_id,
   355	            candidate_ref: $candidate_ref
   356	        }}]->(su)
   357	        """
   358	        tx.run(
   359	            source_query,
   360	            project_id=delta.project_id,
   361	            node_type=candidate_node.node_type,
   362	            merge_key=merge_key,
   363	            source_unit_id=source_unit.source_unit_id,
   364	            run_id=delta.run_id,
   365	            candidate_ref=candidate_node.candidate_node_id,
   366	        ).consume()
   367	
   368	        for evidence_ref in candidate_node.evidence_refs:
   369	            segment = segment_map.get(evidence_ref.segment_id)
   370	            if segment is None:
   371	                continue
   372	            segment_query = f"""
   373	            MATCH (n:CanonicalNode:{label} {{
   374	                project_id: $project_id,
   375	                node_type: $node_type,
   376	                merge_key: $merge_key
   377	            }})
   378	            MATCH (sg:Segment {{segment_id: $segment_id}})
   379	            MERGE (n)-[:SUPPORTED_BY {{
   380	                run_id: $run_id,
   381	                candidate_ref: $candidate_ref,
   382	                segment_id: $segment_id
   383	            }}]->(sg)
   384	            """
   385	            tx.run(
   386	                segment_query,
   387	                project_id=delta.project_id,
   388	                node_type=candidate_node.node_type,
   389	                merge_key=merge_key,
   390	                segment_id=segment.segment_id,
   391	                run_id=delta.run_id,
   392	                candidate_ref=candidate_node.candidate_node_id,
   393	            ).consume()
   394	
   395	        delta_query = f"""
   396	        MERGE (d:GraphDelta {{delta_id: $delta_id}})
   397	        WITH d
   398	        MATCH (n:CanonicalNode:{label} {{
   399	            project_id: $project_id,
   400	            node_type: $node_type,
   401	            merge_key: $merge_key
   402	        }})
   403	        MERGE (d)-[:AFFECTED_NODE {{candidate_ref: $candidate_ref}}]->(n)
   404	        """
   405	        tx.run(
   406	            delta_query,
   407	            delta_id=delta.delta_id,
   408	            project_id=delta.project_id,
   409	            node_type=candidate_node.node_type,
   410	            merge_key=merge_key,
   411	            candidate_ref=candidate_node.candidate_node_id,
   412	        ).consume()
   413	
   414	    def _merge_candidate_relation(
   415	        self,
   416	        tx: ManagedTransaction,
   417	        delta: GraphDelta,
   418	        source_unit: SourceUnit,
   419	        candidate_relation: CandidateRelation,
   420	        from_ref: tuple[str, str],
   421	        to_ref: tuple[str, str],
   422	    ) -> bool:
   423	        relation_type = self._quoted_identifier(candidate_relation.relation_type)
   424	        query = f"""
   425	        MATCH (from_node:CanonicalNode {{
   426	            project_id: $project_id,
   427	            node_type: $from_type,
   428	            merge_key: $from_merge_key
   429	        }})
   430	        MATCH (to_node:CanonicalNode {{
   431	            project_id: $project_id,
   432	            node_type: $to_type,
   433	            merge_key: $to_merge_key
   434	        }})
   435	        MERGE (from_node)-[r:{relation_type} {{
   436	            project_id: $project_id,
   437	            relation_type: $relation_type
   438	        }}]->(to_node)
   439	        ON CREATE SET r.created_at = datetime($created_at)
   440	        SET r += $properties,
   441	            r.source_unit_id = $source_unit_id,
   442	            r.last_run_id = $run_id,
   443	            r.updated_at = datetime($created_at)
   444	        """
   445	        result = tx.run(
   446	            query,
   447	            project_id=delta.project_id,
   448	            from_type=from_ref[0],
   449	            from_merge_key=from_ref[1],
   450	            to_type=to_ref[0],
   451	            to_merge_key=to_ref[1],
   452	            relation_type=candidate_relation.relation_type,
   453	            properties=self._sanitize_property_map(candidate_relation.properties),
   454	            source_unit_id=source_unit.source_unit_id,
   455	            run_id=delta.run_id,
   456	            created_at=delta.created_at.isoformat(),
   457	        )
   458	        summary = result.consume()
   459	        return summary.counters.relationships_created > 0
   460	
   461	    def _link_relation_provenance(
   462	        self,
   463	        tx: ManagedTransaction,
   464	        delta: GraphDelta,
   465	        source_unit: SourceUnit,
   466	        candidate_relation: CandidateRelation,
   467	        from_ref: tuple[str, str],
   468	        to_ref: tuple[str, str],
   469	        segment_map: dict[str, Segment],
   470	    ) -> None:
    ...
  1095	                    else None
  1096	                ),
  1097	                text=str(record["text"]),
  1098	            )
  1099	            for record in records
  1100	        ]
  1101	
  1102	    def _build_merge_key(self, candidate_node: CandidateNode) -> str:
  1103	        return build_canonical_merge_key(
  1104	            merge_key_payload=candidate_node.merge_key_payload,
  1105	            fallback_payload={"candidate_node_id": candidate_node.candidate_node_id},
  1106	        )
  1107	
  1108	    def _quoted_identifier(self, value: str) -> str:
  1109	        if not IDENTIFIER_PATTERN.match(value):
  1110	            raise ValueError(f"Invalid Neo4j identifier '{value}'.")
  1111	        return f"`{value}`"
  1112	
  1113	    def _sanitize_property_map(self, properties: dict[str, object]) -> dict[str, object]:
  1114	        sanitized: dict[str, object] = {}
  1115	        for key, value in properties.items():
  1116	            if value is None:
  1117	                continue
  1118	            sanitized[key] = self._sanitize_property_value(value)
  1119	        return sanitized
  1120	
  1121	    def _sanitize_property_value(self, value: object) -> object:
  1122	        if isinstance(value, (str, bool, int, float)):
  1123	            return value
  1124	        if isinstance(value, list):
  1125	            if all(isinstance(item, (str, bool, int, float)) for item in value):
  1126	                return value
  1127	            return json.dumps(value, sort_keys=True, default=str)
  1128	        if isinstance(value, dict):
  1129	            return json.dumps(value, sort_keys=True, default=str)
  1130	        return str(value)
  1131	
  1132	    def _strip_reserved_properties(
  1133	        self,
  1134	        properties: dict[str, object],
  1135	        reserved_keys: set[str],
  1136	    ) -> dict[str, object]:
  1137	        return {
  1138	            key: value
  1139	            for key, value in properties.items()
  1140	            if key not in reserved_keys
  1141	        }
  1142	
  1143	    def _build_canonical_node_view(
  1144	        self,
  1145	        project_id: str,
```

## FILE: docker-compose.yml
```
services:
  dashboard:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "${DASHBOARD_PORT:-3000}:3000"
    environment:
      NEXT_PUBLIC_API_BASE_URL: "${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}"
      WATCHPACK_POLLING: "true"
    volumes:
      - ./frontend:/app
      - dashboard_node_modules:/app/node_modules
      - dashboard_next:/app/.next
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:3000 > /dev/null 2>&1 || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 10

  backend:
    image: giraffegraph-core-backend
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      APP_ENV: "${APP_ENV:-development}"
      REPOSITORY_BACKEND: "${REPOSITORY_BACKEND:-postgres}"
      AUTO_APPLY_POSTGRES_MIGRATIONS: "${AUTO_APPLY_POSTGRES_MIGRATIONS:-true}"
      ALLOWED_ORIGINS: "${ALLOWED_ORIGINS:-http://localhost:3000}"
      POSTGRES_DSN: "postgresql://${POSTGRES_USER:-giraffegraph}:${POSTGRES_PASSWORD:-giraffegraph}@postgres:5432/${POSTGRES_DB:-giraffegraph}"
      NEO4J_URI: "bolt://neo4j:7687"
      NEO4J_USERNAME: "neo4j"
      NEO4J_PASSWORD: "${NEO4J_PASSWORD:-giraffegraph}"
      OPENAI_API_KEY: "${OPENAI_API_KEY:-}"
      OPENAI_BASE_URL: "${OPENAI_BASE_URL:-https://api.openai.com/v1}"
      OPENAI_TIMEOUT_SECONDS: "${OPENAI_TIMEOUT_SECONDS:-30}"
      DEFAULT_LLM_PROVIDER: "${DEFAULT_LLM_PROVIDER:-noop}"
      DEFAULT_LLM_MODEL: "${DEFAULT_LLM_MODEL:-}"
      DEFAULT_EXTRACTION_PROMPT_VERSION: "${DEFAULT_EXTRACTION_PROMPT_VERSION:-candidate_graph_extraction_v1}"
      PROCESSING_JOB_POLL_INTERVAL_SECONDS: "${PROCESSING_JOB_POLL_INTERVAL_SECONDS:-2}"
      WATCHFILES_FORCE_POLLING: "true"
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8000/health || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 10

  worker:
    image: giraffegraph-core-backend
    command: ["python", "-m", "app.interfaces.cli.processing_jobs_worker"]
    environment:
      APP_ENV: "${APP_ENV:-development}"
      REPOSITORY_BACKEND: "${REPOSITORY_BACKEND:-postgres}"
      AUTO_APPLY_POSTGRES_MIGRATIONS: "false"
      ALLOWED_ORIGINS: "${ALLOWED_ORIGINS:-http://localhost:3000}"
      POSTGRES_DSN: "postgresql://${POSTGRES_USER:-giraffegraph}:${POSTGRES_PASSWORD:-giraffegraph}@postgres:5432/${POSTGRES_DB:-giraffegraph}"
      NEO4J_URI: "bolt://neo4j:7687"
      NEO4J_USERNAME: "neo4j"
      NEO4J_PASSWORD: "${NEO4J_PASSWORD:-giraffegraph}"
      OPENAI_API_KEY: "${OPENAI_API_KEY:-}"
      OPENAI_BASE_URL: "${OPENAI_BASE_URL:-https://api.openai.com/v1}"
      OPENAI_TIMEOUT_SECONDS: "${OPENAI_TIMEOUT_SECONDS:-30}"
      DEFAULT_LLM_PROVIDER: "${DEFAULT_LLM_PROVIDER:-noop}"
      DEFAULT_LLM_MODEL: "${DEFAULT_LLM_MODEL:-}"
      DEFAULT_EXTRACTION_PROMPT_VERSION: "${DEFAULT_EXTRACTION_PROMPT_VERSION:-candidate_graph_extraction_v1}"
      PROCESSING_JOB_POLL_INTERVAL_SECONDS: "${PROCESSING_JOB_POLL_INTERVAL_SECONDS:-2}"
      WATCHFILES_FORCE_POLLING: "true"
    volumes:
      - ./backend:/app
    depends_on:
      backend:
        condition: service_healthy
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    environment:
      POSTGRES_DB: "${POSTGRES_DB:-giraffegraph}"
      POSTGRES_USER: "${POSTGRES_USER:-giraffegraph}"
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD:-giraffegraph}"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-giraffegraph} -d ${POSTGRES_DB:-giraffegraph}"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5
    ports:
      - "${NEO4J_HTTP_PORT:-7474}:7474"
      - "${NEO4J_BOLT_PORT:-7687}:7687"
    environment:
      NEO4J_AUTH: "neo4j/${NEO4J_PASSWORD:-giraffegraph}"
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_apoc_export_file_enabled: "true"
      NEO4J_apoc_import_file_enabled: "true"
      NEO4J_dbms_security_procedures_unrestricted: "apoc.*"
      NEO4J_dbms_security_procedures_allowlist: "apoc.*"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "cypher-shell -u neo4j -p ${NEO4J_PASSWORD:-giraffegraph} 'RETURN 1;' > /dev/null 2>&1 || exit 1"
        ]
      interval: 15s
      timeout: 10s
      retries: 10

volumes:
  dashboard_node_modules:
  dashboard_next:
  postgres_data:
  neo4j_data:
  neo4j_logs:
```

## FILE: .env.example
```
APP_ENV=development
REPOSITORY_BACKEND=postgres
AUTO_APPLY_POSTGRES_MIGRATIONS=true
ALLOWED_ORIGINS=http://localhost:3000

POSTGRES_DB=giraffegraph
POSTGRES_USER=giraffegraph
POSTGRES_PASSWORD=giraffegraph
POSTGRES_PORT=5432

NEO4J_PASSWORD=giraffegraph
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT_SECONDS=30
DEFAULT_LLM_PROVIDER=noop
DEFAULT_LLM_MODEL=
DEFAULT_EXTRACTION_PROMPT_VERSION=candidate_graph_extraction_v1
PROCESSING_JOB_POLL_INTERVAL_SECONDS=2

API_PORT=8000
DASHBOARD_PORT=3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## FILE: backend/pyproject.toml
```
[build-system]
requires = ["hatchling>=1.27.0"]
build-backend = "hatchling.build"

[project]
name = "giraffegraph-core-backend"
version = "0.1.0"
description = "Generic graph production engine backend for GiraffeGraph Core."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
  "alembic>=1.15.0,<2.0.0",
  "fastapi>=0.115.0,<1.0.0",
  "neo4j>=6.0.0,<7.0.0",
  "pydantic>=2.10.0,<3.0.0",
  "pydantic-settings>=2.8.0,<3.0.0",
  "psycopg[binary]>=3.2.0,<4.0.0",
  "sqlalchemy>=2.0.0,<3.0.0",
  "uvicorn[standard]>=0.34.0,<1.0.0",
]

[project.optional-dependencies]
dev = [
  "httpx>=0.28.0,<1.0.0",
  "mypy>=1.15.0,<2.0.0",
  "pytest>=8.3.0,<9.0.0",
  "ruff>=0.11.0,<1.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/app"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_configs = true
```
