from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.dto.contracts import ExtractionExecutionInput
from app.application.use_cases.extraction_management import ExtractionManagementService
from app.interfaces.api.dependencies import get_extraction_management_service
from app.interfaces.api.mappers.extraction import (
    to_extraction_execution_audit_response,
    to_extraction_execution_response,
)
from app.interfaces.api.schemas.extraction import (
    ExtractionExecutionAuditResponse,
    ExtractionExecutionRequest,
    ExtractionExecutionResponse,
)

router = APIRouter(tags=["extraction"])
ExtractionManagementServiceDep = Annotated[
    ExtractionManagementService,
    Depends(get_extraction_management_service),
]


@router.post(
    "/api/runs/{run_id}/extract-candidates",
    response_model=ExtractionExecutionResponse,
)
def extract_candidates(
    run_id: str,
    request: ExtractionExecutionRequest,
    service: ExtractionManagementServiceDep,
) -> ExtractionExecutionResponse:
    report = service.extract_candidates(
        run_id,
        ExtractionExecutionInput(dry_run=request.dry_run),
    )
    return to_extraction_execution_response(report)


@router.get(
    "/api/runs/{run_id}/extraction-executions",
    response_model=list[ExtractionExecutionAuditResponse],
)
def list_extraction_executions(
    run_id: str,
    service: ExtractionManagementServiceDep,
) -> list[ExtractionExecutionAuditResponse]:
    return [
        to_extraction_execution_audit_response(execution)
        for execution in service.list_executions(run_id)
    ]
