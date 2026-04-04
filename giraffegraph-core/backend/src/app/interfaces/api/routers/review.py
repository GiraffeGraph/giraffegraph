from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.dto.contracts import ReviewDecisionInput
from app.application.use_cases.review_management import ReviewManagementService
from app.application.use_cases.review_queue_management import ReviewQueueService
from app.interfaces.api.dependencies import (
    get_review_management_service,
    get_review_queue_service,
)
from app.interfaces.api.mappers.pipeline import to_review_item_response
from app.interfaces.api.mappers.review import to_project_review_queue_response
from app.interfaces.api.schemas.pipeline import ReviewDecisionRequest, ReviewItemResponse
from app.interfaces.api.schemas.review import ProjectReviewQueueResponse

router = APIRouter(tags=["review"])
ReviewManagementServiceDep = Annotated[
    ReviewManagementService,
    Depends(get_review_management_service),
]
ReviewQueueServiceDep = Annotated[ReviewQueueService, Depends(get_review_queue_service)]


@router.get(
    "/api/projects/{project_id}/review-queue",
    response_model=ProjectReviewQueueResponse,
)
def get_project_review_queue(
    project_id: str,
    service: ReviewQueueServiceDep,
    status_filter: str = Query(default="open"),
    run_limit: int = Query(default=12, ge=1, le=100),
) -> ProjectReviewQueueResponse:
    return to_project_review_queue_response(
        service.get_project_review_queue(
            project_id,
            status_filter=status_filter,
            run_limit=run_limit,
        )
    )


@router.get("/api/review-items/{review_item_id}", response_model=ReviewItemResponse)
def get_review_item(
    review_item_id: str,
    service: ReviewManagementServiceDep,
) -> ReviewItemResponse:
    return to_review_item_response(service.get_review_item(review_item_id))


@router.post("/api/review-items/{review_item_id}/decision", response_model=ReviewItemResponse)
def decide_review_item(
    review_item_id: str,
    request: ReviewDecisionRequest,
    service: ReviewManagementServiceDep,
) -> ReviewItemResponse:
    review_item = service.decide_review_item(
        review_item_id=review_item_id,
        payload=ReviewDecisionInput(
            action=request.action,
            reviewer_note=request.reviewer_note,
            node_type=request.node_type,
            relation_type=request.relation_type,
            from_candidate_ref=request.from_candidate_ref,
            to_candidate_ref=request.to_candidate_ref,
            properties=request.properties,
            merge_key_payload=request.merge_key_payload,
            confidence=request.confidence,
        ),
    )
    return to_review_item_response(review_item)
