from dataclasses import dataclass
from uuid import uuid4

from app.application.dto.contracts import ProjectCreateInput, TemplateSchema
from app.application.errors import NotFoundError, RuleViolationError
from app.application.ports.repositories import ProjectRepository
from app.application.ports.template_catalog import DomainTemplateCatalog
from app.application.use_cases.schema_management import (
    AppliedTemplateSchema,
    SchemaManagementService,
)
from app.domain.project.entities import Project
from app.domain.shared.enums import ProjectStatus


@dataclass(slots=True)
class ProjectManagementService:
    project_repository: ProjectRepository
    template_catalog: DomainTemplateCatalog

    def create_project(self, payload: ProjectCreateInput) -> Project:
        template_id = self._resolve_template_id(payload.template_id)
        project = Project(
            project_id=str(uuid4()),
            name=payload.name.strip(),
            description=payload.description,
            template_id=template_id,
            status=ProjectStatus.ACTIVE,
        )
        self.project_repository.add(project)
        return project

    def list_projects(self) -> list[Project]:
        return self.project_repository.list()

    def get_project(self, project_id: str) -> Project:
        project = self.project_repository.get(project_id)
        if project is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")
        return project

    def get_template_schema(self, template_id: str | None) -> TemplateSchema | None:
        if template_id is None:
            return None
        return self.template_catalog.get_schema(template_id)

    def _resolve_template_id(self, template_id: str | None) -> str:
        normalized_template_id = template_id.strip() if template_id is not None else ""
        if normalized_template_id == "":
            return self.template_catalog.get_default().template_id

        template = self.template_catalog.get(normalized_template_id)
        if template is None:
            raise RuleViolationError(
                f"Unknown template '{normalized_template_id}'. Use a registered domain template."
            )
        return template.template_id


@dataclass(slots=True)
class ProjectCreationResult:
    project: Project
    template_schema: AppliedTemplateSchema | None = None


@dataclass(slots=True)
class ProjectSetupService:
    project_management_service: ProjectManagementService
    schema_management_service: SchemaManagementService

    def create_project(self, payload: ProjectCreateInput) -> ProjectCreationResult:
        project = self.project_management_service.create_project(payload)
        template_schema = (
            self.project_management_service.get_template_schema(project.template_id)
            if payload.apply_template_schema
            else None
        )
        if template_schema is None:
            return ProjectCreationResult(project=project)
        return ProjectCreationResult(
            project=project,
            template_schema=self.schema_management_service.apply_template_schema(
                project.project_id,
                template_schema,
            ),
        )
