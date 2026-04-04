from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import (
    PipelineDefinitionCreateInput,
    PipelineStepDefinitionInput,
)
from app.application.use_cases.pipeline_definition_management import (
    PipelineDefinitionManagementService,
)
from app.interfaces.api.dependencies import get_pipeline_definition_management_service
from app.interfaces.api.mappers.pipeline_definitions import (
    to_pipeline_definition_response,
)
from app.interfaces.api.schemas.pipeline_definitions import (
    PipelineDefinitionCreateRequest,
    PipelineDefinitionResponse,
)

router = APIRouter(tags=["pipeline-definitions"])
PipelineDefinitionManagementServiceDep = Annotated[
    PipelineDefinitionManagementService,
    Depends(get_pipeline_definition_management_service),
]


@router.get(
    "/api/schema-versions/{schema_version_id}/pipeline-definitions",
    response_model=list[PipelineDefinitionResponse],
)
def list_pipeline_definitions(
    schema_version_id: str,
    service: PipelineDefinitionManagementServiceDep,
) -> list[PipelineDefinitionResponse]:
    return [
        to_pipeline_definition_response(item)
        for item in service.list_pipeline_definitions(schema_version_id)
    ]


@router.post(
    "/api/schema-versions/{schema_version_id}/pipeline-definitions",
    response_model=PipelineDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pipeline_definition(
    schema_version_id: str,
    request: PipelineDefinitionCreateRequest,
    service: PipelineDefinitionManagementServiceDep,
) -> PipelineDefinitionResponse:
    pipeline_definition = service.create_pipeline_definition(
        PipelineDefinitionCreateInput(
            schema_version_id=schema_version_id,
            version=request.version,
            description=request.description,
            steps=[
                PipelineStepDefinitionInput(
                    job_type=step.job_type,
                    chain_on_success=step.chain_on_success,
                )
                for step in request.steps
            ],
        )
    )
    return to_pipeline_definition_response(pipeline_definition)


@router.get(
    "/api/schema-versions/{schema_version_id}/pipeline-definitions/{version}",
    response_model=PipelineDefinitionResponse,
)
def get_pipeline_definition(
    schema_version_id: str,
    version: str,
    service: PipelineDefinitionManagementServiceDep,
) -> PipelineDefinitionResponse:
    return to_pipeline_definition_response(
        service.get_pipeline_definition(schema_version_id, version)
    )
