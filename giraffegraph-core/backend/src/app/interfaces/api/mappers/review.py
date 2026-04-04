from app.domain.review.entities import (
    ProjectReviewQueue,
    ReviewEvidenceSnippet,
    ReviewQueueItem,
    ReviewQueueRunEntry,
)
from app.interfaces.api.mappers.ingestion import (
    to_processing_run_response,
    to_source_unit_summary_response,
)
from app.interfaces.api.mappers.pipeline import (
    to_candidate_node_response,
    to_candidate_relation_response,
    to_review_item_response,
)
from app.interfaces.api.schemas.review import (
    ProjectReviewQueueResponse,
    ReviewEvidenceSnippetResponse,
    ReviewQueueItemResponse,
    ReviewQueueRunEntryResponse,
)


def to_project_review_queue_response(
    queue: ProjectReviewQueue,
) -> ProjectReviewQueueResponse:
    return ProjectReviewQueueResponse(
        project_id=queue.project_id,
        run_entries=[to_review_queue_run_entry_response(item) for item in queue.run_entries],
        status_filter=queue.status_filter,
        run_limit=queue.run_limit,
        open_review_count=queue.open_review_count,
        total_review_count=queue.total_review_count,
        filtered_run_count=queue.filtered_run_count,
        returned_run_count=queue.returned_run_count,
        returned_review_count=queue.returned_review_count,
        has_more_runs=queue.has_more_runs,
    )


def to_review_queue_run_entry_response(
    entry: ReviewQueueRunEntry,
) -> ReviewQueueRunEntryResponse:
    return ReviewQueueRunEntryResponse(
        run=to_processing_run_response(entry.run),
        source_unit=to_source_unit_summary_response(entry.source_unit),
        review_items=[to_review_queue_item_response(item) for item in entry.review_items],
        open_review_count=entry.open_review_count,
        total_review_count=entry.total_review_count,
    )


def to_review_queue_item_response(item: ReviewQueueItem) -> ReviewQueueItemResponse:
    return ReviewQueueItemResponse(
        review_item=to_review_item_response(item.review_item),
        candidate_node=(
            to_candidate_node_response(item.candidate_node)
            if item.candidate_node is not None
            else None
        ),
        candidate_relation=(
            to_candidate_relation_response(item.candidate_relation)
            if item.candidate_relation is not None
            else None
        ),
        headline=item.headline,
        confidence=item.confidence,
        messages=item.messages,
        evidence_snippets=[
            to_review_evidence_snippet_response(snippet)
            for snippet in item.evidence_snippets
        ],
    )


def to_review_evidence_snippet_response(
    snippet: ReviewEvidenceSnippet,
) -> ReviewEvidenceSnippetResponse:
    return ReviewEvidenceSnippetResponse(
        segment_id=snippet.segment_id,
        segment_order=snippet.segment_order,
        text=snippet.text,
        quote=snippet.quote,
    )
