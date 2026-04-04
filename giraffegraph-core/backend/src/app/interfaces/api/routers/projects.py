from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import ProjectCreateInput
from app.application.use_cases.project_management import ProjectManagementService
from app.interfaces.api.dependencies import get_project_management_service
from app.interfaces.api.mappers.project import to_project_response
from app.interfaces.api.schemas.project import ProjectCreateRequest, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])
ProjectManagementServiceDep = Annotated[
    ProjectManagementService,
    Depends(get_project_management_service),
]


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    service: ProjectManagementServiceDep,
) -> list[ProjectResponse]:
    return [to_project_response(project) for project in service.list_projects()]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    service: ProjectManagementServiceDep,
) -> ProjectResponse:
    project = service.create_project(
        ProjectCreateInput(
            name=request.name,
            description=request.description,
            template_id=request.template_id,
        )
    )
    return to_project_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    service: ProjectManagementServiceDep,
) -> ProjectResponse:
    return to_project_response(service.get_project(project_id))
