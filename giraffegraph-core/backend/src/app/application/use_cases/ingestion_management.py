from dataclasses import dataclass, field
from uuid import uuid4

from app.application.dto.contracts import (
    ExtractionExecutionInput,
    ProcessingRunStartInput,
    SegmentGenerationInput,
    SourceUnitBulkCreateInput,
    SourceUnitCreateInput,
    SourceUnitProcessInput,
)
from app.application.errors import ApplicationError, NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    PipelineDefinitionRepository,
    ProcessingRunRepository,
    ProjectRepository,
    SchemaRepository,
    SourceUnitRepository,
)
from app.application.use_cases.commit_management import CommitManagementService
from app.application.use_cases.extraction_management import ExtractionManagementService
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.application.use_cases.project_management import ProjectManagementService
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.ingestion.lifecycle import reserve_source_for_run
from app.domain.shared.enums import (
    CandidateStatus,
    ReviewStatus,
    RunStatus,
    SchemaStatus,
    SourceUnitStatus,
)

DEFAULT_SEGMENTATION_STRATEGY = "paragraphs"


@dataclass(slots=True, kw_only=True)
class SourceUnitBulkItemResult:
    index: int
    external_ref: str
    status: str
    source_unit: SourceUnit | None = None
    detail: str | None = None


@dataclass(slots=True, kw_only=True)
class SourceUnitBulkCreateResult:
    project_id: str
    schema_version_id: str
    items: list[SourceUnitBulkItemResult] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class SourceUnitProcessingResult:
    source_unit_id: str
    status: str = "failed"
    external_ref: str | None = None
    run_id: str | None = None
    segment_count: int = 0
    candidate_node_count: int = 0
    candidate_relation_count: int = 0
    validated_node_count: int = 0
    validated_relation_count: int = 0
    open_review_count: int = 0
    failed_call_count: int = 0
    detail: str | None = None


@dataclass(slots=True, kw_only=True)
class SourceUnitProcessingReport:
    project_id: str
    segmentation_strategy: str
    llm_provider: str
    llm_model: str | None
    results: list[SourceUnitProcessingResult] = field(default_factory=list)


