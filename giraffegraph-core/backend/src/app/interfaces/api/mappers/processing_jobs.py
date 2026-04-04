from app.domain.orchestration.entities import ProcessingJob
from app.domain.orchestration.queue_views import (
    ProcessingJobQueueRunEntry,
    ProjectProcessingJobQueue,
)
from app.interfaces.api.mappers.ingestion import (
    to_processing_run_response,
    to_source_unit_summary_response,
)
from app.interfaces.api.schemas.processing_jobs import (
    ProcessingJobQueueRunEntryResponse,
    ProcessingJobResponse,
    ProjectProcessingJobQueueResponse,
)


def to_processing_job_response(job: ProcessingJob) -> ProcessingJobResponse:
    return ProcessingJobResponse(
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


def to_project_processing_job_queue_response(
    queue: ProjectProcessingJobQueue,
) -> ProjectProcessingJobQueueResponse:
    return ProjectProcessingJobQueueResponse(
        project_id=queue.project_id,
        run_entries=[
            to_processing_job_queue_run_entry_response(item) for item in queue.run_entries
        ],
        status_filter=queue.status_filter,
        run_limit=queue.run_limit,
        active_job_count=queue.active_job_count,
        failed_job_count=queue.failed_job_count,
        succeeded_job_count=queue.succeeded_job_count,
        total_job_count=queue.total_job_count,
        filtered_run_count=queue.filtered_run_count,
        returned_run_count=queue.returned_run_count,
        returned_job_count=queue.returned_job_count,
        has_more_runs=queue.has_more_runs,
    )


def to_processing_job_queue_run_entry_response(
    entry: ProcessingJobQueueRunEntry,
) -> ProcessingJobQueueRunEntryResponse:
    return ProcessingJobQueueRunEntryResponse(
        run=to_processing_run_response(entry.run),
        source_unit=to_source_unit_summary_response(entry.source_unit),
        jobs=[to_processing_job_response(job) for job in entry.jobs],
        active_job_count=entry.active_job_count,
        failed_job_count=entry.failed_job_count,
        total_job_count=entry.total_job_count,
    )
