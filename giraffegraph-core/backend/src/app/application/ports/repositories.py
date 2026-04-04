from typing import Protocol

from app.application.ports.prompt_catalog import StructuredPromptDefinition
from app.domain.exploration.entities import (
    CanonicalNodeDetail,
    CanonicalNodeView,
    CanonicalRelationDetail,
    CanonicalRelationView,
    GraphOverview,
)
from app.domain.extraction.entities import (
    CandidateNode,
    CandidateRelation,
    ExtractionExecution,
)
from app.domain.graph_commit.entities import CanonicalCommitBundle, GraphDelta
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.orchestration.entities import ProcessingJob
from app.domain.orchestration.pipeline_definitions import PipelineDefinition
from app.domain.orchestration.queue_views import ProjectProcessingJobQueue
from app.domain.project.entities import Project
from app.domain.review.entities import ProjectReviewQueue, ReviewItem
from app.domain.schema.entities import (
    NodeTypeDefinition,
    RelationTypeDefinition,
    SchemaVersion,
)
from app.domain.shared.enums import ProcessingJobType
from app.domain.validation.entities import ValidationResult


class ProjectRepository(Protocol):
    def add(self, project: Project) -> None: ...

    def get(self, project_id: str) -> Project | None: ...

    def list(self) -> list[Project]: ...


class SchemaRepository(Protocol):
    def add_schema_version(self, schema_version: SchemaVersion) -> None: ...

    def get_schema_version(self, schema_version_id: str) -> SchemaVersion | None: ...

    def list_schema_versions(self, project_id: str) -> list[SchemaVersion]: ...

    def save_schema_version(self, schema_version: SchemaVersion) -> None: ...

    def add_node_type(self, node_type: NodeTypeDefinition) -> None: ...

    def list_node_types(self, schema_version_id: str) -> list[NodeTypeDefinition]: ...

    def add_relation_type(self, relation_type: RelationTypeDefinition) -> None: ...

    def list_relation_types(self, schema_version_id: str) -> list[RelationTypeDefinition]: ...

    def get_active_schema(self, project_id: str) -> SchemaVersion | None: ...


class SourceUnitRepository(Protocol):
    def add(self, source_unit: SourceUnit) -> None: ...

    def get(self, source_unit_id: str) -> SourceUnit | None: ...

    def save(self, source_unit: SourceUnit) -> None: ...

    def list_by_project(self, project_id: str) -> list[SourceUnit]: ...


class SegmentRepository(Protocol):
    def replace_for_source_unit(self, source_unit_id: str, segments: list[Segment]) -> None: ...

    def list_by_source_unit(self, source_unit_id: str) -> list[Segment]: ...


class ProcessingRunRepository(Protocol):
    def add(self, run: ProcessingRun) -> None: ...

    def get(self, run_id: str) -> ProcessingRun | None: ...

    def save(self, run: ProcessingRun) -> None: ...

    def list_by_project(self, project_id: str) -> list[ProcessingRun]: ...


class PipelineDefinitionRepository(Protocol):
    def add(self, pipeline_definition: PipelineDefinition) -> None: ...

    def get_by_schema_version_and_version(
        self,
        *,
        schema_version_id: str,
        version: str,
    ) -> PipelineDefinition | None: ...

    def list_by_schema_version(self, schema_version_id: str) -> list[PipelineDefinition]: ...


class StructuredPromptRepository(Protocol):
    def upsert(self, prompt: StructuredPromptDefinition) -> None: ...

    def get(
        self,
        *,
        prompt_key: str,
        version: str,
    ) -> StructuredPromptDefinition | None: ...

    def list(
        self,
        *,
        prompt_key: str | None = None,
    ) -> list[StructuredPromptDefinition]: ...


class CandidateNodeRepository(Protocol):
    def add(self, candidate_node: CandidateNode) -> None: ...

    def get(self, candidate_node_id: str) -> CandidateNode | None: ...

    def save(self, candidate_node: CandidateNode) -> None: ...

    def list_by_run(self, run_id: str) -> list[CandidateNode]: ...


class CandidateRelationRepository(Protocol):
    def add(self, candidate_relation: CandidateRelation) -> None: ...

    def get(self, candidate_relation_id: str) -> CandidateRelation | None: ...

    def save(self, candidate_relation: CandidateRelation) -> None: ...

    def list_by_run(self, run_id: str) -> list[CandidateRelation]: ...


class ExtractionExecutionRepository(Protocol):
    def add(self, execution: ExtractionExecution) -> None: ...

    def save(self, execution: ExtractionExecution) -> None: ...

    def list_by_run(self, run_id: str) -> list[ExtractionExecution]: ...


class ProcessingJobRepository(Protocol):
    def add(self, job: ProcessingJob) -> None: ...

    def get(self, job_id: str) -> ProcessingJob | None: ...

    def save(self, job: ProcessingJob) -> None: ...

    def list_by_run(self, run_id: str) -> list[ProcessingJob]: ...

    def claim_next(
        self,
        *,
        job_type: ProcessingJobType | None = None,
        run_id: str | None = None,
    ) -> ProcessingJob | None: ...


class ProcessingJobQueueRepository(Protocol):
    def get_project_processing_job_queue(
        self,
        project_id: str,
        *,
        status_filter: str,
        run_limit: int,
    ) -> ProjectProcessingJobQueue: ...


class ValidationResultRepository(Protocol):
    def replace_for_run(self, run_id: str, results: list[ValidationResult]) -> None: ...

    def list_by_run(self, run_id: str) -> list[ValidationResult]: ...


class ReviewItemRepository(Protocol):
    def get(self, review_item_id: str) -> ReviewItem | None: ...

    def save(self, item: ReviewItem) -> None: ...

    def replace_for_run(self, run_id: str, items: list[ReviewItem]) -> None: ...

    def list_by_run(self, run_id: str) -> list[ReviewItem]: ...


class ReviewQueueRepository(Protocol):
    def get_project_review_queue(
        self,
        project_id: str,
        *,
        status_filter: str,
        run_limit: int,
    ) -> ProjectReviewQueue: ...


class GraphDeltaRepository(Protocol):
    def add(self, delta: GraphDelta) -> None: ...

    def get_by_run(self, run_id: str) -> GraphDelta | None: ...


class CanonicalGraphRepository(Protocol):
    def commit_bundle(self, bundle: CanonicalCommitBundle) -> GraphDelta: ...

    def get_project_overview(self, project_id: str) -> GraphOverview: ...

    def list_nodes(
        self,
        project_id: str,
        *,
        node_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalNodeView]: ...

    def list_relations(
        self,
        project_id: str,
        *,
        relation_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalRelationView]: ...

    def get_node_detail(
        self,
        project_id: str,
        *,
        node_type: str,
        merge_key: str,
    ) -> CanonicalNodeDetail | None: ...

    def get_relation_detail(
        self,
        project_id: str,
        *,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
    ) -> CanonicalRelationDetail | None: ...
