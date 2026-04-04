from dataclasses import dataclass

from app.application.ports.prompt_catalog import StructuredPromptDefinition
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
    CanonicalGraphRepository,
    ExtractionExecutionRepository,
    GraphDeltaRepository,
    PipelineDefinitionRepository,
    ProcessingJobQueueRepository,
    ProcessingJobRepository,
    ProcessingRunRepository,
    ProjectRepository,
    ReviewItemRepository,
    ReviewQueueRepository,
    SchemaRepository,
    SegmentRepository,
    SourceUnitRepository,
    StructuredPromptRepository,
    ValidationResultRepository,
)
from app.domain.exploration.entities import (
    CanonicalNodeDetail,
    CanonicalNodeView,
    CanonicalRelationDetail,
    CanonicalRelationEndpointView,
    CanonicalRelationView,
    CanonicalSegmentSupport,
    CanonicalSourceUnitRef,
    ConnectedRelationView,
    GraphOverview,
    NodeTypeCount,
)
from app.domain.extraction.entities import (
    CandidateNode,
    CandidateRelation,
    ExtractionExecution,
)
from app.domain.graph_commit.entities import CanonicalCommitBundle, GraphDelta
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.orchestration.entities import ProcessingJob
from app.domain.orchestration.lifecycle import mark_processing_job_running
from app.domain.orchestration.pipeline_definitions import PipelineDefinition
from app.domain.orchestration.queue_views import (
    ProcessingJobQueueRunEntry,
    ProjectProcessingJobQueue,
    filter_processing_jobs,
    sort_processing_jobs,
)
from app.domain.project.entities import Project
from app.domain.review.entities import ProjectReviewQueue, ReviewItem, ReviewQueueRunEntry
from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition, SchemaVersion
from app.domain.shared.enums import ProcessingJobType
from app.domain.shared.resolution import build_canonical_merge_key
from app.domain.validation.entities import ValidationResult
from app.infrastructure.persistence.memory.store import (
    InMemoryCanonicalNodeRecord,
    InMemoryCanonicalRelationRecord,
    InMemoryStore,
)
from app.infrastructure.persistence.review_queue_builders import (
    build_review_queue_item,
    filter_review_items,
    sort_review_items,
)


@dataclass(slots=True)
class InMemoryProjectRepository(ProjectRepository):
    store: InMemoryStore

    def add(self, project: Project) -> None:
        self.store.projects[project.project_id] = project

    def get(self, project_id: str) -> Project | None:
        return self.store.projects.get(project_id)

    def list(self) -> list[Project]:
        return sorted(self.store.projects.values(), key=lambda project: project.created_at)


@dataclass(slots=True)
class InMemorySchemaRepository(SchemaRepository):
    store: InMemoryStore

    def add_schema_version(self, schema_version: SchemaVersion) -> None:
        self.store.schema_versions[schema_version.schema_version_id] = schema_version
        self.store.node_types_by_schema.setdefault(schema_version.schema_version_id, [])
        self.store.relation_types_by_schema.setdefault(schema_version.schema_version_id, [])

    def get_schema_version(self, schema_version_id: str) -> SchemaVersion | None:
        return self.store.schema_versions.get(schema_version_id)

    def list_schema_versions(self, project_id: str) -> list[SchemaVersion]:
        schema_versions = [
            schema_version
            for schema_version in self.store.schema_versions.values()
            if schema_version.project_id == project_id
        ]
        return sorted(schema_versions, key=lambda schema_version: schema_version.version_no)

    def save_schema_version(self, schema_version: SchemaVersion) -> None:
        self.store.schema_versions[schema_version.schema_version_id] = schema_version

    def add_node_type(self, node_type: NodeTypeDefinition) -> None:
        node_types = self.store.node_types_by_schema.setdefault(node_type.schema_version_id, [])
        node_types.append(node_type)

    def list_node_types(self, schema_version_id: str) -> list[NodeTypeDefinition]:
        return sorted(
            self.store.node_types_by_schema.get(schema_version_id, []),
            key=lambda node_type: node_type.name.casefold(),
        )

    def add_relation_type(self, relation_type: RelationTypeDefinition) -> None:
        relation_types = self.store.relation_types_by_schema.setdefault(
            relation_type.schema_version_id,
            [],
        )
        relation_types.append(relation_type)

    def list_relation_types(self, schema_version_id: str) -> list[RelationTypeDefinition]:
        return sorted(
            self.store.relation_types_by_schema.get(schema_version_id, []),
            key=lambda relation_type: relation_type.name.casefold(),
        )

    def get_active_schema(self, project_id: str) -> SchemaVersion | None:
        for schema_version in self.list_schema_versions(project_id):
            if schema_version.status.value == "active":
                return schema_version
        return None


