from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import (
    ProcessingRunStartInput,
    SourceUnitBulkCreateInput,
    SourceUnitBulkItemInput,
    SourceUnitCreateInput,
    SourceUnitProcessInput,
)
from app.application.use_cases.commit_management import CommitManagementService
from app.application.use_cases.extraction_management import ExtractionManagementService
from app.application.use_cases.ingestion_management import (
    IngestionManagementService,
    SourceUnitProcessingService,
)
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.application.use_cases.project_management import ProjectManagementService
from app.interfaces.api.dependencies import (
    get_commit_management_service,
    get_extraction_management_service,
    get_ingestion_management_service,
    get_pipeline_management_service,
    get_project_management_service,
)
from app.interfaces.api.mappers.ingestion import (
    to_processing_run_response,
    to_source_unit_bulk_create_response,
    to_source_unit_process_response,
    to_source_unit_response,
    to_source_unit_summary_response,
)
from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
    ProcessingRunStartRequest,
    SourceUnitBulkCreateRequest,
    SourceUnitBulkCreateResponse,
    SourceUnitCreateRequest,
    SourceUnitProcessRequest,
    SourceUnitProcessResponse,
    SourceUnitResponse,
    SourceUnitSummaryResponse,
)

router = APIRouter(tags=["ingestion"])
IngestionManagementServiceDep = Annotated[
    IngestionManagementService,
    Depends(get_ingestion_management_service),
]


def get_source_unit_processing_service(
    project_management_service: Annotated[
        ProjectManagementService,
        Depends(get_project_management_service),
    ],
    ingestion_management_service: IngestionManagementServiceDep,
    pipeline_management_service: Annotated[
        PipelineManagementService,
        Depends(get_pipeline_management_service),
    ],
    extraction_management_service: Annotated[
        ExtractionManagementService,
        Depends(get_extraction_management_service),
    ],
    commit_management_service: Annotated[
        CommitManagementService,
        Depends(get_commit_management_service),
    ],
) -> SourceUnitProcessingService:
    return SourceUnitProcessingService(
        project_management_service=project_management_service,
        ingestion_management_service=ingestion_management_service,
        pipeline_management_service=pipeline_management_service,
        extraction_management_service=extraction_management_service,
        commit_management_service=commit_management_service,
    )


SourceUnitProcessingServiceDep = Annotated[
    SourceUnitProcessingService,
    Depends(get_source_unit_processing_service),
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


@router.post(
    "/api/projects/{project_id}/source-units/bulk",
    response_model=SourceUnitBulkCreateResponse,
)
def bulk_create_source_units(
    project_id: str,
    request: SourceUnitBulkCreateRequest,
    service: IngestionManagementServiceDep,
) -> SourceUnitBulkCreateResponse:
    result = service.bulk_create_source_units(
        SourceUnitBulkCreateInput(
            project_id=project_id,
            schema_version_id=request.schema_version_id,
            source_type=request.source_type,
            items=[
                SourceUnitBulkItemInput(
                    external_ref=item.external_ref,
                    title=item.title,
                    raw_content=item.raw_content,
                )
                for item in request.items
            ],
        )
    )
    return to_source_unit_bulk_create_response(result)


@router.post(
    "/api/projects/{project_id}/source-units/process",
    response_model=SourceUnitProcessResponse,
)
def process_source_units(
    project_id: str,
    request: SourceUnitProcessRequest,
    service: SourceUnitProcessingServiceDep,
) -> SourceUnitProcessResponse:
    report = service.process_source_units(
        SourceUnitProcessInput(
            project_id=project_id,
            source_unit_ids=request.source_unit_ids,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
            segmentation_strategy=request.segmentation_strategy,
            pipeline_version=request.pipeline_version,
            commit=request.commit,
        )
    )
    return to_source_unit_process_response(report)


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
