from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dto.contracts import (
    ProcessingJobCreateInput,
    ProcessingJobProcessNextInput,
)
from app.application.use_cases.processing_job_management import (
    ProcessingJobManagementService,
)
from app.application.use_cases.processing_job_queue_management import (
    ProcessingJobQueueService,
)
from app.interfaces.api.dependencies import (
    get_processing_job_management_service,
    get_processing_job_queue_service,
)
from app.interfaces.api.mappers.processing_jobs import (
    to_processing_job_response,
    to_project_processing_job_queue_response,
)
from app.interfaces.api.schemas.processing_jobs import (
    ProcessingJobCreateRequest,
    ProcessingJobProcessNextRequest,
    ProcessingJobProcessNextResponse,
    ProcessingJobResponse,
    ProjectProcessingJobQueueResponse,
)

router = APIRouter(tags=["processing-jobs"])
ProcessingJobManagementServiceDep = Annotated[
    ProcessingJobManagementService,
    Depends(get_processing_job_management_service),
]
ProcessingJobQueueServiceDep = Annotated[
    ProcessingJobQueueService,
    Depends(get_processing_job_queue_service),
]


@router.post(
    "/api/runs/{run_id}/processing-jobs",
    response_model=ProcessingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def enqueue_processing_job(
    run_id: str,
    request: ProcessingJobCreateRequest,
    service: ProcessingJobManagementServiceDep,
) -> ProcessingJobResponse:
    job = service.enqueue_job(
        ProcessingJobCreateInput(
            run_id=run_id,
            job_type=request.job_type,
            dry_run=request.dry_run,
            chain_on_success=request.chain_on_success,
        )
    )
    return to_processing_job_response(job)


@router.get(
    "/api/runs/{run_id}/processing-jobs",
    response_model=list[ProcessingJobResponse],
)
def list_processing_jobs(
    run_id: str,
    service: ProcessingJobManagementServiceDep,
) -> list[ProcessingJobResponse]:
    return [to_processing_job_response(job) for job in service.list_jobs(run_id)]


@router.get(
    "/api/projects/{project_id}/processing-jobs",
    response_model=ProjectProcessingJobQueueResponse,
)
def get_project_processing_jobs(
    project_id: str,
    service: ProcessingJobQueueServiceDep,
    status_filter: str = Query(default="active"),
    run_limit: int = Query(default=12, ge=1, le=100),
) -> ProjectProcessingJobQueueResponse:
    return to_project_processing_job_queue_response(
        service.get_project_processing_job_queue(
            project_id,
            status_filter=status_filter,
            run_limit=run_limit,
        )
    )


@router.post(
    "/api/processing-jobs/process-next",
    response_model=ProcessingJobProcessNextResponse,
)
def process_next_job(
    request: ProcessingJobProcessNextRequest,
    service: ProcessingJobManagementServiceDep,
) -> ProcessingJobProcessNextResponse:
    job = service.process_next_job(
        ProcessingJobProcessNextInput(
            job_type=request.job_type,
            run_id=request.run_id,
        )
    )
    if job is None:
        return ProcessingJobProcessNextResponse(processed=False, job=None)
    return ProcessingJobProcessNextResponse(
        processed=True,
        job=to_processing_job_response(job),
    )
