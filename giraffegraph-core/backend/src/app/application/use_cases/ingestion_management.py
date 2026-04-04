from dataclasses import dataclass
from uuid import uuid4

from app.application.dto.contracts import ProcessingRunStartInput, SourceUnitCreateInput
from app.application.errors import NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    PipelineDefinitionRepository,
    ProcessingRunRepository,
    ProjectRepository,
    SchemaRepository,
    SourceUnitRepository,
)
from app.domain.ingestion.entities import ProcessingRun, SourceUnit
from app.domain.ingestion.lifecycle import reserve_source_for_run
from app.domain.shared.enums import RunStatus, SchemaStatus, SourceUnitStatus


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
