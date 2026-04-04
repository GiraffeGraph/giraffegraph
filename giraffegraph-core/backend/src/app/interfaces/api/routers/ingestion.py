from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import ProcessingRunStartInput, SourceUnitCreateInput
from app.application.use_cases.ingestion_management import IngestionManagementService
from app.interfaces.api.dependencies import get_ingestion_management_service
from app.interfaces.api.mappers.ingestion import (
    to_processing_run_response,
    to_source_unit_response,
    to_source_unit_summary_response,
)
from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
    ProcessingRunStartRequest,
    SourceUnitCreateRequest,
    SourceUnitResponse,
    SourceUnitSummaryResponse,
)

router = APIRouter(tags=["ingestion"])
IngestionManagementServiceDep = Annotated[
    IngestionManagementService,
    Depends(get_ingestion_management_service),
]


@router.get(
    "/api/projects/{project_id}/source-units",
    response_model=list[SourceUnitSummaryResponse],
)
def list_source_units(
    project_id: str,
    service: IngestionManagementServiceDep,
) -> list[SourceUnitSummaryResponse]:
    return [
        to_source_unit_summary_response(source_unit)
        for source_unit in service.list_source_units(project_id)
    ]


@router.post(
    "/api/projects/{project_id}/source-units",
    response_model=SourceUnitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_source_unit(
    project_id: str,
    request: SourceUnitCreateRequest,
    service: IngestionManagementServiceDep,
) -> SourceUnitResponse:
    source_unit = service.create_source_unit(
        SourceUnitCreateInput(
            project_id=project_id,
            schema_version_id=request.schema_version_id,
            source_type=request.source_type,
            title=request.title,
            raw_content=request.raw_content,
            sequence_no=request.sequence_no,
            external_ref=request.external_ref,
            metadata_json=request.metadata_json,
        )
    )
    return to_source_unit_response(source_unit)


@router.get("/api/source-units/{source_unit_id}", response_model=SourceUnitResponse)
def get_source_unit(
    source_unit_id: str,
    service: IngestionManagementServiceDep,
) -> SourceUnitResponse:
    return to_source_unit_response(service.get_source_unit(source_unit_id))


@router.get("/api/projects/{project_id}/runs", response_model=list[ProcessingRunResponse])
def list_processing_runs(
    project_id: str,
    service: IngestionManagementServiceDep,
) -> list[ProcessingRunResponse]:
    return [to_processing_run_response(run) for run in service.list_processing_runs(project_id)]


@router.post(
    "/api/source-units/{source_unit_id}/runs",
    response_model=ProcessingRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_processing_run(
    source_unit_id: str,
    request: ProcessingRunStartRequest,
    service: IngestionManagementServiceDep,
) -> ProcessingRunResponse:
    run = service.start_processing_run(
        ProcessingRunStartInput(
            schema_version_id=request.schema_version_id,
            source_unit_id=source_unit_id,
            pipeline_version=request.pipeline_version,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
        )
    )
    return to_processing_run_response(run)


@router.get("/api/runs/{run_id}", response_model=ProcessingRunResponse)
def get_processing_run(
    run_id: str,
    service: IngestionManagementServiceDep,
) -> ProcessingRunResponse:
    return to_processing_run_response(service.get_processing_run(run_id))
