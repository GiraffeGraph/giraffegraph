from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.shared.enums import ProcessingJobStatus, ProcessingJobType
from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
    SourceUnitSummaryResponse,
)


class ProcessingJobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_type: ProcessingJobType
    dry_run: bool = False
    chain_on_success: list[ProcessingJobType] | None = None


class ProcessingJobProcessNextRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_type: ProcessingJobType | None = None
    run_id: str | None = None


class ProcessingJobResponse(BaseModel):
    job_id: str
    project_id: str
    run_id: str
    source_unit_id: str
    job_type: ProcessingJobType
    status: ProcessingJobStatus
    payload_json: dict[str, object]
    output_json: dict[str, object]
    error_message: str | None
    attempt_count: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ProcessingJobProcessNextResponse(BaseModel):
    processed: bool
    job: ProcessingJobResponse | None = None


class ProcessingJobQueueRunEntryResponse(BaseModel):
    run: ProcessingRunResponse
    source_unit: SourceUnitSummaryResponse
    jobs: list[ProcessingJobResponse]
    active_job_count: int
    failed_job_count: int
    total_job_count: int


class ProjectProcessingJobQueueResponse(BaseModel):
    project_id: str
    run_entries: list[ProcessingJobQueueRunEntryResponse]
    status_filter: str
    run_limit: int
    active_job_count: int
    failed_job_count: int
    succeeded_job_count: int
    total_job_count: int
    filtered_run_count: int
    returned_run_count: int
    returned_job_count: int
    has_more_runs: bool
