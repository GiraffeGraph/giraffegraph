from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased, selectinload, sessionmaker

from app.application.ports.prompt_catalog import StructuredPromptDefinition
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
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
from app.domain.extraction.entities import (
    CandidateNode,
    CandidateRelation,
    EvidenceRef,
    ExtractionExecution,
)
from app.domain.graph_commit.entities import GraphDelta
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.orchestration.entities import ProcessingJob
from app.domain.orchestration.lifecycle import mark_processing_job_running
from app.domain.orchestration.pipeline_definitions import (
    PipelineDefinition,
    PipelineStepDefinition,
)
from app.domain.orchestration.queue_views import (
    ProcessingJobQueueRunEntry,
    ProjectProcessingJobQueue,
    filter_processing_jobs,
    sort_processing_jobs,
)
from app.domain.project.entities import Project
from app.domain.review.entities import ProjectReviewQueue, ReviewItem, ReviewQueueRunEntry
from app.domain.schema.entities import (
    NodeTypeDefinition,
    PropertyDefinition,
    RelationTypeDefinition,
    SchemaVersion,
)
from app.domain.shared.enums import ProcessingJobStatus, ProcessingJobType, SchemaStatus
from app.domain.validation.entities import ValidationResult
from app.infrastructure.persistence.postgres.models import (
    CandidateNodeModel,
    CandidateRelationModel,
    ExtractionExecutionModel,
    GraphDeltaModel,
    NodeTypeModel,
    PipelineDefinitionModel,
    ProcessingJobModel,
    ProcessingRunModel,
    ProjectModel,
    PropertyDefinitionModel,
    RelationTypeModel,
    ReviewItemModel,
    SchemaVersionModel,
    SegmentModel,
    SourceUnitModel,
    StructuredPromptModel,
    ValidationResultModel,
)
from app.infrastructure.persistence.review_queue_builders import (
    build_review_queue_item,
    filter_review_items,
    sort_review_items,
)


def to_processing_job_domain(model: ProcessingJobModel) -> ProcessingJob:
    return ProcessingJob(
        job_id=model.job_id,
        project_id=model.project_id,
        run_id=model.run_id,
        source_unit_id=model.source_unit_id,
        job_type=model.job_type,
        status=model.status,
        payload_json=model.payload_json,
        output_json=model.output_json,
        error_message=model.error_message,
        attempt_count=model.attempt_count,
        created_at=model.created_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
    )


