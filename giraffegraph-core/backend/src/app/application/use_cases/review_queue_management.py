from dataclasses import dataclass

from app.application.errors import NotFoundError, RuleViolationError
from app.application.ports.repositories import ProjectRepository, ReviewQueueRepository
from app.domain.review.entities import ProjectReviewQueue


@dataclass(slots=True)
class ReviewQueueService:
    project_repository: ProjectRepository
    review_queue_repository: ReviewQueueRepository

    def get_project_review_queue(
        self,
        project_id: str,
        *,
        status_filter: str = "open",
        run_limit: int = 12,
    ) -> ProjectReviewQueue:
        project = self.project_repository.get(project_id)
        if project is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")
        normalized_status_filter = status_filter.strip().casefold()
        if normalized_status_filter not in {"open", "closed", "all"}:
            raise RuleViolationError(
                "Review queue status_filter must be one of: open, closed, all."
            )
        if run_limit < 1:
            raise RuleViolationError("Review queue run_limit must be at least 1.")

        return self.review_queue_repository.get_project_review_queue(
            project_id,
            status_filter=normalized_status_filter,
            run_limit=run_limit,
        )