@dataclass(slots=True)
class InMemorySourceUnitRepository(SourceUnitRepository):
    store: InMemoryStore

    def add(self, source_unit: SourceUnit) -> None:
        self.store.source_units[source_unit.source_unit_id] = source_unit

    def get(self, source_unit_id: str) -> SourceUnit | None:
        return self.store.source_units.get(source_unit_id)

    def save(self, source_unit: SourceUnit) -> None:
        self.store.source_units[source_unit.source_unit_id] = source_unit

    def list_by_project(self, project_id: str) -> list[SourceUnit]:
        source_units = [
            source_unit
            for source_unit in self.store.source_units.values()
            if source_unit.project_id == project_id
        ]
        return sorted(
            source_units,
            key=lambda source_unit: (
                source_unit.sequence_no is None,
                source_unit.sequence_no or 0,
                source_unit.created_at,
                source_unit.title.casefold(),
            ),
        )


@dataclass(slots=True)
class InMemorySegmentRepository(SegmentRepository):
    store: InMemoryStore

    def replace_for_source_unit(self, source_unit_id: str, segments: list[Segment]) -> None:
        self.store.segments_by_source_unit[source_unit_id] = segments

    def list_by_source_unit(self, source_unit_id: str) -> list[Segment]:
        return sorted(
            self.store.segments_by_source_unit.get(source_unit_id, []),
            key=lambda segment: segment.segment_order,
        )


@dataclass(slots=True)
class InMemoryProcessingRunRepository(ProcessingRunRepository):
    store: InMemoryStore

    def add(self, run: ProcessingRun) -> None:
        self.store.processing_runs[run.run_id] = run

    def get(self, run_id: str) -> ProcessingRun | None:
        return self.store.processing_runs.get(run_id)

    def save(self, run: ProcessingRun) -> None:
        self.store.processing_runs[run.run_id] = run

    def list_by_project(self, project_id: str) -> list[ProcessingRun]:
        runs = [run for run in self.store.processing_runs.values() if run.project_id == project_id]
        return sorted(runs, key=lambda run: run.created_at, reverse=True)


@dataclass(slots=True)
class InMemoryPipelineDefinitionRepository(PipelineDefinitionRepository):
    store: InMemoryStore

    def add(self, pipeline_definition: PipelineDefinition) -> None:
        key = (
            pipeline_definition.schema_version_id,
            pipeline_definition.version.strip(),
        )
        self.store.pipeline_definitions[key] = pipeline_definition

    def get_by_schema_version_and_version(
        self,
        *,
        schema_version_id: str,
        version: str,
    ) -> PipelineDefinition | None:
        return self.store.pipeline_definitions.get((schema_version_id, version.strip()))

    def list_by_schema_version(self, schema_version_id: str) -> list[PipelineDefinition]:
        definitions = [
            pipeline_definition
            for pipeline_definition in self.store.pipeline_definitions.values()
            if pipeline_definition.schema_version_id == schema_version_id
        ]
        return sorted(
            definitions,
            key=lambda pipeline_definition: (
                pipeline_definition.created_at,
                pipeline_definition.version.casefold(),
            ),
        )


