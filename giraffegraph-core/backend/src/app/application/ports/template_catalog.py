from typing import Protocol

from app.application.dto.contracts import TemplateSchema
from app.domain.template.entities import DomainTemplate


class DomainTemplateCatalog(Protocol):
    def get(self, template_id: str) -> DomainTemplate | None: ...

    def list(self) -> list[DomainTemplate]: ...

    def get_default(self) -> DomainTemplate: ...

    def get_schema(self, template_id: str) -> TemplateSchema | None: ...
