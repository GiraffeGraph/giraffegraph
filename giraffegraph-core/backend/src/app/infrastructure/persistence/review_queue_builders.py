from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.ingestion.entities import Segment
from app.domain.review.entities import ReviewEvidenceSnippet, ReviewItem, ReviewQueueItem


def filter_review_items(
    items: list[ReviewItem],
    *,
    status_filter: str,
) -> list[ReviewItem]:
    if status_filter == "all":
        return list(items)
    if status_filter == "open":
        return [item for item in items if item.status.value == "open"]
    return [item for item in items if item.status.value != "open"]


def sort_review_items(items: list[ReviewItem]) -> list[ReviewItem]:
    return sorted(
        items,
        key=lambda item: (
            item.status.value != "open",
            -item.created_at.timestamp(),
        ),
    )


def build_review_queue_item(
    review_item: ReviewItem,
    *,
    candidate_node: CandidateNode | None,
    candidate_relation: CandidateRelation | None,
    candidate_node_by_id: dict[str, CandidateNode],
    segment_by_id: dict[str, Segment],
) -> ReviewQueueItem:
    return ReviewQueueItem(
        review_item=review_item,
        candidate_node=candidate_node,
        candidate_relation=candidate_relation,
        headline=_build_headline(
            review_item,
            candidate_node=candidate_node,
            candidate_relation=candidate_relation,
            candidate_node_by_id=candidate_node_by_id,
        ),
        confidence=_extract_confidence(
            review_item,
            candidate_node=candidate_node,
            candidate_relation=candidate_relation,
        ),
        messages=_extract_messages(review_item),
        evidence_snippets=_build_evidence_snippets(
            candidate_node=candidate_node,
            candidate_relation=candidate_relation,
            segment_by_id=segment_by_id,
        ),
    )


def _build_headline(
    review_item: ReviewItem,
    *,
    candidate_node: CandidateNode | None,
    candidate_relation: CandidateRelation | None,
    candidate_node_by_id: dict[str, CandidateNode],
) -> str:
    if candidate_node is not None:
        return _describe_candidate_node(candidate_node)

    if candidate_relation is not None:
        from_node = candidate_node_by_id.get(candidate_relation.from_candidate_ref)
        to_node = candidate_node_by_id.get(candidate_relation.to_candidate_ref)
        from_label = (
            _describe_candidate_node(from_node)
            if from_node is not None
            else candidate_relation.from_candidate_ref[:8]
        )
        to_label = (
            _describe_candidate_node(to_node)
            if to_node is not None
            else candidate_relation.to_candidate_ref[:8]
        )
        return f"{candidate_relation.relation_type} · {from_label} → {to_label}"

    return review_item.reason_code


def _describe_candidate_node(candidate: CandidateNode) -> str:
    primary_value = _primary_property_value(candidate.properties)
    if primary_value is not None:
        return f"{candidate.node_type} · {primary_value}"
    return f"{candidate.node_type} · {candidate.candidate_node_id[:8]}"


def _primary_property_value(properties: dict[str, object]) -> str | None:
    preferred_keys = ("name", "title", "label", "display_name", "slug", "id")
    for key in preferred_keys:
        value = properties.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    for value in properties.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_messages(review_item: ReviewItem) -> list[str]:
    messages = review_item.payload_json.get("messages")
    if not isinstance(messages, list):
        return []
    return [message for message in messages if isinstance(message, str)]


def _extract_confidence(
    review_item: ReviewItem,
    *,
    candidate_node: CandidateNode | None,
    candidate_relation: CandidateRelation | None,
) -> float | None:
    if candidate_node is not None:
        return candidate_node.confidence
    if candidate_relation is not None:
        return candidate_relation.confidence

    confidence = review_item.payload_json.get("confidence")
    if isinstance(confidence, int | float):
        return float(confidence)
    return None


def _build_evidence_snippets(
    *,
    candidate_node: CandidateNode | None,
    candidate_relation: CandidateRelation | None,
    segment_by_id: dict[str, Segment],
) -> list[ReviewEvidenceSnippet]:
    evidence_refs = []
    if candidate_node is not None:
        evidence_refs = candidate_node.evidence_refs
    elif candidate_relation is not None:
        evidence_refs = candidate_relation.evidence_refs

    snippets: list[ReviewEvidenceSnippet] = []
    for evidence_ref in evidence_refs:
        segment = segment_by_id.get(evidence_ref.segment_id)
        snippets.append(
            ReviewEvidenceSnippet(
                segment_id=evidence_ref.segment_id,
                segment_order=segment.segment_order if segment is not None else None,
                text=segment.text if segment is not None else None,
                quote=evidence_ref.quote,
            )
        )
    return snippets
