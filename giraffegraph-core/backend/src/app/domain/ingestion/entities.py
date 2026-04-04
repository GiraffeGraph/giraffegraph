from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.enums import RunStatus, SourceUnitStatus


@dataclass(slots=True, kw_only=True)
class SourceUnit:
    source_unit_id: str
    project_id: str
    schema_version_id: str
    source_type: str
    title: str
    raw_content: str
    sequence_no: int | None = None
    external_ref: str | None = None
    metadata_json: dict[str, str] = field(default_factory=dict)
    status: SourceUnitStatus = SourceUnitStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True, kw_only=True)
class Segment:
    segment_id: str
    source_unit_id: str
    segment_order: int
    text: str
    metadata_json: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True, kw_only=True)
class ProcessingRun:
    run_id: str
    project_id: str
    schema_version_id: str
    source_unit_id: str
    pipeline_version: str
    status: RunStatus = RunStatus.PENDING
    llm_provider: str | None = None
    llm_model: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    ended_at: datetime | None = None
