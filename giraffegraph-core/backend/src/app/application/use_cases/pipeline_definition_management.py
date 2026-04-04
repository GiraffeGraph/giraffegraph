from dataclasses import dataclass
from uuid import uuid4

from app.application.dto.contracts import (
    PipelineDefinitionCreateInput,
    PipelineStepDefinitionInput,
)
from app.application.errors import ConflictError, NotFoundError, RuleViolationError
from app.application.ports.repositories import PipelineDefinitionRepository, SchemaRepository
from app.domain.orchestration.pipeline_definitions import (
    PipelineDefinition,
    PipelineStepDefinition,
)
from app.domain.schema.entities import SchemaVersion
from app.domain.shared.enums import ProcessingJobType, SchemaStatus


@dataclass(slots=True)
class PipelineDefinitionManagementService:
    schema_repository: SchemaRepository
    pipeline_definition_repository: PipelineDefinitionRepository

    def create_pipeline_definition(
        self,
        payload: PipelineDefinitionCreateInput,
    ) -> PipelineDefinition:
        schema_version = self._require_editable_schema(payload.schema_version_id)
        normalized_version = payload.version.strip()
        existing_definition = self.pipeline_definition_repository.get_by_schema_version_and_version(
            schema_version_id=schema_version.schema_version_id,
            version=normalized_version,
        )
        if existing_definition is not None:
            raise ConflictError(
                "Pipeline definition "
                f"'{normalized_version}' already exists in schema "
                f"'{schema_version.schema_version_id}'."
            )

        pipeline_definition = PipelineDefinition(
            pipeline_definition_id=str(uuid4()),
            schema_version_id=schema_version.schema_version_id,
            version=normalized_version,
            description=self._normalize_optional(payload.description),
            steps=self._build_steps(payload.steps),
        )
        self.pipeline_definition_repository.add(pipeline_definition)
        return pipeline_definition

    def list_pipeline_definitions(self, schema_version_id: str) -> list[PipelineDefinition]:
        self._require_schema(schema_version_id)
        return self.pipeline_definition_repository.list_by_schema_version(schema_version_id)

    def get_pipeline_definition(
        self,
        schema_version_id: str,
        version: str,
    ) -> PipelineDefinition:
        self._require_schema(schema_version_id)
        pipeline_definition = self.pipeline_definition_repository.get_by_schema_version_and_version(
            schema_version_id=schema_version_id,
            version=version.strip(),
        )
        if pipeline_definition is None:
            raise NotFoundError(
                f"Pipeline definition '{version}' was not found in schema '{schema_version_id}'."
            )
        return pipeline_definition

    def _build_steps(
        self,
        steps: list[PipelineStepDefinitionInput],
    ) -> list[PipelineStepDefinition]:
        normalized_steps: list[PipelineStepDefinition] = []
        seen_job_types: set[ProcessingJobType] = set()

        for step in steps:
            if step.job_type in seen_job_types:
                raise ConflictError(
                    f"Pipeline step '{step.job_type.value}' is defined more than once."
                )
            chain_on_success = self._normalize_chain_on_success(
                step.job_type,
                step.chain_on_success,
            )
            normalized_steps.append(
                PipelineStepDefinition(
                    job_type=step.job_type,
                    chain_on_success=chain_on_success,
                )
            )
            seen_job_types.add(step.job_type)

        defined_job_types = {step.job_type for step in normalized_steps}
        for normalized_step in normalized_steps:
            for chained_job_type in normalized_step.chain_on_success:
                if chained_job_type not in defined_job_types:
                    raise RuleViolationError(
                        "Pipeline definitions can only chain to steps "
                        "that are declared in the same definition."
                    )

        self._assert_acyclic(normalized_steps)
        return normalized_steps

    def _normalize_chain_on_success(
        self,
        current_job_type: ProcessingJobType,
        chain_on_success: list[ProcessingJobType],
    ) -> list[ProcessingJobType]:
        normalized: list[ProcessingJobType] = []
        seen: set[ProcessingJobType] = set()

        for job_type in chain_on_success:
            if job_type == current_job_type:
                raise RuleViolationError(
                    f"Pipeline step '{current_job_type.value}' cannot chain to itself."
                )
            if job_type in seen:
                continue
            normalized.append(job_type)
            seen.add(job_type)

        return normalized

    def _assert_acyclic(self, steps: list[PipelineStepDefinition]) -> None:
        graph = {step.job_type: step.chain_on_success for step in steps}
        visited: set[ProcessingJobType] = set()
        visiting: set[ProcessingJobType] = set()

        def visit(job_type: ProcessingJobType) -> None:
            if job_type in visited:
                return
            if job_type in visiting:
                raise RuleViolationError("Pipeline definitions cannot contain circular chains.")

            visiting.add(job_type)
            for child_job_type in graph.get(job_type, []):
                visit(child_job_type)
            visiting.remove(job_type)
            visited.add(job_type)

        for job_type in graph:
            visit(job_type)

    def _require_schema(self, schema_version_id: str) -> SchemaVersion:
        schema_version = self.schema_repository.get_schema_version(schema_version_id)
        if schema_version is None:
            raise NotFoundError(f"Schema version '{schema_version_id}' was not found.")
        return schema_version

    def _require_editable_schema(self, schema_version_id: str) -> SchemaVersion:
        schema_version = self._require_schema(schema_version_id)
        if schema_version.status != SchemaStatus.DRAFT:
            raise RuleViolationError("Only draft schema versions can be edited.")
        return schema_version

    def _normalize_optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