@dataclass(slots=True)
class PostgresProjectRepository(ProjectRepository):
    session_factory: sessionmaker[Session]

    def add(self, project: Project) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(project))
            session.commit()

    def get(self, project_id: str) -> Project | None:
        with self.session_factory() as session:
            model = session.get(ProjectModel, project_id)
            return None if model is None else self._to_domain(model)

    def list(self) -> list[Project]:
        with self.session_factory() as session:
            statement = select(ProjectModel).order_by(ProjectModel.created_at.asc())
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, project: Project) -> ProjectModel:
        return ProjectModel(
            project_id=project.project_id,
            name=project.name,
            description=project.description,
            template_id=project.template_id,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def _to_domain(self, model: ProjectModel) -> Project:
        return Project(
            project_id=model.project_id,
            name=model.name,
            description=model.description,
            template_id=model.template_id,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@dataclass(slots=True)
class PostgresSchemaRepository(SchemaRepository):
    session_factory: sessionmaker[Session]

    def add_schema_version(self, schema_version: SchemaVersion) -> None:
        with self.session_factory() as session:
            session.add(self._to_schema_version_model(schema_version))
            session.commit()

    def get_schema_version(self, schema_version_id: str) -> SchemaVersion | None:
        with self.session_factory() as session:
            model = session.get(SchemaVersionModel, schema_version_id)
            return None if model is None else self._to_schema_version_domain(model)

    def list_schema_versions(self, project_id: str) -> list[SchemaVersion]:
        with self.session_factory() as session:
            statement = (
                select(SchemaVersionModel)
                .where(SchemaVersionModel.project_id == project_id)
                .order_by(SchemaVersionModel.version_no.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_schema_version_domain(model) for model in models]

    def save_schema_version(self, schema_version: SchemaVersion) -> None:
        with self.session_factory() as session:
            model = session.get(SchemaVersionModel, schema_version.schema_version_id)
            if model is None:
                session.add(self._to_schema_version_model(schema_version))
            else:
                model.project_id = schema_version.project_id
                model.version_no = schema_version.version_no
                model.status = schema_version.status
                model.notes = schema_version.notes
                model.created_at = schema_version.created_at
                model.activated_at = schema_version.activated_at
            session.commit()

    def add_node_type(self, node_type: NodeTypeDefinition) -> None:
        with self.session_factory() as session:
            session.add(self._to_node_type_model(node_type))
            session.commit()

    def list_node_types(self, schema_version_id: str) -> list[NodeTypeDefinition]:
        with self.session_factory() as session:
            statement = (
                select(NodeTypeModel)
                .where(NodeTypeModel.schema_version_id == schema_version_id)
                .options(selectinload(NodeTypeModel.properties))
                .order_by(NodeTypeModel.name.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_node_type_domain(model) for model in models]

    def add_relation_type(self, relation_type: RelationTypeDefinition) -> None:
        with self.session_factory() as session:
            session.add(self._to_relation_type_model(relation_type))
            session.commit()

    def list_relation_types(self, schema_version_id: str) -> list[RelationTypeDefinition]:
        with self.session_factory() as session:
            statement = (
                select(RelationTypeModel)
                .where(RelationTypeModel.schema_version_id == schema_version_id)
                .options(selectinload(RelationTypeModel.properties))
                .order_by(RelationTypeModel.name.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_relation_type_domain(model) for model in models]

    def get_active_schema(self, project_id: str) -> SchemaVersion | None:
        with self.session_factory() as session:
            statement = (
                select(SchemaVersionModel)
                .where(SchemaVersionModel.project_id == project_id)
                .where(SchemaVersionModel.status == SchemaStatus.ACTIVE)
                .order_by(SchemaVersionModel.version_no.desc())
            )
            model = session.scalars(statement).first()
            return None if model is None else self._to_schema_version_domain(model)

    def _to_schema_version_model(self, schema_version: SchemaVersion) -> SchemaVersionModel:
        return SchemaVersionModel(
            schema_version_id=schema_version.schema_version_id,
            project_id=schema_version.project_id,
            version_no=schema_version.version_no,
            status=schema_version.status,
            notes=schema_version.notes,
            created_at=schema_version.created_at,
            activated_at=schema_version.activated_at,
        )

    def _to_node_type_model(self, node_type: NodeTypeDefinition) -> NodeTypeModel:
        return NodeTypeModel(
            node_type_id=node_type.node_type_id,
            schema_version_id=node_type.schema_version_id,
            name=node_type.name,
            display_name=node_type.display_name,
            description=node_type.description,
            is_core=node_type.is_core,
            merge_keys=node_type.merge_keys,
            confidence_threshold=node_type.confidence_threshold,
            aliases=node_type.aliases,
            extraction_hints=node_type.extraction_hints,
            is_active=node_type.is_active,
            properties=[
                self._to_property_model(
                    property_definition,
                    schema_version_id=node_type.schema_version_id,
                    node_type_id=node_type.node_type_id,
                    relation_type_id=None,
                )
                for property_definition in node_type.properties
            ],
        )

    def _to_relation_type_model(self, relation_type: RelationTypeDefinition) -> RelationTypeModel:
        return RelationTypeModel(
            relation_type_id=relation_type.relation_type_id,
            schema_version_id=relation_type.schema_version_id,
            name=relation_type.name,
            from_type=relation_type.from_type,
            to_type=relation_type.to_type,
            description=relation_type.description,
            directional=relation_type.directional,
            aliases=relation_type.aliases,
            extraction_hints=relation_type.extraction_hints,
            required_properties=relation_type.required_properties,
            confidence_threshold=relation_type.confidence_threshold,
            is_active=relation_type.is_active,
            properties=[
                self._to_property_model(
                    property_definition,
                    schema_version_id=relation_type.schema_version_id,
                    node_type_id=None,
                    relation_type_id=relation_type.relation_type_id,
                )
                for property_definition in relation_type.properties
            ],
        )

    def _to_property_model(
        self,
        property_definition: PropertyDefinition,
        *,
        schema_version_id: str,
        node_type_id: str | None,
        relation_type_id: str | None,
    ) -> PropertyDefinitionModel:
        return PropertyDefinitionModel(
            property_id=property_definition.property_id,
            schema_version_id=schema_version_id,
            owner_kind=property_definition.owner_kind,
            owner_type_name=property_definition.owner_type_name,
            node_type_id=node_type_id,
            relation_type_id=relation_type_id,
            name=property_definition.name,
            data_type=property_definition.data_type,
            required=property_definition.required,
            description=property_definition.description,
            default_value=property_definition.default_value,
            enum_values=property_definition.enum_values,
        )

    def _to_schema_version_domain(self, model: SchemaVersionModel) -> SchemaVersion:
        return SchemaVersion(
            schema_version_id=model.schema_version_id,
            project_id=model.project_id,
            version_no=model.version_no,
            status=model.status,
            notes=model.notes,
            created_at=model.created_at,
            activated_at=model.activated_at,
        )

    def _to_node_type_domain(self, model: NodeTypeModel) -> NodeTypeDefinition:
        return NodeTypeDefinition(
            node_type_id=model.node_type_id,
            schema_version_id=model.schema_version_id,
            name=model.name,
            display_name=model.display_name,
            description=model.description,
            is_core=model.is_core,
            merge_keys=model.merge_keys,
            confidence_threshold=model.confidence_threshold,
            aliases=model.aliases,
            extraction_hints=model.extraction_hints,
            properties=[self._to_property_domain(item) for item in model.properties],
            is_active=model.is_active,
        )

    def _to_relation_type_domain(self, model: RelationTypeModel) -> RelationTypeDefinition:
        return RelationTypeDefinition(
            relation_type_id=model.relation_type_id,
            schema_version_id=model.schema_version_id,
            name=model.name,
            from_type=model.from_type,
            to_type=model.to_type,
            description=model.description,
            directional=model.directional,
            aliases=model.aliases,
            extraction_hints=model.extraction_hints,
            required_properties=model.required_properties,
            properties=[self._to_property_domain(item) for item in model.properties],
            confidence_threshold=model.confidence_threshold,
            is_active=model.is_active,
        )

    def _to_property_domain(self, model: PropertyDefinitionModel) -> PropertyDefinition:
        return PropertyDefinition(
            property_id=model.property_id,
            owner_kind=model.owner_kind,
            owner_type_name=model.owner_type_name,
            name=model.name,
            data_type=model.data_type,
            required=model.required,
            description=model.description,
            default_value=model.default_value,
            enum_values=model.enum_values,
        )


@dataclass(slots=True)
class PostgresSourceUnitRepository(SourceUnitRepository):
    session_factory: sessionmaker[Session]

    def add(self, source_unit: SourceUnit) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(source_unit))
            session.commit()

    def get(self, source_unit_id: str) -> SourceUnit | None:
        with self.session_factory() as session:
            model = session.get(SourceUnitModel, source_unit_id)
            return None if model is None else self._to_domain(model)

    def save(self, source_unit: SourceUnit) -> None:
        with self.session_factory() as session:
            model = session.get(SourceUnitModel, source_unit.source_unit_id)
            if model is None:
                session.add(self._to_model(source_unit))
            else:
                model.project_id = source_unit.project_id
                model.schema_version_id = source_unit.schema_version_id
                model.source_type = source_unit.source_type
                model.title = source_unit.title
                model.raw_content = source_unit.raw_content
                model.sequence_no = source_unit.sequence_no
                model.external_ref = source_unit.external_ref
                model.metadata_json = source_unit.metadata_json
                model.status = source_unit.status
                model.created_at = source_unit.created_at
            session.commit()

    def list_by_project(self, project_id: str) -> list[SourceUnit]:
        with self.session_factory() as session:
            statement = (
                select(SourceUnitModel)
                .where(SourceUnitModel.project_id == project_id)
                .order_by(SourceUnitModel.created_at.asc())
            )
            models = session.scalars(statement).all()
            source_units = [self._to_domain(model) for model in models]
            return sorted(
                source_units,
                key=lambda source_unit: (
                    source_unit.sequence_no is None,
                    source_unit.sequence_no or 0,
                    source_unit.created_at,
                    source_unit.title.casefold(),
                ),
            )

    def _to_model(self, source_unit: SourceUnit) -> SourceUnitModel:
        return SourceUnitModel(
            source_unit_id=source_unit.source_unit_id,
            project_id=source_unit.project_id,
            schema_version_id=source_unit.schema_version_id,
            source_type=source_unit.source_type,
            title=source_unit.title,
            raw_content=source_unit.raw_content,
            sequence_no=source_unit.sequence_no,
            external_ref=source_unit.external_ref,
            metadata_json=source_unit.metadata_json,
            status=source_unit.status,
            created_at=source_unit.created_at,
        )

    def _to_domain(self, model: SourceUnitModel) -> SourceUnit:
        return SourceUnit(
            source_unit_id=model.source_unit_id,
            project_id=model.project_id,
            schema_version_id=model.schema_version_id,
            source_type=model.source_type,
            title=model.title,
            raw_content=model.raw_content,
            sequence_no=model.sequence_no,
            external_ref=model.external_ref,
            metadata_json=model.metadata_json,
            status=model.status,
            created_at=model.created_at,
        )


@dataclass(slots=True)
class PostgresSegmentRepository(SegmentRepository):
    session_factory: sessionmaker[Session]

    def replace_for_source_unit(self, source_unit_id: str, segments: list[Segment]) -> None:
        with self.session_factory() as session:
            session.query(SegmentModel).filter(
                SegmentModel.source_unit_id == source_unit_id
            ).delete()
            session.add_all([self._to_model(segment) for segment in segments])
            session.commit()

    def list_by_source_unit(self, source_unit_id: str) -> list[Segment]:
        with self.session_factory() as session:
            statement = (
                select(SegmentModel)
                .where(SegmentModel.source_unit_id == source_unit_id)
                .order_by(SegmentModel.segment_order.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, segment: Segment) -> SegmentModel:
        return SegmentModel(
            segment_id=segment.segment_id,
            source_unit_id=segment.source_unit_id,
            segment_order=segment.segment_order,
            text=segment.text,
            metadata_json=segment.metadata_json,
        )

    def _to_domain(self, model: SegmentModel) -> Segment:
        return Segment(
            segment_id=model.segment_id,
            source_unit_id=model.source_unit_id,
            segment_order=model.segment_order,
            text=model.text,
            metadata_json=model.metadata_json,
        )


@dataclass(slots=True)
class PostgresProcessingRunRepository(ProcessingRunRepository):
    session_factory: sessionmaker[Session]

    def add(self, run: ProcessingRun) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(run))
            session.commit()

    def get(self, run_id: str) -> ProcessingRun | None:
        with self.session_factory() as session:
            model = session.get(ProcessingRunModel, run_id)
            return None if model is None else self._to_domain(model)

    def save(self, run: ProcessingRun) -> None:
        with self.session_factory() as session:
            model = session.get(ProcessingRunModel, run.run_id)
            if model is None:
                session.add(self._to_model(run))
            else:
                model.project_id = run.project_id
                model.schema_version_id = run.schema_version_id
                model.source_unit_id = run.source_unit_id
                model.pipeline_version = run.pipeline_version
                model.status = run.status
                model.llm_provider = run.llm_provider
                model.llm_model = run.llm_model
                model.created_at = run.created_at
                model.started_at = run.started_at
                model.ended_at = run.ended_at
            session.commit()

    def list_by_project(self, project_id: str) -> list[ProcessingRun]:
        with self.session_factory() as session:
            statement = (
                select(ProcessingRunModel)
                .where(ProcessingRunModel.project_id == project_id)
                .order_by(ProcessingRunModel.created_at.desc())
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, run: ProcessingRun) -> ProcessingRunModel:
        return ProcessingRunModel(
            run_id=run.run_id,
            project_id=run.project_id,
            schema_version_id=run.schema_version_id,
            source_unit_id=run.source_unit_id,
            pipeline_version=run.pipeline_version,
            status=run.status,
            llm_provider=run.llm_provider,
            llm_model=run.llm_model,
            created_at=run.created_at,
            started_at=run.started_at,
            ended_at=run.ended_at,
        )

    def _to_domain(self, model: ProcessingRunModel) -> ProcessingRun:
        return ProcessingRun(
            run_id=model.run_id,
            project_id=model.project_id,
            schema_version_id=model.schema_version_id,
            source_unit_id=model.source_unit_id,
            pipeline_version=model.pipeline_version,
            status=model.status,
            llm_provider=model.llm_provider,
            llm_model=model.llm_model,
            created_at=model.created_at,
            started_at=model.started_at,
            ended_at=model.ended_at,
        )


@dataclass(slots=True)
class PostgresPipelineDefinitionRepository(PipelineDefinitionRepository):
    session_factory: sessionmaker[Session]

    def add(self, pipeline_definition: PipelineDefinition) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(pipeline_definition))
            session.commit()

    def get_by_schema_version_and_version(
        self,
        *,
        schema_version_id: str,
        version: str,
    ) -> PipelineDefinition | None:
        with self.session_factory() as session:
            statement = select(PipelineDefinitionModel).where(
                PipelineDefinitionModel.schema_version_id == schema_version_id,
                PipelineDefinitionModel.version == version.strip(),
            )
            model = session.scalars(statement).first()
            return None if model is None else self._to_domain(model)

    def list_by_schema_version(self, schema_version_id: str) -> list[PipelineDefinition]:
        with self.session_factory() as session:
            statement = (
                select(PipelineDefinitionModel)
                .where(PipelineDefinitionModel.schema_version_id == schema_version_id)
                .order_by(
                    PipelineDefinitionModel.created_at.asc(),
                    PipelineDefinitionModel.version.asc(),
                )
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, pipeline_definition: PipelineDefinition) -> PipelineDefinitionModel:
        return PipelineDefinitionModel(
            pipeline_definition_id=pipeline_definition.pipeline_definition_id,
            schema_version_id=pipeline_definition.schema_version_id,
            version=pipeline_definition.version,
            description=pipeline_definition.description,
            steps_json=[
                {
                    "job_type": step.job_type.value,
                    "chain_on_success": [item.value for item in step.chain_on_success],
                }
                for step in pipeline_definition.steps
            ],
            created_at=pipeline_definition.created_at,
            updated_at=pipeline_definition.updated_at,
        )

    def _to_domain(self, model: PipelineDefinitionModel) -> PipelineDefinition:
        steps: list[PipelineStepDefinition] = []
        for raw_step in model.steps_json:
            job_type = ProcessingJobType(str(raw_step["job_type"]))
            raw_chain = raw_step.get("chain_on_success", [])
            if not isinstance(raw_chain, list):
                raw_chain = []
            chain_on_success = [
                ProcessingJobType(str(item))
                for item in raw_chain
                if isinstance(item, str)
            ]
            steps.append(
                PipelineStepDefinition(
                    job_type=job_type,
                    chain_on_success=chain_on_success,
                )
            )

        return PipelineDefinition(
            pipeline_definition_id=model.pipeline_definition_id,
            schema_version_id=model.schema_version_id,
            version=model.version,
            description=model.description,
            steps=steps,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@dataclass(slots=True)
class PostgresProcessingJobRepository(ProcessingJobRepository):
    session_factory: sessionmaker[Session]

    def add(self, job: ProcessingJob) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(job))
            session.commit()

    def get(self, job_id: str) -> ProcessingJob | None:
        with self.session_factory() as session:
            model = session.get(ProcessingJobModel, job_id)
            return None if model is None else self._to_domain(model)

    def save(self, job: ProcessingJob) -> None:
        with self.session_factory() as session:
            model = session.get(ProcessingJobModel, job.job_id)
            if model is None:
                session.add(self._to_model(job))
            else:
                model.project_id = job.project_id
                model.run_id = job.run_id
                model.source_unit_id = job.source_unit_id
                model.job_type = job.job_type
                model.status = job.status
                model.payload_json = job.payload_json
                model.output_json = job.output_json
                model.error_message = job.error_message
                model.attempt_count = job.attempt_count
                model.created_at = job.created_at
                model.started_at = job.started_at
                model.completed_at = job.completed_at
            session.commit()

    def list_by_run(self, run_id: str) -> list[ProcessingJob]:
        with self.session_factory() as session:
            statement = (
                select(ProcessingJobModel)
                .where(ProcessingJobModel.run_id == run_id)
                .order_by(
                    ProcessingJobModel.created_at.desc(),
                    ProcessingJobModel.job_id.desc(),
                )
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def claim_next(
        self,
        *,
        job_type: ProcessingJobType | None = None,
        run_id: str | None = None,
    ) -> ProcessingJob | None:
        with self.session_factory() as session:
            running_job = aliased(ProcessingJobModel)
            statement = (
                select(ProcessingJobModel)
                .where(ProcessingJobModel.status == ProcessingJobStatus.PENDING)
                .where(
                    ~select(running_job.job_id)
                    .where(running_job.run_id == ProcessingJobModel.run_id)
                    .where(running_job.status == ProcessingJobStatus.RUNNING)
                    .exists()
                )
                .where(
                    func.pg_try_advisory_xact_lock(
                        func.hashtext(ProcessingJobModel.run_id)
                    )
                )
                .order_by(
                    ProcessingJobModel.created_at.asc(),
                    ProcessingJobModel.job_id.asc(),
                )
                .with_for_update(skip_locked=True)
            )
            if job_type is not None:
                statement = statement.where(ProcessingJobModel.job_type == job_type)
            if run_id is not None:
                statement = statement.where(ProcessingJobModel.run_id == run_id)
            model = session.scalars(statement).first()
            if model is None:
                return None
            job = self._to_domain(model)
            mark_processing_job_running(job)
            model.status = job.status
            model.attempt_count = job.attempt_count
            model.started_at = job.started_at
            model.completed_at = job.completed_at
            model.error_message = job.error_message
            session.commit()
            return job

    def _to_model(self, job: ProcessingJob) -> ProcessingJobModel:
        return ProcessingJobModel(
            job_id=job.job_id,
            project_id=job.project_id,
            run_id=job.run_id,
            source_unit_id=job.source_unit_id,
            job_type=job.job_type,
            status=job.status,
            payload_json=job.payload_json,
            output_json=job.output_json,
            error_message=job.error_message,
            attempt_count=job.attempt_count,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )

    def _to_domain(self, model: ProcessingJobModel) -> ProcessingJob:
        return to_processing_job_domain(model)


@dataclass(slots=True)
class PostgresProcessingJobQueueRepository(ProcessingJobQueueRepository):
    session_factory: sessionmaker[Session]

    def get_project_processing_job_queue(
        self,
        project_id: str,
        *,
        status_filter: str,
        run_limit: int,
    ) -> ProjectProcessingJobQueue:
        with self.session_factory() as session:
            run_rows = session.execute(
                select(ProcessingRunModel, SourceUnitModel)
                .join(
                    SourceUnitModel,
                    ProcessingRunModel.source_unit_id == SourceUnitModel.source_unit_id,
                )
                .where(ProcessingRunModel.project_id == project_id)
                .order_by(ProcessingRunModel.created_at.desc())
            ).all()

            if not run_rows:
                return ProjectProcessingJobQueue(
                    project_id=project_id,
                    status_filter=status_filter,
                    run_limit=run_limit,
                )

            run_ids = [run.run_id for run, _ in run_rows]
            job_models = session.scalars(
                select(ProcessingJobModel)
                .where(ProcessingJobModel.run_id.in_(run_ids))
                .order_by(
                    ProcessingJobModel.created_at.desc(),
                    ProcessingJobModel.job_id.desc(),
                )
            ).all()

            jobs_by_run: dict[str, list[ProcessingJob]] = {}
            for model in job_models:
                jobs_by_run.setdefault(model.run_id, []).append(to_processing_job_domain(model))

            active_job_count = 0
            failed_job_count = 0
            succeeded_job_count = 0
            total_job_count = 0
            all_run_entries: list[ProcessingJobQueueRunEntry] = []

            for run_model, source_unit_model in run_rows:
                all_run_jobs = sort_processing_jobs(jobs_by_run.get(run_model.run_id, []))
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
                        run=self._to_run_domain(run_model),
                        source_unit=self._to_source_unit_domain(source_unit_model),
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

    def _to_run_domain(self, model: ProcessingRunModel) -> ProcessingRun:
        return ProcessingRun(
            run_id=model.run_id,
            project_id=model.project_id,
            schema_version_id=model.schema_version_id,
            source_unit_id=model.source_unit_id,
            pipeline_version=model.pipeline_version,
            status=model.status,
            llm_provider=model.llm_provider,
            llm_model=model.llm_model,
            created_at=model.created_at,
            started_at=model.started_at,
            ended_at=model.ended_at,
        )

    def _to_source_unit_domain(self, model: SourceUnitModel) -> SourceUnit:
        return SourceUnit(
            source_unit_id=model.source_unit_id,
            project_id=model.project_id,
            schema_version_id=model.schema_version_id,
            source_type=model.source_type,
            title=model.title,
            raw_content=model.raw_content,
            sequence_no=model.sequence_no,
            external_ref=model.external_ref,
            metadata_json=model.metadata_json,
            status=model.status,
            created_at=model.created_at,
        )


@dataclass(slots=True)
class PostgresStructuredPromptRepository(StructuredPromptRepository):
    session_factory: sessionmaker[Session]

    def upsert(self, prompt: StructuredPromptDefinition) -> None:
        normalized_prompt_key = prompt.prompt_key.strip().casefold()
        normalized_version = prompt.version.strip()
        with self.session_factory() as session:
            statement = select(StructuredPromptModel).where(
                StructuredPromptModel.prompt_key == normalized_prompt_key,
                StructuredPromptModel.version == normalized_version,
            )
            model = session.scalars(statement).first()
            if model is None:
                session.add(
                    StructuredPromptModel(
                        prompt_id=str(uuid4()),
                        prompt_key=normalized_prompt_key,
                        version=normalized_version,
                        schema_name=prompt.schema_name,
                        prompt_text=prompt.prompt_text,
                    )
                )
            else:
                model.schema_name = prompt.schema_name
                model.prompt_text = prompt.prompt_text
            session.commit()

    def get(
        self,
        *,
        prompt_key: str,
        version: str,
    ) -> StructuredPromptDefinition | None:
        normalized_prompt_key = prompt_key.strip().casefold()
        normalized_version = version.strip()
        with self.session_factory() as session:
            statement = select(StructuredPromptModel).where(
                StructuredPromptModel.prompt_key == normalized_prompt_key,
                StructuredPromptModel.version == normalized_version,
            )
            model = session.scalars(statement).first()
            return None if model is None else self._to_domain(model)

    def list(
        self,
        *,
        prompt_key: str | None = None,
    ) -> list[StructuredPromptDefinition]:
        with self.session_factory() as session:
            statement = select(StructuredPromptModel)
            if prompt_key is not None:
                statement = statement.where(
                    StructuredPromptModel.prompt_key == prompt_key.strip().casefold()
                )
            statement = statement.order_by(
                StructuredPromptModel.prompt_key.asc(),
                StructuredPromptModel.version.asc(),
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_domain(self, model: StructuredPromptModel) -> StructuredPromptDefinition:
        return StructuredPromptDefinition(
            prompt_key=model.prompt_key,
            version=model.version,
            schema_name=model.schema_name,
            prompt_text=model.prompt_text,
        )


@dataclass(slots=True)
class PostgresCandidateNodeRepository(CandidateNodeRepository):
    session_factory: sessionmaker[Session]

    def add(self, candidate_node: CandidateNode) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(candidate_node))
            session.commit()

    def get(self, candidate_node_id: str) -> CandidateNode | None:
        with self.session_factory() as session:
            model = session.get(CandidateNodeModel, candidate_node_id)
            return None if model is None else self._to_domain(model)

    def save(self, candidate_node: CandidateNode) -> None:
        with self.session_factory() as session:
            model = session.get(CandidateNodeModel, candidate_node.candidate_node_id)
            if model is None:
                session.add(self._to_model(candidate_node))
            else:
                model.run_id = candidate_node.run_id
                model.node_type = candidate_node.node_type
                model.properties_json = candidate_node.properties
                model.merge_key_payload = candidate_node.merge_key_payload
                model.confidence = candidate_node.confidence
                model.evidence_refs_json = self._serialize_evidence_refs(
                    candidate_node.evidence_refs
                )
                model.status = candidate_node.status
            session.commit()

    def list_by_run(self, run_id: str) -> list[CandidateNode]:
        with self.session_factory() as session:
            statement = (
                select(CandidateNodeModel)
                .where(CandidateNodeModel.run_id == run_id)
                .order_by(CandidateNodeModel.candidate_node_id.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, candidate_node: CandidateNode) -> CandidateNodeModel:
        return CandidateNodeModel(
            candidate_node_id=candidate_node.candidate_node_id,
            run_id=candidate_node.run_id,
            node_type=candidate_node.node_type,
            properties_json=candidate_node.properties,
            merge_key_payload=candidate_node.merge_key_payload,
            confidence=candidate_node.confidence,
            evidence_refs_json=self._serialize_evidence_refs(candidate_node.evidence_refs),
            status=candidate_node.status,
        )

    def _to_domain(self, model: CandidateNodeModel) -> CandidateNode:
        return CandidateNode(
            candidate_node_id=model.candidate_node_id,
            run_id=model.run_id,
            node_type=model.node_type,
            properties=model.properties_json,
            merge_key_payload=model.merge_key_payload,
            confidence=model.confidence,
            evidence_refs=self._deserialize_evidence_refs(model.evidence_refs_json),
            status=model.status,
        )

    def _serialize_evidence_refs(
        self,
        evidence_refs: list[EvidenceRef],
    ) -> list[dict[str, object]]:
        return [
            {
                "segment_id": evidence_ref.segment_id,
                "quote": evidence_ref.quote,
                "start_offset": evidence_ref.start_offset,
                "end_offset": evidence_ref.end_offset,
            }
            for evidence_ref in evidence_refs
        ]

    def _deserialize_evidence_refs(
        self,
        payload: list[dict[str, object]],
    ) -> list[EvidenceRef]:
        return [
            EvidenceRef(
                segment_id=str(item["segment_id"]),
                quote=self._as_optional_str(item.get("quote")),
                start_offset=self._as_optional_int(item.get("start_offset")),
                end_offset=self._as_optional_int(item.get("end_offset")),
            )
            for item in payload
        ]

    def _as_optional_str(self, value: object) -> str | None:
        return value if isinstance(value, str) else None

    def _as_optional_int(self, value: object) -> int | None:
        return value if isinstance(value, int) else None


@dataclass(slots=True)
class PostgresCandidateRelationRepository(CandidateRelationRepository):
    session_factory: sessionmaker[Session]

    def add(self, candidate_relation: CandidateRelation) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(candidate_relation))
            session.commit()

    def get(self, candidate_relation_id: str) -> CandidateRelation | None:
        with self.session_factory() as session:
            model = session.get(CandidateRelationModel, candidate_relation_id)
            return None if model is None else self._to_domain(model)

    def save(self, candidate_relation: CandidateRelation) -> None:
        with self.session_factory() as session:
            model = session.get(CandidateRelationModel, candidate_relation.candidate_relation_id)
            if model is None:
                session.add(self._to_model(candidate_relation))
            else:
                model.run_id = candidate_relation.run_id
                model.relation_type = candidate_relation.relation_type
                model.from_candidate_ref = candidate_relation.from_candidate_ref
                model.to_candidate_ref = candidate_relation.to_candidate_ref
                model.properties_json = candidate_relation.properties
                model.confidence = candidate_relation.confidence
                model.evidence_refs_json = self._serialize_evidence_refs(
                    candidate_relation.evidence_refs
                )
                model.status = candidate_relation.status
            session.commit()

    def list_by_run(self, run_id: str) -> list[CandidateRelation]:
        with self.session_factory() as session:
            statement = (
                select(CandidateRelationModel)
                .where(CandidateRelationModel.run_id == run_id)
                .order_by(CandidateRelationModel.candidate_relation_id.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, candidate_relation: CandidateRelation) -> CandidateRelationModel:
        return CandidateRelationModel(
            candidate_relation_id=candidate_relation.candidate_relation_id,
            run_id=candidate_relation.run_id,
            relation_type=candidate_relation.relation_type,
            from_candidate_ref=candidate_relation.from_candidate_ref,
            to_candidate_ref=candidate_relation.to_candidate_ref,
            properties_json=candidate_relation.properties,
            confidence=candidate_relation.confidence,
            evidence_refs_json=self._serialize_evidence_refs(candidate_relation.evidence_refs),
            status=candidate_relation.status,
        )

    def _to_domain(self, model: CandidateRelationModel) -> CandidateRelation:
        return CandidateRelation(
            candidate_relation_id=model.candidate_relation_id,
            run_id=model.run_id,
            relation_type=model.relation_type,
            from_candidate_ref=model.from_candidate_ref,
            to_candidate_ref=model.to_candidate_ref,
            properties=model.properties_json,
            confidence=model.confidence,
            evidence_refs=self._deserialize_evidence_refs(model.evidence_refs_json),
            status=model.status,
        )

    def _serialize_evidence_refs(
        self,
        evidence_refs: list[EvidenceRef],
    ) -> list[dict[str, object]]:
        return [
            {
                "segment_id": evidence_ref.segment_id,
                "quote": evidence_ref.quote,
                "start_offset": evidence_ref.start_offset,
                "end_offset": evidence_ref.end_offset,
            }
            for evidence_ref in evidence_refs
        ]

    def _deserialize_evidence_refs(
        self,
        payload: list[dict[str, object]],
    ) -> list[EvidenceRef]:
        return [
            EvidenceRef(
                segment_id=str(item["segment_id"]),
                quote=self._as_optional_str(item.get("quote")),
                start_offset=self._as_optional_int(item.get("start_offset")),
                end_offset=self._as_optional_int(item.get("end_offset")),
            )
            for item in payload
        ]

    def _as_optional_str(self, value: object) -> str | None:
        return value if isinstance(value, str) else None

    def _as_optional_int(self, value: object) -> int | None:
        return value if isinstance(value, int) else None


@dataclass(slots=True)
class PostgresExtractionExecutionRepository(ExtractionExecutionRepository):
    session_factory: sessionmaker[Session]

    def add(self, execution: ExtractionExecution) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(execution))
            session.commit()

    def save(self, execution: ExtractionExecution) -> None:
        with self.session_factory() as session:
            model = session.get(ExtractionExecutionModel, execution.execution_id)
            if model is None:
                session.add(self._to_model(execution))
            else:
                model.run_id = execution.run_id
                model.dry_run = execution.dry_run
                model.status = execution.status
                model.prompt_key = execution.prompt_key
                model.prompt_version = execution.prompt_version
                model.schema_name = execution.schema_name
                model.provider_name = execution.provider_name
                model.requested_llm_provider = execution.requested_llm_provider
                model.requested_llm_model = execution.requested_llm_model
                model.resolved_llm_model = execution.resolved_llm_model
                model.segment_count = execution.segment_count
                model.suggested_node_count = execution.suggested_node_count
                model.suggested_relation_count = execution.suggested_relation_count
                model.created_candidate_node_count = execution.created_candidate_node_count
                model.created_candidate_relation_count = (
                    execution.created_candidate_relation_count
                )
                model.error_message = execution.error_message
                model.started_at = execution.started_at
                model.completed_at = execution.completed_at
            session.commit()

    def list_by_run(self, run_id: str) -> list[ExtractionExecution]:
        with self.session_factory() as session:
            statement = (
                select(ExtractionExecutionModel)
                .where(ExtractionExecutionModel.run_id == run_id)
                .order_by(
                    ExtractionExecutionModel.started_at.desc(),
                    ExtractionExecutionModel.execution_id.desc(),
                )
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, execution: ExtractionExecution) -> ExtractionExecutionModel:
        return ExtractionExecutionModel(
            execution_id=execution.execution_id,
            run_id=execution.run_id,
            dry_run=execution.dry_run,
            status=execution.status,
            prompt_key=execution.prompt_key,
            prompt_version=execution.prompt_version,
            schema_name=execution.schema_name,
            provider_name=execution.provider_name,
            requested_llm_provider=execution.requested_llm_provider,
            requested_llm_model=execution.requested_llm_model,
            resolved_llm_model=execution.resolved_llm_model,
            segment_count=execution.segment_count,
            suggested_node_count=execution.suggested_node_count,
            suggested_relation_count=execution.suggested_relation_count,
            created_candidate_node_count=execution.created_candidate_node_count,
            created_candidate_relation_count=execution.created_candidate_relation_count,
            error_message=execution.error_message,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
        )

    def _to_domain(self, model: ExtractionExecutionModel) -> ExtractionExecution:
        return ExtractionExecution(
            execution_id=model.execution_id,
            run_id=model.run_id,
            dry_run=model.dry_run,
            status=model.status,
            prompt_key=model.prompt_key,
            prompt_version=model.prompt_version,
            schema_name=model.schema_name,
            provider_name=model.provider_name,
            requested_llm_provider=model.requested_llm_provider,
            requested_llm_model=model.requested_llm_model,
            resolved_llm_model=model.resolved_llm_model,
            segment_count=model.segment_count,
            suggested_node_count=model.suggested_node_count,
            suggested_relation_count=model.suggested_relation_count,
            created_candidate_node_count=model.created_candidate_node_count,
            created_candidate_relation_count=model.created_candidate_relation_count,
            error_message=model.error_message,
            started_at=model.started_at,
            completed_at=model.completed_at,
        )


@dataclass(slots=True)
class PostgresValidationResultRepository(ValidationResultRepository):
    session_factory: sessionmaker[Session]

    def replace_for_run(self, run_id: str, results: list[ValidationResult]) -> None:
        with self.session_factory() as session:
            session.query(ValidationResultModel).filter(
                ValidationResultModel.run_id == run_id
            ).delete()
            session.add_all([self._to_model(result) for result in results])
            session.commit()

    def list_by_run(self, run_id: str) -> list[ValidationResult]:
        with self.session_factory() as session:
            statement = (
                select(ValidationResultModel)
                .where(ValidationResultModel.run_id == run_id)
                .order_by(ValidationResultModel.validation_result_id.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, result: ValidationResult) -> ValidationResultModel:
        return ValidationResultModel(
            validation_result_id=result.validation_result_id,
            run_id=result.run_id,
            candidate_ref=result.candidate_ref,
            rule_code=result.rule_code,
            severity=result.severity,
            result=result.result,
            message=result.message,
        )

    def _to_domain(self, model: ValidationResultModel) -> ValidationResult:
        return ValidationResult(
            validation_result_id=model.validation_result_id,
            run_id=model.run_id,
            candidate_ref=model.candidate_ref,
            rule_code=model.rule_code,
            severity=model.severity,
            result=model.result,
            message=model.message,
        )


@dataclass(slots=True)
class PostgresReviewItemRepository(ReviewItemRepository):
    session_factory: sessionmaker[Session]

    def get(self, review_item_id: str) -> ReviewItem | None:
        with self.session_factory() as session:
            model = session.get(ReviewItemModel, review_item_id)
            return None if model is None else self._to_domain(model)

    def save(self, item: ReviewItem) -> None:
        with self.session_factory() as session:
            model = session.get(ReviewItemModel, item.review_item_id)
            if model is None:
                session.add(self._to_model(item))
            else:
                model.run_id = item.run_id
                model.item_type = item.item_type
                model.item_ref = item.item_ref
                model.reason_code = item.reason_code
                model.payload_json = item.payload_json
                model.status = item.status
                model.reviewer_note = item.reviewer_note
                model.created_at = item.created_at
            session.commit()

    def replace_for_run(self, run_id: str, items: list[ReviewItem]) -> None:
        with self.session_factory() as session:
            session.query(ReviewItemModel).filter(ReviewItemModel.run_id == run_id).delete()
            session.add_all([self._to_model(item) for item in items])
            session.commit()

    def list_by_run(self, run_id: str) -> list[ReviewItem]:
        with self.session_factory() as session:
            statement = (
                select(ReviewItemModel)
                .where(ReviewItemModel.run_id == run_id)
                .order_by(ReviewItemModel.created_at.asc())
            )
            models = session.scalars(statement).all()
            return [self._to_domain(model) for model in models]

    def _to_model(self, item: ReviewItem) -> ReviewItemModel:
        return ReviewItemModel(
            review_item_id=item.review_item_id,
            run_id=item.run_id,
            item_type=item.item_type,
            item_ref=item.item_ref,
            reason_code=item.reason_code,
            payload_json=item.payload_json,
            status=item.status,
            reviewer_note=item.reviewer_note,
            created_at=item.created_at,
        )

    def _to_domain(self, model: ReviewItemModel) -> ReviewItem:
        return ReviewItem(
            review_item_id=model.review_item_id,
            run_id=model.run_id,
            item_type=model.item_type,
            item_ref=model.item_ref,
            reason_code=model.reason_code,
            payload_json=model.payload_json,
            status=model.status,
            reviewer_note=model.reviewer_note,
            created_at=model.created_at,
        )


@dataclass(slots=True)
class PostgresReviewQueueRepository(ReviewQueueRepository):
    session_factory: sessionmaker[Session]

    def get_project_review_queue(
        self,
        project_id: str,
        *,
        status_filter: str,
        run_limit: int,
    ) -> ProjectReviewQueue:
        with self.session_factory() as session:
            run_rows = session.execute(
                select(ProcessingRunModel, SourceUnitModel)
                .join(
                    SourceUnitModel,
                    ProcessingRunModel.source_unit_id == SourceUnitModel.source_unit_id,
                )
                .where(ProcessingRunModel.project_id == project_id)
                .order_by(ProcessingRunModel.created_at.desc())
            ).all()

            if not run_rows:
                return ProjectReviewQueue(
                    project_id=project_id,
                    status_filter=status_filter,
                    run_limit=run_limit,
                )

            run_ids = [run.run_id for run, _ in run_rows]
            review_item_models = session.scalars(
                select(ReviewItemModel)
                .where(ReviewItemModel.run_id.in_(run_ids))
                .order_by(ReviewItemModel.created_at.desc())
            ).all()

            review_items_by_run: dict[str, list[ReviewItem]] = {}
            for model in review_item_models:
                review_items_by_run.setdefault(model.run_id, []).append(
                    self._to_review_item_domain(model)
                )

            open_review_count = 0
            total_review_count = 0
            selected_run_specs: list[
                tuple[
                    ProcessingRunModel,
                    SourceUnitModel,
                    int,
                    int,
                    list[ReviewItem],
                ]
            ] = []
            filtered_run_count = 0

            for run_model, source_unit_model in run_rows:
                all_run_items = review_items_by_run.get(run_model.run_id, [])
                run_open_review_count = sum(
                    1 for review_item in all_run_items if review_item.status.value == "open"
                )
                run_total_review_count = len(all_run_items)
                open_review_count += run_open_review_count
                total_review_count += run_total_review_count

                filtered_review_items = sort_review_items(
                    filter_review_items(all_run_items, status_filter=status_filter)
                )
                if status_filter != "all" and not filtered_review_items:
                    continue

                filtered_run_count += 1
                if len(selected_run_specs) < run_limit:
                    selected_run_specs.append(
                        (
                            run_model,
                            source_unit_model,
                            run_open_review_count,
                            run_total_review_count,
                            filtered_review_items,
                        )
                    )

            selected_node_ids = {
                review_item.item_ref
                for _, _, _, _, review_items in selected_run_specs
                for review_item in review_items
                if review_item.item_type == "candidate_node"
            }
            selected_relation_ids = {
                review_item.item_ref
                for _, _, _, _, review_items in selected_run_specs
                for review_item in review_items
                if review_item.item_type == "candidate_relation"
            }

            candidate_relation_models = (
                session.scalars(
                    select(CandidateRelationModel).where(
                        CandidateRelationModel.candidate_relation_id.in_(selected_relation_ids)
                    )
                ).all()
                if selected_relation_ids
                else []
            )
            candidate_node_ids = set(selected_node_ids)
            candidate_node_ids.update(
                model.from_candidate_ref for model in candidate_relation_models
            )
            candidate_node_ids.update(
                model.to_candidate_ref for model in candidate_relation_models
            )
            candidate_node_models = (
                session.scalars(
                    select(CandidateNodeModel).where(
                        CandidateNodeModel.candidate_node_id.in_(candidate_node_ids)
                    )
                ).all()
                if candidate_node_ids
                else []
            )

            candidate_node_by_id = {
                model.candidate_node_id: self._to_candidate_node_domain(model)
                for model in candidate_node_models
            }
            candidate_relation_by_id = {
                model.candidate_relation_id: self._to_candidate_relation_domain(model)
                for model in candidate_relation_models
            }

            segment_ids = {
                str(evidence_ref.segment_id)
                for candidate in candidate_node_by_id.values()
                for evidence_ref in candidate.evidence_refs
            }
            segment_ids.update(
                str(evidence_ref.segment_id)
                for candidate in candidate_relation_by_id.values()
                for evidence_ref in candidate.evidence_refs
            )
            segment_models = (
                session.scalars(select(SegmentModel).where(SegmentModel.segment_id.in_(segment_ids)))
                .all()
                if segment_ids
                else []
            )
            segment_by_id = {
                model.segment_id: self._to_segment_domain(model)
                for model in segment_models
            }

            run_entries: list[ReviewQueueRunEntry] = []
            for (
                run_model,
                source_unit_model,
                run_open_review_count,
                run_total_review_count,
                filtered_review_items,
            ) in selected_run_specs:
                run = self._to_run_domain(run_model)
                source_unit = self._to_source_unit_domain(source_unit_model)
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

                run_entries.append(
                    ReviewQueueRunEntry(
                        run=run,
                        source_unit=source_unit,
                        review_items=queue_items,
                        open_review_count=run_open_review_count,
                        total_review_count=run_total_review_count,
                    )
                )

        return ProjectReviewQueue(
            project_id=project_id,
            run_entries=run_entries,
            status_filter=status_filter,
            run_limit=run_limit,
            open_review_count=open_review_count,
            total_review_count=total_review_count,
            filtered_run_count=filtered_run_count,
            returned_run_count=len(run_entries),
            returned_review_count=sum(len(run_entry.review_items) for run_entry in run_entries),
            has_more_runs=filtered_run_count > len(run_entries),
        )

    def _to_run_domain(self, model: ProcessingRunModel) -> ProcessingRun:
        return ProcessingRun(
            run_id=model.run_id,
            project_id=model.project_id,
            schema_version_id=model.schema_version_id,
            source_unit_id=model.source_unit_id,
            pipeline_version=model.pipeline_version,
            status=model.status,
            llm_provider=model.llm_provider,
            llm_model=model.llm_model,
            created_at=model.created_at,
            started_at=model.started_at,
            ended_at=model.ended_at,
        )

    def _to_source_unit_domain(self, model: SourceUnitModel) -> SourceUnit:
        return SourceUnit(
            source_unit_id=model.source_unit_id,
            project_id=model.project_id,
            schema_version_id=model.schema_version_id,
            source_type=model.source_type,
            title=model.title,
            raw_content=model.raw_content,
            sequence_no=model.sequence_no,
            external_ref=model.external_ref,
            metadata_json=model.metadata_json,
            status=model.status,
            created_at=model.created_at,
        )

    def _to_segment_domain(self, model: SegmentModel) -> Segment:
        return Segment(
            segment_id=model.segment_id,
            source_unit_id=model.source_unit_id,
            segment_order=model.segment_order,
            text=model.text,
            metadata_json=model.metadata_json,
        )

    def _to_review_item_domain(self, model: ReviewItemModel) -> ReviewItem:
        return ReviewItem(
            review_item_id=model.review_item_id,
            run_id=model.run_id,
            item_type=model.item_type,
            item_ref=model.item_ref,
            reason_code=model.reason_code,
            payload_json=model.payload_json,
            status=model.status,
            reviewer_note=model.reviewer_note,
            created_at=model.created_at,
        )

    def _to_candidate_node_domain(self, model: CandidateNodeModel) -> CandidateNode:
        return CandidateNode(
            candidate_node_id=model.candidate_node_id,
            run_id=model.run_id,
            node_type=model.node_type,
            properties=model.properties_json,
            merge_key_payload=model.merge_key_payload,
            confidence=model.confidence,
            evidence_refs=self._deserialize_evidence_refs(model.evidence_refs_json),
            status=model.status,
        )

    def _to_candidate_relation_domain(
        self,
        model: CandidateRelationModel,
    ) -> CandidateRelation:
        return CandidateRelation(
            candidate_relation_id=model.candidate_relation_id,
            run_id=model.run_id,
            relation_type=model.relation_type,
            from_candidate_ref=model.from_candidate_ref,
            to_candidate_ref=model.to_candidate_ref,
            properties=model.properties_json,
            confidence=model.confidence,
            evidence_refs=self._deserialize_evidence_refs(model.evidence_refs_json),
            status=model.status,
        )

    def _deserialize_evidence_refs(
        self,
        payload: list[dict[str, object]],
    ) -> list[EvidenceRef]:
        return [
            EvidenceRef(
                segment_id=str(item["segment_id"]),
                quote=self._as_optional_str(item.get("quote")),
                start_offset=self._as_optional_int(item.get("start_offset")),
                end_offset=self._as_optional_int(item.get("end_offset")),
            )
            for item in payload
        ]

    def _as_optional_str(self, value: object) -> str | None:
        return value if isinstance(value, str) else None

    def _as_optional_int(self, value: object) -> int | None:
        return value if isinstance(value, int) else None


@dataclass(slots=True)
class PostgresGraphDeltaRepository(GraphDeltaRepository):
    session_factory: sessionmaker[Session]

    def add(self, delta: GraphDelta) -> None:
        with self.session_factory() as session:
            session.add(self._to_model(delta))
            session.commit()

    def get_by_run(self, run_id: str) -> GraphDelta | None:
        with self.session_factory() as session:
            statement = select(GraphDeltaModel).where(GraphDeltaModel.run_id == run_id)
            model = session.scalars(statement).first()
            return None if model is None else self._to_domain(model)

    def _to_model(self, delta: GraphDelta) -> GraphDeltaModel:
        return GraphDeltaModel(
            delta_id=delta.delta_id,
            run_id=delta.run_id,
            project_id=delta.project_id,
            nodes_created=delta.nodes_created,
            nodes_merged=delta.nodes_merged,
            relations_created=delta.relations_created,
            relations_merged=delta.relations_merged,
            review_count=delta.review_count,
            rejected_count=delta.rejected_count,
            created_at=delta.created_at,
        )

    def _to_domain(self, model: GraphDeltaModel) -> GraphDelta:
        return GraphDelta(
            delta_id=model.delta_id,
            run_id=model.run_id,
            project_id=model.project_id,
            nodes_created=model.nodes_created,
            nodes_merged=model.nodes_merged,
            relations_created=model.relations_created,
            relations_merged=model.relations_merged,
            review_count=model.review_count,
            rejected_count=model.rejected_count,
            created_at=model.created_at,
        )
