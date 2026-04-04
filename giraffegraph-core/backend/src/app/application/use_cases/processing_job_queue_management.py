from dataclasses import dataclass

from app.application.errors import NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    ProcessingJobQueueRepository,
    ProjectRepository,
)
from app.domain.orchestration.queue_views import ProjectProcessingJobQueue


@dataclass(slots=True)
class ProcessingJobQueueService:
    project_repository: ProjectRepository
    processing_job_queue_repository: ProcessingJobQueueRepository

    def get_project_processing_job_queue(
        self,
        project_id: str,
        *,
        status_filter: str = "active",
        run_limit: int = 12,
    ) -> ProjectProcessingJobQueue:
        project = self.project_repository.get(project_id)
        if project is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")

        normalized_status_filter = status_filter.strip().casefold()
        if normalized_status_filter not in {"active", "failed", "succeeded", "all"}:
            raise RuleViolationError(
                "Processing job queue status_filter must be one of: active, failed, "
                "succeeded, all."
            )
        if run_limit < 1:
            raise RuleViolationError("Processing job queue run_limit must be at least 1.")

        return self.processing_job_queue_repository.get_project_processing_job_queue(
            project_id,
            status_filter=normalized_status_filter,
            run_limit=run_limit,
        )
