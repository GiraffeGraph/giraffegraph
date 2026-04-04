from dataclasses import dataclass, field

from app.domain.ingestion.entities import ProcessingRun, SourceUnit
from app.domain.orchestration.entities import ProcessingJob
from app.domain.shared.enums import ProcessingJobStatus


@dataclass(slots=True, kw_only=True)
class ProcessingJobQueueRunEntry:
    run: ProcessingRun
    source_unit: SourceUnit
    jobs: list[ProcessingJob] = field(default_factory=list)
    active_job_count: int = 0
    failed_job_count: int = 0
    total_job_count: int = 0


@dataclass(slots=True, kw_only=True)
class ProjectProcessingJobQueue:
    project_id: str
    run_entries: list[ProcessingJobQueueRunEntry] = field(default_factory=list)
    status_filter: str = "all"
    run_limit: int = 0
    active_job_count: int = 0
    failed_job_count: int = 0
    succeeded_job_count: int = 0
    total_job_count: int = 0
    filtered_run_count: int = 0
    returned_run_count: int = 0
    returned_job_count: int = 0
    has_more_runs: bool = False


def filter_processing_jobs(
    jobs: list[ProcessingJob],
    *,
    status_filter: str,
) -> list[ProcessingJob]:
    if status_filter == "all":
        return list(jobs)
    if status_filter == "active":
        return [
            job
            for job in jobs
            if job.status in {ProcessingJobStatus.PENDING, ProcessingJobStatus.RUNNING}
        ]
    if status_filter == "failed":
        return [job for job in jobs if job.status == ProcessingJobStatus.FAILED]
    if status_filter == "succeeded":
        return [job for job in jobs if job.status == ProcessingJobStatus.SUCCEEDED]
    return []


def sort_processing_jobs(jobs: list[ProcessingJob]) -> list[ProcessingJob]:
    return sorted(
        jobs,
        key=lambda job: (job.created_at, job.job_id),
        reverse=True,
    )
