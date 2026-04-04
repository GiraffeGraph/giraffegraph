from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.enums import ProcessingJobType

DEFAULT_PIPELINE_VERSION = "v1"
DEFAULT_PIPELINE_DESCRIPTION = "Default extraction, validation, and commit pipeline."


@dataclass(slots=True, kw_only=True)
class PipelineStepDefinition:
    job_type: ProcessingJobType
    chain_on_success: list[ProcessingJobType] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class PipelineDefinition:
    pipeline_definition_id: str
    schema_version_id: str
    version: str
    description: str | None = None
    steps: list[PipelineStepDefinition] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


def build_default_pipeline_steps() -> list[PipelineStepDefinition]:
    return [
        PipelineStepDefinition(
            job_type=ProcessingJobType.EXTRACT_CANDIDATES,
            chain_on_success=[ProcessingJobType.VALIDATE_RUN],
        ),
        PipelineStepDefinition(
            job_type=ProcessingJobType.VALIDATE_RUN,
            chain_on_success=[ProcessingJobType.COMMIT_RUN],
        ),
        PipelineStepDefinition(
            job_type=ProcessingJobType.COMMIT_RUN,
            chain_on_success=[],
        ),
    ]