@dataclass(slots=True)
class IngestionManagementService:
    project_repository: ProjectRepository
    schema_repository: SchemaRepository
    source_unit_repository: SourceUnitRepository
    processing_run_repository: ProcessingRunRepository
    pipeline_definition_repository: PipelineDefinitionRepository

    def create_source_unit(self, payload: SourceUnitCreateInput) -> SourceUnit:
        self._require_project(payload.project_id)
        self._require_usable_schema(
            project_id=payload.project_id,
            schema_version_id=payload.schema_version_id,
            operation_name="Source units",
        )

        return self._persist_source_unit(payload)

    def bulk_create_source_units(
        self,
        payload: SourceUnitBulkCreateInput,
    ) -> SourceUnitBulkCreateResult:
        self._require_project(payload.project_id)
        schema_version_id = payload.schema_version_id
        if schema_version_id is None:
            active_schema = self.schema_repository.get_active_schema(payload.project_id)
            if active_schema is None:
                raise RuleViolationError(
                    f"Project '{payload.project_id}' has no active schema; activate one or "
                    "pass schema_version_id."
                )
            schema_version_id = active_schema.schema_version_id
        self._require_usable_schema(
            project_id=payload.project_id,
            schema_version_id=schema_version_id,
            operation_name="Source units",
        )

        stored_refs = {
            source_unit.external_ref
            for source_unit in self.source_unit_repository.list_by_project(payload.project_id)
            if source_unit.external_ref is not None
        }
        request_refs: set[str] = set()
        result = SourceUnitBulkCreateResult(
            project_id=payload.project_id,
            schema_version_id=schema_version_id,
        )
        for index, item in enumerate(payload.items):
            external_ref = item.external_ref
            duplicate_detail: str | None = None
            if external_ref in stored_refs:
                duplicate_detail = (
                    f"A source unit with external_ref '{external_ref}' already exists "
                    "in this project."
                )
            elif external_ref in request_refs:
                duplicate_detail = (
                    f"external_ref '{external_ref}' occurs more than once in this request."
                )
            if duplicate_detail is not None:
                result.items.append(
                    SourceUnitBulkItemResult(
                        index=index,
                        external_ref=external_ref,
                        status="duplicate",
                        detail=duplicate_detail,
                    )
                )
                continue
            request_refs.add(external_ref)
            title = item.title.strip() if item.title is not None else ""
            result.items.append(
                SourceUnitBulkItemResult(
                    index=index,
                    external_ref=external_ref,
                    status="created",
                    source_unit=self._persist_source_unit(
                        SourceUnitCreateInput(
                            project_id=payload.project_id,
                            schema_version_id=schema_version_id,
                            source_type=payload.source_type,
                            title=title or external_ref,
                            raw_content=item.raw_content,
                            external_ref=external_ref,
                        )
                    ),
                )
            )
        return result

    def list_source_units(self, project_id: str) -> list[SourceUnit]:
        self._require_project(project_id)
        return self.source_unit_repository.list_by_project(project_id)

    def get_source_unit(self, source_unit_id: str) -> SourceUnit:
        source_unit = self.source_unit_repository.get(source_unit_id)
        if source_unit is None:
            raise NotFoundError(f"Source unit '{source_unit_id}' was not found.")
        return source_unit

    def start_processing_run(self, payload: ProcessingRunStartInput) -> ProcessingRun:
        source_unit = self.get_source_unit(payload.source_unit_id)
        if source_unit.status == SourceUnitStatus.DRAFT:
            raise RuleViolationError("Processing runs can only start from ready source units.")
        if source_unit.status == SourceUnitStatus.PROCESSING:
            raise RuleViolationError("Source unit is already processing.")
        if source_unit.schema_version_id != payload.schema_version_id:
            raise RuleViolationError(
                "Processing runs must use the same schema version as their source unit."
            )

        self._require_usable_schema(
            project_id=source_unit.project_id,
            schema_version_id=payload.schema_version_id,
            operation_name="Processing runs",
        )
        self._require_pipeline_definition(
            schema_version_id=payload.schema_version_id,
            pipeline_version=payload.pipeline_version,
        )

        run = ProcessingRun(
            run_id=str(uuid4()),
            project_id=source_unit.project_id,
            schema_version_id=payload.schema_version_id,
            source_unit_id=source_unit.source_unit_id,
            pipeline_version=payload.pipeline_version.strip(),
            status=RunStatus.PENDING,
            llm_provider=self._normalize_optional(payload.llm_provider),
            llm_model=self._normalize_optional(payload.llm_model),
        )
        self.processing_run_repository.add(run)
        reserve_source_for_run(source_unit)
        self.source_unit_repository.save(source_unit)
        return run

    def list_processing_runs(self, project_id: str) -> list[ProcessingRun]:
        self._require_project(project_id)
        return self.processing_run_repository.list_by_project(project_id)

    def get_processing_run(self, run_id: str) -> ProcessingRun:
        run = self.processing_run_repository.get(run_id)
        if run is None:
            raise NotFoundError(f"Processing run '{run_id}' was not found.")
        return run

    def _persist_source_unit(self, payload: SourceUnitCreateInput) -> SourceUnit:
        source_unit = SourceUnit(
            source_unit_id=str(uuid4()),
            project_id=payload.project_id,
            schema_version_id=payload.schema_version_id,
            source_type=payload.source_type.strip(),
            title=payload.title.strip(),
            raw_content=payload.raw_content,
            sequence_no=payload.sequence_no,
            external_ref=self._normalize_optional(payload.external_ref),
            metadata_json=payload.metadata_json,
            status=SourceUnitStatus.READY,
        )
        self.source_unit_repository.add(source_unit)
        return source_unit

    def _require_project(self, project_id: str) -> None:
        if self.project_repository.get(project_id) is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")

    def _require_usable_schema(
        self,
        *,
        project_id: str,
        schema_version_id: str,
        operation_name: str,
    ) -> None:
        schema_version = self.schema_repository.get_schema_version(schema_version_id)
        if schema_version is None or schema_version.project_id != project_id:
            raise NotFoundError(f"Schema version '{schema_version_id}' was not found.")
        if schema_version.status == SchemaStatus.DRAFT:
            raise RuleViolationError(
                f"{operation_name} can only use published or active schema versions."
            )

    def _require_pipeline_definition(
        self,
        *,
        schema_version_id: str,
        pipeline_version: str,
    ) -> None:
        pipeline_definition = self.pipeline_definition_repository.get_by_schema_version_and_version(
            schema_version_id=schema_version_id,
            version=pipeline_version.strip(),
        )
        if pipeline_definition is None:
            raise RuleViolationError(
                "Processing runs require a pipeline definition for the requested pipeline version."
            )

    def _normalize_optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