@dataclass(slots=True)
class InMemoryProcessingJobRepository(ProcessingJobRepository):
    store: InMemoryStore

    def add(self, job: ProcessingJob) -> None:
        self.store.processing_jobs[job.job_id] = job

    def get(self, job_id: str) -> ProcessingJob | None:
        return self.store.processing_jobs.get(job_id)

    def save(self, job: ProcessingJob) -> None:
        self.store.processing_jobs[job.job_id] = job

    def list_by_run(self, run_id: str) -> list[ProcessingJob]:
        jobs = [job for job in self.store.processing_jobs.values() if job.run_id == run_id]
        return sorted(jobs, key=lambda job: (job.created_at, job.job_id), reverse=True)

    def claim_next(
        self,
        *,
        job_type: ProcessingJobType | None = None,
        run_id: str | None = None,
    ) -> ProcessingJob | None:
        running_run_ids = {
            job.run_id
            for job in self.store.processing_jobs.values()
            if job.status.value == "running"
        }
        jobs = [
            job
            for job in self.store.processing_jobs.values()
            if job.status.value == "pending"
            and (job_type is None or job.job_type == job_type)
            and (run_id is None or job.run_id == run_id)
            and job.run_id not in running_run_ids
        ]
        jobs.sort(key=lambda job: (job.created_at, job.job_id))
        if not jobs:
            return None
        job = jobs[0]
        mark_processing_job_running(job)
        self.store.processing_jobs[job.job_id] = job
        return job


@dataclass(slots=True)
class InMemoryProcessingJobQueueRepository(ProcessingJobQueueRepository):
    store: InMemoryStore

    def get_project_processing_job_queue(
        self,
        project_id: str,
        *,
        status_filter: str,
        run_limit: int,
    ) -> ProjectProcessingJobQueue:
        all_run_entries: list[ProcessingJobQueueRunEntry] = []
        active_job_count = 0
        failed_job_count = 0
        succeeded_job_count = 0
        total_job_count = 0

        runs = [
            run for run in self.store.processing_runs.values() if run.project_id == project_id
        ]
        runs.sort(key=lambda run: run.created_at, reverse=True)

        for run in runs:
            source_unit = self.store.source_units.get(run.source_unit_id)
            if source_unit is None:
                continue

            all_run_jobs = sort_processing_jobs(
                [
                    job
                    for job in self.store.processing_jobs.values()
                    if job.run_id == run.run_id
                ]
            )
            run_active_job_count = sum(
                1
                for job in all_run_jobs
                if job.status.value in {"pending", "running"}
            )
            run_failed_job_count = sum(
                1 for job in all_run_jobs if job.status.value == "failed"
            )
            run_succeeded_job_count = sum(
                1 for job in all_run_jobs if job.status.value == "succeeded"
            )
            run_total_job_count = len(all_run_jobs)

            active_job_count += run_active_job_count
            failed_job_count += run_failed_job_count
            succeeded_job_count += run_succeeded_job_count
            total_job_count += run_total_job_count

            filtered_jobs = filter_processing_jobs(
                all_run_jobs,
                status_filter=status_filter,
            )
            if status_filter != "all" and not filtered_jobs:
                continue

            all_run_entries.append(
                ProcessingJobQueueRunEntry(
                    run=run,
                    source_unit=source_unit,
                    jobs=filtered_jobs,
                    active_job_count=run_active_job_count,
                    failed_job_count=run_failed_job_count,
                    total_job_count=run_total_job_count,
                )
            )

        filtered_run_count = len(all_run_entries)
        run_entries = all_run_entries[:run_limit]
        returned_job_count = sum(len(run_entry.jobs) for run_entry in run_entries)

        return ProjectProcessingJobQueue(
            project_id=project_id,
            run_entries=run_entries,
            status_filter=status_filter,
            run_limit=run_limit,
            active_job_count=active_job_count,
            failed_job_count=failed_job_count,
            succeeded_job_count=succeeded_job_count,
            total_job_count=total_job_count,
            filtered_run_count=filtered_run_count,
            returned_run_count=len(run_entries),
            returned_job_count=returned_job_count,
            has_more_runs=filtered_run_count > len(run_entries),
        )


