from app.application.use_cases.project_management import ProjectCreationResult
from app.domain.project.entities import Project
from app.interfaces.api.schemas.project import (
    AppliedTemplateSchemaResponse,
    ProjectCreateResponse,
    ProjectResponse,
)


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


def to_project_create_response(result: ProjectCreationResult) -> ProjectCreateResponse:
    applied = result.template_schema
    return ProjectCreateResponse(
        **to_project_response(result.project).model_dump(),
        template_schema=(
            AppliedTemplateSchemaResponse(
                schema_version_id=applied.schema_version.schema_version_id,
                version_no=applied.schema_version.version_no,
                status=applied.schema_version.status,
                pipeline_version=applied.pipeline_version,
                segmentation_strategy=applied.segmentation_strategy,
            )
            if applied is not None
            else None
        ),
    )
