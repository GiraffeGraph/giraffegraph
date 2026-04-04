from dataclasses import dataclass

from app.application.errors import NotFoundError
from app.application.ports.template_catalog import DomainTemplateCatalog
from app.domain.template.entities import DomainTemplate


@dataclass(slots=True)
class TemplateManagementService:
    template_catalog: DomainTemplateCatalog

    def list_templates(self) -> list[DomainTemplate]:
        return self.template_catalog.list()

    def get_template(self, template_id: str) -> DomainTemplate:
        template = self.template_catalog.get(template_id)
        if template is None:
            raise NotFoundError(f"Template '{template_id}' was not found.")
        return template