@dataclass(slots=True)
class InMemoryStructuredPromptRepository(StructuredPromptRepository):
    store: InMemoryStore

    def upsert(self, prompt: StructuredPromptDefinition) -> None:
        key = (prompt.prompt_key.strip().casefold(), prompt.version.strip())
        self.store.structured_prompts[key] = prompt

    def get(
        self,
        *,
        prompt_key: str,
        version: str,
    ) -> StructuredPromptDefinition | None:
        key = (prompt_key.strip().casefold(), version.strip())
        return self.store.structured_prompts.get(key)

    def list(
        self,
        *,
        prompt_key: str | None = None,
    ) -> list[StructuredPromptDefinition]:
        prompts = list(self.store.structured_prompts.values())
        if prompt_key is not None:
            normalized_key = prompt_key.strip().casefold()
            prompts = [
                prompt
                for prompt in prompts
                if prompt.prompt_key.strip().casefold() == normalized_key
            ]
        return sorted(
            prompts,
            key=lambda prompt: (prompt.prompt_key.casefold(), prompt.version),
        )


@dataclass(slots=True)
class InMemoryCandidateNodeRepository(CandidateNodeRepository):
    store: InMemoryStore

    def add(self, candidate_node: CandidateNode) -> None:
        self.store.candidate_nodes[candidate_node.candidate_node_id] = candidate_node

    def get(self, candidate_node_id: str) -> CandidateNode | None:
        return self.store.candidate_nodes.get(candidate_node_id)

    def save(self, candidate_node: CandidateNode) -> None:
        self.store.candidate_nodes[candidate_node.candidate_node_id] = candidate_node

    def list_by_run(self, run_id: str) -> list[CandidateNode]:
        candidate_nodes = [
            candidate_node
            for candidate_node in self.store.candidate_nodes.values()
            if candidate_node.run_id == run_id
        ]
        return sorted(candidate_nodes, key=lambda candidate_node: candidate_node.candidate_node_id)


@dataclass(slots=True)
class InMemoryCandidateRelationRepository(CandidateRelationRepository):
    store: InMemoryStore

    def add(self, candidate_relation: CandidateRelation) -> None:
        self.store.candidate_relations[candidate_relation.candidate_relation_id] = (
            candidate_relation
        )

    def get(self, candidate_relation_id: str) -> CandidateRelation | None:
        return self.store.candidate_relations.get(candidate_relation_id)

    def save(self, candidate_relation: CandidateRelation) -> None:
        self.store.candidate_relations[candidate_relation.candidate_relation_id] = (
            candidate_relation
        )

    def list_by_run(self, run_id: str) -> list[CandidateRelation]:
        candidate_relations = [
            candidate_relation
            for candidate_relation in self.store.candidate_relations.values()
            if candidate_relation.run_id == run_id
        ]
        return sorted(
            candidate_relations,
            key=lambda candidate_relation: candidate_relation.candidate_relation_id,
        )


@dataclass(slots=True)
class InMemoryExtractionExecutionRepository(ExtractionExecutionRepository):
    store: InMemoryStore

    def add(self, execution: ExtractionExecution) -> None:
        self.store.extraction_executions[execution.execution_id] = execution

    def save(self, execution: ExtractionExecution) -> None:
        self.store.extraction_executions[execution.execution_id] = execution

    def list_by_run(self, run_id: str) -> list[ExtractionExecution]:
        executions = [
            execution
            for execution in self.store.extraction_executions.values()
            if execution.run_id == run_id
        ]
        return sorted(
            executions,
            key=lambda execution: (execution.started_at, execution.execution_id),
            reverse=True,
        )


@dataclass(slots=True)
class InMemoryValidationResultRepository(ValidationResultRepository):
    store: InMemoryStore

    def replace_for_run(self, run_id: str, results: list[ValidationResult]) -> None:
        self.store.validation_results_by_run[run_id] = results

    def list_by_run(self, run_id: str) -> list[ValidationResult]:
        return list(self.store.validation_results_by_run.get(run_id, []))


