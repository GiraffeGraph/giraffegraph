from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import (
    CandidateNodeInput,
    CandidateRelationInput,
    EvidenceRefInput,
    SegmentGenerationInput,
)
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.interfaces.api.dependencies import get_pipeline_management_service
from app.interfaces.api.mappers.pipeline import (
    to_candidate_node_response,
    to_candidate_relation_response,
    to_review_item_response,
    to_run_validation_response,
    to_segment_response,
    to_validation_result_response,
)
from app.interfaces.api.schemas.pipeline import (
    CandidateNodeCreateRequest,
    CandidateNodeResponse,
    CandidateRelationCreateRequest,
    CandidateRelationResponse,
    ReviewItemResponse,
    RunValidationResponse,
    SegmentGenerationRequest,
    SegmentResponse,
    ValidationResultResponse,
)

router = APIRouter(tags=["pipeline"])
PipelineManagementServiceDep = Annotated[
    PipelineManagementService,
    Depends(get_pipeline_management_service),
]


@router.post(
    "/api/source-units/{source_unit_id}/segments/generate",
    response_model=list[SegmentResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_segments(
    source_unit_id: str,
    request: SegmentGenerationRequest,
    service: PipelineManagementServiceDep,
) -> list[SegmentResponse]:
    segments = service.generate_segments(
        SegmentGenerationInput(
            source_unit_id=source_unit_id,
            strategy=request.strategy,
        )
    )
    return [to_segment_response(segment) for segment in segments]


@router.get("/api/source-units/{source_unit_id}/segments", response_model=list[SegmentResponse])
def list_segments(
    source_unit_id: str,
    service: PipelineManagementServiceDep,
) -> list[SegmentResponse]:
    return [to_segment_response(segment) for segment in service.list_segments(source_unit_id)]


@router.post(
    "/api/runs/{run_id}/candidate-nodes",
    response_model=CandidateNodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_candidate_node(
    run_id: str,
    request: CandidateNodeCreateRequest,
    service: PipelineManagementServiceDep,
) -> CandidateNodeResponse:
    candidate_node = service.add_candidate_node(
        run_id=run_id,
        payload=CandidateNodeInput(
            node_type=request.node_type,
            properties=request.properties,
            merge_key_payload=request.merge_key_payload,
            confidence=request.confidence,
            evidence_refs=[
                EvidenceRefInput(
                    segment_id=item.segment_id,
                    quote=item.quote,
                    start_offset=item.start_offset,
                    end_offset=item.end_offset,
                )
                for item in request.evidence_refs
            ],
        ),
    )
    return to_candidate_node_response(candidate_node)


@router.get("/api/runs/{run_id}/candidate-nodes", response_model=list[CandidateNodeResponse])
def list_candidate_nodes(
    run_id: str,
    service: PipelineManagementServiceDep,
) -> list[CandidateNodeResponse]:
    return [
        to_candidate_node_response(candidate_node)
        for candidate_node in service.list_candidate_nodes(run_id)
    ]


@router.post(
    "/api/runs/{run_id}/candidate-relations",
    response_model=CandidateRelationResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_candidate_relation(
    run_id: str,
    request: CandidateRelationCreateRequest,
    service: PipelineManagementServiceDep,
) -> CandidateRelationResponse:
    candidate_relation = service.add_candidate_relation(
        run_id=run_id,
        payload=CandidateRelationInput(
            relation_type=request.relation_type,
            from_candidate_ref=request.from_candidate_ref,
            to_candidate_ref=request.to_candidate_ref,
            properties=request.properties,
            confidence=request.confidence,
            evidence_refs=[
                EvidenceRefInput(
                    segment_id=item.segment_id,
                    quote=item.quote,
                    start_offset=item.start_offset,
                    end_offset=item.end_offset,
                )
                for item in request.evidence_refs
            ],
        ),
    )
    return to_candidate_relation_response(candidate_relation)


@router.get(
    "/api/runs/{run_id}/candidate-relations",
    response_model=list[CandidateRelationResponse],
)
def list_candidate_relations(
    run_id: str,
    service: PipelineManagementServiceDep,
) -> list[CandidateRelationResponse]:
    return [
        to_candidate_relation_response(candidate_relation)
        for candidate_relation in service.list_candidate_relations(run_id)
    ]


@router.post("/api/runs/{run_id}/validate", response_model=RunValidationResponse)
def validate_run(
    run_id: str,
    service: PipelineManagementServiceDep,
) -> RunValidationResponse:
    return to_run_validation_response(service.validate_run(run_id))


@router.post("/api/runs/{run_id}/resolve-duplicates", response_model=RunValidationResponse)
def resolve_duplicates(
    run_id: str,
    service: PipelineManagementServiceDep,
) -> RunValidationResponse:
    return to_run_validation_response(service.resolve_duplicates(run_id))


@router.get(
    "/api/runs/{run_id}/validation-results",
    response_model=list[ValidationResultResponse],
)
def list_validation_results(
    run_id: str,
    service: PipelineManagementServiceDep,
) -> list[ValidationResultResponse]:
    return [
        to_validation_result_response(result)
        for result in service.list_validation_results(run_id)
    ]


@router.get("/api/runs/{run_id}/review-items", response_model=list[ReviewItemResponse])
def list_review_items(
    run_id: str,
    service: PipelineManagementServiceDep,
) -> list[ReviewItemResponse]:
    return [to_review_item_response(item) for item in service.list_review_items(run_id)]
