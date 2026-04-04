from app.domain.project.entities import Project
from app.interfaces.api.schemas.project import ProjectResponse


def to_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        project_id=project.project_id,
        name=project.name,
        description=project.description,
        template_id=project.template_id,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
