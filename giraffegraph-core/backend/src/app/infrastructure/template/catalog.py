from dataclasses import dataclass, field

from app.application.ports.template_catalog import DomainTemplateCatalog
from app.domain.template.entities import DomainTemplate

BLANK_TEMPLATE_ID = "blank"
STORY_TEMPLATE_ID = "story"

SYSTEM_DOMAIN_TEMPLATES = [
    DomainTemplate(
        template_id=BLANK_TEMPLATE_ID,
        name="Blank",
        slug=BLANK_TEMPLATE_ID,
        description="Start from an empty generic graph schema and configure everything manually.",
    ),
    DomainTemplate(
        template_id=STORY_TEMPLATE_ID,
        name="Story / Series / Film",
        slug=STORY_TEMPLATE_ID,
        description=(
            "Story-oriented starter template for transcripts, scripts, episodes, scenes, "
            "characters, events, and related narrative structures."
        ),
    ),
]


@dataclass(slots=True)
class StaticDomainTemplateCatalog(DomainTemplateCatalog):
    templates: dict[str, DomainTemplate] = field(default_factory=dict)
    default_template_id: str = BLANK_TEMPLATE_ID

    def __init__(
        self,
        *,
        templates: list[DomainTemplate],
        default_template_id: str = BLANK_TEMPLATE_ID,
    ) -> None:
        normalized_templates: dict[str, DomainTemplate] = {}
        for template in templates:
            normalized_templates[self._normalize(template.template_id)] = template
        normalized_default_template_id = self._normalize(default_template_id)
        if normalized_default_template_id not in normalized_templates:
            raise ValueError(
                f"Default template '{default_template_id}' is not registered in the catalog."
            )
        self.templates = normalized_templates
        self.default_template_id = normalized_default_template_id

    def get(self, template_id: str) -> DomainTemplate | None:
        normalized_template_id = self._normalize(template_id)
        if normalized_template_id == "":
            return None
        return self.templates.get(normalized_template_id)

    def list(self) -> list[DomainTemplate]:
        return sorted(
            self.templates.values(),
            key=lambda template: (template.is_system is False, template.name.casefold()),
        )

    def get_default(self) -> DomainTemplate:
        return self.templates[self.default_template_id]

    def _normalize(self, value: str) -> str:
        return value.strip().casefold()
