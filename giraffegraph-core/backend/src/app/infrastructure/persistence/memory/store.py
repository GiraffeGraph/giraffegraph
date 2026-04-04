from dataclasses import dataclass, field

from app.application.ports.prompt_catalog import StructuredPromptDefinition
from app.domain.extraction.entities import CandidateNode, CandidateRelation, ExtractionExecution
from app.domain.graph_commit.entities import GraphDelta
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.orchestration.entities import ProcessingJob
from app.domain.orchestration.pipeline_definitions import PipelineDefinition
from app.domain.project.entities import Project
from app.domain.review.entities import ReviewItem
from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition, SchemaVersion
from app.domain.validation.entities import ValidationResult


@dataclass(slots=True)
class InMemoryCanonicalNodeRecord:
    project_id: str
    node_type: str
    merge_key: str
    properties: dict[str, object] = field(default_factory=dict)
    source_unit_ids: set[str] = field(default_factory=set)
    segment_ids: set[str] = field(default_factory=set)
    last_run_id: str | None = None
    updated_at: str | None = None


@dataclass(slots=True)
class InMemoryCanonicalRelationRecord:
    project_id: str
    relation_type: str
    from_node_type: str
    from_merge_key: str
    to_node_type: str
    to_merge_key: str
    properties: dict[str, object] = field(default_factory=dict)
    source_unit_ids: set[str] = field(default_factory=set)
    segment_ids: set[str] = field(default_factory=set)
    last_run_id: str | None = None
    updated_at: str | None = None


@dataclass(slots=True)
class InMemoryStore:
    projects: dict[str, Project] = field(default_factory=dict)
    schema_versions: dict[str, SchemaVersion] = field(default_factory=dict)
    node_types_by_schema: dict[str, list[NodeTypeDefinition]] = field(default_factory=dict)
    relation_types_by_schema: dict[str, list[RelationTypeDefinition]] = field(default_factory=dict)
    source_units: dict[str, SourceUnit] = field(default_factory=dict)
    segments_by_source_unit: dict[str, list[Segment]] = field(default_factory=dict)
    processing_runs: dict[str, ProcessingRun] = field(default_factory=dict)
    pipeline_definitions: dict[tuple[str, str], PipelineDefinition] = field(default_factory=dict)
    processing_jobs: dict[str, ProcessingJob] = field(default_factory=dict)
    structured_prompts: dict[tuple[str, str], StructuredPromptDefinition] = field(
        default_factory=dict
    )
    candidate_nodes: dict[str, CandidateNode] = field(default_factory=dict)
    candidate_relations: dict[str, CandidateRelation] = field(default_factory=dict)
    extraction_executions: dict[str, ExtractionExecution] = field(default_factory=dict)
    validation_results_by_run: dict[str, list[ValidationResult]] = field(default_factory=dict)
    review_items_by_run: dict[str, list[ReviewItem]] = field(default_factory=dict)
    graph_deltas_by_run: dict[str, GraphDelta] = field(default_factory=dict)
    canonical_nodes: dict[tuple[str, str, str], InMemoryCanonicalNodeRecord] = field(
        default_factory=dict
    )
    canonical_relations: dict[
        tuple[str, str, str, str, str, str],
        InMemoryCanonicalRelationRecord,
    ] = field(default_factory=dict)
