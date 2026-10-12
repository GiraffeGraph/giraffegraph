from app.domain.review.entities import (
    AcceptanceRecord,
    ProjectReviewQueue,
    ReviewDecision,
    ReviewEvidenceSnippet,
    ReviewItem,
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
    AcceptanceRecordResponse,
    ProjectReviewQueueResponse,
    ReviewDecisionResponse,
    ReviewEvidenceSnippetResponse,
    ReviewItemWithDecisionsResponse,
    ReviewQueueItemResponse,
    ReviewQueueRunEntryResponse,
)


def to_review_decision_response(decision: ReviewDecision) -> ReviewDecisionResponse:
    return ReviewDecisionResponse(
        decision_id=decision.decision_id,
        review_item_id=decision.review_item_id,
        run_id=decision.run_id,
        item_type=decision.item_type,
        item_ref=decision.item_ref,
        action=decision.action,
        reviewer_id=decision.reviewer_id,
        reviewer_note=decision.reviewer_note,
        duration_ms=decision.duration_ms,
        before_json=decision.before_json,
        after_json=decision.after_json,
        decided_at=decision.decided_at,
    )


def to_review_item_with_decisions_response(item: ReviewItem) -> ReviewItemWithDecisionsResponse:
    return ReviewItemWithDecisionsResponse(
        **to_review_item_response(item).model_dump(),
        decisions=[to_review_decision_response(decision) for decision in item.decisions],
    )


def to_acceptance_record_response(record: AcceptanceRecord) -> AcceptanceRecordResponse:
    return AcceptanceRecordResponse(
        candidate_type=record.candidate_type,
        candidate_ref=record.candidate_ref,
        policy=record.policy,
        rule_code=record.rule_code,
        decision=(
            to_review_decision_response(record.decision)
            if record.decision is not None
            else None
        ),
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
        review_item=to_review_item_with_decisions_response(item.review_item),
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
