from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import ProjectCreateInput
from app.application.use_cases.project_management import (
    ProjectManagementService,
    ProjectSetupService,
)
from app.application.use_cases.schema_management import SchemaManagementService
from app.interfaces.api.dependencies import (
    get_project_management_service,
    get_schema_management_service,
)
from app.interfaces.api.mappers.project import to_project_create_response, to_project_response
from app.interfaces.api.schemas.project import (
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectResponse,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])
ProjectManagementServiceDep = Annotated[
    ProjectManagementService,
    Depends(get_project_management_service),
]


def get_project_setup_service(
    project_management_service: ProjectManagementServiceDep,
    schema_management_service: Annotated[
        SchemaManagementService,
        Depends(get_schema_management_service),
    ],
) -> ProjectSetupService:
    return ProjectSetupService(
        project_management_service=project_management_service,
        schema_management_service=schema_management_service,
    )


ProjectSetupServiceDep = Annotated[ProjectSetupService, Depends(get_project_setup_service)]


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    service: ProjectManagementServiceDep,
) -> list[ProjectResponse]:
    return [to_project_response(project) for project in service.list_projects()]


@router.post("", response_model=ProjectCreateResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    service: ProjectSetupServiceDep,
) -> ProjectCreateResponse:
    result = service.create_project(
        ProjectCreateInput(
            name=request.name,
            description=request.description,
            template_id=request.template_id,
            apply_template_schema=request.apply_template_schema,
        )
    )
    return to_project_create_response(result)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    service: ProjectManagementServiceDep,
) -> ProjectResponse:
    return to_project_response(service.get_project(project_id))