@dataclass(slots=True)
class InMemoryReviewItemRepository(ReviewItemRepository):
    store: InMemoryStore

    def get(self, review_item_id: str) -> ReviewItem | None:
        for items in self.store.review_items_by_run.values():
            for item in items:
                if item.review_item_id == review_item_id:
                    return item
        return None

    def save(self, item: ReviewItem) -> None:
        items = self.store.review_items_by_run.setdefault(item.run_id, [])
        for index, existing in enumerate(items):
            if existing.review_item_id == item.review_item_id:
                items[index] = item
                return
        items.append(item)

    def replace_for_run(self, run_id: str, items: list[ReviewItem]) -> None:
        self.store.review_items_by_run[run_id] = items

    def list_by_run(self, run_id: str) -> list[ReviewItem]:
        return list(self.store.review_items_by_run.get(run_id, []))


@dataclass(slots=True)
class InMemoryReviewQueueRepository(ReviewQueueRepository):
    store: InMemoryStore

    def get_project_review_queue(
        self,
        project_id: str,
        *,
        status_filter: str,
        run_limit: int,
    ) -> ProjectReviewQueue:
        all_run_entries: list[ReviewQueueRunEntry] = []
        open_review_count = 0
        total_review_count = 0

        runs = [
            run for run in self.store.processing_runs.values() if run.project_id == project_id
        ]
        runs.sort(key=lambda run: run.created_at, reverse=True)

        for run in runs:
            source_unit = self.store.source_units.get(run.source_unit_id)
            if source_unit is None:
                continue

            candidate_node_by_id = {
                candidate.candidate_node_id: candidate
                for candidate in self.store.candidate_nodes.values()
                if candidate.run_id == run.run_id
            }
            candidate_relation_by_id = {
                candidate.candidate_relation_id: candidate
                for candidate in self.store.candidate_relations.values()
                if candidate.run_id == run.run_id
            }
            segment_by_id = {
                segment.segment_id: segment
                for segment in self.store.segments_by_source_unit.get(
                    source_unit.source_unit_id,
                    [],
                )
            }

            all_review_items = list(self.store.review_items_by_run.get(run.run_id, []))
            run_open_review_count = sum(
                1 for review_item in all_review_items if review_item.status.value == "open"
            )
            run_total_review_count = len(all_review_items)
            open_review_count += run_open_review_count
            total_review_count += run_total_review_count

            filtered_review_items = sort_review_items(
                filter_review_items(all_review_items, status_filter=status_filter)
            )
            if status_filter != "all" and not filtered_review_items:
                continue

            queue_items = []
            for review_item in filtered_review_items:
                candidate_node = (
                    candidate_node_by_id.get(review_item.item_ref)
                    if review_item.item_type == "candidate_node"
                    else None
                )
                candidate_relation = (
                    candidate_relation_by_id.get(review_item.item_ref)
                    if review_item.item_type == "candidate_relation"
                    else None
                )
                queue_items.append(
                    build_review_queue_item(
                        review_item,
                        candidate_node=candidate_node,
                        candidate_relation=candidate_relation,
                        candidate_node_by_id=candidate_node_by_id,
                        segment_by_id=segment_by_id,
                    )
                )

            all_run_entries.append(
                ReviewQueueRunEntry(
                    run=run,
                    source_unit=source_unit,
                    review_items=queue_items,
                    open_review_count=run_open_review_count,
                    total_review_count=run_total_review_count,
                )
            )

        filtered_run_count = len(all_run_entries)
        run_entries = all_run_entries[:run_limit]
        returned_review_count = sum(len(run_entry.review_items) for run_entry in run_entries)

        return ProjectReviewQueue(
            project_id=project_id,
            run_entries=run_entries,
            status_filter=status_filter,
            run_limit=run_limit,
            open_review_count=open_review_count,
            total_review_count=total_review_count,
            filtered_run_count=filtered_run_count,
            returned_run_count=len(run_entries),
            returned_review_count=returned_review_count,
            has_more_runs=filtered_run_count > len(run_entries),
        )


