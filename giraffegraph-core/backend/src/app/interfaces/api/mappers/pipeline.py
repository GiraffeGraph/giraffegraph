from app.application.use_cases.pipeline_management import RunValidationReport
from app.domain.extraction.entities import CandidateNode, CandidateRelation, EvidenceRef
from app.domain.ingestion.entities import Segment
from app.domain.review.entities import ReviewItem
from app.domain.shared.enums import CandidateStatus
from app.domain.validation.entities import ValidationResult
from app.interfaces.api.schemas.pipeline import (
    CandidateNodeResponse,
    CandidateRelationResponse,
    EvidenceRefResponse,
    ReviewItemResponse,
    RunValidationResponse,
    SegmentResponse,
    ValidationResultResponse,
)


def to_segment_response(segment: Segment) -> SegmentResponse:
    return SegmentResponse(
        segment_id=segment.segment_id,
        source_unit_id=segment.source_unit_id,
        segment_order=segment.segment_order,
        text=segment.text,
        metadata_json=segment.metadata_json,
    )


def to_candidate_node_response(candidate_node: CandidateNode) -> CandidateNodeResponse:
    return CandidateNodeResponse(
        candidate_node_id=candidate_node.candidate_node_id,
        run_id=candidate_node.run_id,
        node_type=candidate_node.node_type,
        properties=candidate_node.properties,
        merge_key_payload=candidate_node.merge_key_payload,
        confidence=candidate_node.confidence,
        evidence_refs=[to_evidence_ref_response(item) for item in candidate_node.evidence_refs],
        status=candidate_node.status,
    )


def to_candidate_relation_response(
    candidate_relation: CandidateRelation,
) -> CandidateRelationResponse:
    return CandidateRelationResponse(
        candidate_relation_id=candidate_relation.candidate_relation_id,
        run_id=candidate_relation.run_id,
        relation_type=candidate_relation.relation_type,
        from_candidate_ref=candidate_relation.from_candidate_ref,
        to_candidate_ref=candidate_relation.to_candidate_ref,
        properties=candidate_relation.properties,
        confidence=candidate_relation.confidence,
        evidence_refs=[to_evidence_ref_response(item) for item in candidate_relation.evidence_refs],
        status=candidate_relation.status,
    )


def to_validation_result_response(result: ValidationResult) -> ValidationResultResponse:
    return ValidationResultResponse(
        validation_result_id=result.validation_result_id,
        run_id=result.run_id,
        candidate_ref=result.candidate_ref,
        rule_code=result.rule_code,
        severity=result.severity,
        result=result.result,
        message=result.message,
    )


def to_review_item_response(item: ReviewItem) -> ReviewItemResponse:
    return ReviewItemResponse(
        review_item_id=item.review_item_id,
        run_id=item.run_id,
        item_type=item.item_type,
        item_ref=item.item_ref,
        reason_code=item.reason_code,
        payload_json=item.payload_json,
        status=item.status,
        reviewer_note=item.reviewer_note,
        created_at=item.created_at,
    )


def to_run_validation_response(report: RunValidationReport) -> RunValidationResponse:
    node_statuses = [candidate_node.status for candidate_node in report.candidate_nodes]
    relation_statuses = [
        candidate_relation.status for candidate_relation in report.candidate_relations
    ]
    return RunValidationResponse(
        run_id=report.run.run_id,
        node_total=len(report.candidate_nodes),
        node_validated=node_statuses.count(CandidateStatus.VALIDATED),
        node_review=node_statuses.count(CandidateStatus.REVIEW),
        node_rejected=node_statuses.count(CandidateStatus.REJECTED),
        relation_total=len(report.candidate_relations),
        relation_validated=relation_statuses.count(CandidateStatus.VALIDATED),
        relation_review=relation_statuses.count(CandidateStatus.REVIEW),
        relation_rejected=relation_statuses.count(CandidateStatus.REJECTED),
        validation_results=[
            to_validation_result_response(result) for result in report.validation_results
        ],
    )


def to_evidence_ref_response(evidence_ref: EvidenceRef) -> EvidenceRefResponse:
    return EvidenceRefResponse(
        segment_id=evidence_ref.segment_id,
        quote=evidence_ref.quote,
        start_offset=evidence_ref.start_offset,
        end_offset=evidence_ref.end_offset,
    )
