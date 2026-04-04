from pydantic import BaseModel

from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
    SourceUnitSummaryResponse,
)
from app.interfaces.api.schemas.pipeline import (
    CandidateNodeResponse,
    CandidateRelationResponse,
    ReviewItemResponse,
)


class ReviewEvidenceSnippetResponse(BaseModel):
    segment_id: str
    segment_order: int | None
    text: str | None
    quote: str | None


class ReviewQueueItemResponse(BaseModel):
    review_item: ReviewItemResponse
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
