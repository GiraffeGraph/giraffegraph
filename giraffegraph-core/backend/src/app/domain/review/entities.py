from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.ingestion.entities import ProcessingRun, SourceUnit
from app.domain.shared.enums import ReviewStatus


@dataclass(slots=True, kw_only=True)
class ReviewItem:
    review_item_id: str
    run_id: str
    item_type: str
    item_ref: str
    reason_code: str
    payload_json: dict[str, object]
    status: ReviewStatus = ReviewStatus.OPEN
    reviewer_note: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True, kw_only=True)
class ReviewEvidenceSnippet:
    segment_id: str
    segment_order: int | None = None
    text: str | None = None
    quote: str | None = None


@dataclass(slots=True, kw_only=True)
class ReviewQueueItem:
    review_item: ReviewItem
    candidate_node: CandidateNode | None = None
    candidate_relation: CandidateRelation | None = None
    headline: str = ""
    confidence: float | None = None
    messages: list[str] = field(default_factory=list)
    evidence_snippets: list[ReviewEvidenceSnippet] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class ReviewQueueRunEntry:
    run: ProcessingRun
    source_unit: SourceUnit
    review_items: list[ReviewQueueItem] = field(default_factory=list)
    open_review_count: int = 0
    total_review_count: int = 0


@dataclass(slots=True, kw_only=True)
class ProjectReviewQueue:
    project_id: str
    run_entries: list[ReviewQueueRunEntry] = field(default_factory=list)
    status_filter: str = "all"
    run_limit: int = 0
    open_review_count: int = 0
    total_review_count: int = 0
    filtered_run_count: int = 0
    returned_run_count: int = 0
    returned_review_count: int = 0
    has_more_runs: bool = False