@dataclass(slots=True)
class InMemoryGraphDeltaRepository(GraphDeltaRepository):
    store: InMemoryStore

    def add(self, delta: GraphDelta) -> None:
        self.store.graph_deltas_by_run[delta.run_id] = delta

    def get_by_run(self, run_id: str) -> GraphDelta | None:
        return self.store.graph_deltas_by_run.get(run_id)


@dataclass(slots=True)
class InMemoryCanonicalGraphRepository(CanonicalGraphRepository):
    store: InMemoryStore

    def commit_bundle(self, bundle: CanonicalCommitBundle) -> GraphDelta:
        delta = bundle.delta
        node_refs_by_candidate: dict[str, tuple[str, str]] = {}

        nodes_created = 0
        nodes_merged = 0
        for candidate_node in bundle.candidate_nodes:
            merge_key = build_canonical_merge_key(
                merge_key_payload=candidate_node.merge_key_payload,
                fallback_payload={"candidate_node_id": candidate_node.candidate_node_id},
            )
            node_record_key = (delta.project_id, candidate_node.node_type, merge_key)
            node_record = self.store.canonical_nodes.get(node_record_key)
            created = node_record is None
            if node_record is None:
                node_record = InMemoryCanonicalNodeRecord(
                    project_id=delta.project_id,
                    node_type=candidate_node.node_type,
                    merge_key=merge_key,
                )
                self.store.canonical_nodes[node_record_key] = node_record

            node_record.properties = dict(candidate_node.properties)
            node_record.source_unit_ids.add(bundle.source_unit.source_unit_id)
            node_record.segment_ids.update(
                evidence_ref.segment_id for evidence_ref in candidate_node.evidence_refs
            )
            node_record.last_run_id = delta.run_id
            node_record.updated_at = delta.created_at.isoformat()
            node_refs_by_candidate[candidate_node.candidate_node_id] = (
                candidate_node.node_type,
                merge_key,
            )
            if created:
                nodes_created += 1
            else:
                nodes_merged += 1

        relations_created = 0
        relations_merged = 0
        for candidate_relation in bundle.candidate_relations:
            from_ref = node_refs_by_candidate.get(candidate_relation.from_candidate_ref)
            to_ref = node_refs_by_candidate.get(candidate_relation.to_candidate_ref)
            if from_ref is None or to_ref is None:
                raise ValueError(
                    "Canonical commit received relation candidates without canonical node refs."
                )

            relation_record_key = (
                delta.project_id,
                candidate_relation.relation_type,
                from_ref[0],
                from_ref[1],
                to_ref[0],
                to_ref[1],
            )
            relation_record = self.store.canonical_relations.get(relation_record_key)
            created = relation_record is None
            if relation_record is None:
                relation_record = InMemoryCanonicalRelationRecord(
                    project_id=delta.project_id,
                    relation_type=candidate_relation.relation_type,
                    from_node_type=from_ref[0],
                    from_merge_key=from_ref[1],
                    to_node_type=to_ref[0],
                    to_merge_key=to_ref[1],
                )
                self.store.canonical_relations[relation_record_key] = relation_record

            relation_record.properties = dict(candidate_relation.properties)
            relation_record.source_unit_ids.add(bundle.source_unit.source_unit_id)
            relation_record.segment_ids.update(
                evidence_ref.segment_id for evidence_ref in candidate_relation.evidence_refs
            )
            relation_record.last_run_id = delta.run_id
            relation_record.updated_at = delta.created_at.isoformat()
            if created:
                relations_created += 1
            else:
                relations_merged += 1

        delta.nodes_created = nodes_created
        delta.nodes_merged = nodes_merged
        delta.relations_created = relations_created
        delta.relations_merged = relations_merged
        delta.review_count = 0
        return delta

    def get_project_overview(self, project_id: str) -> GraphOverview:
        project_nodes = [
            record
            for record in self.store.canonical_nodes.values()
            if record.project_id == project_id
        ]
        project_relations = [
            record
            for record in self.store.canonical_relations.values()
            if record.project_id == project_id
        ]
        node_type_counts: dict[str, int] = {}
        for record in project_nodes:
            node_type_counts[record.node_type] = node_type_counts.get(record.node_type, 0) + 1
        return GraphOverview(
            project_id=project_id,
            node_count=len(project_nodes),
            relation_count=len(project_relations),
            node_type_counts=[
                NodeTypeCount(node_type=node_type, count=count)
                for node_type, count in sorted(node_type_counts.items())
            ],
        )

    def list_nodes(
        self,
        project_id: str,
        *,
        node_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalNodeView]:
        normalized_type = node_type.casefold() if node_type is not None else None
        nodes = [
            self._to_canonical_node_view(record)
            for record in self.store.canonical_nodes.values()
            if record.project_id == project_id
            and (
                normalized_type is None or record.node_type.casefold() == normalized_type
            )
        ]
        nodes.sort(key=lambda node: (node.node_type.casefold(), node.merge_key))
        nodes.sort(key=lambda node: node.updated_at or "", reverse=True)
        return nodes[:limit]

    def list_relations(
        self,
        project_id: str,
        *,
        relation_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalRelationView]:
        normalized_type = relation_type.casefold() if relation_type is not None else None
        relations = [
            self._to_canonical_relation_view(record)
            for record in self.store.canonical_relations.values()
            if record.project_id == project_id
            and (
                normalized_type is None
                or record.relation_type.casefold() == normalized_type
            )
        ]
        relations.sort(
            key=lambda relation: (
                relation.relation_type.casefold(),
                relation.from_merge_key,
                relation.to_merge_key,
            )
        )
        relations.sort(key=lambda relation: relation.updated_at or "", reverse=True)
        return relations[:limit]

    def get_node_detail(
        self,
        project_id: str,
        *,
        node_type: str,
        merge_key: str,
    ) -> CanonicalNodeDetail | None:
        record = self.store.canonical_nodes.get((project_id, node_type, merge_key))
        if record is None:
            return None
        return CanonicalNodeDetail(
            node=self._to_canonical_node_view(record),
            source_units=self._source_unit_refs(record.source_unit_ids),
            supporting_segments=self._segment_support(record.segment_ids),
            connected_relations=self._connected_relations(
                project_id=project_id,
                node_type=node_type,
                merge_key=merge_key,
            ),
        )

    def get_relation_detail(
        self,
        project_id: str,
        *,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
    ) -> CanonicalRelationDetail | None:
        record = self.store.canonical_relations.get(
            (
                project_id,
                relation_type,
                from_node_type,
                from_merge_key,
                to_node_type,
                to_merge_key,
            )
        )
        if record is None:
            return None

        from_node = self.store.canonical_nodes.get(
            (project_id, from_node_type, from_merge_key)
        )
        to_node = self.store.canonical_nodes.get((project_id, to_node_type, to_merge_key))
        if from_node is None or to_node is None:
            return None

        return CanonicalRelationDetail(
            relation=self._to_canonical_relation_view(record),
            from_node=CanonicalRelationEndpointView(
                node_type=from_node.node_type,
                merge_key=from_node.merge_key,
                properties=dict(from_node.properties),
            ),
            to_node=CanonicalRelationEndpointView(
                node_type=to_node.node_type,
                merge_key=to_node.merge_key,
                properties=dict(to_node.properties),
            ),
            source_units=self._source_unit_refs(record.source_unit_ids),
            supporting_segments=self._segment_support(record.segment_ids),
        )

    def _to_canonical_node_view(
        self,
        record: InMemoryCanonicalNodeRecord,
    ) -> CanonicalNodeView:
        source_unit_id = next(iter(sorted(record.source_unit_ids)), None)
        return CanonicalNodeView(
            project_id=record.project_id,
            node_type=record.node_type,
            merge_key=record.merge_key,
            properties=dict(record.properties),
            source_unit_id=source_unit_id,
            last_run_id=record.last_run_id,
            updated_at=record.updated_at,
        )

    def _to_canonical_relation_view(
        self,
        record: InMemoryCanonicalRelationRecord,
    ) -> CanonicalRelationView:
        source_unit_id = next(iter(sorted(record.source_unit_ids)), None)
        return CanonicalRelationView(
            project_id=record.project_id,
            relation_type=record.relation_type,
            from_node_type=record.from_node_type,
            from_merge_key=record.from_merge_key,
            to_node_type=record.to_node_type,
            to_merge_key=record.to_merge_key,
            properties=dict(record.properties),
            source_unit_id=source_unit_id,
            last_run_id=record.last_run_id,
            updated_at=record.updated_at,
        )

    def _source_unit_refs(self, source_unit_ids: set[str]) -> list[CanonicalSourceUnitRef]:
        source_units = [
            source_unit
            for source_unit_id in source_unit_ids
            if (source_unit := self.store.source_units.get(source_unit_id)) is not None
        ]
        source_units.sort(
            key=lambda source_unit: (
                source_unit.sequence_no is None,
                source_unit.sequence_no or 0,
                source_unit.created_at,
                source_unit.source_unit_id,
            )
        )
        return [
            CanonicalSourceUnitRef(
                source_unit_id=source_unit.source_unit_id,
                title=source_unit.title,
                source_type=source_unit.source_type,
                sequence_no=source_unit.sequence_no,
            )
            for source_unit in source_units
        ]

    def _segment_support(self, segment_ids: set[str]) -> list[CanonicalSegmentSupport]:
        segment_by_id = {
            segment.segment_id: segment
            for segments in self.store.segments_by_source_unit.values()
            for segment in segments
        }
        segments = [
            segment
            for segment_id in segment_ids
            if (segment := segment_by_id.get(segment_id)) is not None
        ]
        segments.sort(
            key=lambda segment: (
                segment.source_unit_id,
                segment.segment_order,
                segment.segment_id,
            )
        )
        return [
            CanonicalSegmentSupport(
                segment_id=segment.segment_id,
                source_unit_id=segment.source_unit_id,
                segment_order=segment.segment_order,
                text=segment.text,
            )
            for segment in segments
        ]

    def _connected_relations(
        self,
        *,
        project_id: str,
        node_type: str,
        merge_key: str,
    ) -> list[ConnectedRelationView]:
        connected: list[ConnectedRelationView] = []
        for record in self.store.canonical_relations.values():
            if record.project_id != project_id:
                continue

            direction: str | None = None
            other_node_type: str
            other_merge_key: str
            if (
                record.from_node_type == node_type
                and record.from_merge_key == merge_key
            ):
                direction = "outgoing"
                other_node_type = record.to_node_type
                other_merge_key = record.to_merge_key
            elif (
                record.to_node_type == node_type
                and record.to_merge_key == merge_key
            ):
                direction = "incoming"
                other_node_type = record.from_node_type
                other_merge_key = record.from_merge_key
            else:
                continue

            other_record = self.store.canonical_nodes.get(
                (project_id, other_node_type, other_merge_key)
            )
            connected.append(
                ConnectedRelationView(
                    relation_type=record.relation_type,
                    direction=direction,
                    other_node_type=other_node_type,
                    other_merge_key=other_merge_key,
                    other_node_properties=(
                        dict(other_record.properties) if other_record is not None else {}
                    ),
                    properties=dict(record.properties),
                    updated_at=record.updated_at,
                )
            )
        connected.sort(
            key=lambda relation: (
                relation.relation_type.casefold(),
                relation.other_node_type.casefold(),
                relation.other_merge_key,
            )
        )
        connected.sort(key=lambda relation: relation.updated_at or "", reverse=True)
        return connected
