from app.domain.extraction.entities import (
    ExtractionExecution,
    ExtractionExecutionReport,
    SuggestedNode,
    SuggestedRelation,
)
from app.interfaces.api.mappers.pipeline import to_evidence_ref_response
from app.interfaces.api.schemas.extraction import (
    ExtractionExecutionAuditResponse,
    ExtractionExecutionResponse,
    FailedExtractionCallResponse,
    SchemaProposalResponse,
    SuggestedNodeResponse,
    SuggestedRelationResponse,
)


def to_extraction_execution_response(
    report: ExtractionExecutionReport,
) -> ExtractionExecutionResponse:
    return ExtractionExecutionResponse(
        execution_id=report.execution_id,
        run_id=report.run_id,
        dry_run=report.dry_run,
        prompt_version=report.prompt_version,
        schema_name=report.schema_name,
        provider_name=report.provider_name,
        requested_llm_provider=report.requested_llm_provider,
        requested_llm_model=report.requested_llm_model,
        resolved_llm_model=report.resolved_llm_model,
        segment_count=report.segment_count,
        suggested_nodes=[to_suggested_node_response(item) for item in report.suggested_nodes],
        suggested_relations=[
            to_suggested_relation_response(item) for item in report.suggested_relations
        ],
        created_candidate_node_ids=report.created_candidate_node_ids,
        created_candidate_relation_ids=report.created_candidate_relation_ids,
        call_count=report.call_count,
        failed_calls=[
            FailedExtractionCallResponse(
                segment_ids=item.segment_ids,
                error_message=item.error_message,
            )
            for item in report.failed_calls
        ],
        dropped_node_count=report.dropped_node_count,
        dropped_relation_count=report.dropped_relation_count,
        schema_proposals=[
            SchemaProposalResponse(
                reason_code=item.reason_code,
                kind=item.kind,
                type_name=item.type_name,
                property_name=item.property_name,
                count=item.count,
                sample_quote=item.sample_quote,
                sample_value=item.sample_value,
                dropped_relation_count=item.dropped_relation_count,
            )
            for item in report.schema_proposals
        ],
        started_at=report.started_at,
        completed_at=report.completed_at,
    )


def to_suggested_node_response(item: SuggestedNode) -> SuggestedNodeResponse:
    return SuggestedNodeResponse(
        ref=item.ref,
        node_type=item.node_type,
        properties=item.properties,
        merge_key_payload=item.merge_key_payload,
        confidence=item.confidence,
        evidence_refs=[to_evidence_ref_response(ref) for ref in item.evidence_refs],
    )


def to_suggested_relation_response(item: SuggestedRelation) -> SuggestedRelationResponse:
    return SuggestedRelationResponse(
        relation_type=item.relation_type,
        from_ref=item.from_ref,
        to_ref=item.to_ref,
        properties=item.properties,
        confidence=item.confidence,
        evidence_refs=[to_evidence_ref_response(ref) for ref in item.evidence_refs],
    )


def to_extraction_execution_audit_response(
    execution: ExtractionExecution,
) -> ExtractionExecutionAuditResponse:
    return ExtractionExecutionAuditResponse(
        execution_id=execution.execution_id,
        run_id=execution.run_id,
        dry_run=execution.dry_run,
        status=execution.status.value,
        prompt_key=execution.prompt_key,
        prompt_version=execution.prompt_version,
        schema_name=execution.schema_name,
        provider_name=execution.provider_name,
        requested_llm_provider=execution.requested_llm_provider,
        requested_llm_model=execution.requested_llm_model,
        resolved_llm_model=execution.resolved_llm_model,
        segment_count=execution.segment_count,
        suggested_node_count=execution.suggested_node_count,
        suggested_relation_count=execution.suggested_relation_count,
        created_candidate_node_count=execution.created_candidate_node_count,
        created_candidate_relation_count=execution.created_candidate_relation_count,
        error_message=execution.error_message,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
    )
