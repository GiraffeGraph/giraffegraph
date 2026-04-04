from typing import Protocol

from app.domain.template.entities import DomainTemplate


class DomainTemplateCatalog(Protocol):
    def get(self, template_id: str) -> DomainTemplate | None: ...

    def list(self) -> list[DomainTemplate]: ...

    def get_default(self) -> DomainTemplate: ...
