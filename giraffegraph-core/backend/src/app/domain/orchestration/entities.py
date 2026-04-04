from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.enums import ProcessingJobStatus, ProcessingJobType


@dataclass(slots=True, kw_only=True)
class ProcessingJob:
    job_id: str
    project_id: str
    run_id: str
    source_unit_id: str
    job_type: ProcessingJobType
    status: ProcessingJobStatus = ProcessingJobStatus.PENDING
    payload_json: dict[str, object] = field(default_factory=dict)
    output_json: dict[str, object] = field(default_factory=dict)
    error_message: str | None = None
    attempt_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None

