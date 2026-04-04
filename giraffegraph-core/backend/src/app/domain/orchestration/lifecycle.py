from datetime import UTC, datetime

from app.domain.orchestration.entities import ProcessingJob
from app.domain.shared.enums import ProcessingJobStatus


def mark_processing_job_running(job: ProcessingJob) -> None:
    job.status = ProcessingJobStatus.RUNNING
    job.attempt_count += 1
    job.started_at = datetime.now(UTC)
    job.completed_at = None
    job.error_message = None


def mark_processing_job_succeeded(
    job: ProcessingJob,
    *,
    output_json: dict[str, object],
) -> None:
    job.status = ProcessingJobStatus.SUCCEEDED
    job.output_json = output_json
    job.error_message = None
    job.completed_at = datetime.now(UTC)


def mark_processing_job_failed(job: ProcessingJob, *, error_message: str) -> None:
    job.status = ProcessingJobStatus.FAILED
    job.error_message = error_message
    job.completed_at = datetime.now(UTC)