@dataclass(slots=True)
class SourceUnitProcessingService:
    project_management_service: ProjectManagementService
    ingestion_management_service: IngestionManagementService
    pipeline_management_service: PipelineManagementService
    extraction_management_service: ExtractionManagementService
    commit_management_service: CommitManagementService

    def process_source_units(self, payload: SourceUnitProcessInput) -> SourceUnitProcessingReport:
        project = self.project_management_service.get_project(payload.project_id)
        strategy = self._resolve_strategy(payload.segmentation_strategy, project.template_id)
        provider_name = self._resolve_provider_name(payload.llm_provider)
        report = SourceUnitProcessingReport(
            project_id=project.project_id,
            segmentation_strategy=strategy,
            llm_provider=provider_name,
            llm_model=payload.llm_model,
        )
        for source_unit_id in payload.source_unit_ids:
            result = SourceUnitProcessingResult(source_unit_id=source_unit_id)
            report.results.append(result)
            try:
                self._process_source_unit(
                    result,
                    payload=payload,
                    strategy=strategy,
                    provider_name=provider_name,
                )
            except ApplicationError as exc:
                result.detail = str(exc)
        return report

    def _process_source_unit(
        self,
        result: SourceUnitProcessingResult,
        *,
        payload: SourceUnitProcessInput,
        strategy: str,
        provider_name: str,
    ) -> None:
        source_unit = self.ingestion_management_service.get_source_unit(result.source_unit_id)
        if source_unit.project_id != payload.project_id:
            raise NotFoundError(
                f"Source unit '{result.source_unit_id}' was not found in project "
                f"'{payload.project_id}'."
            )
        result.external_ref = source_unit.external_ref
        run_id = self.ingestion_management_service.start_processing_run(
            ProcessingRunStartInput(
                schema_version_id=source_unit.schema_version_id,
                source_unit_id=source_unit.source_unit_id,
                pipeline_version=payload.pipeline_version,
                llm_provider=provider_name,
                llm_model=payload.llm_model,
            )
        ).run_id
        result.run_id = run_id
        result.segment_count = len(self._ensure_segments(source_unit.source_unit_id, strategy))
        extraction = self.extraction_management_service.extract_candidates(
            run_id,
            ExtractionExecutionInput(),
        )
        result.failed_call_count = len(extraction.failed_calls)
        validation = self.pipeline_management_service.validate_run(run_id)
        result.candidate_node_count = len(validation.candidate_nodes)
        result.candidate_relation_count = len(validation.candidate_relations)
        result.validated_node_count = sum(
            candidate.status == CandidateStatus.VALIDATED
            for candidate in validation.candidate_nodes
        )
        result.validated_relation_count = sum(
            candidate.status == CandidateStatus.VALIDATED
            for candidate in validation.candidate_relations
        )
        result.open_review_count = sum(
            item.status == ReviewStatus.OPEN
            for item in self.pipeline_management_service.list_review_items(run_id)
        )
        if result.open_review_count > 0:
            result.status = "needs_review"
        elif payload.commit:
            self.commit_management_service.commit_run(run_id)
            result.status = "committed"
        else:
            result.status = "validated"

    def _ensure_segments(self, source_unit_id: str, strategy: str) -> list[Segment]:
        # Segments already cut with this strategy are kept: earlier runs quote them by id.
        segments = self.pipeline_management_service.list_segments(source_unit_id)
        if segments and all(
            segment.metadata_json.get("strategy") == strategy for segment in segments
        ):
            return segments
        return self.pipeline_management_service.generate_segments(
            SegmentGenerationInput(source_unit_id=source_unit_id, strategy=strategy)
        )

    def _resolve_strategy(self, requested_strategy: str | None, template_id: str | None) -> str:
        strategy = (requested_strategy or "").strip().casefold()
        if strategy == "":
            template_schema = self.project_management_service.get_template_schema(template_id)
            strategy = (
                template_schema.segmentation_strategy
                if template_schema is not None
                else DEFAULT_SEGMENTATION_STRATEGY
            )
        strategies = self.pipeline_management_service.segmentation_strategies
        if strategy not in strategies:
            raise RuleViolationError(
                "Segmentation strategy must be one of: " + ", ".join(sorted(strategies)) + "."
            )
        return strategy

    def _resolve_provider_name(self, requested_provider: str | None) -> str:
        provider_name = (
            requested_provider or self.extraction_management_service.default_llm_provider
        ).strip()
        if self.extraction_management_service.provider_registry.get(provider_name) is None:
            raise RuleViolationError(
                f"LLM provider '{provider_name}' is not configured for candidate extraction."
            )
        return provider_name
