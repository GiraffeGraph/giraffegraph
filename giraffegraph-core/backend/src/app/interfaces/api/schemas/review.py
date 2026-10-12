from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
    SourceUnitSummaryResponse,
)
from app.interfaces.api.schemas.pipeline import (
    CandidateNodeResponse,
    CandidateRelationResponse,
    ReviewDecisionRequest,
    ReviewItemResponse,
)


class ReviewerDecisionRequest(ReviewDecisionRequest):
    reviewer_id: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
    ]
    duration_ms: int | None = Field(default=None, ge=0, le=2_147_483_647)


class ReviewDecisionResponse(BaseModel):
    decision_id: str
    review_item_id: str
    run_id: str
    item_type: str
    item_ref: str
    action: str
    reviewer_id: str
    reviewer_note: str | None
    duration_ms: int | None
    before_json: dict[str, object] | None
    after_json: dict[str, object] | None
    decided_at: datetime


class ReviewItemWithDecisionsResponse(ReviewItemResponse):
    decisions: list[ReviewDecisionResponse]


class AcceptanceRecordResponse(BaseModel):
    candidate_type: str
    candidate_ref: str
    policy: str | None
    rule_code: str | None
    decision: ReviewDecisionResponse | None


class ReviewEvidenceSnippetResponse(BaseModel):
    segment_id: str
    segment_order: int | None
    text: str | None
    quote: str | None


class ReviewQueueItemResponse(BaseModel):
    review_item: ReviewItemWithDecisionsResponse
    candidate_node: CandidateNodeResponse | None
    candidate_relation: CandidateRelationResponse | None
    headline: str
    confidence: float | None
    messages: list[str]
    evidence_snippets: list[ReviewEvidenceSnippetResponse]


class ReviewQueueRunEntryResponse(BaseModel):
    run: ProcessingRunResponse
    source_unit: SourceUnitSummaryResponse
    review_items: list[ReviewQueueItemResponse]
    open_review_count: int
    total_review_count: int


class ProjectReviewQueueResponse(BaseModel):
    project_id: str
    run_entries: list[ReviewQueueRunEntryResponse]
    status_filter: str
    run_limit: int
    open_review_count: int
    total_review_count: int
    filtered_run_count: int
    returned_run_count: int
    returned_review_count: int
    has_more_runs: bool
